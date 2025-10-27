"""
Views for quiz and assessment functionality.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.core.cache import cache
from .models import (
    Quiz, Question, QuizAttempt, Answer, QuizResult,
    QuizSession, QuizFeedback, QuizAnalytics
)
from .serializers import (
    QuizSerializer, QuizDetailSerializer, QuizAttemptSerializer,
    QuizAttemptCreateSerializer, QuizSessionSerializer,
    SubmitAnswerSerializer, QuizResultSerializer,
    QuizFeedbackSerializer, QuizAnalyticsSerializer,
    QuizStatsSerializer
)
from apps.accounts.models import User
import logging
import uuid

logger = logging.getLogger(__name__)


class QuizListView(generics.ListAPIView):
    """List quizzes for a subject or grade level"""
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Quiz.objects.filter(is_active=True).select_related(
            'subject', 'lesson', 'created_by'
        ).prefetch_related('questions', 'attempts')
        
        # Filter by grade level for students
        if user.is_student() and user.grade_level:
            queryset = queryset.filter(grade_level=user.grade_level)
        
        # Filter by subject if provided
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        # Filter by lesson if provided
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        
        return queryset.order_by('-created_at')


class QuizDetailView(generics.RetrieveAPIView):
    """Get detailed quiz information"""
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Quiz.objects.filter(is_active=True).select_related(
            'subject', 'lesson'
        ).prefetch_related('questions')


class QuizAttemptListView(generics.ListAPIView):
    """List user's quiz attempts"""
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = QuizAttempt.objects.filter(student=user).select_related(
            'quiz__subject', 'quiz__lesson'
        ).prefetch_related('answers__question')
        
        # Filter by quiz if provided
        quiz_id = self.request.query_params.get('quiz')
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
        
        # Filter by completion status
        completed = self.request.query_params.get('completed')
        if completed is not None:
            if completed.lower() == 'true':
                queryset = queryset.filter(completed_at__isnull=False)
            else:
                queryset = queryset.filter(completed_at__isnull=True)
        
        return queryset.order_by('-started_at')


class QuizAttemptCreateView(generics.CreateAPIView):
    """Start a new quiz attempt"""
    serializer_class = QuizAttemptCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        return serializer.save()


class QuizSessionView(generics.RetrieveUpdateAPIView):
    """Manage active quiz session"""
    serializer_class = QuizSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizSession.objects.filter(
            student=self.request.user,
            is_active=True
        ).select_related('quiz')
    
    def get_object(self):
        session_key = self.kwargs.get('session_key')
        return QuizSession.objects.get(
            session_key=session_key,
            student=self.request.user,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_answer(request, session_key):
    """Submit an answer for the current question in a quiz session"""
    try:
        session = QuizSession.objects.get(
            session_key=session_key,
            student=request.user,
            is_active=True
        )
    except QuizSession.DoesNotExist:
        return Response({
            'error': 'Active quiz session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = SubmitAnswerSerializer(data=request.data)
    if serializer.is_valid():
        question_id = serializer.validated_data['question_id']
        answer_text = serializer.validated_data.get('answer_text', '')
        time_spent = serializer.validated_data.get('time_spent', 0)
        
        try:
            question = Question.objects.get(id=question_id, is_active=True)
        except Question.DoesNotExist:
            return Response({
                'error': 'Question not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if this is the current question
        questions = session.quiz.questions.filter(is_active=True).order_by('order_index')
        if session.current_question_index >= questions.count():
            return Response({
                'error': 'Quiz already completed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        current_question = questions[session.current_question_index]
        if current_question.id != question_id:
            return Response({
                'error': 'This is not the current question'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update answer
        answer, created = Answer.objects.get_or_create(
            attempt=session.attempt,
            question=question,
            defaults={
                'answer_text': answer_text,
                'time_spent': time_spent
            }
        )
        
        if not created:
            answer.answer_text = answer_text
            answer.time_spent = time_spent
            answer.save()
        
        # Check if answer is correct
        is_correct = check_answer_correctness(question, answer_text)
        answer.is_correct = is_correct
        answer.points_earned = question.points if is_correct else 0
        answer.save()
        
        # Update session
        session.current_question_index += 1
        session.answers_data[str(question_id)] = {
            'answer': answer_text,
            'is_correct': is_correct,
            'time_spent': time_spent
        }
        session.save()
        
        # Check if quiz is completed
        if session.current_question_index >= questions.count():
            complete_quiz_attempt(session)
        
        return Response({
            'message': 'Answer submitted successfully',
            'is_correct': is_correct,
            'explanation': question.explanation if is_correct else None,
            'next_question_index': session.current_question_index,
            'is_completed': session.current_question_index >= questions.count()
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_quiz(request, session_key):
    """Complete a quiz attempt"""
    try:
        session = QuizSession.objects.get(
            session_key=session_key,
            student=request.user,
            is_active=True
        )
    except QuizSession.DoesNotExist:
        return Response({
            'error': 'Active quiz session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Complete the quiz attempt
    attempt = complete_quiz_attempt(session)
    
    # Generate detailed result
    result = generate_quiz_result(attempt)
    
    return Response({
        'message': 'Quiz completed successfully',
        'attempt': QuizAttemptSerializer(attempt).data,
        'result': QuizResultSerializer(result).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def abandon_quiz(request, session_key):
    """Abandon a quiz attempt"""
    try:
        session = QuizSession.objects.get(
            session_key=session_key,
            student=request.user,
            is_active=True
        )
    except QuizSession.DoesNotExist:
        return Response({
            'error': 'Active quiz session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Mark attempt as abandoned
    attempt = session.attempt
    attempt.is_abandoned = True
    attempt.completed_at = timezone.now()
    attempt.save()
    
    # Deactivate session
    session.is_active = False
    session.save()
    
    logger.info(f"Quiz abandoned: {request.user.username} - {attempt.quiz.title}")
    
    return Response({
        'message': 'Quiz abandoned successfully'
    }, status=status.HTTP_200_OK)


class QuizFeedbackView(generics.ListCreateAPIView):
    """List and create quiz feedback"""
    serializer_class = QuizFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizFeedback.objects.filter(
            attempt__student=self.request.user
        ).select_related('attempt__quiz')
    
    def perform_create(self, serializer):
        attempt_id = self.request.data.get('attempt')
        if attempt_id:
            try:
                attempt = QuizAttempt.objects.get(
                    id=attempt_id,
                    student=self.request.user,
                    completed_at__isnull=False
                )
                serializer.save(attempt=attempt)
            except QuizAttempt.DoesNotExist:
                raise serializers.ValidationError("Invalid attempt ID")


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def quiz_stats(request):
    """Get user's quiz statistics"""
    user = request.user
    
    # Get user's attempts
    attempts = QuizAttempt.objects.filter(
        student=user,
        completed_at__isnull=False
    ).select_related('quiz__subject')
    
    if not attempts.exists():
        return Response({
            'total_quizzes': 0,
            'completed_quizzes': 0,
            'average_score': 0,
            'total_attempts': 0,
            'passed_quizzes': 0,
            'failed_quizzes': 0,
            'total_time_spent': 0,
            'favorite_subject': None,
            'improvement_areas': []
        })
    
    # Calculate statistics
    total_quizzes = Quiz.objects.filter(is_active=True).count()
    completed_quizzes = attempts.count()
    average_score = attempts.aggregate(avg_score=Avg('score'))['avg_score'] or 0
    total_attempts = QuizAttempt.objects.filter(student=user).count()
    passed_quizzes = attempts.filter(is_passed=True).count()
    failed_quizzes = completed_quizzes - passed_quizzes
    total_time_spent = attempts.aggregate(total_time=Sum('time_spent'))['total_time'] or 0
    
    # Find favorite subject
    subject_scores = {}
    for attempt in attempts:
        subject = attempt.quiz.subject.name
        if subject not in subject_scores:
            subject_scores[subject] = []
        subject_scores[subject].append(attempt.score)
    
    favorite_subject = None
    if subject_scores:
        avg_scores = {subject: sum(scores)/len(scores) for subject, scores in subject_scores.items()}
        favorite_subject = max(avg_scores, key=avg_scores.get)
    
    # Identify improvement areas
    improvement_areas = []
    low_score_attempts = attempts.filter(score__lt=70)
    if low_score_attempts.exists():
        subjects_needing_improvement = set()
        for attempt in low_score_attempts:
            subjects_needing_improvement.add(attempt.quiz.subject.name)
        improvement_areas = list(subjects_needing_improvement)
    
    stats = {
        'total_quizzes': total_quizzes,
        'completed_quizzes': completed_quizzes,
        'average_score': round(average_score, 2),
        'total_attempts': total_attempts,
        'passed_quizzes': passed_quizzes,
        'failed_quizzes': failed_quizzes,
        'total_time_spent': total_time_spent,
        'favorite_subject': favorite_subject,
        'improvement_areas': improvement_areas
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def quiz_analytics(request, quiz_id):
    """Get analytics for a specific quiz (teachers only)"""
    if not request.user.is_teacher():
        return Response({
            'error': 'Access denied. Teacher account required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        quiz = Quiz.objects.get(id=quiz_id, is_active=True)
    except Quiz.DoesNotExist:
        return Response({
            'error': 'Quiz not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create analytics
    analytics, created = QuizAnalytics.objects.get_or_create(quiz=quiz)
    analytics.update_analytics()
    
    serializer = QuizAnalyticsSerializer(analytics)
    return Response(serializer.data, status=status.HTTP_200_OK)


def check_answer_correctness(question, answer_text):
    """Check if the provided answer is correct"""
    if question.question_type == 'MULTIPLE_CHOICE':
        return answer_text.lower() == str(question.correct_answer).lower()
    elif question.question_type == 'TRUE_FALSE':
        return answer_text.lower() == str(question.correct_answer).lower()
    elif question.question_type == 'FILL_IN_BLANK':
        # For fill in the blank, check if answer is in the correct answers list
        correct_answers = question.correct_answer if isinstance(question.correct_answer, list) else [question.correct_answer]
        return answer_text.lower().strip() in [ans.lower().strip() for ans in correct_answers]
    elif question.question_type == 'SHORT_ANSWER':
        # For short answer, do a more flexible comparison
        correct_answer = str(question.correct_answer).lower()
        return answer_text.lower().strip() in correct_answer or correct_answer in answer_text.lower().strip()
    
    return False


def complete_quiz_attempt(session):
    """Complete a quiz attempt and calculate final score"""
    attempt = session.attempt
    attempt.completed_at = timezone.now()
    attempt.calculate_score()
    
    # Deactivate session
    session.is_active = False
    session.save()
    
    logger.info(f"Quiz completed: {attempt.student.username} - {attempt.quiz.title} - Score: {attempt.score}")
    
    return attempt


def generate_quiz_result(attempt):
    """Generate detailed quiz result and analytics"""
    # Calculate total time
    total_time = attempt.time_spent
    
    # Calculate average time per question
    total_questions = attempt.total_questions
    average_time_per_question = total_time / total_questions if total_questions > 0 else 0
    
    # Analyze performance by difficulty
    difficulty_breakdown = {}
    for answer in attempt.answers.all():
        difficulty = answer.question.difficulty_level
        if difficulty not in difficulty_breakdown:
            difficulty_breakdown[difficulty] = {'correct': 0, 'total': 0}
        difficulty_breakdown[difficulty]['total'] += 1
        if answer.is_correct:
            difficulty_breakdown[difficulty]['correct'] += 1
    
    # Generate improvement suggestions
    improvement_suggestions = []
    if attempt.score < 70:
        improvement_suggestions.append("Review the lesson content before retaking the quiz")
        improvement_suggestions.append("Focus on areas where you scored lower")
    
    # Create or update result
    result, created = QuizResult.objects.get_or_create(
        attempt=attempt,
        defaults={
            'total_time': total_time,
            'average_time_per_question': average_time_per_question,
            'difficulty_breakdown': difficulty_breakdown,
            'subject_areas': {},
            'improvement_suggestions': improvement_suggestions
        }
    )
    
    return result



"""
Serializers for quiz and assessment functionality.
"""
from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (
    Quiz, Question, QuizAttempt, Answer, QuizResult,
    QuizSession, QuizFeedback, QuizAnalytics
)
from apps.content.serializers import LessonSerializer, SubjectSerializer
from apps.accounts.serializers import UserProfileSerializer


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'question_type', 'options',
            'explanation', 'points', 'order_index', 'difficulty_level',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuestionWithAnswerSerializer(QuestionSerializer):
    """Serializer for Question with correct answer (for teachers)"""
    
    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['correct_answer']


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model"""
    subject = SubjectSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    attempt_count = serializers.SerializerMethodField()
    is_attempted = serializers.SerializerMethodField()
    best_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'lesson', 'subject', 'grade_level',
            'time_limit', 'max_attempts', 'passing_score', 'is_active',
            'is_premium', 'instructions', 'question_count', 'average_score',
            'attempt_count', 'is_attempted', 'best_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True).count()
    
    def get_average_score(self, obj):
        avg_score = obj.attempts.filter(
            completed_at__isnull=False
        ).aggregate(avg_score=Avg('score'))['avg_score']
        return round(avg_score, 2) if avg_score else 0
    
    def get_attempt_count(self, obj):
        return obj.attempts.count()
    
    def get_is_attempted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attempts.filter(student=request.user).exists()
        return False
    
    def get_best_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            best_attempt = obj.attempts.filter(
                student=request.user,
                completed_at__isnull=False
            ).order_by('-score').first()
            return best_attempt.score if best_attempt else None
        return None


class QuizDetailSerializer(QuizSerializer):
    """Detailed serializer for Quiz with questions"""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta(QuizSerializer.Meta):
        fields = QuizSerializer.Meta.fields + ['questions']


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model"""
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = Answer
        fields = [
            'id', 'question', 'answer_text', 'is_correct',
            'points_earned', 'time_spent', 'created_at'
        ]
        read_only_fields = ['id', 'is_correct', 'points_earned', 'created_at']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for QuizAttempt model"""
    student = UserProfileSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    time_spent_display = serializers.CharField(source='get_time_spent_display', read_only=True)
    score_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student', 'quiz', 'started_at', 'completed_at',
            'score', 'total_questions', 'correct_answers', 'time_spent',
            'time_spent_display', 'score_percentage', 'is_passed',
            'is_abandoned', 'answers'
        ]
        read_only_fields = [
            'id', 'student', 'started_at', 'completed_at', 'score',
            'total_questions', 'correct_answers', 'time_spent', 'is_passed'
        ]
    
    def get_score_percentage(self, obj):
        if obj.score is not None:
            return round(obj.score, 2)
        return None


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating quiz attempts"""
    
    class Meta:
        model = QuizAttempt
        fields = ['quiz']
    
    def create(self, validated_data):
        student = self.context['request'].user
        quiz = validated_data['quiz']
        
        # Check if student has reached max attempts
        attempt_count = QuizAttempt.objects.filter(
            student=student,
            quiz=quiz
        ).count()
        
        if attempt_count >= quiz.max_attempts:
            raise serializers.ValidationError(
                f"You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz."
            )
        
        # Check if student has an active session
        active_session = QuizSession.objects.filter(
            student=student,
            quiz=quiz,
            is_active=True
        ).first()
        
        if active_session:
            raise serializers.ValidationError(
                "You have an active quiz session. Please complete or abandon it first."
            )
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            student=student,
            quiz=quiz,
            total_questions=quiz.questions.filter(is_active=True).count()
        )
        
        # Create quiz session
        QuizSession.objects.create(
            student=student,
            quiz=quiz,
            session_key=f"{student.id}_{quiz.id}_{attempt.id}"
        )
        
        return attempt


class QuizSessionSerializer(serializers.ModelSerializer):
    """Serializer for QuizSession model"""
    quiz = QuizSerializer(read_only=True)
    current_question = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizSession
        fields = [
            'id', 'quiz', 'session_key', 'current_question_index',
            'current_question', 'progress', 'started_at', 'last_activity',
            'is_active'
        ]
        read_only_fields = [
            'id', 'session_key', 'started_at', 'last_activity', 'is_active'
        ]
    
    def get_current_question(self, obj):
        questions = obj.quiz.questions.filter(is_active=True).order_by('order_index')
        if obj.current_question_index < questions.count():
            question = questions[obj.current_question_index]
            return QuestionSerializer(question).data
        return None
    
    def get_progress(self, obj):
        total_questions = obj.quiz.questions.filter(is_active=True).count()
        if total_questions > 0:
            return round((obj.current_question_index / total_questions) * 100, 2)
        return 0


class SubmitAnswerSerializer(serializers.Serializer):
    """Serializer for submitting quiz answers"""
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField(required=False, allow_blank=True)
    time_spent = serializers.IntegerField(default=0)
    
    def validate_question_id(self, value):
        try:
            question = Question.objects.get(id=value, is_active=True)
            return value
        except Question.DoesNotExist:
            raise serializers.ValidationError("Invalid question ID")
    
    def validate(self, attrs):
        question = Question.objects.get(id=attrs['question_id'])
        
        # Validate answer based on question type
        if question.question_type == 'MULTIPLE_CHOICE':
            if not attrs.get('answer_text'):
                raise serializers.ValidationError("Answer is required for multiple choice questions")
        elif question.question_type == 'TRUE_FALSE':
            if attrs.get('answer_text') not in ['true', 'false', 'True', 'False']:
                raise serializers.ValidationError("Answer must be 'true' or 'false'")
        elif question.question_type in ['FILL_IN_BLANK', 'SHORT_ANSWER']:
            if not attrs.get('answer_text'):
                raise serializers.ValidationError("Answer text is required")
        
        return attrs


class QuizResultSerializer(serializers.ModelSerializer):
    """Serializer for QuizResult model"""
    attempt = QuizAttemptSerializer(read_only=True)
    
    class Meta:
        model = QuizResult
        fields = [
            'id', 'attempt', 'total_time', 'average_time_per_question',
            'difficulty_breakdown', 'subject_areas', 'improvement_suggestions',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuizFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for QuizFeedback model"""
    attempt = QuizAttemptSerializer(read_only=True)
    
    class Meta:
        model = QuizFeedback
        fields = [
            'id', 'attempt', 'rating', 'comment', 'difficulty_rating', 'created_at'
        ]
        read_only_fields = ['id', 'attempt', 'created_at']
    
    def create(self, validated_data):
        attempt_id = self.context['request'].data.get('attempt')
        if attempt_id:
            # Check if feedback already exists
            existing_feedback = QuizFeedback.objects.filter(attempt_id=attempt_id).first()
            if existing_feedback:
                # Update existing feedback
                for key, value in validated_data.items():
                    setattr(existing_feedback, key, value)
                existing_feedback.save()
                return existing_feedback
        
        return super().create(validated_data)


class QuizAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for QuizAnalytics model"""
    quiz = QuizSerializer(read_only=True)
    
    class Meta:
        model = QuizAnalytics
        fields = [
            'id', 'quiz', 'total_attempts', 'total_completions',
            'average_score', 'pass_rate', 'average_time',
            'difficulty_distribution', 'common_mistakes', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


class QuizStatsSerializer(serializers.Serializer):
    """Serializer for quiz statistics"""
    total_quizzes = serializers.IntegerField()
    completed_quizzes = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_attempts = serializers.IntegerField()
    passed_quizzes = serializers.IntegerField()
    failed_quizzes = serializers.IntegerField()
    total_time_spent = serializers.IntegerField()
    favorite_subject = serializers.CharField()
    improvement_areas = serializers.ListField(child=serializers.CharField())



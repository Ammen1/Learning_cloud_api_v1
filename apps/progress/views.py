"""
Views for progress tracking functionality.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Avg, Count, Sum, F
from django.utils import timezone
from datetime import timedelta, date
from .models import (
    StudentProgress, LearningStreak, SubjectProgress,
    GradeProgress, ProgressMilestone, ProgressReport,
    ParentDashboard
)
from .serializers import (
    StudentProgressSerializer, LearningStreakSerializer,
    SubjectProgressSerializer, GradeProgressSerializer,
    ProgressMilestoneSerializer, ProgressReportSerializer,
    ParentDashboardSerializer, ProgressStatsSerializer,
    WeeklyProgressSerializer, MonthlyProgressSerializer,
    ProgressComparisonSerializer
)
from apps.accounts.models import User
from apps.content.models import Lesson, Subject
from apps.quizzes.models import QuizAttempt
import logging

logger = logging.getLogger(__name__)


class StudentProgressListView(generics.ListAPIView):
    """List student's progress across all lessons"""
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = StudentProgress.objects.filter(student=user).select_related(
            'lesson__chapter__subject'
        ).prefetch_related('lesson__media_files')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(lesson__chapter__subject_id=subject_id)
        
        # Filter by grade level
        grade_level = self.request.query_params.get('grade_level')
        if grade_level:
            queryset = queryset.filter(lesson__chapter__subject__grade_level=grade_level)
        
        return queryset.order_by('-updated_at')


class StudentProgressDetailView(generics.RetrieveUpdateAPIView):
    """Get and update specific student progress"""
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return StudentProgress.objects.filter(student=self.request.user).select_related(
            'lesson__chapter__subject'
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_lesson_progress(request, lesson_id):
    """Update progress for a specific lesson"""
    try:
        lesson = Lesson.objects.get(id=lesson_id, is_active=True)
    except Lesson.DoesNotExist:
        return Response({
            'error': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if not user.is_student():
        return Response({
            'error': 'Only students can update lesson progress'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get or create progress record
    progress, created = StudentProgress.objects.get_or_create(
        student=user,
        lesson=lesson,
        defaults={'status': 'NOT_STARTED'}
    )
    
    # Update progress based on request data
    action = request.data.get('action')
    time_spent = request.data.get('time_spent', 0)
    last_position = request.data.get('last_position', 0)
    notes = request.data.get('notes', '')
    
    if action == 'start':
        progress.mark_started()
    elif action == 'complete':
        score = request.data.get('score')
        progress.mark_completed(score=score)
    elif action == 'pause':
        progress.status = 'PAUSED'
        progress.save(update_fields=['status', 'updated_at'])
    elif action == 'resume':
        progress.status = 'IN_PROGRESS'
        progress.save(update_fields=['status', 'updated_at'])
    
    # Update time spent and position
    if time_spent > 0:
        progress.update_time_spent(time_spent)
    
    if last_position > 0:
        progress.last_position = last_position
        progress.save(update_fields=['last_position', 'updated_at'])
    
    if notes:
        progress.notes = notes
        progress.save(update_fields=['notes', 'updated_at'])
    
    # Update learning streak
    update_learning_streak(user)
    
    # Check for milestones
    check_milestones(user, progress)
    
    # Update subject and grade progress
    update_subject_progress(user, lesson.chapter.subject)
    update_grade_progress(user)
    
    serializer = StudentProgressSerializer(progress)
    return Response(serializer.data, status=status.HTTP_200_OK)


class LearningStreakView(generics.RetrieveAPIView):
    """Get user's learning streak information"""
    serializer_class = LearningStreakSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        streak, created = LearningStreak.objects.get_or_create(
            student=self.request.user
        )
        return streak


class SubjectProgressListView(generics.ListAPIView):
    """List progress by subject"""
    serializer_class = SubjectProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = SubjectProgress.objects.filter(student=user).select_related('subject')
        
        # Filter by grade level
        grade_level = self.request.query_params.get('grade_level')
        if grade_level:
            queryset = queryset.filter(subject__grade_level=grade_level)
        
        return queryset.order_by('-updated_at')


class GradeProgressView(generics.RetrieveAPIView):
    """Get grade-level progress"""
    serializer_class = GradeProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        if not user.is_student() or not user.grade_level:
            return None
        
        progress, created = GradeProgress.objects.get_or_create(
            student=user,
            grade_level=user.grade_level
        )
        
        if created:
            progress.calculate_grade_progress()
        
        return progress


class ProgressMilestoneListView(generics.ListAPIView):
    """List user's progress milestones"""
    serializer_class = ProgressMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = ProgressMilestone.objects.filter(student=user)
        
        # Filter by milestone type
        milestone_type = self.request.query_params.get('type')
        if milestone_type:
            queryset = queryset.filter(milestone_type=milestone_type)
        
        # Filter by notification status
        is_notified = self.request.query_params.get('is_notified')
        if is_notified is not None:
            queryset = queryset.filter(is_notified=is_notified.lower() == 'true')
        
        return queryset.order_by('-achieved_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def progress_stats(request):
    """Get comprehensive progress statistics"""
    user = request.user
    
    if not user.is_student():
        return Response({
            'error': 'Only students can view progress statistics'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get basic progress data
    progress_records = StudentProgress.objects.filter(student=user)
    
    total_lessons = progress_records.count()
    completed_lessons = progress_records.filter(status='COMPLETED').count()
    in_progress_lessons = progress_records.filter(status='IN_PROGRESS').count()
    
    total_time_spent = progress_records.aggregate(
        total_time=Sum('time_spent')
    )['total_time'] or 0
    
    average_score = progress_records.filter(
        score__isnull=False
    ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    # Get learning streak
    streak, created = LearningStreak.objects.get_or_create(student=user)
    
    # Get recent milestones
    recent_milestones = ProgressMilestone.objects.filter(
        student=user
    ).order_by('-achieved_at')[:5]
    
    # Get subject progress
    subject_progress = SubjectProgress.objects.filter(student=user).select_related('subject')
    
    # Get grade progress
    grade_progress = None
    if user.grade_level:
        grade_progress, created = GradeProgress.objects.get_or_create(
            student=user,
            grade_level=user.grade_level
        )
        if created:
            grade_progress.calculate_grade_progress()
    
    stats = {
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'in_progress_lessons': in_progress_lessons,
        'total_time_spent': total_time_spent,
        'average_score': round(average_score, 2),
        'current_streak': streak.current_streak,
        'longest_streak': streak.longest_streak,
        'total_milestones': ProgressMilestone.objects.filter(student=user).count(),
        'recent_milestones': ProgressMilestoneSerializer(recent_milestones, many=True).data,
        'subject_progress': SubjectProgressSerializer(subject_progress, many=True).data,
        'grade_progress': GradeProgressSerializer(grade_progress).data if grade_progress else None
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def weekly_progress(request):
    """Get weekly progress data"""
    user = request.user
    
    if not user.is_student():
        return Response({
            'error': 'Only students can view progress data'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get current week
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get progress for this week
    week_progress = StudentProgress.objects.filter(
        student=user,
        completed_at__date__range=[week_start, week_end]
    )
    
    lessons_completed = week_progress.filter(status='COMPLETED').count()
    time_spent = week_progress.aggregate(total_time=Sum('time_spent'))['total_time'] or 0
    
    # Get quiz attempts for this week
    week_quizzes = QuizAttempt.objects.filter(
        student=user,
        started_at__date__range=[week_start, week_end]
    )
    
    quizzes_taken = week_quizzes.count()
    quizzes_passed = week_quizzes.filter(is_passed=True).count()
    
    average_score = week_quizzes.filter(
        score__isnull=False
    ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
    
    # Get daily activity
    daily_activity = {}
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_progress = StudentProgress.objects.filter(
            student=user,
            completed_at__date=day
        )
        daily_activity[day.strftime('%Y-%m-%d')] = {
            'lessons_completed': day_progress.filter(status='COMPLETED').count(),
            'time_spent': day_progress.aggregate(total_time=Sum('time_spent'))['total_time'] or 0
        }
    
    weekly_data = {
        'week_start': week_start,
        'week_end': week_end,
        'lessons_completed': lessons_completed,
        'time_spent': time_spent,
        'quizzes_taken': quizzes_taken,
        'quizzes_passed': quizzes_passed,
        'average_score': round(average_score, 2),
        'daily_activity': daily_activity
    }
    
    return Response(weekly_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def parent_dashboard(request, child_id):
    """Get parent dashboard data for a specific child"""
    user = request.user
    
    if not user.is_parent():
        return Response({
            'error': 'Only parents can access dashboard data'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        child = User.objects.get(id=child_id, parent=user)
    except User.DoesNotExist:
        return Response({
            'error': 'Child not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get or create dashboard data
    dashboard, created = ParentDashboard.objects.get_or_create(
        parent=user,
        child=child
    )
    
    # Update dashboard data
    update_parent_dashboard_data(dashboard)
    
    serializer = ParentDashboardSerializer(dashboard)
    return Response(serializer.data, status=status.HTTP_200_OK)


def update_learning_streak(user):
    """Update user's learning streak"""
    if not user.is_student():
        return
    
    streak, created = LearningStreak.objects.get_or_create(student=user)
    streak.update_streak()


def check_milestones(user, progress):
    """Check and create milestones for user progress"""
    if not user.is_student():
        return
    
    # Lesson completion milestone
    if progress.status == 'COMPLETED':
        completed_count = StudentProgress.objects.filter(
            student=user,
            status='COMPLETED'
        ).count()
        
        if completed_count == 1:
            create_milestone(
                user, 'LESSON_COMPLETION',
                'First Lesson Completed!',
                'Congratulations on completing your first lesson!'
            )
        elif completed_count == 10:
            create_milestone(
                user, 'LESSON_COMPLETION',
                '10 Lessons Completed!',
                'Amazing! You\'ve completed 10 lessons. Keep up the great work!'
            )
        elif completed_count == 50:
            create_milestone(
                user, 'LESSON_COMPLETION',
                '50 Lessons Completed!',
                'Outstanding! You\'ve completed 50 lessons. You\'re a learning champion!'
            )
    
    # Streak milestones
    streak, created = LearningStreak.objects.get_or_create(student=user)
    if streak.current_streak == 7:
        create_milestone(
            user, 'STREAK_ACHIEVEMENT',
            '7-Day Learning Streak!',
            'Fantastic! You\'ve maintained a 7-day learning streak!'
        )
    elif streak.current_streak == 30:
        create_milestone(
            user, 'STREAK_ACHIEVEMENT',
            '30-Day Learning Streak!',
            'Incredible! You\'ve maintained a 30-day learning streak!'
        )


def create_milestone(user, milestone_type, title, description, metadata=None):
    """Create a new milestone for the user"""
    milestone, created = ProgressMilestone.objects.get_or_create(
        student=user,
        milestone_type=milestone_type,
        title=title,
        defaults={
            'description': description,
            'metadata': metadata or {}
        }
    )
    
    if created:
        logger.info(f"Milestone created: {user.username} - {title}")


def update_subject_progress(user, subject):
    """Update subject progress for a user"""
    if not user.is_student():
        return
    
    progress, created = SubjectProgress.objects.get_or_create(
        student=user,
        subject=subject
    )
    progress.calculate_progress()


def update_grade_progress(user):
    """Update grade-level progress for a user"""
    if not user.is_student() or not user.grade_level:
        return
    
    progress, created = GradeProgress.objects.get_or_create(
        student=user,
        grade_level=user.grade_level
    )
    progress.calculate_grade_progress()


def update_parent_dashboard_data(dashboard):
    """Update parent dashboard data"""
    child = dashboard.child
    
    # Get child's progress data
    progress_data = {
        'total_lessons': StudentProgress.objects.filter(student=child).count(),
        'completed_lessons': StudentProgress.objects.filter(
            student=child, status='COMPLETED'
        ).count(),
        'total_time_spent': StudentProgress.objects.filter(
            student=child
        ).aggregate(total_time=Sum('time_spent'))['total_time'] or 0,
        'average_score': StudentProgress.objects.filter(
            student=child, score__isnull=False
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0,
        'current_streak': 0,
        'recent_activity': [],
        'subject_progress': {},
        'milestones': []
    }
    
    # Get learning streak
    try:
        streak = LearningStreak.objects.get(student=child)
        progress_data['current_streak'] = streak.current_streak
    except LearningStreak.DoesNotExist:
        pass
    
    # Get recent activity
    recent_progress = StudentProgress.objects.filter(
        student=child
    ).order_by('-updated_at')[:10]
    
    for progress in recent_progress:
        progress_data['recent_activity'].append({
            'lesson_title': progress.lesson.title,
            'status': progress.status,
            'updated_at': progress.updated_at,
            'subject': progress.lesson.chapter.subject.name
        })
    
    # Get subject progress
    subject_progress = SubjectProgress.objects.filter(student=child)
    for progress in subject_progress:
        progress_data['subject_progress'][progress.subject.name] = {
            'completed_lessons': progress.completed_lessons,
            'total_lessons': progress.total_lessons,
            'completion_percentage': round(
                (progress.completed_lessons / progress.total_lessons * 100) 
                if progress.total_lessons > 0 else 0, 2
            ),
            'average_score': progress.average_score
        }
    
    # Get recent milestones
    recent_milestones = ProgressMilestone.objects.filter(
        student=child
    ).order_by('-achieved_at')[:5]
    
    for milestone in recent_milestones:
        progress_data['milestones'].append({
            'title': milestone.title,
            'description': milestone.description,
            'achieved_at': milestone.achieved_at,
            'type': milestone.milestone_type
        })
    
    dashboard.data = progress_data
    dashboard.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def weekly_progress(request):
    """Get weekly progress data for the authenticated user"""
    user = request.user
    
    if not user.is_student():
        return Response({
            'error': 'Only students can access progress data'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get current week start and end dates
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get progress data for the week
    week_progress = StudentProgress.objects.filter(
        student=user,
        updated_at__date__range=[week_start, week_end]
    ).select_related('lesson__chapter__subject')
    
    # Calculate weekly statistics
    total_lessons = week_progress.count()
    completed_lessons = week_progress.filter(status='COMPLETED').count()
    total_time = week_progress.aggregate(total=Sum('time_spent'))['total'] or 0
    average_score = week_progress.filter(score__isnull=False).aggregate(
        avg=Avg('score')
    )['avg'] or 0
    
    # Get daily breakdown
    daily_data = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_progress = week_progress.filter(updated_at__date=day)
        
        daily_data.append({
            'date': day,
            'lessons_completed': day_progress.filter(status='COMPLETED').count(),
            'time_spent': day_progress.aggregate(total=Sum('time_spent'))['total'] or 0,
            'average_score': day_progress.filter(score__isnull=False).aggregate(
                avg=Avg('score')
            )['avg'] or 0
        })
    
    # Get subject breakdown
    subject_data = {}
    for progress in week_progress:
        subject_name = progress.lesson.chapter.subject.name
        if subject_name not in subject_data:
            subject_data[subject_name] = {
                'lessons_completed': 0,
                'time_spent': 0,
                'average_score': 0
            }
        
        if progress.status == 'COMPLETED':
            subject_data[subject_name]['lessons_completed'] += 1
        
        subject_data[subject_name]['time_spent'] += progress.time_spent
        
        if progress.score:
            current_avg = subject_data[subject_name]['average_score']
            if current_avg == 0:
                subject_data[subject_name]['average_score'] = progress.score
            else:
                subject_data[subject_name]['average_score'] = (current_avg + progress.score) / 2
    
    return Response({
        'week_start': week_start,
        'week_end': week_end,
        'summary': {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_rate': round((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0, 2),
            'total_time_spent': total_time,
            'average_score': round(average_score, 2)
        },
        'daily_breakdown': daily_data,
        'subject_breakdown': subject_data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def monthly_progress(request):
    """Get monthly progress data for the authenticated user"""
    user = request.user
    
    if not user.is_student():
        return Response({
            'error': 'Only students can access progress data'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get current month start and end dates
    today = timezone.now().date()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Get progress data for the month
    month_progress = StudentProgress.objects.filter(
        student=user,
        updated_at__date__range=[month_start, month_end]
    ).select_related('lesson__chapter__subject')
    
    # Calculate monthly statistics
    total_lessons = month_progress.count()
    completed_lessons = month_progress.filter(status='COMPLETED').count()
    total_time = month_progress.aggregate(total=Sum('time_spent'))['total'] or 0
    average_score = month_progress.filter(score__isnull=False).aggregate(
        avg=Avg('score')
    )['avg'] or 0
    
    # Get weekly breakdown
    weekly_data = []
    current_week_start = month_start
    week_num = 1
    
    while current_week_start <= month_end:
        week_end = min(current_week_start + timedelta(days=6), month_end)
        week_progress = month_progress.filter(
            updated_at__date__range=[current_week_start, week_end]
        )
        
        weekly_data.append({
            'week': week_num,
            'week_start': current_week_start,
            'week_end': week_end,
            'lessons_completed': week_progress.filter(status='COMPLETED').count(),
            'time_spent': week_progress.aggregate(total=Sum('time_spent'))['total'] or 0,
            'average_score': week_progress.filter(score__isnull=False).aggregate(
                avg=Avg('score')
            )['avg'] or 0
        })
        
        current_week_start += timedelta(days=7)
        week_num += 1
    
    # Get subject breakdown
    subject_data = {}
    for progress in month_progress:
        subject_name = progress.lesson.chapter.subject.name
        if subject_name not in subject_data:
            subject_data[subject_name] = {
                'lessons_completed': 0,
                'time_spent': 0,
                'average_score': 0,
                'completion_rate': 0
            }
        
        if progress.status == 'COMPLETED':
            subject_data[subject_name]['lessons_completed'] += 1
        
        subject_data[subject_name]['time_spent'] += progress.time_spent
        
        if progress.score:
            current_avg = subject_data[subject_name]['average_score']
            if current_avg == 0:
                subject_data[subject_name]['average_score'] = progress.score
            else:
                subject_data[subject_name]['average_score'] = (current_avg + progress.score) / 2
    
    # Calculate completion rates for subjects
    for subject_name in subject_data:
        subject_lessons = Lesson.objects.filter(
            chapter__subject__name=subject_name,
            is_active=True
        ).count()
        
        if subject_lessons > 0:
            subject_data[subject_name]['completion_rate'] = round(
                (subject_data[subject_name]['lessons_completed'] / subject_lessons * 100), 2
            )
    
    return Response({
        'month_start': month_start,
        'month_end': month_end,
        'summary': {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_rate': round((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0, 2),
            'total_time_spent': total_time,
            'average_score': round(average_score, 2)
        },
        'weekly_breakdown': weekly_data,
        'subject_breakdown': subject_data
    }, status=status.HTTP_200_OK)



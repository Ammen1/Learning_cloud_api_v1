"""
Django management command to update analytics data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from apps.analytics.models import Analytics, UserEngagement, ContentAnalytics, SchoolAnalytics, SystemAnalytics
from apps.accounts.models import User, School
from apps.content.models import Lesson, Subject
from apps.quizzes.models import Quiz, QuizAttempt
from apps.progress.models import StudentProgress
from django.db.models import Count, Avg, Sum
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update analytics data for the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date to update analytics for (YYYY-MM-DD)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days to update analytics for'
        )

    def handle(self, *args, **options):
        if options['date']:
            target_date = date.fromisoformat(options['date'])
            self.update_analytics_for_date(target_date)
        else:
            # Update analytics for the last N days
            for i in range(options['days']):
                target_date = date.today() - timedelta(days=i)
                self.update_analytics_for_date(target_date)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated analytics data')
        )

    def update_analytics_for_date(self, target_date):
        """Update analytics for a specific date"""
        self.stdout.write(f'Updating analytics for {target_date}')
        
        # Update user engagement
        self.update_user_engagement(target_date)
        
        # Update content analytics
        self.update_content_analytics(target_date)
        
        # Update school analytics
        self.update_school_analytics(target_date)
        
        # Update system analytics
        self.update_system_analytics(target_date)

    def update_user_engagement(self, target_date):
        """Update user engagement metrics for a specific date"""
        users = User.objects.filter(is_active=True)
        
        for user in users:
            engagement, created = UserEngagement.objects.get_or_create(
                user=user,
                date=target_date
            )
            
            # Update metrics based on actual data
            engagement.login_count = Analytics.objects.filter(
                student=user,
                metric_type='login_activity',
                date=target_date
            ).count()
            
            engagement.lessons_accessed = Analytics.objects.filter(
                student=user,
                metric_type='lesson_access',
                date=target_date
            ).count()
            
            engagement.lessons_completed = Analytics.objects.filter(
                student=user,
                metric_type='lesson_completion',
                date=target_date
            ).count()
            
            engagement.quizzes_attempted = Analytics.objects.filter(
                student=user,
                metric_type='quiz_attempt',
                date=target_date
            ).count()
            
            engagement.quizzes_completed = Analytics.objects.filter(
                student=user,
                metric_type='quiz_completion',
                date=target_date
            ).count()
            
            # Calculate time spent learning
            time_spent = Analytics.objects.filter(
                student=user,
                metric_type='time_spent',
                date=target_date
            ).aggregate(total=Sum('metric_value'))['total'] or 0
            engagement.time_spent_learning = time_spent
            
            engagement.save()

    def update_content_analytics(self, target_date):
        """Update content analytics for a specific date"""
        # Update lesson analytics
        lessons = Lesson.objects.filter(is_active=True)
        
        for lesson in lessons:
            analytics, created = ContentAnalytics.objects.get_or_create(
                content_type='lesson',
                content_id=lesson.id,
                date=target_date
            )
            
            # Calculate metrics
            analytics.total_views = Analytics.objects.filter(
                lesson=lesson,
                metric_type='lesson_access',
                date=target_date
            ).count()
            
            analytics.unique_viewers = Analytics.objects.filter(
                lesson=lesson,
                metric_type='lesson_access',
                date=target_date
            ).values('student').distinct().count()
            
            # Calculate completion rate
            total_accesses = analytics.total_views
            completions = Analytics.objects.filter(
                lesson=lesson,
                metric_type='lesson_completion',
                date=target_date
            ).count()
            
            if total_accesses > 0:
                analytics.completion_rate = (completions / total_accesses) * 100
            else:
                analytics.completion_rate = 0
            
            # Calculate average time spent
            time_data = Analytics.objects.filter(
                lesson=lesson,
                metric_type='time_spent',
                date=target_date
            ).aggregate(avg_time=Avg('metric_value'))
            
            analytics.average_time_spent = time_data['avg_time'] or 0
            
            # Calculate average score
            score_data = Analytics.objects.filter(
                lesson=lesson,
                metric_type='score_achieved',
                date=target_date
            ).aggregate(avg_score=Avg('metric_value'))
            
            analytics.average_score = score_data['avg_score'] or 0
            
            analytics.save()
        
        # Update quiz analytics
        quizzes = Quiz.objects.filter(is_active=True)
        
        for quiz in quizzes:
            analytics, created = ContentAnalytics.objects.get_or_create(
                content_type='quiz',
                content_id=quiz.id,
                date=target_date
            )
            
            # Calculate metrics
            analytics.total_views = Analytics.objects.filter(
                quiz=quiz,
                metric_type='quiz_attempt',
                date=target_date
            ).count()
            
            analytics.unique_viewers = Analytics.objects.filter(
                quiz=quiz,
                metric_type='quiz_attempt',
                date=target_date
            ).values('student').distinct().count()
            
            # Calculate completion rate
            total_attempts = analytics.total_views
            completions = Analytics.objects.filter(
                quiz=quiz,
                metric_type='quiz_completion',
                date=target_date
            ).count()
            
            if total_attempts > 0:
                analytics.completion_rate = (completions / total_attempts) * 100
            else:
                analytics.completion_rate = 0
            
            # Calculate average score
            score_data = Analytics.objects.filter(
                quiz=quiz,
                metric_type='score_achieved',
                date=target_date
            ).aggregate(avg_score=Avg('metric_value'))
            
            analytics.average_score = score_data['avg_score'] or 0
            
            analytics.save()

    def update_school_analytics(self, target_date):
        """Update school analytics for a specific date"""
        schools = School.objects.filter(is_active=True)
        
        for school in schools:
            analytics, created = SchoolAnalytics.objects.get_or_create(
                school=school,
                date=target_date
            )
            
            # Calculate school metrics
            students = User.objects.filter(school=school, role='STUDENT', is_active=True)
            analytics.total_students = students.count()
            
            # Active students (logged in on this date)
            analytics.active_students = students.filter(
                last_login__date=target_date
            ).count()
            
            # Engaged students (completed lessons on this date)
            analytics.engaged_students = students.filter(
                progress__completed_at__date=target_date,
                progress__status='COMPLETED'
            ).distinct().count()
            
            # Learning metrics
            analytics.total_lessons_completed = StudentProgress.objects.filter(
                student__school=school,
                status='COMPLETED',
                completed_at__date=target_date
            ).count()
            
            analytics.total_quizzes_attempted = QuizAttempt.objects.filter(
                student__school=school,
                started_at__date=target_date
            ).count()
            
            analytics.total_quizzes_passed = QuizAttempt.objects.filter(
                student__school=school,
                started_at__date=target_date,
                is_passed=True
            ).count()
            
            # Calculate total time spent
            time_data = StudentProgress.objects.filter(
                student__school=school,
                completed_at__date=target_date
            ).aggregate(total_time=Sum('time_spent'))
            
            analytics.total_time_spent = time_data['total_time'] or 0
            
            # Calculate average score
            score_data = StudentProgress.objects.filter(
                student__school=school,
                completed_at__date=target_date,
                score__isnull=False
            ).aggregate(avg_score=Avg('score'))
            
            analytics.average_score = score_data['avg_score'] or 0
            
            # Grade-level breakdown
            analytics.grade_1_students = students.filter(grade_level=1).count()
            analytics.grade_2_students = students.filter(grade_level=2).count()
            analytics.grade_3_students = students.filter(grade_level=3).count()
            analytics.grade_4_students = students.filter(grade_level=4).count()
            
            # Subject performance
            subject_performance = {}
            subjects = Subject.objects.filter(grade_level__in=[1, 2, 3, 4])
            
            for subject in subjects:
                subject_students = students.filter(grade_level=subject.grade_level)
                subject_progress = StudentProgress.objects.filter(
                    student__in=subject_students,
                    lesson__chapter__subject=subject,
                    completed_at__date=target_date
                )
                
                subject_performance[subject.name] = {
                    'lessons_completed': subject_progress.filter(status='COMPLETED').count(),
                    'average_score': subject_progress.aggregate(avg_score=Avg('score'))['avg_score'] or 0
                }
            
            analytics.subject_performance = subject_performance
            analytics.save()

    def update_system_analytics(self, target_date):
        """Update system analytics for a specific date"""
        analytics, created = SystemAnalytics.objects.get_or_create(date=target_date)
        
        # Calculate system-wide metrics
        analytics.total_users = User.objects.filter(is_active=True).count()
        analytics.total_students = User.objects.filter(role='STUDENT', is_active=True).count()
        analytics.total_teachers = User.objects.filter(role='TEACHER', is_active=True).count()
        analytics.total_parents = User.objects.filter(role='PARENT', is_active=True).count()
        
        # Active users (logged in on this date)
        analytics.active_users = User.objects.filter(
            last_login__date=target_date,
            is_active=True
        ).count()
        
        # New registrations on this date
        analytics.new_registrations = User.objects.filter(
            created_at__date=target_date
        ).count()
        
        # Content metrics
        analytics.total_lessons = Lesson.objects.filter(is_active=True).count()
        analytics.total_quizzes = Quiz.objects.filter(is_active=True).count()
        analytics.total_subjects = Subject.objects.filter(is_active=True).count()
        
        # Content views (sum of all lesson and quiz accesses)
        analytics.content_views = Analytics.objects.filter(
            metric_type__in=['lesson_access', 'quiz_attempt'],
            date=target_date
        ).count()
        
        # Learning metrics
        analytics.lessons_completed = StudentProgress.objects.filter(
            status='COMPLETED',
            completed_at__date=target_date
        ).count()
        
        analytics.quizzes_attempted = QuizAttempt.objects.filter(
            started_at__date=target_date
        ).count()
        
        analytics.quizzes_passed = QuizAttempt.objects.filter(
            started_at__date=target_date,
            is_passed=True
        ).count()
        
        # Calculate total learning time
        time_data = StudentProgress.objects.filter(
            completed_at__date=target_date
        ).aggregate(total_time=Sum('time_spent'))
        
        analytics.total_learning_time = time_data['total_time'] or 0
        
        # Calculate average session duration
        session_data = UserEngagement.objects.filter(
            date=target_date
        ).aggregate(avg_duration=Avg('session_duration'))
        
        analytics.average_session_duration = session_data['avg_duration'] or 0
        
        # Calculate average lesson completion rate
        total_lessons_started = StudentProgress.objects.filter(
            started_at__date=target_date
        ).count()
        
        if total_lessons_started > 0:
            analytics.average_lesson_completion_rate = (analytics.lessons_completed / total_lessons_started) * 100
        else:
            analytics.average_lesson_completion_rate = 0
        
        # Calculate average quiz pass rate
        if analytics.quizzes_attempted > 0:
            analytics.average_quiz_pass_rate = (analytics.quizzes_passed / analytics.quizzes_attempted) * 100
        else:
            analytics.average_quiz_pass_rate = 0
        
        # Technical metrics (these would typically come from monitoring systems)
        analytics.page_load_time = 1.5  # Placeholder
        analytics.error_rate = 0.1  # Placeholder
        analytics.uptime = 99.9  # Placeholder
        
        analytics.save()

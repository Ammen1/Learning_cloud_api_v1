"""
Celery tasks for Learning Cloud API.
Handles background processing for various operations.
"""
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count, Avg, Sum
from datetime import timedelta, date
import logging

from apps.accounts.models import User
from apps.content.models import Lesson, Subject
from apps.quizzes.models import Quiz, QuizAttempt, QuizAnalytics
from apps.progress.models import (
    StudentProgress, LearningStreak, SubjectProgress, 
    GradeProgress, ProgressMilestone, ProgressReport
)
from apps.analytics.models import (
    Analytics, UserEngagement, ContentAnalytics,
    SchoolAnalytics, SystemAnalytics
)
from apps.notifications.models import Notification, NotificationTemplate

logger = logging.getLogger(__name__)


@shared_task
def send_notification_email(user_id, notification_id):
    """Send notification email to user"""
    try:
        user = User.objects.get(id=user_id)
        notification = Notification.objects.get(id=notification_id)
        
        # Send email
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        # Mark notification as sent
        notification.mark_as_sent()
        
        logger.info(f"Notification email sent to {user.email}: {notification.title}")
        
    except Exception as e:
        logger.error(f"Failed to send notification email: {str(e)}")


@shared_task
def update_learning_streaks():
    """Update learning streaks for all students"""
    try:
        students = User.objects.filter(role='STUDENT', is_active=True)
        
        for student in students:
            streak, created = LearningStreak.objects.get_or_create(student=student)
            streak.update_streak()
        
        logger.info(f"Updated learning streaks for {students.count()} students")
        
    except Exception as e:
        logger.error(f"Failed to update learning streaks: {str(e)}")


@shared_task
def check_and_create_milestones():
    """Check and create milestones for all students"""
    try:
        students = User.objects.filter(role='STUDENT', is_active=True)
        
        for student in students:
            # Check lesson completion milestones
            completed_lessons = StudentProgress.objects.filter(
                student=student,
                status='COMPLETED'
            ).count()
            
            if completed_lessons == 1:
                create_milestone_if_not_exists(
                    student, 'LESSON_COMPLETION',
                    'First Lesson Completed!',
                    'Congratulations on completing your first lesson!'
                )
            elif completed_lessons == 10:
                create_milestone_if_not_exists(
                    student, 'LESSON_COMPLETION',
                    '10 Lessons Completed!',
                    'Amazing! You\'ve completed 10 lessons. Keep up the great work!'
                )
            elif completed_lessons == 50:
                create_milestone_if_not_exists(
                    student, 'LESSON_COMPLETION',
                    '50 Lessons Completed!',
                    'Outstanding! You\'ve completed 50 lessons. You\'re a learning champion!'
                )
            
            # Check streak milestones
            try:
                streak = LearningStreak.objects.get(student=student)
                if streak.current_streak == 7:
                    create_milestone_if_not_exists(
                        student, 'STREAK_ACHIEVEMENT',
                        '7-Day Learning Streak!',
                        'Fantastic! You\'ve maintained a 7-day learning streak!'
                    )
                elif streak.current_streak == 30:
                    create_milestone_if_not_exists(
                        student, 'STREAK_ACHIEVEMENT',
                        '30-Day Learning Streak!',
                        'Incredible! You\'ve maintained a 30-day learning streak!'
                    )
            except LearningStreak.DoesNotExist:
                pass
        
        logger.info(f"Checked milestones for {students.count()} students")
        
    except Exception as e:
        logger.error(f"Failed to check milestones: {str(e)}")


def create_milestone_if_not_exists(student, milestone_type, title, description):
    """Create milestone if it doesn't already exist"""
    milestone, created = ProgressMilestone.objects.get_or_create(
        student=student,
        milestone_type=milestone_type,
        title=title,
        defaults={'description': description}
    )
    
    if created:
        logger.info(f"Milestone created: {student.username} - {title}")


@shared_task
def update_quiz_analytics():
    """Update analytics for all quizzes"""
    try:
        quizzes = Quiz.objects.filter(is_active=True)
        
        for quiz in quizzes:
            analytics, created = QuizAnalytics.objects.get_or_create(quiz=quiz)
            analytics.update_analytics()
        
        logger.info(f"Updated analytics for {quizzes.count()} quizzes")
        
    except Exception as e:
        logger.error(f"Failed to update quiz analytics: {str(e)}")


@shared_task
def update_subject_progress():
    """Update subject progress for all students"""
    try:
        students = User.objects.filter(role='STUDENT', is_active=True)
        
        for student in students:
            subjects = Subject.objects.filter(grade_level=student.grade_level)
            
            for subject in subjects:
                progress, created = SubjectProgress.objects.get_or_create(
                    student=student,
                    subject=subject
                )
                progress.calculate_progress()
        
        logger.info(f"Updated subject progress for {students.count()} students")
        
    except Exception as e:
        logger.error(f"Failed to update subject progress: {str(e)}")


@shared_task
def update_grade_progress():
    """Update grade progress for all students"""
    try:
        students = User.objects.filter(role='STUDENT', is_active=True, grade_level__isnull=False)
        
        for student in students:
            progress, created = GradeProgress.objects.get_or_create(
                student=student,
                grade_level=student.grade_level
            )
            progress.calculate_grade_progress()
        
        logger.info(f"Updated grade progress for {students.count()} students")
        
    except Exception as e:
        logger.error(f"Failed to update grade progress: {str(e)}")


@shared_task
def generate_daily_analytics():
    """Generate daily analytics data"""
    try:
        today = date.today()
        
        # Update user engagement
        update_user_engagement(today)
        
        # Update content analytics
        update_content_analytics(today)
        
        # Update school analytics
        update_school_analytics(today)
        
        # Update system analytics
        update_system_analytics(today)
        
        logger.info(f"Generated daily analytics for {today}")
        
    except Exception as e:
        logger.error(f"Failed to generate daily analytics: {str(e)}")


def update_user_engagement(date):
    """Update user engagement metrics for a specific date"""
    users = User.objects.filter(is_active=True)
    
    for user in users:
        engagement, created = UserEngagement.objects.get_or_create(
            user=user,
            date=date
        )
        
        # Update engagement metrics based on user activity
        # This would typically be called from views when users perform actions
        pass


def update_content_analytics(date):
    """Update content analytics for a specific date"""
    # Update lesson analytics
    lessons = Lesson.objects.filter(is_active=True)
    
    for lesson in lessons:
        analytics, created = ContentAnalytics.objects.get_or_create(
            content_type='lesson',
            content_id=lesson.id,
            date=date
        )
        
        # Calculate metrics
        analytics.total_views = Analytics.objects.filter(
            lesson=lesson,
            metric_type='lesson_access',
            date=date
        ).count()
        
        analytics.unique_viewers = Analytics.objects.filter(
            lesson=lesson,
            metric_type='lesson_access',
            date=date
        ).values('student').distinct().count()
        
        analytics.save()


def update_school_analytics(date):
    """Update school analytics for a specific date"""
    from apps.accounts.models import School
    
    schools = School.objects.filter(is_active=True)
    
    for school in schools:
        analytics, created = SchoolAnalytics.objects.get_or_create(
            school=school,
            date=date
        )
        
        # Calculate school metrics
        students = User.objects.filter(school=school, role='STUDENT', is_active=True)
        analytics.total_students = students.count()
        
        # Active students (logged in today)
        analytics.active_students = students.filter(
            last_login__date=date
        ).count()
        
        # Engaged students (completed lessons today)
        analytics.engaged_students = students.filter(
            progress__completed_at__date=date,
            progress__status='COMPLETED'
        ).distinct().count()
        
        analytics.save()


def update_system_analytics(date):
    """Update system analytics for a specific date"""
    analytics, created = SystemAnalytics.objects.get_or_create(date=date)
    
    # Calculate system-wide metrics
    analytics.total_users = User.objects.filter(is_active=True).count()
    analytics.total_students = User.objects.filter(role='STUDENT', is_active=True).count()
    analytics.total_teachers = User.objects.filter(role='TEACHER', is_active=True).count()
    analytics.total_parents = User.objects.filter(role='PARENT', is_active=True).count()
    
    # Active users (logged in today)
    analytics.active_users = User.objects.filter(
        last_login__date=date,
        is_active=True
    ).count()
    
    # New registrations today
    analytics.new_registrations = User.objects.filter(
        created_at__date=date
    ).count()
    
    # Content metrics
    analytics.total_lessons = Lesson.objects.filter(is_active=True).count()
    analytics.total_quizzes = Quiz.objects.filter(is_active=True).count()
    analytics.total_subjects = Subject.objects.filter(is_active=True).count()
    
    # Learning metrics
    analytics.lessons_completed = StudentProgress.objects.filter(
        status='COMPLETED',
        completed_at__date=date
    ).count()
    
    analytics.quizzes_attempted = QuizAttempt.objects.filter(
        started_at__date=date
    ).count()
    
    analytics.quizzes_passed = QuizAttempt.objects.filter(
        started_at__date=date,
        is_passed=True
    ).count()
    
    analytics.save()


@shared_task
def send_reminder_notifications():
    """Send reminder notifications to users"""
    try:
        # Get users who haven't logged in for 3 days
        three_days_ago = timezone.now() - timedelta(days=3)
        inactive_students = User.objects.filter(
            role='STUDENT',
            is_active=True,
            last_login__lt=three_days_ago
        )
        
        for student in inactive_students:
            # Check if user has notification preferences
            try:
                preferences = student.notification_preferences.get()
                if not preferences.email_reminders:
                    continue
            except:
                pass  # Send if no preferences set
            
            # Create reminder notification
            notification = Notification.objects.create(
                user=student,
                title="Come back and continue learning!",
                message="We miss you! Come back and continue your learning journey.",
                notification_type='REMINDER',
                priority='MEDIUM'
            )
            
            # Send email
            send_notification_email.delay(student.id, notification.id)
        
        logger.info(f"Sent reminder notifications to {inactive_students.count()} students")
        
    except Exception as e:
        logger.error(f"Failed to send reminder notifications: {str(e)}")


@shared_task
def cleanup_old_data():
    """Clean up old data to maintain performance"""
    try:
        # Clean up old login attempts (older than 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        from apps.accounts.models import LoginAttempt
        
        old_attempts = LoginAttempt.objects.filter(attempted_at__lt=thirty_days_ago)
        deleted_count = old_attempts.count()
        old_attempts.delete()
        
        # Clean up old analytics data (older than 1 year)
        one_year_ago = timezone.now() - timedelta(days=365)
        old_analytics = Analytics.objects.filter(created_at__lt=one_year_ago)
        deleted_analytics = old_analytics.count()
        old_analytics.delete()
        
        logger.info(f"Cleaned up {deleted_count} old login attempts and {deleted_analytics} old analytics records")
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {str(e)}")


@shared_task
def generate_progress_reports():
    """Generate progress reports for students"""
    try:
        students = User.objects.filter(role='STUDENT', is_active=True)
        
        for student in students:
            # Generate weekly report
            generate_weekly_report(student)
            
            # Generate monthly report if it's the first of the month
            if date.today().day == 1:
                generate_monthly_report(student)
        
        logger.info(f"Generated progress reports for {students.count()} students")
        
    except Exception as e:
        logger.error(f"Failed to generate progress reports: {str(e)}")


def generate_weekly_report(student):
    """Generate weekly progress report for a student"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get progress data for the week
    week_progress = StudentProgress.objects.filter(
        student=student,
        completed_at__date__range=[week_start, week_end]
    )
    
    lessons_completed = week_progress.filter(status='COMPLETED').count()
    time_spent = week_progress.aggregate(total_time=Sum('time_spent'))['total_time'] or 0
    
    # Create report
    report_data = {
        'lessons_completed': lessons_completed,
        'time_spent': time_spent,
        'average_score': week_progress.filter(
            score__isnull=False
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0,
        'daily_activity': {}
    }
    
    # Daily breakdown
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_progress = week_progress.filter(completed_at__date=day)
        report_data['daily_activity'][day.strftime('%Y-%m-%d')] = {
            'lessons_completed': day_progress.filter(status='COMPLETED').count(),
            'time_spent': day_progress.aggregate(total_time=Sum('time_spent'))['total_time'] or 0
        }
    
    ProgressReport.objects.create(
        student=student,
        report_type='WEEKLY',
        period_start=week_start,
        period_end=week_end,
        data=report_data
    )


def generate_monthly_report(student):
    """Generate monthly progress report for a student"""
    today = date.today()
    month_start = today.replace(day=1)
    
    # Get previous month
    if month_start.month == 1:
        prev_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        prev_month_start = month_start.replace(month=month_start.month - 1)
    
    # Get progress data for the month
    month_progress = StudentProgress.objects.filter(
        student=student,
        completed_at__date__range=[prev_month_start, month_start - timedelta(days=1)]
    )
    
    lessons_completed = month_progress.filter(status='COMPLETED').count()
    time_spent = month_progress.aggregate(total_time=Sum('time_spent'))['total_time'] or 0
    
    # Create report
    report_data = {
        'lessons_completed': lessons_completed,
        'time_spent': time_spent,
        'average_score': month_progress.filter(
            score__isnull=False
        ).aggregate(avg_score=Avg('score'))['avg_score'] or 0,
        'subject_breakdown': {},
        'milestones_achieved': []
    }
    
    # Subject breakdown
    subjects = Subject.objects.filter(grade_level=student.grade_level)
    for subject in subjects:
        subject_progress = month_progress.filter(lesson__chapter__subject=subject)
        report_data['subject_breakdown'][subject.name] = {
            'lessons_completed': subject_progress.filter(status='COMPLETED').count(),
            'time_spent': subject_progress.aggregate(total_time=Sum('time_spent'))['total_time'] or 0
        }
    
    # Milestones achieved
    milestones = ProgressMilestone.objects.filter(
        student=student,
        achieved_at__date__range=[prev_month_start, month_start - timedelta(days=1)]
    )
    
    for milestone in milestones:
        report_data['milestones_achieved'].append({
            'title': milestone.title,
            'description': milestone.description,
            'achieved_at': milestone.achieved_at
        })
    
    ProgressReport.objects.create(
        student=student,
        report_type='MONTHLY',
        period_start=prev_month_start,
        period_end=month_start - timedelta(days=1),
        data=report_data
    )


@shared_task
def send_campaign_notifications(campaign_id):
    """Send notifications for a campaign"""
    try:
        from apps.notifications.models import NotificationCampaign
        
        campaign = NotificationCampaign.objects.get(id=campaign_id)
        
        if campaign.status != 'DRAFT':
            logger.error(f"Campaign {campaign_id} is not in draft status")
            return
        
        # Update campaign status
        campaign.status = 'RUNNING'
        campaign.save()
        
        # Get target users based on campaign criteria
        target_users = get_campaign_target_users(campaign)
        campaign.target_count = target_users.count()
        campaign.save()
        
        # Send notifications
        sent_count = 0
        for user in target_users:
            notification = Notification.objects.create(
                user=user,
                title=campaign.title,
                message=campaign.message,
                notification_type=campaign.notification_type,
                priority=campaign.priority,
                data=campaign.target_users
            )
            
            # Send via email
            send_notification_email.delay(user.id, notification.id)
            sent_count += 1
        
        # Update campaign results
        campaign.sent_count = sent_count
        campaign.status = 'COMPLETED'
        campaign.save()
        
        logger.info(f"Sent campaign {campaign_id} to {sent_count} users")
        
    except Exception as e:
        logger.error(f"Failed to send campaign notifications: {str(e)}")


def get_campaign_target_users(campaign):
    """Get target users for a campaign based on criteria"""
    users = User.objects.filter(is_active=True)
    
    # Apply targeting criteria
    target_criteria = campaign.target_users
    
    if 'role' in target_criteria:
        users = users.filter(role=target_criteria['role'])
    
    if 'grade_level' in target_criteria:
        users = users.filter(grade_level=target_criteria['grade_level'])
    
    if 'school' in target_criteria:
        users = users.filter(school_id=target_criteria['school'])
    
    if 'last_login_days' in target_criteria:
        days_ago = timezone.now() - timedelta(days=target_criteria['last_login_days'])
        users = users.filter(last_login__gte=days_ago)
    
    return users

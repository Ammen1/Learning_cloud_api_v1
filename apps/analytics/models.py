"""
Analytics models for Learning Cloud.
Optimized for handling large-scale data analytics for 20M+ students.
"""
from django.db import models
from django.utils import timezone
from apps.accounts.models import User, School
from apps.content.models import Lesson, Subject
from apps.quizzes.models import Quiz, QuizAttempt


class Analytics(models.Model):
    """Main analytics model for tracking various metrics"""
    METRIC_TYPES = [
        ('lesson_access', 'Lesson Access'),
        ('lesson_completion', 'Lesson Completion'),
        ('quiz_attempt', 'Quiz Attempt'),
        ('quiz_completion', 'Quiz Completion'),
        ('time_spent', 'Time Spent'),
        ('score_achieved', 'Score Achieved'),
        ('login_activity', 'Login Activity'),
        ('content_rating', 'Content Rating'),
        ('bookmark_created', 'Bookmark Created'),
        ('search_performed', 'Search Performed'),
        ('error_occurred', 'Error Occurred'),
    ]
    
    # User identification
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='student_analytics'
    )
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='teacher_analytics'
    )
    parent = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='parent_analytics'
    )
    
    # Context information
    school = models.ForeignKey(
        School, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_records'
    )
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    quiz = models.ForeignKey(
        Quiz, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_records'
    )
    
    # Metric data
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    metric_value = models.FloatField()
    metadata = models.JSONField(default=dict)  # Additional context data
    
    # Timestamps
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['teacher']),
            models.Index(fields=['parent']),
            models.Index(fields=['school']),
            models.Index(fields=['subject']),
            models.Index(fields=['lesson']),
            models.Index(fields=['quiz']),
            models.Index(fields=['metric_type']),
            models.Index(fields=['date']),
            models.Index(fields=['created_at']),
            models.Index(fields=['student', 'metric_type']),
            models.Index(fields=['school', 'metric_type']),
            models.Index(fields=['date', 'metric_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        user = self.student or self.teacher or self.parent
        return f"{user.get_full_name() if user else 'Unknown'} - {self.metric_type} - {self.date}"


class UserEngagement(models.Model):
    """Model for tracking user engagement metrics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='engagement_metrics')
    date = models.DateField(default=timezone.now)
    
    # Engagement metrics
    login_count = models.IntegerField(default=0)
    session_duration = models.IntegerField(default=0)  # Total session duration in seconds
    lessons_accessed = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    quizzes_attempted = models.IntegerField(default=0)
    quizzes_completed = models.IntegerField(default=0)
    time_spent_learning = models.IntegerField(default=0)  # Time spent in seconds
    content_rated = models.IntegerField(default=0)
    bookmarks_created = models.IntegerField(default=0)
    searches_performed = models.IntegerField(default=0)
    
    # Device and platform info
    device_type = models.CharField(max_length=50, blank=True)  # mobile, tablet, desktop
    platform = models.CharField(max_length=50, blank=True)  # web, android, ios
    browser = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_engagement'
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['date']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['device_type']),
            models.Index(fields=['platform']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date}"


class ContentAnalytics(models.Model):
    """Model for tracking content performance analytics"""
    content_type = models.CharField(max_length=20)  # lesson, quiz, subject, chapter
    content_id = models.IntegerField()
    
    # Performance metrics
    total_views = models.IntegerField(default=0)
    unique_viewers = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0)  # Percentage
    average_time_spent = models.FloatField(default=0)  # Average time in seconds
    average_score = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    bookmark_count = models.IntegerField(default=0)
    
    # Engagement metrics
    bounce_rate = models.FloatField(default=0)  # Percentage
    return_visitors = models.IntegerField(default=0)
    social_shares = models.IntegerField(default=0)
    
    # Date range for this analytics record
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_analytics'
        unique_together = ['content_type', 'content_id', 'date']
        indexes = [
            models.Index(fields=['content_type']),
            models.Index(fields=['content_id']),
            models.Index(fields=['date']),
            models.Index(fields=['content_type', 'content_id']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.content_type} {self.content_id} - {self.date}"


class SchoolAnalytics(models.Model):
    """Model for tracking school-level analytics"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField(default=timezone.now)
    
    # Student metrics
    total_students = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)  # Students who logged in
    engaged_students = models.IntegerField(default=0)  # Students with learning activity
    
    # Learning metrics
    total_lessons_completed = models.IntegerField(default=0)
    total_quizzes_attempted = models.IntegerField(default=0)
    total_quizzes_passed = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0)  # Total time in seconds
    average_score = models.FloatField(default=0)
    
    # Grade-level breakdown
    grade_1_students = models.IntegerField(default=0)
    grade_2_students = models.IntegerField(default=0)
    grade_3_students = models.IntegerField(default=0)
    grade_4_students = models.IntegerField(default=0)
    
    # Subject performance
    subject_performance = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'school_analytics'
        unique_together = ['school', 'date']
        indexes = [
            models.Index(fields=['school']),
            models.Index(fields=['date']),
            models.Index(fields=['school', 'date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.school.name} - {self.date}"


class SystemAnalytics(models.Model):
    """Model for tracking system-wide analytics"""
    date = models.DateField(default=timezone.now)
    
    # User metrics
    total_users = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)
    total_teachers = models.IntegerField(default=0)
    total_parents = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_registrations = models.IntegerField(default=0)
    
    # Content metrics
    total_lessons = models.IntegerField(default=0)
    total_quizzes = models.IntegerField(default=0)
    total_subjects = models.IntegerField(default=0)
    content_views = models.IntegerField(default=0)
    
    # Learning metrics
    lessons_completed = models.IntegerField(default=0)
    quizzes_attempted = models.IntegerField(default=0)
    quizzes_passed = models.IntegerField(default=0)
    total_learning_time = models.IntegerField(default=0)  # Total time in seconds
    
    # Performance metrics
    average_session_duration = models.FloatField(default=0)
    average_lesson_completion_rate = models.FloatField(default=0)
    average_quiz_pass_rate = models.FloatField(default=0)
    
    # Technical metrics
    page_load_time = models.FloatField(default=0)  # Average page load time
    error_rate = models.FloatField(default=0)  # Error rate percentage
    uptime = models.FloatField(default=100)  # System uptime percentage
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_analytics'
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"System Analytics - {self.date}"


class AnalyticsReport(models.Model):
    """Model for storing generated analytics reports"""
    REPORT_TYPES = [
        ('DAILY', 'Daily Report'),
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report'),
        ('QUARTERLY', 'Quarterly Report'),
        ('YEARLY', 'Yearly Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    REPORT_SCOPES = [
        ('SYSTEM', 'System-wide'),
        ('SCHOOL', 'School-level'),
        ('STUDENT', 'Student-level'),
        ('TEACHER', 'Teacher-level'),
        ('CONTENT', 'Content-level'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    report_scope = models.CharField(max_length=20, choices=REPORT_SCOPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Report parameters
    start_date = models.DateField()
    end_date = models.DateField()
    filters = models.JSONField(default=dict)  # Applied filters
    
    # Report data
    data = models.JSONField()  # Report data
    summary = models.JSONField(default=dict)  # Report summary
    
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)  # daily, weekly, monthly
    
    class Meta:
        db_table = 'analytics_reports'
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['report_scope']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['generated_at']),
        ]
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} - {self.start_date} to {self.end_date}"



"""
Progress tracking models for Learning Cloud.
Optimized for handling 20M+ students with efficient queries and indexing.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.accounts.models import User
from apps.content.models import Lesson, Subject, Chapter
from apps.quizzes.models import Quiz, QuizAttempt


class StudentProgress(models.Model):
    """Model for tracking student progress through lessons"""
    PROGRESS_STATUS = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PAUSED', 'Paused'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    status = models.CharField(max_length=20, choices=PROGRESS_STATUS, default='NOT_STARTED')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0)  # Time spent in seconds
    score = models.FloatField(null=True, blank=True)  # Score from associated quiz
    last_position = models.IntegerField(default=0)  # Last position in lesson (for videos/slides)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_progress'
        unique_together = ['student', 'lesson']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['lesson']),
            models.Index(fields=['status']),
            models.Index(fields=['completed_at']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['student', 'completed_at']),
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.lesson.title} ({self.status})"
    
    def mark_started(self):
        """Mark lesson as started"""
        if self.status == 'NOT_STARTED':
            self.status = 'IN_PROGRESS'
            self.started_at = timezone.now()
            self.save(update_fields=['status', 'started_at', 'updated_at'])
    
    def mark_completed(self, score=None):
        """Mark lesson as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if score is not None:
            self.score = score
        self.save(update_fields=['status', 'completed_at', 'score', 'updated_at'])
    
    def update_time_spent(self, additional_time):
        """Update time spent on lesson"""
        self.time_spent += additional_time
        self.save(update_fields=['time_spent', 'updated_at'])


class LearningStreak(models.Model):
    """Model for tracking learning streaks"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_streaks')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    streak_start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learning_streaks'
        unique_together = ['student']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['current_streak']),
            models.Index(fields=['last_activity_date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.current_streak} day streak"
    
    def update_streak(self, activity_date=None):
        """Update learning streak based on activity"""
        if activity_date is None:
            activity_date = timezone.now().date()
        
        if self.last_activity_date is None:
            # First activity
            self.current_streak = 1
            self.longest_streak = 1
            self.streak_start_date = activity_date
        elif activity_date == self.last_activity_date:
            # Same day activity, no change
            return
        elif activity_date == self.last_activity_date + timezone.timedelta(days=1):
            # Consecutive day
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            # Streak broken
            self.current_streak = 1
            self.streak_start_date = activity_date
        
        self.last_activity_date = activity_date
        self.save()


class SubjectProgress(models.Model):
    """Model for tracking progress by subject"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_progress')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_progress')
    total_lessons = models.IntegerField(default=0)
    completed_lessons = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0)  # Total time in seconds
    average_score = models.FloatField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subject_progress'
        unique_together = ['student', 'subject']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['subject']),
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['last_activity']),
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name}"
    
    def calculate_progress(self):
        """Calculate and update progress statistics"""
        # Get all lessons for this subject
        lessons = Lesson.objects.filter(
            chapter__subject=self.subject,
            is_active=True
        )
        
        self.total_lessons = lessons.count()
        
        # Get completed lessons
        completed_progress = StudentProgress.objects.filter(
            student=self.student,
            lesson__in=lessons,
            status='COMPLETED'
        )
        
        self.completed_lessons = completed_progress.count()
        
        # Calculate total time spent
        self.total_time_spent = completed_progress.aggregate(
            total_time=models.Sum('time_spent')
        )['total_time'] or 0
        
        # Calculate average score
        scores = completed_progress.exclude(score__isnull=True).values_list('score', flat=True)
        if scores:
            self.average_score = sum(scores) / len(scores)
        else:
            self.average_score = 0
        
        # Update last activity
        if completed_progress.exists():
            self.last_activity = completed_progress.order_by('-completed_at').first().completed_at
        
        self.save()


class GradeProgress(models.Model):
    """Model for tracking overall grade-level progress"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grade_progress')
    grade_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    total_subjects = models.IntegerField(default=0)
    completed_subjects = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=0)
    completed_lessons = models.IntegerField(default=0)
    total_quizzes = models.IntegerField(default=0)
    passed_quizzes = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0)  # Total time in seconds
    overall_average = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grade_progress'
        unique_together = ['student', 'grade_level']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['grade_level']),
            models.Index(fields=['student', 'grade_level']),
        ]
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - Grade {self.grade_level}"
    
    def calculate_grade_progress(self):
        """Calculate overall grade-level progress"""
        # Get all subjects for this grade level
        subjects = Subject.objects.filter(
            grade_level=self.grade_level,
            is_active=True
        )
        
        self.total_subjects = subjects.count()
        
        # Get all lessons for this grade level
        lessons = Lesson.objects.filter(
            chapter__subject__in=subjects,
            is_active=True
        )
        
        self.total_lessons = lessons.count()
        
        # Get all quizzes for this grade level
        quizzes = Quiz.objects.filter(
            grade_level=self.grade_level,
            is_active=True
        )
        
        self.total_quizzes = quizzes.count()
        
        # Calculate completed lessons
        completed_lessons = StudentProgress.objects.filter(
            student=self.student,
            lesson__in=lessons,
            status='COMPLETED'
        )
        
        self.completed_lessons = completed_lessons.count()
        
        # Calculate passed quizzes
        passed_quizzes = QuizAttempt.objects.filter(
            student=self.student,
            quiz__in=quizzes,
            is_passed=True
        )
        
        self.passed_quizzes = passed_quizzes.count()
        
        # Calculate total time spent
        self.total_time_spent = completed_lessons.aggregate(
            total_time=models.Sum('time_spent')
        )['total_time'] or 0
        
        # Calculate overall average
        scores = completed_lessons.exclude(score__isnull=True).values_list('score', flat=True)
        if scores:
            self.overall_average = sum(scores) / len(scores)
        else:
            self.overall_average = 0
        
        # Calculate completed subjects (subjects with 80%+ completion)
        completed_subjects = 0
        for subject in subjects:
            subject_lessons = lessons.filter(chapter__subject=subject)
            if subject_lessons.exists():
                completed_count = StudentProgress.objects.filter(
                    student=self.student,
                    lesson__in=subject_lessons,
                    status='COMPLETED'
                ).count()
                completion_rate = (completed_count / subject_lessons.count()) * 100
                if completion_rate >= 80:
                    completed_subjects += 1
        
        self.completed_subjects = completed_subjects
        
        self.save()


class ProgressMilestone(models.Model):
    """Model for tracking learning milestones and achievements"""
    MILESTONE_TYPES = [
        ('LESSON_COMPLETION', 'Lesson Completion'),
        ('SUBJECT_COMPLETION', 'Subject Completion'),
        ('STREAK_ACHIEVEMENT', 'Streak Achievement'),
        ('SCORE_ACHIEVEMENT', 'Score Achievement'),
        ('TIME_ACHIEVEMENT', 'Time Achievement'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='milestones')
    milestone_type = models.CharField(max_length=20, choices=MILESTONE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    achieved_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)  # Additional milestone data
    is_notified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'progress_milestones'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['milestone_type']),
            models.Index(fields=['achieved_at']),
            models.Index(fields=['is_notified']),
        ]
        ordering = ['-achieved_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.title}"


class ProgressReport(models.Model):
    """Model for generating progress reports"""
    REPORT_TYPES = [
        ('WEEKLY', 'Weekly Report'),
        ('MONTHLY', 'Monthly Report'),
        ('SUBJECT', 'Subject Report'),
        ('GRADE', 'Grade Report'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    data = models.JSONField()  # Report data
    generated_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'progress_reports'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['report_type']),
            models.Index(fields=['period_start']),
            models.Index(fields=['period_end']),
            models.Index(fields=['generated_at']),
        ]
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.report_type} Report"


class ParentDashboard(models.Model):
    """Model for parent dashboard data"""
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parent_dashboard')
    child = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_dashboard')
    last_updated = models.DateTimeField(auto_now=True)
    data = models.JSONField(default=dict)  # Dashboard data
    
    class Meta:
        db_table = 'parent_dashboard'
        unique_together = ['parent', 'child']
        indexes = [
            models.Index(fields=['parent']),
            models.Index(fields=['child']),
            models.Index(fields=['last_updated']),
        ]
    
    def __str__(self):
        return f"{self.parent.get_full_name()} - {self.child.get_full_name()} Dashboard"



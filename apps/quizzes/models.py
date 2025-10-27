"""
Quiz and assessment models for Learning Cloud.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.accounts.models import User
from apps.content.models import Lesson, Subject


class Quiz(models.Model):
    """Quiz model for assessments"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='quiz')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    grade_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    time_limit = models.IntegerField(null=True, blank=True)  # Time limit in minutes
    max_attempts = models.IntegerField(default=3)
    passing_score = models.IntegerField(default=70)  # Percentage
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    instructions = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['grade_level']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_by']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class Question(models.Model):
    """Question model for quiz questions"""
    QUESTION_TYPES = [
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
        ('TRUE_FALSE', 'True/False'),
        ('MATCHING', 'Matching'),
        ('FILL_IN_BLANK', 'Fill in the Blank'),
        ('SHORT_ANSWER', 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    options = models.JSONField(default=list, blank=True)  # For multiple choice questions
    correct_answer = models.JSONField()  # Flexible answer format
    explanation = models.TextField(blank=True, null=True)
    points = models.IntegerField(default=1)
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    difficulty_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        unique_together = ['quiz', 'order_index']
        indexes = [
            models.Index(fields=['quiz']),
            models.Index(fields=['order_index']),
            models.Index(fields=['is_active']),
            models.Index(fields=['difficulty_level']),
        ]
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.question_text[:50]}... - {self.quiz.title}"


class QuizAttempt(models.Model):
    """Model for tracking quiz attempts"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)  # Time spent in seconds
    is_passed = models.BooleanField(default=False)
    is_abandoned = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'quiz_attempts'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['quiz']),
            models.Index(fields=['completed_at']),
            models.Index(fields=['is_passed']),
            models.Index(fields=['started_at']),
        ]
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.quiz.title} - {self.started_at}"
    
    def calculate_score(self):
        """Calculate and update quiz score"""
        if self.completed_at:
            total_points = sum(q.points for q in self.quiz.questions.filter(is_active=True))
            earned_points = sum(answer.points_earned for answer in self.answers.all())
            
            if total_points > 0:
                self.score = (earned_points / total_points) * 100
                self.is_passed = self.score >= self.quiz.passing_score
                self.save(update_fields=['score', 'is_passed'])
    
    def get_time_spent_display(self):
        """Get formatted time spent"""
        minutes = self.time_spent // 60
        seconds = self.time_spent % 60
        return f"{minutes}m {seconds}s"


class Answer(models.Model):
    """Model for storing student answers"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    points_earned = models.FloatField(default=0)
    time_spent = models.IntegerField(default=0)  # Time spent on this question in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'answers'
        unique_together = ['attempt', 'question']
        indexes = [
            models.Index(fields=['attempt']),
            models.Index(fields=['question']),
            models.Index(fields=['is_correct']),
        ]
    
    def __str__(self):
        return f"{self.attempt.student.get_full_name()} - {self.question.question_text[:30]}..."


class QuizResult(models.Model):
    """Model for storing detailed quiz results and analytics"""
    attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='result')
    total_time = models.IntegerField()  # Total time in seconds
    average_time_per_question = models.FloatField()
    difficulty_breakdown = models.JSONField(default=dict)  # Performance by difficulty level
    subject_areas = models.JSONField(default=dict)  # Performance by subject areas
    improvement_suggestions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_results'
    
    def __str__(self):
        return f"Result for {self.attempt.student.get_full_name()} - {self.attempt.quiz.title}"


class QuizSession(models.Model):
    """Model for tracking active quiz sessions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    current_question_index = models.IntegerField(default=0)
    answers_data = models.JSONField(default=dict)  # Store answers temporarily
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'quiz_sessions'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['quiz']),
            models.Index(fields=['session_key']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Session {self.session_key} - {self.student.get_full_name()}"


class QuizFeedback(models.Model):
    """Model for quiz feedback and comments"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, null=True)
    difficulty_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_feedback'
        unique_together = ['attempt']
    
    def __str__(self):
        return f"Feedback for {self.attempt.student.get_full_name()} - {self.attempt.quiz.title}"


class QuizAnalytics(models.Model):
    """Model for quiz analytics and statistics"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='analytics')
    total_attempts = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    pass_rate = models.FloatField(default=0)
    average_time = models.FloatField(default=0)  # Average time in minutes
    difficulty_distribution = models.JSONField(default=dict)
    common_mistakes = models.JSONField(default=list)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quiz_analytics'
        unique_together = ['quiz']
    
    def __str__(self):
        return f"Analytics for {self.quiz.title}"
    
    def update_analytics(self):
        """Update quiz analytics based on attempts"""
        attempts = self.quiz.attempts.filter(completed_at__isnull=False)
        
        self.total_attempts = attempts.count()
        self.total_completions = attempts.filter(is_passed=True).count()
        
        if self.total_attempts > 0:
            self.average_score = attempts.aggregate(avg_score=models.Avg('score'))['avg_score'] or 0
            self.pass_rate = (self.total_completions / self.total_attempts) * 100
            self.average_time = attempts.aggregate(avg_time=models.Avg('time_spent'))['avg_time'] or 0
            self.average_time = self.average_time / 60  # Convert to minutes
        
        self.save()



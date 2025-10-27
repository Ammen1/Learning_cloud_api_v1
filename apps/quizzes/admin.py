"""
Admin configuration for quizzes app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Quiz, Question, QuizAttempt, Answer, QuizResult,
    QuizSession, QuizFeedback, QuizAnalytics
)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Quiz admin"""
    list_display = [
        'title', 'subject', 'grade_level', 'time_limit', 'max_attempts',
        'passing_score', 'is_active', 'is_premium', 'created_by', 'created_at'
    ]
    list_filter = ['grade_level', 'is_active', 'is_premium', 'created_at']
    search_fields = ['title', 'description', 'subject__name']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject', 'lesson', 'created_by')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Question admin"""
    list_display = [
        'question_text_short', 'quiz', 'question_type', 'points',
        'difficulty_level', 'order_index', 'is_active'
    ]
    list_filter = ['question_type', 'difficulty_level', 'is_active', 'quiz__grade_level']
    search_fields = ['question_text', 'quiz__title']
    ordering = ['quiz', 'order_index']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question Text'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """QuizAttempt admin"""
    list_display = [
        'student', 'quiz', 'started_at', 'completed_at', 'score',
        'is_passed', 'time_spent_display', 'is_abandoned'
    ]
    list_filter = ['is_passed', 'is_abandoned', 'started_at', 'quiz__grade_level']
    search_fields = ['student__username', 'student__email', 'quiz__title']
    readonly_fields = ['started_at', 'time_spent_display']
    ordering = ['-started_at']
    
    def time_spent_display(self, obj):
        return obj.get_time_spent_display()
    time_spent_display.short_description = 'Time Spent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'quiz')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Answer admin"""
    list_display = [
        'attempt', 'question_short', 'answer_text_short', 'is_correct',
        'points_earned', 'time_spent', 'created_at'
    ]
    list_filter = ['is_correct', 'created_at']
    search_fields = ['attempt__student__username', 'question__question_text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def question_short(self, obj):
        return obj.question.question_text[:30] + '...' if len(obj.question.question_text) > 30 else obj.question.question_text
    question_short.short_description = 'Question'
    
    def answer_text_short(self, obj):
        return obj.answer_text[:30] + '...' if obj.answer_text and len(obj.answer_text) > 30 else obj.answer_text
    answer_text_short.short_description = 'Answer'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attempt__student', 'question')


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    """QuizResult admin"""
    list_display = ['attempt', 'total_time', 'average_time_per_question', 'created_at']
    list_filter = ['created_at']
    search_fields = ['attempt__student__username', 'attempt__quiz__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attempt__student', 'attempt__quiz')


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    """QuizSession admin"""
    list_display = [
        'student', 'quiz', 'session_key', 'current_question_index',
        'is_active', 'started_at', 'last_activity'
    ]
    list_filter = ['is_active', 'started_at']
    search_fields = ['student__username', 'quiz__title', 'session_key']
    readonly_fields = ['session_key', 'started_at', 'last_activity']
    ordering = ['-started_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'quiz')


@admin.register(QuizFeedback)
class QuizFeedbackAdmin(admin.ModelAdmin):
    """QuizFeedback admin"""
    list_display = ['attempt', 'rating', 'difficulty_rating', 'created_at']
    list_filter = ['rating', 'difficulty_rating', 'created_at']
    search_fields = ['attempt__student__username', 'attempt__quiz__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attempt__student', 'attempt__quiz')


@admin.register(QuizAnalytics)
class QuizAnalyticsAdmin(admin.ModelAdmin):
    """QuizAnalytics admin"""
    list_display = [
        'quiz', 'total_attempts', 'total_completions', 'average_score',
        'pass_rate', 'average_time', 'last_updated'
    ]
    list_filter = ['last_updated']
    search_fields = ['quiz__title']
    readonly_fields = ['last_updated']
    ordering = ['-last_updated']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')



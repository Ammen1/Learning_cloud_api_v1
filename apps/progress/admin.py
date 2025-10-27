"""
Admin configuration for progress app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    StudentProgress, LearningStreak, SubjectProgress,
    GradeProgress, ProgressMilestone, ProgressReport,
    ParentDashboard
)


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    """StudentProgress admin"""
    list_display = [
        'student', 'lesson', 'status', 'progress_percentage',
        'time_spent_display', 'score', 'started_at', 'completed_at'
    ]
    list_filter = ['status', 'lesson__chapter__subject__grade_level', 'started_at', 'completed_at']
    search_fields = ['student__username', 'student__email', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at', 'progress_percentage', 'time_spent_display']
    ordering = ['-updated_at']
    
    def progress_percentage(self, obj):
        if obj.status == 'COMPLETED':
            return '100%'
        elif obj.status == 'NOT_STARTED':
            return '0%'
        elif obj.lesson.content_type == 'VIDEO' and obj.lesson.duration:
            percentage = min((obj.last_position / (obj.lesson.duration * 60)) * 100, 99)
            return f'{percentage:.1f}%'
        else:
            return '50%' if obj.status == 'IN_PROGRESS' else '0%'
    progress_percentage.short_description = 'Progress'
    
    def time_spent_display(self, obj):
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    time_spent_display.short_description = 'Time Spent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'lesson__chapter__subject')


@admin.register(LearningStreak)
class LearningStreakAdmin(admin.ModelAdmin):
    """LearningStreak admin"""
    list_display = [
        'student', 'current_streak', 'longest_streak',
        'last_activity_date', 'streak_start_date'
    ]
    list_filter = ['last_activity_date', 'streak_start_date']
    search_fields = ['student__username', 'student__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-current_streak']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(SubjectProgress)
class SubjectProgressAdmin(admin.ModelAdmin):
    """SubjectProgress admin"""
    list_display = [
        'student', 'subject', 'completion_percentage',
        'completed_lessons', 'total_lessons', 'average_score',
        'time_spent_display', 'last_activity'
    ]
    list_filter = ['subject__grade_level', 'last_activity']
    search_fields = ['student__username', 'student__email', 'subject__name']
    readonly_fields = ['created_at', 'updated_at', 'completion_percentage', 'time_spent_display']
    ordering = ['-updated_at']
    
    def completion_percentage(self, obj):
        if obj.total_lessons > 0:
            return f"{(obj.completed_lessons / obj.total_lessons) * 100:.1f}%"
        return "0%"
    completion_percentage.short_description = 'Completion'
    
    def time_spent_display(self, obj):
        hours = obj.total_time_spent // 3600
        minutes = (obj.total_time_spent % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    time_spent_display.short_description = 'Time Spent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'subject')


@admin.register(GradeProgress)
class GradeProgressAdmin(admin.ModelAdmin):
    """GradeProgress admin"""
    list_display = [
        'student', 'grade_level', 'lesson_completion_percentage',
        'quiz_pass_percentage', 'subject_completion_percentage',
        'overall_average', 'time_spent_display'
    ]
    list_filter = ['grade_level']
    search_fields = ['student__username', 'student__email']
    readonly_fields = ['created_at', 'updated_at', 'lesson_completion_percentage', 'quiz_pass_percentage', 'subject_completion_percentage', 'time_spent_display']
    ordering = ['-updated_at']
    
    def lesson_completion_percentage(self, obj):
        if obj.total_lessons > 0:
            return f"{(obj.completed_lessons / obj.total_lessons) * 100:.1f}%"
        return "0%"
    lesson_completion_percentage.short_description = 'Lesson Completion'
    
    def quiz_pass_percentage(self, obj):
        if obj.total_quizzes > 0:
            return f"{(obj.passed_quizzes / obj.total_quizzes) * 100:.1f}%"
        return "0%"
    quiz_pass_percentage.short_description = 'Quiz Pass Rate'
    
    def subject_completion_percentage(self, obj):
        if obj.total_subjects > 0:
            return f"{(obj.completed_subjects / obj.total_subjects) * 100:.1f}%"
        return "0%"
    subject_completion_percentage.short_description = 'Subject Completion'
    
    def time_spent_display(self, obj):
        hours = obj.total_time_spent // 3600
        minutes = (obj.total_time_spent % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    time_spent_display.short_description = 'Time Spent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(ProgressMilestone)
class ProgressMilestoneAdmin(admin.ModelAdmin):
    """ProgressMilestone admin"""
    list_display = [
        'student', 'milestone_type', 'title', 'achieved_at', 'is_notified'
    ]
    list_filter = ['milestone_type', 'achieved_at', 'is_notified']
    search_fields = ['student__username', 'student__email', 'title']
    readonly_fields = ['achieved_at']
    ordering = ['-achieved_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    """ProgressReport admin"""
    list_display = [
        'student', 'report_type', 'period_start', 'period_end',
        'generated_at', 'is_sent'
    ]
    list_filter = ['report_type', 'generated_at', 'is_sent']
    search_fields = ['student__username', 'student__email']
    readonly_fields = ['generated_at']
    ordering = ['-generated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


@admin.register(ParentDashboard)
class ParentDashboardAdmin(admin.ModelAdmin):
    """ParentDashboard admin"""
    list_display = ['parent', 'child', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['parent__username', 'parent__email', 'child__username', 'child__email']
    readonly_fields = ['last_updated']
    ordering = ['-last_updated']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent', 'child')



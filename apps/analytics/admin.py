"""
Admin configuration for analytics app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Analytics, UserEngagement, ContentAnalytics,
    SchoolAnalytics, SystemAnalytics, AnalyticsReport
)


@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    """Analytics admin"""
    list_display = [
        'user_display', 'metric_type', 'metric_value', 'date', 'created_at'
    ]
    list_filter = ['metric_type', 'date', 'created_at']
    search_fields = [
        'student__username', 'student__email', 'teacher__username',
        'teacher__email', 'parent__username', 'parent__email'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def user_display(self, obj):
        user = obj.student or obj.teacher or obj.parent
        if user:
            return f"{user.get_full_name()} ({user.get_role_display()})"
        return "System"
    user_display.short_description = 'User'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'teacher', 'parent', 'subject', 'lesson')


@admin.register(UserEngagement)
class UserEngagementAdmin(admin.ModelAdmin):
    """UserEngagement admin"""
    list_display = [
        'user', 'date', 'login_count', 'lessons_completed',
        'quizzes_completed', 'time_spent_learning', 'device_type', 'platform'
    ]
    list_filter = ['date', 'device_type', 'platform']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ContentAnalytics)
class ContentAnalyticsAdmin(admin.ModelAdmin):
    """ContentAnalytics admin"""
    list_display = [
        'content_display', 'total_views', 'unique_viewers',
        'completion_rate', 'average_score', 'date'
    ]
    list_filter = ['content_type', 'date']
    search_fields = ['content_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
    
    def content_display(self, obj):
        return f"{obj.content_type} #{obj.content_id}"
    content_display.short_description = 'Content'
    
    def completion_rate(self, obj):
        return f"{obj.completion_rate:.1f}%"
    completion_rate.short_description = 'Completion Rate'


@admin.register(SchoolAnalytics)
class SchoolAnalyticsAdmin(admin.ModelAdmin):
    """SchoolAnalytics admin"""
    list_display = [
        'school', 'date', 'total_students', 'active_students',
        'engaged_students', 'average_score', 'total_time_spent'
    ]
    list_filter = ['date']
    search_fields = ['school__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('school')


@admin.register(SystemAnalytics)
class SystemAnalyticsAdmin(admin.ModelAdmin):
    """SystemAnalytics admin"""
    list_display = [
        'date', 'total_users', 'active_users', 'new_registrations',
        'lessons_completed', 'quizzes_attempted',
        'uptime', 'error_rate'
    ]
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']


@admin.register(AnalyticsReport)
class AnalyticsReportAdmin(admin.ModelAdmin):
    """AnalyticsReport admin"""
    list_display = [
        'title', 'report_type', 'report_scope', 'start_date',
        'end_date', 'generated_by', 'generated_at', 'is_scheduled'
    ]
    list_filter = ['report_type', 'report_scope', 'generated_at', 'is_scheduled']
    search_fields = ['title', 'description', 'generated_by__username']
    readonly_fields = ['generated_at']
    ordering = ['-generated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by')



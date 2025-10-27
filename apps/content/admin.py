"""
Admin configuration for content app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Subject, Chapter, Lesson, LessonMedia, ContentVersion,
    OfflineContent, ContentAccess, ContentRating, ContentBookmark
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Subject admin"""
    list_display = ['name', 'grade_level', 'school', 'is_active', 'order_index', 'created_at']
    list_filter = ['grade_level', 'is_active', 'school', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['grade_level', 'order_index']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('school')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """Chapter admin"""
    list_display = ['title', 'subject', 'order_index', 'estimated_duration', 'is_active', 'created_at']
    list_filter = ['is_active', 'subject__grade_level', 'created_at']
    search_fields = ['title', 'description', 'subject__name']
    ordering = ['subject__grade_level', 'order_index']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Lesson admin"""
    list_display = [
        'title', 'chapter', 'content_type', 'duration', 'order_index',
        'is_active', 'is_premium', 'created_at'
    ]
    list_filter = ['content_type', 'is_active', 'is_premium', 'chapter__subject__grade_level', 'created_at']
    search_fields = ['title', 'content', 'chapter__title', 'chapter__subject__name']
    ordering = ['chapter__subject__grade_level', 'chapter__order_index', 'order_index']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('chapter__subject')


@admin.register(LessonMedia)
class LessonMediaAdmin(admin.ModelAdmin):
    """LessonMedia admin"""
    list_display = ['file_name', 'lesson', 'media_type', 'file_size', 'order_index', 'is_active']
    list_filter = ['media_type', 'is_active', 'lesson__chapter__subject__grade_level']
    search_fields = ['file_name', 'lesson__title']
    ordering = ['lesson__chapter__subject__grade_level', 'lesson__chapter__order_index', 'lesson__order_index', 'order_index']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lesson__chapter__subject')


@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    """ContentVersion admin"""
    list_display = ['lesson', 'version_number', 'created_by', 'is_current', 'created_at']
    list_filter = ['is_current', 'created_at']
    search_fields = ['lesson__title', 'version_number', 'created_by__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lesson', 'created_by')


@admin.register(OfflineContent)
class OfflineContentAdmin(admin.ModelAdmin):
    """OfflineContent admin"""
    list_display = ['lesson', 'file_size', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at']
    search_fields = ['lesson__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lesson')


@admin.register(ContentAccess)
class ContentAccessAdmin(admin.ModelAdmin):
    """ContentAccess admin"""
    list_display = ['user', 'lesson', 'access_type', 'is_active', 'granted_at', 'expires_at']
    list_filter = ['access_type', 'is_active', 'granted_at']
    search_fields = ['user__username', 'user__email', 'lesson__title']
    readonly_fields = ['granted_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson')


@admin.register(ContentRating)
class ContentRatingAdmin(admin.ModelAdmin):
    """ContentRating admin"""
    list_display = ['user', 'lesson', 'rating', 'is_helpful', 'created_at']
    list_filter = ['rating', 'is_helpful', 'created_at']
    search_fields = ['user__username', 'user__email', 'lesson__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson')


@admin.register(ContentBookmark)
class ContentBookmarkAdmin(admin.ModelAdmin):
    """ContentBookmark admin"""
    list_display = ['user', 'lesson', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'lesson__title']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson')



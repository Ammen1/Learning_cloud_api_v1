"""
Admin configuration for notifications app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationLog, NotificationCampaign
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin"""
    list_display = [
        'user', 'title_short', 'notification_type', 'priority',
        'is_read', 'is_sent', 'created_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_read', 'is_sent', 'created_at']
    search_fields = ['user__username', 'user__email', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at', 'read_at', 'sent_at']
    ordering = ['-created_at']
    
    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """NotificationTemplate admin"""
    list_display = [
        'name', 'notification_type', 'priority', 'is_active', 'auto_send'
    ]
    list_filter = ['notification_type', 'priority', 'is_active', 'auto_send']
    search_fields = ['name', 'title_template', 'message_template']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """NotificationPreference admin"""
    list_display = [
        'user', 'email_enabled', 'push_enabled', 'in_app_enabled',
        'reminder_frequency', 'timezone'
    ]
    list_filter = ['email_enabled', 'push_enabled', 'in_app_enabled', 'reminder_frequency']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['user__username']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """NotificationLog admin"""
    list_display = [
        'notification', 'delivery_method', 'status', 'delivery_time',
        'retry_count', 'created_at'
    ]
    list_filter = ['delivery_method', 'status', 'delivery_time', 'created_at']
    search_fields = ['notification__title', 'external_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('notification')


@admin.register(NotificationCampaign)
class NotificationCampaignAdmin(admin.ModelAdmin):
    """NotificationCampaign admin"""
    list_display = [
        'name', 'campaign_type', 'status', 'target_count',
        'sent_count', 'delivered_count', 'created_by', 'created_at'
    ]
    list_filter = ['campaign_type', 'status', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'sent_count', 'delivered_count', 'failed_count', 'read_count']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')



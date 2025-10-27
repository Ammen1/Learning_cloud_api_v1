"""
Serializers for notifications functionality.
"""
from rest_framework import serializers
from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationLog, NotificationCampaign
)
from apps.accounts.serializers import UserProfileSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type',
            'priority', 'data', 'action_url', 'action_text',
            'is_read', 'is_sent', 'read_at', 'sent_at',
            'scheduled_for', 'expires_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_read', 'is_sent', 'read_at',
            'sent_at', 'created_at', 'updated_at'
        ]


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model"""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'title_template', 'message_template',
            'notification_type', 'priority', 'variables',
            'is_active', 'auto_send', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'email_enabled', 'email_lesson_completed',
            'email_quiz_result', 'email_achievement', 'email_reminders',
            'email_system', 'push_enabled', 'push_lesson_completed',
            'push_quiz_result', 'push_achievement', 'push_reminders',
            'push_system', 'in_app_enabled', 'in_app_lesson_completed',
            'in_app_quiz_result', 'in_app_achievement', 'in_app_reminders',
            'in_app_system', 'quiet_hours_start', 'quiet_hours_end',
            'timezone', 'reminder_frequency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for NotificationLog model"""
    notification = NotificationSerializer(read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'delivery_method', 'status',
            'external_id', 'error_message', 'delivery_time',
            'retry_count', 'next_retry_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationCampaignSerializer(serializers.ModelSerializer):
    """Serializer for NotificationCampaign model"""
    created_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = NotificationCampaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'title',
            'message', 'notification_type', 'priority', 'target_users',
            'target_count', 'scheduled_for', 'expires_at', 'status',
            'sent_count', 'delivered_count', 'failed_count', 'read_count',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'target_count', 'sent_count', 'delivered_count',
            'failed_count', 'read_count', 'created_by', 'created_at', 'updated_at'
        ]



"""
Notifications models for Learning Cloud.
"""
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = [
        ('LESSON_COMPLETED', 'Lesson Completed'),
        ('QUIZ_RESULT', 'Quiz Result'),
        ('ACHIEVEMENT', 'Achievement Unlocked'),
        ('STREAK_MILESTONE', 'Streak Milestone'),
        ('REMINDER', 'Learning Reminder'),
        ('SYSTEM', 'System Notification'),
        ('PARENT_UPDATE', 'Parent Update'),
        ('TEACHER_MESSAGE', 'Teacher Message'),
        ('CONTENT_UPDATE', 'Content Update'),
        ('MAINTENANCE', 'Maintenance Notice'),
    ]
    
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')
    
    # Notification data
    data = models.JSONField(default=dict)  # Additional data for the notification
    action_url = models.URLField(blank=True, null=True)  # URL to navigate to when clicked
    action_text = models.CharField(max_length=100, blank=True, null=True)  # Text for action button
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)  # For scheduled notifications
    expires_at = models.DateTimeField(null=True, blank=True)  # When notification expires
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_read']),
            models.Index(fields=['is_sent']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'notification_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=['is_sent', 'sent_at', 'updated_at'])
    
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class NotificationTemplate(models.Model):
    """Model for notification templates"""
    name = models.CharField(max_length=100, unique=True)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    notification_type = models.CharField(max_length=30, choices=Notification.NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_LEVELS, default='MEDIUM')
    
    # Template variables
    variables = models.JSONField(default=list)  # List of available variables
    
    # Settings
    is_active = models.BooleanField(default=True)
    auto_send = models.BooleanField(default=False)  # Whether to send automatically
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    """Model for user notification preferences"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_lesson_completed = models.BooleanField(default=True)
    email_quiz_result = models.BooleanField(default=True)
    email_achievement = models.BooleanField(default=True)
    email_reminders = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)
    
    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_lesson_completed = models.BooleanField(default=True)
    push_quiz_result = models.BooleanField(default=True)
    push_achievement = models.BooleanField(default=True)
    push_reminders = models.BooleanField(default=True)
    push_system = models.BooleanField(default=True)
    
    # In-app notification preferences
    in_app_enabled = models.BooleanField(default=True)
    in_app_lesson_completed = models.BooleanField(default=True)
    in_app_quiz_result = models.BooleanField(default=True)
    in_app_achievement = models.BooleanField(default=True)
    in_app_reminders = models.BooleanField(default=True)
    in_app_system = models.BooleanField(default=True)
    
    # Timing preferences
    quiet_hours_start = models.TimeField(null=True, blank=True)  # e.g., 22:00
    quiet_hours_end = models.TimeField(null=True, blank=True)    # e.g., 08:00
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Frequency preferences
    reminder_frequency = models.CharField(
        max_length=20,
        choices=[
            ('DAILY', 'Daily'),
            ('WEEKLY', 'Weekly'),
            ('MONTHLY', 'Monthly'),
            ('NEVER', 'Never'),
        ],
        default='DAILY'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        unique_together = ['user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Notification Preferences"


class NotificationLog(models.Model):
    """Model for logging notification delivery attempts"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_logs')
    delivery_method = models.CharField(max_length=20, choices=[
        ('EMAIL', 'Email'),
        ('PUSH', 'Push Notification'),
        ('SMS', 'SMS'),
        ('IN_APP', 'In-App'),
    ])
    
    # Delivery status
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
    ])
    
    # Delivery details
    external_id = models.CharField(max_length=100, blank=True, null=True)  # External service ID
    error_message = models.TextField(blank=True, null=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Retry information
    retry_count = models.IntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_logs'
        indexes = [
            models.Index(fields=['notification']),
            models.Index(fields=['delivery_method']),
            models.Index(fields=['status']),
            models.Index(fields=['delivery_time']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification.title} - {self.delivery_method} - {self.status}"


class NotificationCampaign(models.Model):
    """Model for managing notification campaigns"""
    CAMPAIGN_TYPES = [
        ('BROADCAST', 'Broadcast'),
        ('TARGETED', 'Targeted'),
        ('SCHEDULED', 'Scheduled'),
        ('TRIGGERED', 'Triggered'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    
    # Campaign content
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=Notification.NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_LEVELS, default='MEDIUM')
    
    # Targeting
    target_users = models.JSONField(default=dict)  # Targeting criteria
    target_count = models.IntegerField(default=0)  # Estimated target count
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ], default='DRAFT')
    
    # Results
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_campaigns'
        indexes = [
            models.Index(fields=['campaign_type']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['created_by']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name



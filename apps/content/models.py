"""
Content management models for Learning Cloud.
Handles subjects, chapters, lessons, and multimedia content.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.accounts.models import User, School


class Subject(models.Model):
    """Subject model for organizing content by grade level"""
    GRADE_LEVELS = [
        (1, 'Grade 1'),
        (2, 'Grade 2'),
        (3, 'Grade 3'),
        (4, 'Grade 4'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    grade_level = models.IntegerField(
        choices=GRADE_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order_index = models.IntegerField(default=0)
    icon_url = models.URLField(blank=True, null=True)
    color_code = models.CharField(max_length=7, default='#007bff')  # Hex color
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subjects'
        unique_together = ['name', 'grade_level', 'school']
        indexes = [
            models.Index(fields=['grade_level']),
            models.Index(fields=['school']),
            models.Index(fields=['is_active']),
            models.Index(fields=['order_index']),
        ]
        ordering = ['grade_level', 'order_index', 'name']
    
    def __str__(self):
        return f"{self.name} - Grade {self.grade_level}"


class Chapter(models.Model):
    """Chapter model for organizing lessons within subjects"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    estimated_duration = models.IntegerField(default=0)  # Duration in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chapters'
        unique_together = ['subject', 'order_index']
        indexes = [
            models.Index(fields=['subject']),
            models.Index(fields=['order_index']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class Lesson(models.Model):
    """Lesson model for individual learning content"""
    LESSON_TYPES = [
        ('SLIDES', 'Slides'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('READING', 'Reading'),
        ('INTERACTIVE', 'Interactive'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()  # Rich text content
    content_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='SLIDES')
    video_url = models.URLField(blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    duration = models.IntegerField(default=0)  # Duration in minutes
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons')
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    thumbnail_url = models.URLField(blank=True, null=True)
    learning_objectives = models.JSONField(default=list, blank=True)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        unique_together = ['chapter', 'order_index']
        indexes = [
            models.Index(fields=['chapter']),
            models.Index(fields=['order_index']),
            models.Index(fields=['is_active']),
            models.Index(fields=['content_type']),
        ]
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.title} - {self.chapter.title}"
    
    def update_average_rating(self):
        """Update the average rating for this lesson"""
        from django.db.models import Avg, Count
        from .models import ContentRating
        
        rating_stats = ContentRating.objects.filter(
            lesson=self
        ).aggregate(
            avg=Avg('rating'),
            count=Count('id')
        )
        
        if rating_stats['avg']:
            self.average_rating = round(rating_stats['avg'], 2)
        else:
            self.average_rating = 0.0
        
        self.rating_count = rating_stats['count']
        self.save(update_fields=['average_rating', 'rating_count'])


class LessonMedia(models.Model):
    """Model for storing lesson media files"""
    MEDIA_TYPES = [
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('DOCUMENT', 'Document'),
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='media_files')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file_url = models.URLField()
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)  # Size in bytes
    mime_type = models.CharField(max_length=100)
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lesson_media'
        indexes = [
            models.Index(fields=['lesson']),
            models.Index(fields=['media_type']),
            models.Index(fields=['order_index']),
        ]
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.file_name} - {self.lesson.title}"


class ContentVersion(models.Model):
    """Model for tracking content versions and updates"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=20)
    content_snapshot = models.JSONField()  # Store content at this version
    change_log = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'content_versions'
        unique_together = ['lesson', 'version_number']
        indexes = [
            models.Index(fields=['lesson']),
            models.Index(fields=['is_current']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.lesson.title} - v{self.version_number}"


class OfflineContent(models.Model):
    """Model for managing offline content downloads"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='offline_content')
    download_url = models.URLField()
    file_size = models.BigIntegerField()  # Size in bytes
    checksum = models.CharField(max_length=64)  # SHA-256 checksum
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'offline_content'
        indexes = [
            models.Index(fields=['lesson']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"Offline content for {self.lesson.title}"


class ContentAccess(models.Model):
    """Model for tracking content access permissions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=[
        ('FREE', 'Free Access'),
        ('PREMIUM', 'Premium Access'),
        ('RESTRICTED', 'Restricted Access'),
    ])
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'content_access'
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['lesson']),
            models.Index(fields=['access_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.lesson.title}"


class ContentRating(models.Model):
    """Model for user ratings and reviews of content"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'content_ratings'
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['lesson']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.lesson.title} ({self.rating} stars)"


class ContentBookmark(models.Model):
    """Model for user bookmarks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'content_bookmarks'
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['lesson']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} bookmarked {self.lesson.title}"



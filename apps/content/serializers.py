"""
Serializers for content management.
"""
from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (
    Subject, Chapter, Lesson, LessonMedia, ContentVersion,
    OfflineContent, ContentAccess, ContentRating, ContentBookmark
)
from apps.accounts.serializers import UserProfileSerializer


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""
    chapter_count = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'description', 'grade_level', 'school',
            'is_active', 'order_index', 'icon_url', 'color_code',
            'chapter_count', 'lesson_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_chapter_count(self, obj):
        return obj.chapters.filter(is_active=True).count()
    
    def get_lesson_count(self, obj):
        return Lesson.objects.filter(
            chapter__subject=obj,
            is_active=True
        ).count()


class ChapterSerializer(serializers.ModelSerializer):
    """Serializer for Chapter model"""
    lesson_count = serializers.SerializerMethodField()
    estimated_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'description', 'subject', 'order_index',
            'is_active', 'estimated_duration', 'lesson_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_lesson_count(self, obj):
        return obj.lessons.filter(is_active=True).count()
    
    def get_estimated_duration(self, obj):
        total_duration = obj.lessons.filter(is_active=True).aggregate(
            total=models.Sum('duration')
        )['total']
        return total_duration or 0


class LessonMediaSerializer(serializers.ModelSerializer):
    """Serializer for LessonMedia model"""
    
    class Meta:
        model = LessonMedia
        fields = [
            'id', 'media_type', 'file_url', 'file_name',
            'file_size', 'mime_type', 'order_index', 'is_active'
        ]
        read_only_fields = ['id']


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""
    media_files = LessonMediaSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'content_type', 'video_url',
            'audio_url', 'duration', 'chapter', 'order_index',
            'is_active', 'is_premium', 'thumbnail_url',
            'learning_objectives', 'prerequisites', 'media_files',
            'average_rating', 'rating_count', 'is_bookmarked',
            'user_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_average_rating(self, obj):
        rating = obj.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(rating, 2) if rating else 0
    
    def get_rating_count(self, obj):
        return obj.ratings.count()
    
    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False
    
    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.ratings.filter(user=request.user).first()
            return rating.rating if rating else None
        return None


class LessonDetailSerializer(LessonSerializer):
    """Detailed serializer for Lesson with full content"""
    chapter = ChapterSerializer(read_only=True)
    prerequisites = LessonSerializer(many=True, read_only=True)
    
    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + ['chapter', 'prerequisites']


class ContentVersionSerializer(serializers.ModelSerializer):
    """Serializer for ContentVersion model"""
    created_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ContentVersion
        fields = [
            'id', 'version_number', 'content_snapshot',
            'change_log', 'created_by', 'created_at', 'is_current'
        ]
        read_only_fields = ['id', 'created_at']


class OfflineContentSerializer(serializers.ModelSerializer):
    """Serializer for OfflineContent model"""
    
    class Meta:
        model = OfflineContent
        fields = [
            'id', 'lesson', 'download_url', 'file_size',
            'checksum', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContentAccessSerializer(serializers.ModelSerializer):
    """Serializer for ContentAccess model"""
    user = UserProfileSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = ContentAccess
        fields = [
            'id', 'user', 'lesson', 'access_type',
            'granted_at', 'expires_at', 'is_active'
        ]
        read_only_fields = ['id', 'granted_at']


class ContentRatingSerializer(serializers.ModelSerializer):
    """Serializer for ContentRating model"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ContentRating
        fields = [
            'id', 'user', 'lesson', 'rating', 'review',
            'is_helpful', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ContentBookmarkSerializer(serializers.ModelSerializer):
    """Serializer for ContentBookmark model"""
    user = UserProfileSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = ContentBookmark
        fields = ['id', 'user', 'lesson', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SubjectWithChaptersSerializer(SubjectSerializer):
    """Serializer for Subject with nested chapters"""
    chapters = ChapterSerializer(many=True, read_only=True)
    
    class Meta(SubjectSerializer.Meta):
        fields = SubjectSerializer.Meta.fields + ['chapters']


class ChapterWithLessonsSerializer(ChapterSerializer):
    """Serializer for Chapter with nested lessons"""
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta(ChapterSerializer.Meta):
        fields = ChapterSerializer.Meta.fields + ['lessons']


class ContentSearchSerializer(serializers.Serializer):
    """Serializer for content search"""
    query = serializers.CharField(max_length=255)
    grade_level = serializers.IntegerField(required=False, min_value=1, max_value=4)
    subject = serializers.CharField(required=False, max_length=100)
    content_type = serializers.ChoiceField(
        choices=Lesson.LESSON_TYPES,
        required=False
    )
    is_premium = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        if not attrs.get('query') and not any([
            attrs.get('grade_level'),
            attrs.get('subject'),
            attrs.get('content_type')
        ]):
            raise serializers.ValidationError(
                "At least one search parameter is required"
            )
        return attrs



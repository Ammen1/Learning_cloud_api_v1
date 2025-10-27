"""
Serializers for analytics functionality.
"""
from rest_framework import serializers
from .models import (
    Analytics, UserEngagement, ContentAnalytics,
    SchoolAnalytics, SystemAnalytics, AnalyticsReport
)
from apps.accounts.serializers import UserProfileSerializer
from apps.content.serializers import SubjectSerializer, LessonSerializer


class AnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for Analytics model"""
    student = UserProfileSerializer(read_only=True)
    teacher = UserProfileSerializer(read_only=True)
    parent = UserProfileSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = Analytics
        fields = [
            'id', 'student', 'teacher', 'parent', 'subject', 'lesson',
            'metric_type', 'metric_value', 'metadata', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserEngagementSerializer(serializers.ModelSerializer):
    """Serializer for UserEngagement model"""
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = UserEngagement
        fields = [
            'id', 'user', 'date', 'login_count', 'session_duration',
            'lessons_accessed', 'lessons_completed', 'quizzes_attempted',
            'quizzes_completed', 'time_spent_learning', 'content_rated',
            'bookmarks_created', 'searches_performed', 'device_type',
            'platform', 'browser', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ContentAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for ContentAnalytics model"""
    
    class Meta:
        model = ContentAnalytics
        fields = [
            'id', 'content_type', 'content_id', 'total_views',
            'unique_viewers', 'completion_rate', 'average_time_spent',
            'average_score', 'rating_count', 'average_rating',
            'bookmark_count', 'bounce_rate', 'return_visitors',
            'social_shares', 'date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SchoolAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for SchoolAnalytics model"""
    
    class Meta:
        model = SchoolAnalytics
        fields = [
            'id', 'school', 'date', 'total_students', 'active_students',
            'engaged_students', 'total_lessons_completed', 'total_quizzes_attempted',
            'total_quizzes_passed', 'total_time_spent', 'average_score',
            'grade_1_students', 'grade_2_students', 'grade_3_students',
            'grade_4_students', 'subject_performance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SystemAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for SystemAnalytics model"""
    
    class Meta:
        model = SystemAnalytics
        fields = [
            'id', 'date', 'total_users', 'total_students', 'total_teachers',
            'total_parents', 'active_users', 'new_registrations', 'total_lessons',
            'total_quizzes', 'total_subjects', 'content_views', 'lessons_completed',
            'quizzes_attempted', 'quizzes_passed', 'total_learning_time',
            'average_session_duration', 'average_lesson_completion_rate',
            'average_quiz_pass_rate', 'page_load_time', 'error_rate',
            'uptime', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsReport model"""
    generated_by = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = AnalyticsReport
        fields = [
            'id', 'report_type', 'report_scope', 'title', 'description',
            'start_date', 'end_date', 'filters', 'data', 'summary',
            'generated_by', 'generated_at', 'is_scheduled', 'schedule_frequency'
        ]
        read_only_fields = ['id', 'generated_at']

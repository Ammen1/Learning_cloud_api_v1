"""
Serializers for progress tracking functionality.
"""
from rest_framework import serializers
from django.db.models import Avg, Count, Sum
from .models import (
    StudentProgress, LearningStreak, SubjectProgress,
    GradeProgress, ProgressMilestone, ProgressReport,
    ParentDashboard
)
from apps.content.serializers import LessonSerializer, SubjectSerializer
from apps.accounts.serializers import UserProfileSerializer


class StudentProgressSerializer(serializers.ModelSerializer):
    """Serializer for StudentProgress model"""
    lesson = LessonSerializer(read_only=True)
    student = UserProfileSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    time_spent_display = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProgress
        fields = [
            'id', 'student', 'lesson', 'status', 'started_at',
            'completed_at', 'time_spent', 'time_spent_display',
            'score', 'last_position', 'notes', 'progress_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage based on lesson type and position"""
        if obj.status == 'COMPLETED':
            return 100
        elif obj.status == 'NOT_STARTED':
            return 0
        elif obj.lesson.content_type == 'VIDEO' and obj.lesson.duration:
            # For videos, calculate based on last position
            return min((obj.last_position / (obj.lesson.duration * 60)) * 100, 99)
        elif obj.lesson.content_type == 'SLIDES':
            # For slides, estimate based on time spent
            estimated_duration = obj.lesson.duration * 60 if obj.lesson.duration else 300  # 5 min default
            return min((obj.time_spent / estimated_duration) * 100, 99)
        else:
            return 50 if obj.status == 'IN_PROGRESS' else 0
    
    def get_time_spent_display(self, obj):
        """Get formatted time spent"""
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"


class LearningStreakSerializer(serializers.ModelSerializer):
    """Serializer for LearningStreak model"""
    student = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = LearningStreak
        fields = [
            'id', 'student', 'current_streak', 'longest_streak',
            'last_activity_date', 'streak_start_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubjectProgressSerializer(serializers.ModelSerializer):
    """Serializer for SubjectProgress model"""
    subject = SubjectSerializer(read_only=True)
    student = UserProfileSerializer(read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    time_spent_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SubjectProgress
        fields = [
            'id', 'student', 'subject', 'total_lessons', 'completed_lessons',
            'completion_percentage', 'total_time_spent', 'time_spent_display',
            'average_score', 'last_activity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_completion_percentage(self, obj):
        """Calculate completion percentage"""
        if obj.total_lessons > 0:
            return round((obj.completed_lessons / obj.total_lessons) * 100, 2)
        return 0
    
    def get_time_spent_display(self, obj):
        """Get formatted time spent"""
        hours = obj.total_time_spent // 3600
        minutes = (obj.total_time_spent % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class GradeProgressSerializer(serializers.ModelSerializer):
    """Serializer for GradeProgress model"""
    student = UserProfileSerializer(read_only=True)
    lesson_completion_percentage = serializers.SerializerMethodField()
    quiz_pass_percentage = serializers.SerializerMethodField()
    subject_completion_percentage = serializers.SerializerMethodField()
    time_spent_display = serializers.SerializerMethodField()
    
    class Meta:
        model = GradeProgress
        fields = [
            'id', 'student', 'grade_level', 'total_subjects', 'completed_subjects',
            'subject_completion_percentage', 'total_lessons', 'completed_lessons',
            'lesson_completion_percentage', 'total_quizzes', 'passed_quizzes',
            'quiz_pass_percentage', 'total_time_spent', 'time_spent_display',
            'overall_average', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_lesson_completion_percentage(self, obj):
        """Calculate lesson completion percentage"""
        if obj.total_lessons > 0:
            return round((obj.completed_lessons / obj.total_lessons) * 100, 2)
        return 0
    
    def get_quiz_pass_percentage(self, obj):
        """Calculate quiz pass percentage"""
        if obj.total_quizzes > 0:
            return round((obj.passed_quizzes / obj.total_quizzes) * 100, 2)
        return 0
    
    def get_subject_completion_percentage(self, obj):
        """Calculate subject completion percentage"""
        if obj.total_subjects > 0:
            return round((obj.completed_subjects / obj.total_subjects) * 100, 2)
        return 0
    
    def get_time_spent_display(self, obj):
        """Get formatted time spent"""
        hours = obj.total_time_spent // 3600
        minutes = (obj.total_time_spent % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class ProgressMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for ProgressMilestone model"""
    student = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ProgressMilestone
        fields = [
            'id', 'student', 'milestone_type', 'title', 'description',
            'achieved_at', 'metadata', 'is_notified'
        ]
        read_only_fields = ['id', 'achieved_at']


class ProgressReportSerializer(serializers.ModelSerializer):
    """Serializer for ProgressReport model"""
    student = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ProgressReport
        fields = [
            'id', 'student', 'report_type', 'period_start', 'period_end',
            'data', 'generated_at', 'is_sent'
        ]
        read_only_fields = ['id', 'generated_at']


class ParentDashboardSerializer(serializers.ModelSerializer):
    """Serializer for ParentDashboard model"""
    parent = UserProfileSerializer(read_only=True)
    child = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ParentDashboard
        fields = [
            'id', 'parent', 'child', 'last_updated', 'data'
        ]
        read_only_fields = ['id', 'last_updated']


class ProgressStatsSerializer(serializers.Serializer):
    """Serializer for progress statistics"""
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    in_progress_lessons = serializers.IntegerField()
    total_time_spent = serializers.IntegerField()
    average_score = serializers.FloatField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    total_milestones = serializers.IntegerField()
    recent_milestones = serializers.ListField(child=ProgressMilestoneSerializer())
    subject_progress = serializers.ListField(child=SubjectProgressSerializer())
    grade_progress = GradeProgressSerializer()


class WeeklyProgressSerializer(serializers.Serializer):
    """Serializer for weekly progress data"""
    week_start = serializers.DateField()
    week_end = serializers.DateField()
    lessons_completed = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    quizzes_taken = serializers.IntegerField()
    quizzes_passed = serializers.IntegerField()
    average_score = serializers.FloatField()
    daily_activity = serializers.DictField()


class MonthlyProgressSerializer(serializers.Serializer):
    """Serializer for monthly progress data"""
    month = serializers.DateField()
    lessons_completed = serializers.IntegerField()
    time_spent = serializers.IntegerField()
    quizzes_taken = serializers.IntegerField()
    quizzes_passed = serializers.IntegerField()
    average_score = serializers.FloatField()
    weekly_breakdown = serializers.ListField(child=WeeklyProgressSerializer())
    subject_breakdown = serializers.DictField()
    milestones_achieved = serializers.ListField(child=ProgressMilestoneSerializer())


class ProgressComparisonSerializer(serializers.Serializer):
    """Serializer for progress comparison data"""
    student_progress = ProgressStatsSerializer()
    class_average = serializers.DictField()
    grade_average = serializers.DictField()
    improvement_areas = serializers.ListField(child=serializers.CharField())
    strengths = serializers.ListField(child=serializers.CharField())
    recommendations = serializers.ListField(child=serializers.CharField())



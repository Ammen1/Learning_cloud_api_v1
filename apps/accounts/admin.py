"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, School, UserSession, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'role', 
        'grade_level', 'student_id', 'teacher_id', 'is_active', 'is_verified'
    ]
    list_filter = ['role', 'grade_level', 'is_active', 'is_verified', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id', 'teacher_id']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role & Access', {'fields': ('role', 'is_active', 'is_verified')}),
        ('Student Info', {'fields': ('student_id', 'pin', 'grade_level', 'parent_email', 'school')}),
        ('Teacher Info', {'fields': ('teacher_id', 'subject_specialties')}),
        ('Parent Info', {'fields': ('parent',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    readonly_fields = ['created_at', 'date_joined']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('school', 'parent')


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """School admin"""
    list_display = ['name', 'city', 'country', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['name', 'city', 'address']
    ordering = ['name']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """User session admin"""
    list_display = ['user', 'ip_address', 'login_time', 'last_activity', 'is_active']
    list_filter = ['is_active', 'login_time']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['session_key', 'login_time', 'last_activity']
    ordering = ['-login_time']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Login attempt admin"""
    list_display = ['username', 'ip_address', 'success', 'failure_reason', 'attempted_at']
    list_filter = ['success', 'attempted_at']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['attempted_at']
    ordering = ['-attempted_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False



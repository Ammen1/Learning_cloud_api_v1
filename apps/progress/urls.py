"""
URL patterns for progress app.
"""
from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    # Progress tracking
    path('', views.StudentProgressListView.as_view(), name='progress_list'),
    path('<int:pk>/', views.StudentProgressDetailView.as_view(), name='progress_detail'),
    path('lessons/<int:lesson_id>/update/', views.update_lesson_progress, name='update_lesson_progress'),
    
    # Learning streak
    path('streak/', views.LearningStreakView.as_view(), name='learning_streak'),
    
    # Subject and grade progress
    path('subjects/', views.SubjectProgressListView.as_view(), name='subject_progress'),
    path('grade/', views.GradeProgressView.as_view(), name='grade_progress'),
    
    # Milestones
    path('milestones/', views.ProgressMilestoneListView.as_view(), name='milestones'),
    
    # Statistics and reports
    path('stats/', views.progress_stats, name='progress_stats'),
    path('weekly/', views.weekly_progress, name='weekly_progress'),
    path('monthly/', views.monthly_progress, name='monthly_progress'),
    
    # Parent dashboard
    path('parent-dashboard/<int:child_id>/', views.parent_dashboard, name='parent_dashboard'),
]



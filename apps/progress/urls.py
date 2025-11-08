"""
URL patterns for progress app.
"""
from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    # Progress tracking
    path('progress/', views.StudentProgressListView.as_view(), name='progress_list'),
    path('progress/<int:pk>/', views.StudentProgressDetailView.as_view(), name='progress_detail'),
    path('progress/lessons/<int:lesson_id>/update/', views.update_lesson_progress, name='update_lesson_progress'),
    
    # Learning streak
    path('progress/streak/', views.LearningStreakView.as_view(), name='learning_streak'),
    
    # Subject and grade progress
    path('progress/subjects/', views.SubjectProgressListView.as_view(), name='subject_progress'),
    path('progress/grade/', views.GradeProgressView.as_view(), name='grade_progress'),
    
    # Milestones
    path('progress/milestones/', views.ProgressMilestoneListView.as_view(), name='milestones'),
    
    # Statistics and reports
    path('progress/stats/', views.progress_stats, name='progress_stats'),
    path('progress/weekly/', views.weekly_progress, name='weekly_progress'),
    path('progress/monthly/', views.monthly_progress, name='monthly_progress'),
    
    # Parent dashboard
    path('progress/parent-dashboard/<int:child_id>/', views.parent_dashboard, name='parent_dashboard'),
]



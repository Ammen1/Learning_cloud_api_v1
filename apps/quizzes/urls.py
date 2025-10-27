"""
URL patterns for quizzes app.
"""
from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    # Quiz endpoints
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:quiz_id>/analytics/', views.quiz_analytics, name='quiz_analytics'),
    
    # Quiz attempts
    path('attempts/', views.QuizAttemptListView.as_view(), name='attempt_list'),
    path('attempts/start/', views.QuizAttemptCreateView.as_view(), name='start_attempt'),
    
    # Quiz sessions
    path('sessions/<str:session_key>/', views.QuizSessionView.as_view(), name='quiz_session'),
    path('sessions/<str:session_key>/submit-answer/', views.submit_answer, name='submit_answer'),
    path('sessions/<str:session_key>/complete/', views.complete_quiz, name='complete_quiz'),
    path('sessions/<str:session_key>/abandon/', views.abandon_quiz, name='abandon_quiz'),
    
    # Feedback
    path('feedback/', views.QuizFeedbackView.as_view(), name='quiz_feedback'),
    
    # Statistics
    path('stats/', views.quiz_stats, name='quiz_stats'),
]



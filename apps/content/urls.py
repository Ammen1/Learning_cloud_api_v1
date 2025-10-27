"""
URL patterns for content app.
"""
from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Subject endpoints
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    
    # Chapter endpoints
    path('chapters/', views.ChapterListView.as_view(), name='chapter_list'),
    path('chapters/<int:pk>/', views.ChapterDetailView.as_view(), name='chapter_detail'),
    
    # Lesson endpoints
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    
    # Search and discovery
    path('search/', views.ContentSearchView.as_view(), name='content_search'),
    
    # User interactions
    path('ratings/', views.ContentRatingView.as_view(), name='content_ratings'),
    path('bookmarks/', views.ContentBookmarkView.as_view(), name='content_bookmarks'),
    path('bookmarks/<int:pk>/', views.ContentBookmarkView.as_view(), name='bookmark_detail'),
    
    # Offline content
    path('offline/', views.OfflineContentListView.as_view(), name='offline_content'),
    
    # Premium access
    path('lessons/<int:lesson_id>/request-access/', views.request_premium_access, name='request_premium_access'),
    
    # Statistics
    path('stats/', views.content_stats, name='content_stats'),
    
    # Additional endpoints
    path('search/', views.search_content, name='search_content'),
    path('rate/', views.rate_content, name='rate_content'),
    path('bookmark/', views.bookmark_content, name='bookmark_content'),
    path('bookmarks/<int:bookmark_id>/remove/', views.remove_bookmark, name='remove_bookmark'),
    path('lessons/<int:lesson_id>/media/', views.upload_lesson_media, name='upload_lesson_media'),
]



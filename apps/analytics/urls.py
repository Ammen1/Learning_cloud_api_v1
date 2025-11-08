"""
URL patterns for analytics app.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Analytics endpoints
    path('analytics/', views.AnalyticsListView.as_view(), name='analytics_list'),
    path('analytics/reports/', views.AnalyticsReportListView.as_view(), name='reports_list'),
    path('analytics/reports/<int:pk>/', views.AnalyticsReportDetailView.as_view(), name='report_detail'),
    path('analytics/dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
]



"""
URL patterns for analytics app.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Analytics endpoints
    path('', views.AnalyticsListView.as_view(), name='analytics_list'),
    path('reports/', views.AnalyticsReportListView.as_view(), name='reports_list'),
    path('reports/<int:pk>/', views.AnalyticsReportDetailView.as_view(), name='report_detail'),
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('export/', views.export_analytics, name='export_analytics'),
]



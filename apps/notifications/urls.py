"""
URL patterns for notifications app.
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification endpoints
    path('', views.NotificationListView.as_view(), name='notification_list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('unread-count/', views.unread_notification_count, name='unread_notification_count'),
    
    # Preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification_preferences'),
    
    # Templates (admin only)
    path('templates/', views.NotificationTemplateListView.as_view(), name='notification_templates'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='notification_template_detail'),
    
    # Campaigns (admin only)
    path('campaigns/', views.NotificationCampaignListView.as_view(), name='notification_campaigns'),
    path('campaigns/<int:pk>/', views.NotificationCampaignDetailView.as_view(), name='notification_campaign_detail'),
    path('campaigns/<int:pk>/send/', views.send_campaign, name='send_campaign'),
]



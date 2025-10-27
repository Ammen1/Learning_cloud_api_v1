"""
Views for notifications functionality.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from .models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationLog, NotificationCampaign
)
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer,
    NotificationPreferenceSerializer, NotificationLogSerializer,
    NotificationCampaignSerializer
)
from apps.accounts.models import User
import logging

logger = logging.getLogger(__name__)


class NotificationListView(generics.ListAPIView):
    """List user's notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(user=user)
        
        # Filter by notification type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    """Get notification details"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Mark as read when viewed
        if not instance.is_read:
            instance.mark_as_read()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(
            id=pk,
            user=request.user
        )
        notification.mark_as_read()
        
        return Response({
            'message': 'Notification marked as read'
        }, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read for the user"""
    user = request.user
    
    # Get notification type filter if provided
    notification_type = request.data.get('notification_type')
    
    queryset = Notification.objects.filter(user=user, is_read=False)
    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)
    
    updated_count = queryset.update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'message': f'{updated_count} notifications marked as read'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_notification_count(request):
    """Get count of unread notifications"""
    user = request.user
    
    # Get total unread count
    total_unread = Notification.objects.filter(
        user=user,
        is_read=False
    ).count()
    
    # Get unread count by type
    unread_by_type = Notification.objects.filter(
        user=user,
        is_read=False
    ).values('notification_type').annotate(
        count=Count('id')
    ).order_by('notification_type')
    
    # Get unread count by priority
    unread_by_priority = Notification.objects.filter(
        user=user,
        is_read=False
    ).values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    return Response({
        'total_unread': total_unread,
        'unread_by_type': list(unread_by_type),
        'unread_by_priority': list(unread_by_priority)
    }, status=status.HTTP_200_OK)


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Get and update notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


class NotificationTemplateListView(generics.ListCreateAPIView):
    """List and create notification templates (admin only)"""
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return NotificationTemplate.objects.filter(is_active=True)


class NotificationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, and delete notification templates (admin only)"""
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return NotificationTemplate.objects.all()


class NotificationCampaignListView(generics.ListCreateAPIView):
    """List and create notification campaigns (admin only)"""
    serializer_class = NotificationCampaignSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return NotificationCampaign.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class NotificationCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, and delete notification campaigns (admin only)"""
    serializer_class = NotificationCampaignSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return NotificationCampaign.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def send_campaign(request, pk):
    """Send a notification campaign (admin only)"""
    try:
        campaign = NotificationCampaign.objects.get(id=pk)
    except NotificationCampaign.DoesNotExist:
        return Response({
            'error': 'Campaign not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if campaign.status != 'DRAFT':
        return Response({
            'error': 'Campaign can only be sent from draft status'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update campaign status
    campaign.status = 'RUNNING'
    campaign.save()
    
    # TODO: Implement actual sending logic
    # This would typically involve:
    # 1. Getting target users based on campaign criteria
    # 2. Creating notifications for each user
    # 3. Sending notifications via appropriate channels
    # 4. Updating campaign statistics
    
    logger.info(f"Campaign '{campaign.name}' started by {request.user.username}")
    
    return Response({
        'message': 'Campaign started successfully'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_notification(request):
    """Create a new notification (for system use)"""
    # This endpoint is typically used by the system to create notifications
    # based on user actions or scheduled events
    
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        # Set the user if not provided
        if not serializer.validated_data.get('user'):
            serializer.validated_data['user'] = request.user
        
        notification = serializer.save()
        
        # TODO: Send notification via appropriate channels
        # based on user preferences
        
        return Response({
            'message': 'Notification created successfully',
            'notification': NotificationSerializer(notification).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_notification(user, title, message, notification_type='SYSTEM', 
                     priority='MEDIUM', data=None, action_url=None):
    """Helper function to send notifications"""
    try:
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            data=data or {},
            action_url=action_url
        )
        
        # TODO: Send via email, push notification, etc.
        # based on user preferences
        
        logger.info(f"Notification sent to {user.username}: {title}")
        return notification
    
    except Exception as e:
        logger.error(f"Failed to send notification to {user.username}: {str(e)}")
        return None


def send_bulk_notification(users, title, message, notification_type='SYSTEM',
                          priority='MEDIUM', data=None, action_url=None):
    """Helper function to send notifications to multiple users"""
    notifications = []
    
    for user in users:
        notification = send_notification(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            data=data,
            action_url=action_url
        )
        if notification:
            notifications.append(notification)
    
    return notifications



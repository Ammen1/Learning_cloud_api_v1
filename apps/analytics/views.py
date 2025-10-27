"""
Views for analytics and reporting functionality.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta, date
from .models import Analytics, UserEngagement, ContentAnalytics, SchoolAnalytics, SystemAnalytics, AnalyticsReport
from .serializers import (
    AnalyticsSerializer, UserEngagementSerializer, ContentAnalyticsSerializer,
    SchoolAnalyticsSerializer, SystemAnalyticsSerializer, AnalyticsReportSerializer
)
from apps.accounts.models import User
import logging

logger = logging.getLogger(__name__)


class AnalyticsListView(generics.ListAPIView):
    """List analytics data with filtering"""
    serializer_class = AnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Analytics.objects.all()
        
        # Filter by user role
        if user.is_student():
            queryset = queryset.filter(student=user)
        elif user.is_teacher():
            queryset = queryset.filter(teacher=user)
        elif user.is_parent():
            queryset = queryset.filter(parent=user)
        
        # Apply filters
        metric_type = self.request.query_params.get('metric_type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-created_at')


class AnalyticsReportListView(generics.ListAPIView):
    """List analytics reports"""
    serializer_class = AnalyticsReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = AnalyticsReport.objects.all()
        
        # Filter by user role and permissions
        if user.is_student():
            # Students can only see their own reports
            queryset = queryset.filter(
                Q(report_scope='STUDENT') | Q(report_scope='SYSTEM')
            )
        elif user.is_teacher():
            # Teachers can see school and system reports
            queryset = queryset.filter(
                Q(report_scope='SCHOOL') | Q(report_scope='SYSTEM')
            )
        
        return queryset.order_by('-generated_at')


class AnalyticsReportDetailView(generics.RetrieveAPIView):
    """Get detailed analytics report"""
    serializer_class = AnalyticsReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = AnalyticsReport.objects.all()
        
        # Apply same filtering as list view
        if user.is_student():
            queryset = queryset.filter(
                Q(report_scope='STUDENT') | Q(report_scope='SYSTEM')
            )
        elif user.is_teacher():
            queryset = queryset.filter(
                Q(report_scope='SCHOOL') | Q(report_scope='SYSTEM')
            )
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analytics_dashboard(request):
    """Get analytics dashboard data"""
    user = request.user
    
    # Get date range (default to last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Get date range from query params if provided
    if request.query_params.get('start_date'):
        start_date = date.fromisoformat(request.query_params.get('start_date'))
    if request.query_params.get('end_date'):
        end_date = date.fromisoformat(request.query_params.get('end_date'))
    
    dashboard_data = {
        'date_range': {
            'start_date': start_date,
            'end_date': end_date
        },
        'summary': {},
        'trends': {},
        'top_content': [],
        'user_engagement': {}
    }
    
    if user.is_student():
        # Student dashboard
        student_analytics = Analytics.objects.filter(
            student=user,
            date__range=[start_date, end_date]
        )
        
        dashboard_data['summary'] = {
            'total_lessons_completed': student_analytics.filter(
                metric_type='lesson_completion'
            ).count(),
            'total_quizzes_taken': student_analytics.filter(
                metric_type='quiz_attempt'
            ).count(),
            'total_time_spent': student_analytics.filter(
                metric_type='time_spent'
            ).aggregate(total=Sum('metric_value'))['total'] or 0,
            'average_score': student_analytics.filter(
                metric_type='score_achieved'
            ).aggregate(avg=Avg('metric_value'))['avg'] or 0
        }
        
        # Get engagement data
        engagement = UserEngagement.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        dashboard_data['user_engagement'] = {
            'daily_activity': list(engagement.values('date', 'lessons_completed', 'time_spent_learning')),
            'total_sessions': engagement.aggregate(total=Sum('login_count'))['total'] or 0,
            'average_session_duration': engagement.aggregate(avg=Avg('session_duration'))['avg'] or 0
        }
    
    elif user.is_teacher():
        # Teacher dashboard
        teacher_analytics = Analytics.objects.filter(
            teacher=user,
            date__range=[start_date, end_date]
        )
        
        dashboard_data['summary'] = {
            'total_students': teacher_analytics.filter(
                metric_type='lesson_completion'
            ).values('student').distinct().count(),
            'total_lessons_created': teacher_analytics.filter(
                metric_type='lesson_access'
            ).count(),
            'average_student_score': teacher_analytics.filter(
                metric_type='score_achieved'
            ).aggregate(avg=Avg('metric_value'))['avg'] or 0
        }
    
    elif user.is_parent():
        # Parent dashboard
        children = User.objects.filter(parent=user)
        children_analytics = Analytics.objects.filter(
            student__in=children,
            date__range=[start_date, end_date]
        )
        
        dashboard_data['summary'] = {
            'total_children': children.count(),
            'total_lessons_completed': children_analytics.filter(
                metric_type='lesson_completion'
            ).count(),
            'total_time_spent': children_analytics.filter(
                metric_type='time_spent'
            ).aggregate(total=Sum('metric_value'))['total'] or 0,
            'average_score': children_analytics.filter(
                metric_type='score_achieved'
            ).aggregate(avg=Avg('metric_value'))['avg'] or 0
        }
    
    return Response(dashboard_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_analytics(request):
    """Export analytics data"""
    user = request.user
    
    # Get export parameters
    format_type = request.query_params.get('format', 'json')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Build queryset based on user role
    queryset = Analytics.objects.all()
    
    if user.is_student():
        queryset = queryset.filter(student=user)
    elif user.is_teacher():
        queryset = queryset.filter(teacher=user)
    elif user.is_parent():
        children = User.objects.filter(parent=user)
        queryset = queryset.filter(student__in=children)
    
    # Apply date filters
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    if end_date:
        queryset = queryset.filter(date__lte=end_date)
    
    # Get data
    data = list(queryset.values())
    
    if format_type == 'csv':
        # Convert to CSV format
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics_export.csv"'
        
        if data:
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return response
    
    else:
        # Return JSON format
        return Response({
            'data': data,
            'count': len(data),
            'exported_at': timezone.now(),
            'format': format_type
        }, status=status.HTTP_200_OK)



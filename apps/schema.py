from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.openapi import AutoSchema
from rest_framework import serializers
from .accounts.serializers import UserProfileSerializer
from .content.serializers import SubjectSerializer, ChapterSerializer, LessonSerializer
from .quizzes.serializers import QuizSerializer, QuizAttemptSerializer
from .progress.serializers import StudentProgressSerializer
from .analytics.serializers import AnalyticsSerializer
from .notifications.serializers import NotificationSerializer


# Use default AutoSchema for simplicity
from drf_spectacular.openapi import AutoSchema as CustomAutoSchema


# Schema extensions for better documentation
# Schema extensions for better documentation
# Note: These are template classes for documentation purposes


# Additional schema classes removed for simplicity


# Custom response schemas
class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Error type")
    message = serializers.CharField(help_text="Detailed error message")
    details = serializers.DictField(required=False, help_text="Additional error details")


class SuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(help_text="Operation success status")
    message = serializers.CharField(help_text="Success message")
    data = serializers.DictField(required=False, help_text="Response data")


class PaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(help_text="Total number of items")
    next = serializers.URLField(required=False, help_text="URL for next page")
    previous = serializers.URLField(required=False, help_text="URL for previous page")
    results = serializers.ListField(help_text="List of items")


# API documentation configuration
API_DOCS_CONFIG = {
    'TITLE': 'Learning Cloud API',
    'DESCRIPTION': '''
    A comprehensive learning management system API designed to support 20M+ students.
    
    ## Features
    - **User Management**: Student, teacher, and parent accounts with role-based access
    - **Content Management**: Subjects, chapters, lessons with multimedia support
    - **Quiz System**: Interactive quizzes with multiple question types and analytics
    - **Progress Tracking**: Detailed progress monitoring and learning streaks
    - **Analytics**: Comprehensive analytics and reporting
    - **Notifications**: Real-time notifications and communication
    - **Parent Dashboard**: Parent access to child's learning progress
    
    ## Authentication
    This API uses OAuth2 token-based authentication. Include the access token in the Authorization header:
    ```
    Authorization: Bearer <your_access_token>
    ```
    
    ## Rate Limiting
    API requests are rate limited to ensure fair usage:
    - Authentication endpoints: 5 requests per minute
    - General API endpoints: 1000 requests per hour per user
    - Analytics endpoints: 10 requests per minute
    
    ## Pagination
    All list endpoints support pagination with the following parameters:
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    
    ## Filtering and Search
    Most endpoints support filtering and search:
    - Use query parameters to filter results
    - Use `search` parameter for text search
    - Use `ordering` parameter for sorting
    
    ## Error Handling
    The API returns appropriate HTTP status codes and detailed error messages:
    - 400: Bad Request - Invalid input data
    - 401: Unauthorized - Authentication required
    - 403: Forbidden - Insufficient permissions
    - 404: Not Found - Resource not found
    - 429: Too Many Requests - Rate limit exceeded
    - 500: Internal Server Error - Server error
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENTS': {
        'securitySchemes': {
            'OAuth2': {
                'type': 'oauth2',
                'flows': {
                    'authorizationCode': {
                        'authorizationUrl': '/api/auth/authorize/',
                        'tokenUrl': '/api/auth/token/',
                        'scopes': {
                            'read': 'Read access',
                            'write': 'Write access',
                            'admin': 'Admin access'
                        }
                    }
                }
            }
        }
    },
    'TAGS': [
        {
            'name': 'Authentication',
            'description': 'User authentication and account management'
        },
        {
            'name': 'Content Management',
            'description': 'Subjects, chapters, lessons, and media management'
        },
        {
            'name': 'Quiz System',
            'description': 'Quiz creation, attempts, and analytics'
        },
        {
            'name': 'Progress Tracking',
            'description': 'Student progress monitoring and learning streaks'
        },
        {
            'name': 'Analytics',
            'description': 'Data analytics and reporting'
        },
        {
            'name': 'Notifications',
            'description': 'Notification management and preferences'
        },
        {
            'name': 'Parent Dashboard',
            'description': 'Parent access to child progress and analytics'
        }
    ]
}

"""
Views for content management.
"""
from rest_framework import generics, status, permissions, filters, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from django.core.cache import cache
from django.utils import timezone
from django.core.files.storage import default_storage
from .models import (
    Subject, Chapter, Lesson, LessonMedia, ContentVersion,
    OfflineContent, ContentAccess, ContentRating, ContentBookmark
)
from .serializers import (
    SubjectSerializer, ChapterSerializer, LessonSerializer,
    LessonDetailSerializer, ContentVersionSerializer,
    OfflineContentSerializer, ContentAccessSerializer,
    ContentRatingSerializer, ContentBookmarkSerializer,
    SubjectWithChaptersSerializer, ChapterWithLessonsSerializer,
    ContentSearchSerializer
)
from apps.accounts.models import User
import logging

logger = logging.getLogger(__name__)


class SubjectListView(generics.ListAPIView):
    """List all subjects for a grade level"""
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade_level', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order_index', 'created_at']
    ordering = ['grade_level', 'order_index']
    
    def get_queryset(self):
        user = self.request.user
        queryset = Subject.objects.filter(is_active=True)
        
        # Filter by user's grade level if student
        if user.is_student() and user.grade_level:
            queryset = queryset.filter(grade_level=user.grade_level)
        
        return queryset.select_related('school').prefetch_related('chapters')


class SubjectDetailView(generics.RetrieveAPIView):
    """Get detailed subject information with chapters"""
    serializer_class = SubjectWithChaptersSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Subject.objects.filter(is_active=True).prefetch_related(
            Prefetch('chapters', queryset=Chapter.objects.filter(is_active=True).order_by('order_index'))
        )


class ChapterListView(generics.ListAPIView):
    """List chapters for a subject"""
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['subject', 'is_active']
    ordering_fields = ['title', 'order_index', 'created_at']
    ordering = ['order_index']
    
    def get_queryset(self):
        return Chapter.objects.filter(is_active=True).select_related('subject').prefetch_related('lessons')


class ChapterDetailView(generics.RetrieveAPIView):
    """Get detailed chapter information with lessons"""
    serializer_class = ChapterWithLessonsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Chapter.objects.filter(is_active=True).prefetch_related(
            Prefetch('lessons', queryset=Lesson.objects.filter(is_active=True).order_by('order_index'))
        )


class LessonListView(generics.ListAPIView):
    """List lessons for a chapter"""
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['chapter', 'content_type', 'is_premium', 'is_active']
    search_fields = ['title', 'content', 'learning_objectives']
    ordering_fields = ['title', 'order_index', 'duration', 'created_at']
    ordering = ['order_index']
    
    def get_queryset(self):
        queryset = Lesson.objects.filter(is_active=True).select_related(
            'chapter__subject'
        ).prefetch_related('media_files', 'ratings', 'bookmarks')
        
        # Filter by user's access level
        user = self.request.user
        if user.is_student():
            # Students can see free content and premium if they have access
            queryset = queryset.filter(
                Q(is_premium=False) | 
                Q(contentaccess__user=user, contentaccess__is_active=True)
            )
        
        return queryset


class LessonDetailView(generics.RetrieveAPIView):
    """Get detailed lesson information"""
    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Lesson.objects.filter(is_active=True).select_related(
            'chapter__subject'
        ).prefetch_related(
            'media_files', 'ratings', 'bookmarks', 'prerequisites'
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check access permissions
        if instance.is_premium and not self._has_premium_access(request.user, instance):
            return Response({
                'error': 'Premium content requires special access'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Track lesson access for analytics
        self._track_lesson_access(request.user, instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def _has_premium_access(self, user, lesson):
        """Check if user has premium access to lesson"""
        if user.is_student():
            return ContentAccess.objects.filter(
                user=user,
                lesson=lesson,
                is_active=True
            ).exists()
        return True  # Teachers and parents have full access
    
    def _track_lesson_access(self, user, lesson):
        """Track lesson access for analytics"""
        try:
            from apps.analytics.models import Analytics
            Analytics.objects.create(
                student_id=user.id if user.is_student() else None,
                teacher_id=user.id if user.is_teacher() else None,
                metric_type='lesson_access',
                metric_value=1,
                metadata={
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'subject': lesson.chapter.subject.name,
                    'grade_level': lesson.chapter.subject.grade_level
                }
            )
        except Exception as e:
            logger.error(f"Failed to track lesson access: {str(e)}")


class ContentSearchView(generics.ListAPIView):
    """Search content across subjects, chapters, and lessons"""
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        serializer = ContentSearchSerializer(data=self.request.query_params)
        if not serializer.is_valid():
            return Lesson.objects.none()
        
        data = serializer.validated_data
        queryset = Lesson.objects.filter(is_active=True).select_related(
            'chapter__subject'
        )
        
        # Apply search filters
        if data.get('query'):
            queryset = queryset.filter(
                Q(title__icontains=data['query']) |
                Q(content__icontains=data['query']) |
                Q(chapter__title__icontains=data['query']) |
                Q(chapter__subject__name__icontains=data['query'])
            )
        
        if data.get('grade_level'):
            queryset = queryset.filter(chapter__subject__grade_level=data['grade_level'])
        
        if data.get('subject'):
            queryset = queryset.filter(chapter__subject__name__icontains=data['subject'])
        
        if data.get('content_type'):
            queryset = queryset.filter(content_type=data['content_type'])
        
        if data.get('is_premium') is not None:
            queryset = queryset.filter(is_premium=data['is_premium'])
        
        return queryset.order_by('-created_at')


class ContentRatingView(generics.ListCreateAPIView):
    """List and create content ratings"""
    serializer_class = ContentRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson', 'rating']
    
    def get_queryset(self):
        return ContentRating.objects.filter(
            lesson__is_active=True
        ).select_related('user', 'lesson')
    
    def perform_create(self, serializer):
        lesson_id = self.request.data.get('lesson')
        if lesson_id:
            # Check if user already rated this lesson
            existing_rating = ContentRating.objects.filter(
                user=self.request.user,
                lesson_id=lesson_id
            ).first()
            
            if existing_rating:
                # Update existing rating
                existing_rating.rating = serializer.validated_data['rating']
                existing_rating.review = serializer.validated_data.get('review', '')
                existing_rating.save()
                return existing_rating
        
        return serializer.save()


class ContentBookmarkView(mixins.DestroyModelMixin, generics.ListCreateAPIView):
    """Manage content bookmarks"""
    serializer_class = ContentBookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ContentBookmark.objects.filter(
            user=self.request.user,
            lesson__is_active=True
        ).select_related('lesson__chapter__subject')
    
    def perform_create(self, serializer):
        lesson_id = self.request.data.get('lesson')
        if lesson_id:
            # Check if already bookmarked
            existing_bookmark = ContentBookmark.objects.filter(
                user=self.request.user,
                lesson_id=lesson_id
            ).first()
            
            if existing_bookmark:
                return existing_bookmark
        
        return serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfflineContentListView(generics.ListAPIView):
    """List available offline content"""
    serializer_class = OfflineContentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lesson', 'is_available']
    
    def get_queryset(self):
        return OfflineContent.objects.filter(
            is_available=True,
            lesson__is_active=True
        ).select_related('lesson')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def content_stats(request):
    """Get content statistics for the user"""
    user = request.user
    
    stats = {
        'total_subjects': 0,
        'total_chapters': 0,
        'total_lessons': 0,
        'completed_lessons': 0,
        'bookmarked_lessons': 0,
        'rated_lessons': 0,
    }
    
    if user.is_student() and user.grade_level:
        # Get stats for student's grade level
        subjects = Subject.objects.filter(
            grade_level=user.grade_level,
            is_active=True
        )
        
        stats['total_subjects'] = subjects.count()
        stats['total_chapters'] = Chapter.objects.filter(
            subject__in=subjects,
            is_active=True
        ).count()
        
        lessons = Lesson.objects.filter(
            chapter__subject__in=subjects,
            is_active=True
        )
        stats['total_lessons'] = lessons.count()
        
        # Get user-specific stats
        stats['bookmarked_lessons'] = ContentBookmark.objects.filter(
            user=user,
            lesson__in=lessons
        ).count()
        
        stats['rated_lessons'] = ContentRating.objects.filter(
            user=user,
            lesson__in=lessons
        ).count()
        
        # Get completed lessons from progress tracking
        from apps.progress.models import StudentProgress
        stats['completed_lessons'] = StudentProgress.objects.filter(
            student=user,
            lesson__in=lessons,
            status='COMPLETED'
        ).count()
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_premium_access(request, lesson_id):
    """Request premium access to a lesson"""
    try:
        lesson = Lesson.objects.get(id=lesson_id, is_active=True)
        
        if not lesson.is_premium:
            return Response({
                'error': 'This lesson is already free'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if access already exists
        existing_access = ContentAccess.objects.filter(
            user=request.user,
            lesson=lesson
        ).first()
        
        if existing_access:
            if existing_access.is_active:
                return Response({
                    'message': 'You already have access to this lesson'
                }, status=status.HTTP_200_OK)
            else:
                existing_access.is_active = True
                existing_access.save()
        else:
            # Create new access request
            ContentAccess.objects.create(
                user=request.user,
                lesson=lesson,
                access_type='PREMIUM'
            )
        
        logger.info(f"Premium access requested: {request.user.username} - {lesson.title}")
        
        return Response({
            'message': 'Premium access request submitted successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Lesson.DoesNotExist:
        return Response({
            'error': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_lesson_media(request, lesson_id):
    """Upload media files for a lesson"""
    try:
        lesson = Lesson.objects.get(id=lesson_id, is_active=True)
        
        # Check if user has permission to upload media
        if not (request.user.is_teacher() or request.user.is_staff):
            return Response({
                'error': 'Only teachers can upload media files'
            }, status=status.HTTP_403_FORBIDDEN)
        
        file = request.FILES.get('file')
        if not file:
            return Response({
                'error': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file type and size
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/webm', 'audio/mp3', 'audio/wav']
        if file.content_type not in allowed_types:
            return Response({
                'error': 'Invalid file type. Allowed types: JPEG, PNG, GIF, MP4, WebM, MP3, WAV'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            return Response({
                'error': 'File size too large. Maximum size is 50MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create media file
        media = LessonMedia.objects.create(
            lesson=lesson,
            media_type=request.data.get('media_type', 'IMAGE'),
            file=file,
            file_name=file.name,
            order_index=request.data.get('order_index', 0)
        )
        
        return Response({
            'message': 'Media file uploaded successfully',
            'media_id': media.id,
            'file_url': media.file.url
        }, status=status.HTTP_201_CREATED)
        
    except Lesson.DoesNotExist:
        return Response({
            'error': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error uploading media: {str(e)}")
        return Response({
            'error': 'Failed to upload media file'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_content(request):
    """Search content across subjects, chapters, and lessons"""
    query = request.GET.get('query', '')
    grade_level = request.GET.get('grade_level')
    subject = request.GET.get('subject')
    content_type = request.GET.get('content_type')
    is_premium = request.GET.get('is_premium')
    
    if not query:
        return Response({
            'error': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Build search query
    search_filters = Q(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(chapter__title__icontains=query) |
        Q(chapter__subject__name__icontains=query)
    )
    
    queryset = Lesson.objects.filter(
        search_filters,
        is_active=True
    ).select_related('chapter__subject')
    
    # Apply additional filters
    if grade_level:
        queryset = queryset.filter(chapter__subject__grade_level=grade_level)
    
    if subject:
        queryset = queryset.filter(chapter__subject__name__icontains=subject)
    
    if content_type:
        queryset = queryset.filter(content_type=content_type)
    
    if is_premium is not None:
        queryset = queryset.filter(is_premium=is_premium.lower() == 'true')
    
    # Filter by user access
    user = request.user
    if user.is_student():
        queryset = queryset.filter(
            Q(is_premium=False) | 
            Q(contentaccess__user=user, contentaccess__is_active=True)
        )
    
    # Order by relevance (exact title matches first)
    queryset = queryset.order_by(
        '-title__icontains',  # Exact title matches
        '-created_at'  # Then by newest
    )
    
    # Paginate results
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = 20
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = LessonSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = LessonSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_content(request):
    """Rate a lesson"""
    lesson_id = request.data.get('lesson')
    rating = request.data.get('rating')
    review = request.data.get('review', '')
    
    if not lesson_id or not rating:
        return Response({
            'error': 'Lesson ID and rating are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not (1 <= rating <= 5):
        return Response({
            'error': 'Rating must be between 1 and 5'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        lesson = Lesson.objects.get(id=lesson_id, is_active=True)
        
        # Check if user already rated this lesson
        existing_rating = ContentRating.objects.filter(
            user=request.user,
            lesson=lesson
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.review = review
            existing_rating.save()
            message = 'Rating updated successfully'
        else:
            # Create new rating
            ContentRating.objects.create(
                user=request.user,
                lesson=lesson,
                rating=rating,
                review=review
            )
            message = 'Rating submitted successfully'
        
        # Update lesson's average rating
        lesson.update_average_rating()
        
        return Response({
            'message': message,
            'rating': rating,
            'review': review
        }, status=status.HTTP_201_CREATED)
        
    except Lesson.DoesNotExist:
        return Response({
            'error': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bookmark_content(request):
    """Bookmark a lesson"""
    lesson_id = request.data.get('lesson')
    
    if not lesson_id:
        return Response({
            'error': 'Lesson ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        lesson = Lesson.objects.get(id=lesson_id, is_active=True)
        
        # Check if already bookmarked
        existing_bookmark = ContentBookmark.objects.filter(
            user=request.user,
            lesson=lesson
        ).first()
        
        if existing_bookmark:
            return Response({
                'message': 'Lesson already bookmarked'
            }, status=status.HTTP_200_OK)
        
        # Create new bookmark
        bookmark = ContentBookmark.objects.create(
            user=request.user,
            lesson=lesson
        )
        
        return Response({
            'message': 'Lesson bookmarked successfully',
            'bookmark_id': bookmark.id
        }, status=status.HTTP_201_CREATED)
        
    except Lesson.DoesNotExist:
        return Response({
            'error': 'Lesson not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_bookmark(request, bookmark_id):
    """Remove a bookmark"""
    try:
        bookmark = ContentBookmark.objects.get(
            id=bookmark_id,
            user=request.user
        )
        bookmark.delete()
        
        return Response({
            'message': 'Bookmark removed successfully'
        }, status=status.HTTP_200_OK)
        
    except ContentBookmark.DoesNotExist:
        return Response({
            'error': 'Bookmark not found'
        }, status=status.HTTP_404_NOT_FOUND)



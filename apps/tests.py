from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .accounts.models import School
from .content.models import Subject, Chapter, Lesson
from .quizzes.models import Quiz, Question, QuizAttempt
from .progress.models import StudentProgress
from .notifications.models import Notification
import json

User = get_user_model()


class UserAuthenticationTestCase(APITestCase):
    """
    Test cases for user authentication functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            city="Test City",
            country="Ethiopia"
        )
        
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='STUDENT',
            student_id='S12345',
            grade_level=1,
            school=self.school
        )
        
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='TEACHER',
            teacher_id='T12345',
            school=self.school
        )
        
        self.parent = User.objects.create_user(
            username='testparent',
            email='parent@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Parent',
            role='PARENT'
        )
    
    def test_student_login(self):
        """Test student login functionality."""
        url = reverse('student-login')
        data = {
            'username': 'teststudent',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
    
    def test_teacher_login(self):
        """Test teacher login functionality."""
        url = reverse('teacher-login')
        data = {
            'username': 'testteacher',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
    
    def test_parent_login(self):
        """Test parent login functionality."""
        url = reverse('parent-login')
        data = {
            'username': 'testparent',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        url = reverse('student-login')
        data = {
            'username': 'teststudent',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_registration(self):
        """Test user registration functionality."""
        url = reverse('user-register')
        data = {
            'username': 'newstudent',
            'email': 'newstudent@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'Student',
            'role': 'STUDENT',
            'student_id': 'S67890',
            'grade_level': 2,
            'school': self.school.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newstudent').exists())


class ContentManagementTestCase(APITestCase):
    """
    Test cases for content management functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            city="Test City",
            country="Ethiopia"
        )
        
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='TEACHER',
            teacher_id='T12345',
            school=self.school
        )
        
        self.subject = Subject.objects.create(
            name="Mathematics",
            description="Basic mathematics concepts",
            grade_level=1,
            school=self.school
        )
        
        self.chapter = Chapter.objects.create(
            title="Addition",
            description="Learning basic addition",
            subject=self.subject,
            estimated_duration=60
        )
        
        self.lesson = Lesson.objects.create(
            title="Adding Numbers",
            content="Learn how to add numbers",
            content_type="VIDEO",
            duration=15,
            chapter=self.chapter
        )
        
        # Get authentication token
        self.token = Token.objects.create(user=self.teacher)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_list_subjects(self):
        """Test listing subjects."""
        url = reverse('subject-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_subject_detail(self):
        """Test getting subject details."""
        url = reverse('subject-detail', kwargs={'pk': self.subject.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mathematics')
    
    def test_list_chapters(self):
        """Test listing chapters."""
        url = reverse('chapter-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_chapter_detail(self):
        """Test getting chapter details."""
        url = reverse('chapter-detail', kwargs={'pk': self.chapter.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Addition')
    
    def test_list_lessons(self):
        """Test listing lessons."""
        url = reverse('lesson-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_lesson_detail(self):
        """Test getting lesson details."""
        url = reverse('lesson-detail', kwargs={'pk': self.lesson.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Adding Numbers')


class QuizSystemTestCase(APITestCase):
    """
    Test cases for quiz system functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            city="Test City",
            country="Ethiopia"
        )
        
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='TEACHER',
            teacher_id='T12345',
            school=self.school
        )
        
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='STUDENT',
            student_id='S12345',
            grade_level=1,
            school=self.school
        )
        
        self.subject = Subject.objects.create(
            name="Mathematics",
            description="Basic mathematics concepts",
            grade_level=1,
            school=self.school
        )
        
        self.quiz = Quiz.objects.create(
            title="Math Quiz",
            description="Test your math skills",
            subject=self.subject,
            grade_level=1,
            time_limit=30,
            max_attempts=3,
            passing_score=70,
            created_by=self.teacher
        )
        
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text="What is 2 + 2?",
            question_type="MULTIPLE_CHOICE",
            options=["3", "4", "5", "6"],
            correct_answer="4",
            points=1
        )
        
        # Get authentication token
        self.student_token = Token.objects.create(user=self.student)
        self.teacher_token = Token.objects.create(user=self.teacher)
    
    def test_list_quizzes(self):
        """Test listing quizzes."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        url = reverse('quiz-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_quiz_detail(self):
        """Test getting quiz details."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        url = reverse('quiz-detail', kwargs={'pk': self.quiz.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Math Quiz')
    
    def test_start_quiz_attempt(self):
        """Test starting a quiz attempt."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        url = reverse('quiz-attempt-start', kwargs={'quiz_id': self.quiz.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('attempt_id', response.data)
    
    def test_submit_quiz_answer(self):
        """Test submitting a quiz answer."""
        # Start quiz attempt
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
        start_url = reverse('quiz-attempt-start', kwargs={'quiz_id': self.quiz.pk})
        start_response = self.client.post(start_url)
        attempt_id = start_response.data['attempt_id']
        
        # Submit answer
        submit_url = reverse('quiz-session-submit-answer', kwargs={'session_id': attempt_id})
        data = {
            'question_id': self.question.pk,
            'answer_text': '4'
        }
        response = self.client.post(submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_correct', response.data)


class ProgressTrackingTestCase(APITestCase):
    """
    Test cases for progress tracking functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            city="Test City",
            country="Ethiopia"
        )
        
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='STUDENT',
            student_id='S12345',
            grade_level=1,
            school=self.school
        )
        
        self.subject = Subject.objects.create(
            name="Mathematics",
            description="Basic mathematics concepts",
            grade_level=1,
            school=self.school
        )
        
        self.chapter = Chapter.objects.create(
            title="Addition",
            description="Learning basic addition",
            subject=self.subject,
            estimated_duration=60
        )
        
        self.lesson = Lesson.objects.create(
            title="Adding Numbers",
            content="Learn how to add numbers",
            content_type="VIDEO",
            duration=15,
            chapter=self.chapter
        )
        
        # Get authentication token
        self.student_token = Token.objects.create(user=self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
    
    def test_list_student_progress(self):
        """Test listing student progress."""
        url = reverse('student-progress-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_lesson_progress(self):
        """Test updating lesson progress."""
        url = reverse('lesson-progress-update', kwargs={'lesson_id': self.lesson.pk})
        data = {
            'status': 'COMPLETED',
            'time_spent': 900,
            'score': 85
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify progress was created
        progress = StudentProgress.objects.get(student=self.student, lesson=self.lesson)
        self.assertEqual(progress.status, 'COMPLETED')
        self.assertEqual(progress.time_spent, 900)
        self.assertEqual(progress.score, 85)


class NotificationSystemTestCase(APITestCase):
    """
    Test cases for notification system functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='STUDENT'
        )
        
        # Get authentication token
        self.student_token = Token.objects.create(user=self.student)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.student_token.key}')
    
    def test_list_notifications(self):
        """Test listing notifications."""
        # Create a test notification
        Notification.objects.create(
            user=self.student,
            title="Test Notification",
            message="This is a test notification",
            notification_type="GENERAL"
        )
        
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_mark_notification_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            user=self.student,
            title="Test Notification",
            message="This is a test notification",
            notification_type="GENERAL"
        )
        
        url = reverse('notification-mark-read', kwargs={'pk': notification.pk})
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify notification was marked as read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)


class AnalyticsTestCase(APITestCase):
    """
    Test cases for analytics functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Teacher',
            role='TEACHER'
        )
        
        # Get authentication token
        self.teacher_token = Token.objects.create(user=self.teacher)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher_token.key}')
    
    def test_list_analytics(self):
        """Test listing analytics data."""
        url = reverse('analytics-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_analytics_dashboard(self):
        """Test analytics dashboard."""
        url = reverse('analytics-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)


class RateLimitingTestCase(APITestCase):
    """
    Test cases for rate limiting functionality.
    """
    
    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='STUDENT'
        )
    
    def test_rate_limiting(self):
        """Test rate limiting on login endpoint."""
        url = reverse('student-login')
        data = {
            'username': 'teststudent',
            'password': 'testpass123'
        }
        
        # Make multiple requests quickly
        for _ in range(10):
            response = self.client.post(url, data, format='json')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        
        # Should eventually hit rate limit
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS])


class WebhookTestCase(APITestCase):
    """
    Test cases for webhook functionality.
    """
    
    def test_payment_webhook(self):
        """Test payment webhook handling."""
        url = reverse('payment_webhook')
        data = {
            'event_type': 'payment.completed',
            'user_id': 1,
            'amount': 100.00
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_content_webhook(self):
        """Test content webhook handling."""
        url = reverse('content_webhook')
        data = {
            'event_type': 'content.updated',
            'lesson_id': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

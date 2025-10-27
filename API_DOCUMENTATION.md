# Learning Cloud API Documentation

## Overview

The Learning Cloud API is a comprehensive RESTful API built with Django and Django REST Framework, designed to support an educational platform for students in grades 1-4. The API handles authentication, content management, quizzes, progress tracking, analytics, and notifications.

## Base URL

```
Production: https://api.learningcloud.com
Development: http://localhost:8000
```

## Authentication

The API uses OAuth2 token-based authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

### Student Login
Students log in using their Student ID and PIN:

```http
POST /api/auth/student-login/
Content-Type: application/json

{
    "student_id": "12345",
    "pin": "1234"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "student123",
        "first_name": "John",
        "last_name": "Doe",
        "role": "STUDENT",
        "grade_level": 1,
        "student_id": "12345"
    },
    "token": "your-oauth-token"
}
```

### Teacher Login
```http
POST /api/auth/teacher-login/
Content-Type: application/json

{
    "username": "teacher@school.com",
    "password": "password123"
}
```

### Parent Login
```http
POST /api/auth/parent-login/
Content-Type: application/json

{
    "username": "parent@email.com",
    "password": "password123"
}
```

## Content Management

### Get Subjects by Grade
```http
GET /api/subjects/?grade_level=1
Authorization: Bearer <token>
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "name": "Mathematics",
            "description": "Basic math concepts for Grade 1",
            "grade_level": 1,
            "icon_url": "https://cdn.example.com/math-icon.png",
            "color_code": "#FF6B6B",
            "chapter_count": 8,
            "lesson_count": 24
        }
    ]
}
```

### Get Chapters for a Subject
```http
GET /api/chapters/?subject=1
Authorization: Bearer <token>
```

### Get Lessons for a Chapter
```http
GET /api/lessons/?chapter=1
Authorization: Bearer <token>
```

### Get Lesson Details
```http
GET /api/lessons/123/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "id": 123,
    "title": "Addition Basics",
    "content": "<p>Learn the basics of addition...</p>",
    "content_type": "SLIDES",
    "video_url": "https://cdn.example.com/lesson123.mp4",
    "duration": 15,
    "chapter": {
        "id": 1,
        "title": "Numbers 1-10",
        "subject": {
            "id": 1,
            "name": "Mathematics"
        }
    },
    "media_files": [
        {
            "id": 1,
            "media_type": "IMAGE",
            "file_url": "https://cdn.example.com/image1.jpg",
            "file_name": "addition_example.jpg"
        }
    ],
    "average_rating": 4.5,
    "rating_count": 12,
    "is_bookmarked": false
}
```

## Quiz System

### Get Available Quizzes
```http
GET /api/quizzes/?subject=1&grade_level=1
Authorization: Bearer <token>
```

### Start Quiz Attempt
```http
POST /api/quizzes/attempts/start/
Authorization: Bearer <token>
Content-Type: application/json

{
    "quiz": 1
}
```

**Response:**
```json
{
    "id": 1,
    "student": {
        "id": 1,
        "username": "student123",
        "first_name": "John",
        "last_name": "Doe"
    },
    "quiz": {
        "id": 1,
        "title": "Addition Quiz",
        "time_limit": 30,
        "max_attempts": 3
    },
    "started_at": "2024-01-15T10:30:00Z",
    "total_questions": 10,
    "session_key": "student123_1_1"
}
```

### Submit Answer
```http
POST /api/quizzes/sessions/student123_1_1/submit-answer/
Authorization: Bearer <token>
Content-Type: application/json

{
    "question_id": 1,
    "answer_text": "5",
    "time_spent": 15
}
```

### Complete Quiz
```http
POST /api/quizzes/sessions/student123_1_1/complete/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "message": "Quiz completed successfully",
    "attempt": {
        "id": 1,
        "score": 85.0,
        "total_questions": 10,
        "correct_answers": 8,
        "time_spent": 420,
        "is_passed": true
    },
    "result": {
        "id": 1,
        "total_time": 420,
        "average_time_per_question": 42.0,
        "improvement_suggestions": [
            "Review addition with larger numbers",
            "Practice mental math techniques"
        ]
    }
}
```

## Progress Tracking

### Update Lesson Progress
```http
POST /api/progress/lessons/123/update/
Authorization: Bearer <token>
Content-Type: application/json

{
    "action": "complete",
    "time_spent": 900,
    "score": 95
}
```

### Get Student Progress
```http
GET /api/progress/?status=completed
Authorization: Bearer <token>
```

### Get Progress Statistics
```http
GET /api/progress/stats/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "total_lessons": 50,
    "completed_lessons": 35,
    "in_progress_lessons": 5,
    "total_time_spent": 18000,
    "average_score": 87.5,
    "current_streak": 7,
    "longest_streak": 15,
    "total_milestones": 8,
    "recent_milestones": [
        {
            "id": 1,
            "title": "10 Lessons Completed!",
            "description": "Amazing! You've completed 10 lessons.",
            "achieved_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Get Learning Streak
```http
GET /api/progress/streak/
Authorization: Bearer <token>
```

## Analytics

### Get Analytics Dashboard
```http
GET /api/analytics/dashboard/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

### Get Weekly Progress
```http
GET /api/progress/weekly/
Authorization: Bearer <token>
```

## Notifications

### Get Notifications
```http
GET /api/notifications/?is_read=false
Authorization: Bearer <token>
```

### Mark Notification as Read
```http
POST /api/notifications/123/mark-read/
Authorization: Bearer <token>
```

### Get Unread Count
```http
GET /api/notifications/unread-count/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "total_unread": 3,
    "unread_by_type": [
        {
            "notification_type": "ACHIEVEMENT",
            "count": 1
        },
        {
            "notification_type": "QUIZ_RESULT",
            "count": 2
        }
    ]
}
```

## Content Interactions

### Rate Content
```http
POST /api/ratings/
Authorization: Bearer <token>
Content-Type: application/json

{
    "lesson": 123,
    "rating": 5,
    "review": "Great lesson! Very helpful."
}
```

### Bookmark Content
```http
POST /api/bookmarks/
Authorization: Bearer <token>
Content-Type: application/json

{
    "lesson": 123
}
```

### Search Content
```http
GET /api/search/?query=addition&grade_level=1&content_type=SLIDES
Authorization: Bearer <token>
```

## Parent Dashboard

### Get Child's Progress
```http
GET /api/progress/parent-dashboard/456/
Authorization: Bearer <token>
```

**Response:**
```json
{
    "id": 1,
    "parent": {
        "id": 1,
        "username": "parent@email.com",
        "first_name": "Jane",
        "last_name": "Doe"
    },
    "child": {
        "id": 456,
        "username": "student456",
        "first_name": "Alice",
        "last_name": "Doe",
        "grade_level": 2
    },
    "data": {
        "total_lessons": 40,
        "completed_lessons": 28,
        "total_time_spent": 14400,
        "average_score": 89.2,
        "current_streak": 5,
        "recent_activity": [
            {
                "lesson_title": "Subtraction Basics",
                "status": "COMPLETED",
                "updated_at": "2024-01-15T14:30:00Z",
                "subject": "Mathematics"
            }
        ],
        "subject_progress": {
            "Mathematics": {
                "completed_lessons": 15,
                "total_lessons": 20,
                "completion_percentage": 75.0,
                "average_score": 92.5
            }
        }
    }
}
```

## Error Handling

The API uses standard HTTP status codes and returns error responses in the following format:

```json
{
    "error": "Error message",
    "details": "Additional error details",
    "code": "ERROR_CODE"
}
```

### Common Error Codes

- `400` - Bad Request: Invalid input data
- `401` - Unauthorized: Invalid or missing authentication token
- `403` - Forbidden: Insufficient permissions
- `404` - Not Found: Resource not found
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Server error

### Example Error Response
```json
{
    "error": "Invalid Student ID or PIN",
    "code": "INVALID_CREDENTIALS"
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authentication endpoints**: 5 requests per minute per IP
- **General API endpoints**: 100 requests per hour per user
- **Search endpoints**: 20 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination using query parameters:

```http
GET /api/lessons/?page=2&page_size=20
```

**Response:**
```json
{
    "count": 150,
    "next": "http://api.learningcloud.com/api/lessons/?page=3",
    "previous": "http://api.learningcloud.com/api/lessons/?page=1",
    "results": [...]
}
```

## Filtering and Search

Most list endpoints support filtering and search:

```http
GET /api/lessons/?chapter=1&content_type=VIDEO&search=addition
```

## Sorting

Endpoints support sorting using the `ordering` parameter:

```http
GET /api/lessons/?ordering=-created_at,title
```

## File Uploads

For content with media files, use multipart/form-data:

```http
POST /api/lessons/123/media/
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: [binary data]
media_type: IMAGE
order_index: 1
```

## Webhooks

The API supports webhooks for real-time notifications:

```http
POST /api/webhooks/
Authorization: Bearer <token>
Content-Type: application/json

{
    "url": "https://your-app.com/webhook",
    "events": ["lesson.completed", "quiz.completed"],
    "secret": "your-webhook-secret"
}
```

## SDKs and Libraries

Official SDKs are available for:

- **Python**: `pip install learning-cloud-sdk`
- **JavaScript**: `npm install @learning-cloud/sdk`
- **React Native**: `npm install @learning-cloud/react-native`

## Support

For API support and questions:

- **Documentation**: https://docs.learningcloud.com
- **Support Email**: api-support@learningcloud.com
- **Status Page**: https://status.learningcloud.com



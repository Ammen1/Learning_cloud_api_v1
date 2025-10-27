# Learning Cloud API - Complete Swagger Documentation Guide

## Overview

Your Learning Cloud API is already configured with Swagger/OpenAPI documentation using `drf-spectacular`. All endpoints are automatically documented and accessible through an interactive Swagger UI.

## Access Swagger Documentation

Once your server is running, you can access the Swagger documentation at:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc UI**: http://localhost:8000/api/redoc/
- **OpenAPI Schema (JSON)**: http://localhost:8000/api/schema/

## Complete List of All API Endpoints

### 🔐 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/student-login/` | Student login (Student ID + PIN) |
| POST | `/api/auth/teacher-login/` | Teacher login (Email + Password) |
| POST | `/api/auth/parent-login/` | Parent login (Email + Password) |
| POST | `/api/auth/logout/` | Logout current session |
| POST | `/api/auth/token/` | OAuth2 token endpoint |
| GET | `/api/auth/authorize/` | OAuth2 authorization endpoint |
| POST | `/api/auth/revoke-token/` | Revoke OAuth2 token |

### 👤 Account Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile/` | Get user profile |
| PUT/PATCH | `/api/profile/` | Update user profile |
| POST | `/api/change-password/` | Change user password |
| POST | `/api/change-pin/` | Change student PIN |
| GET | `/api/sessions/` | Get active user sessions |
| POST | `/api/sessions/<session_id>/terminate/` | Terminate specific session |
| GET | `/api/stats/` | Get user statistics |
| GET | `/api/schools/` | List all schools (public) |

### 📚 Content Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subjects/` | List all subjects (filterable by grade) |
| GET | `/api/subjects/<id>/` | Get subject details |
| GET | `/api/chapters/` | List all chapters (filterable by subject) |
| GET | `/api/chapters/<id>/` | Get chapter details |
| GET | `/api/lessons/` Kak | List all lessons (filterable by chapter) |
| GET | `/api/lessons/<id>/` | Get lesson details |
| GET | `/api/search/` | Search content (query, grade_level, content_type) |
| POST | `/api/ratings/` | Rate a lesson |
| GET/POST | `/api/bookmarks/` | Get or create bookmarks |
| DELETE | `/api/bookmarks/<id>/` | Delete a bookmark |
| GET | `/api/offline/` | Get offline downloadable content |
| POST | `/api/lessons/<lesson_id>/request-access/` | Request premium access |
| POST | `/api/lessons/<lesson_id>/media/` | Upload media to a lesson |
| GET | `/api/stats/` | Get content statistics |

### 🎯 Quiz System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quizzes/` | List all quizzes (filterable) |
| GET | `/api/quizzes/<id>/` | Get quiz details |
| GET | `/api/quizzes/<quiz_id>/analytics/` | Get quiz analytics |
| GET | `/api/attempts/` | Get user's quiz attempts |
| POST | `/api/attempts/start/` | Start a new quiz attempt |
| GET | `/api/sessions/<session_key>/` | Get quiz session details |
| POST | `/api/sessions/<session_key>/submit-answer/` | Submit an answer |
| POST | `/api/sessions/<session_key>/complete/` | Complete a quiz |
| POST | `/api/sessions/<session_key>/abandon/` | Abandon quiz attempt |
| POST | `/api/feedback/` | Submit quiz feedback |
| GET | `/api/stats/` | Get quiz statistics |

### 📊 Progress Tracking

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/progress/` | List all progress records |
| GET | `/api/progress/<id>/` | Get specific progress record |
| POST | `/api/progress/lessons/<lesson_id>/update/` | Update lesson progress |
| GET | `/api/progress/streak/` | Get learning streak information |
| GET | `/api/progress/subjects/` | Get progress by subject |
| GET | `/api/progress/grade/` | Get progress by grade |
| GET | `/api/progress/milestones/` | Get achieved milestones |
| GET | `/api/progress/stats/` | Get progress statistics |
| GET | `/api/progress/weekly/` | Get weekly progress |
| GET | `/api/progress/monthly/` | Get monthly progress |
| GET | `/api/progress/parent-dashboard/<child_id>/` Than | Parent view of child's progress |

### 📈 Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/` | List analytics data |
| GET | `/api/analytics/reports/` | List analytics reports |
| GET | `/api/analytics/reports/<id>/` | Get specific report |
| GET | `/api/analytics/dashboard/` | Get analytics dashboard |
| POST | `/api/analytics/export/` | Export analytics data |

### 🔔 Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/` | List notifications (filterable by is_read) |
| GET | `/api/notifications/<id>/` | Get notification details |
| POST | `/api/notifications/<id>/mark-read/` | Mark notification as read |
| POST | `/api/notifications/mark-all-read/` | Mark all notifications as read |
| GET | `/api/notifications/unread-count/` | Get unread count |
| GET/POST | `/api/notifications/preferences/` | Get or update notification preferences |
| GET | `/api/notifications/templates/` | List notification templates (admin) |
| GET | `/api/notifications/templates/<id>/` | Get template details (admin) |
| GET | `/api/notifications/campaigns/` | List notification campaigns (admin) |
| GET | `/api/notifications/campaigns/<id>/` | Get campaign details (admin) |
| POST | `/api/notifications/campaigns/<id>/send/` | Send campaign (admin) |

### 🔗 Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/payment/` | Payment webhook handler |
| POST | `/webhooks/content/` | Content webhook handler |
| POST | `/webhooks/<webhook_type>/` | Generic webhook handler |
| POST | `/webhooks/register/` | Register a webhook |
| GET | `/webhooks/list/` | List registered webhooks |
| DELETE | `/webhooks/unregister/<webhook_id>/` | Unregister a webhook |

## How to Access Swagger UI

### Step 1: Start the Server

```bash
# For development
python manage.py runserver

# Or using Docker
docker-compose up
```

### Step 2: Open Swagger UI

Open your browser and navigate to:
```
http://localhost:8000/api/docs/
```

### Step 3: Authenticate

1. Click the "Authorize" button at the top right
2. Enter your OAuth2 token in the format: `Bearer <your-token>`
3. Click "Authorize"

### Step 4: Test Endpoints

1. Browse endpoints by category
2. Expand any endpoint to see details
3. Click "Try it out" to test the endpoint
4. Fill in the required parameters
5. Click "Execute" to send the request
6. View the response below

## Authentication

The API uses OAuth2 token-based authentication. To get a token:

### Student Login Flow:
```bash
curl -X POST http://localhost:8000/api/auth/student-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "12345",
    "pin": "1234"
  }'
```

### Using the Token:
Add the token to your requests:
```bash
curl -X GET http://localhost:8000/api/subjects/ \
  -H "Authorization: Bearer <your-token>"
```

## Features of Swagger UI

1. **Interactive Testing**: Test endpoints directly from the browser
2. **Schema Validation**: See request/response schemas
3. **Parameter Examples**: View example values for parameters
4. **Response Examples**: See example responses
5. **Try It Out**: Execute requests and see real responses
6. **Authentication**: Easy token-based authentication
7. **Export**: Export API definitions

## Filtering and Query Parameters

Most list endpoints support:

### Pagination
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Search
- `search`: Text search across relevant fields

### Filtering
- Specific filters per endpoint (e.g., `grade_level`, `subject`, `chapter`)
- See Swagger UI for available filters per endpoint

### Ordering
- `ordering`: Sort by field(s) (e.g., `-created_at`, `title`)

## Example Usage in Swagger UI

### Get Subjects for Grade 1:

1. Go to `/api/subjects/` endpoint
2. Click "Try it out"
3. Add query parameter: `grade_level` = `1`
4. Click "Execute"
5. View the response

### Update Lesson Progress:

1. Go to `/api/progress/lessons/{lesson_id}/update/` endpoint
2. Click "Try it out"
3. Enter the `lesson_id` in the path
4. Fill in the request body:
   ```json
   {
     "action": "complete",
     "time_spent": 900,
     "score": 95
   }
   ```
5. Click "Execute"

## Rate Limiting

The API implements rate limiting:

- **Authentication**: 5 requests/minute
- **General API**: 1000 requests/hour per user
- **Analytics**: 10 requests/minute

Headers show your current rate limit status:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remqwaining: 995
X-RateLimit-Reset: 1640995200
```

## Error Responses

All endpoints follow standard HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

## Additional Resources

- **API Documentation**: `API_DOCUMENTATION.md`
- **README**: `README.md`
- **Schema URL**: `http://localhost:8000/api/schema/`
- **ReDoc UI**: `http://localhost:8000/api/redoc/`

## Troubleshooting

### Swagger UI not loading?
- Ensure `DEBUG=True` in settings (or add Swagger paths to allowed hosts)
- Check that `drf-spectacular` is installed: `pip list | grep spectacular`
- Verify the server is running

### Authentication not working?
- Ensure you're using the correct token format: `Bearer <token>`
- Check that the token hasn't expired (default: 1 hour)
- Verify user permissions for protected endpoints

### Can't see all endpoints?
- Clear browser cache
- Check that all apps are in `INSTALLED_APPS`
- Verify URL patterns are included in main `urls.py`

## Next Steps

1. **Start the server**: `python manage.py runserver`
2. **Open Swagger**: http://localhost:8000/api/docs/
3. **Authenticate**: Get a token and authorize
4. **Explore**: Browse and test all endpoints
5. **Integrate**: Use the documented endpoints in your app

---

**Happy API Testing! 🚀**


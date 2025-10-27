# Learning Cloud API - Complete Endpoints Summary

## 🎯 Access Your Swagger Documentation

**Swagger UI**: http://localhost:8000/api/docs/  
**ReDoc UI**: http://localhost:8000/api/redoc/  
**OpenAPI Schema**: http://localhost:8000/api/schema/

## 📊 Statistics

- **Total Endpoints**: 76+ API endpoints
- **Authentication**: OAuth2 with Bearer tokens
- **Documentation**: Fully automated with drf-spectacular
- **Rate Limiting**: Configured for all endpoints

## 📋 Complete Endpoint List

### 🔐 1. Authentication & Accounts (8 endpoints)

```
POST   /api/auth/register/                          Register new user
POST   /api/auth/student-login/                     Student login (Student ID + PIN)
POST   /api/auth/teacher-login/                     Teacher login (Email + Password)
POST   /api/auth/parent-login/                      Parent login (Email + Password)
POST   /api/auth/logout/                            Logout current session
POST   /api/auth/token/                             Get OAuth2 token
GET    /api/auth/authorize/                         OAuth2 authorization
POST   /api/auth/revoke-token/                      Revoke token
```

### 👤 2. Account Management (8 endpoints)

```
GET    /api/profile/                                Get user profile
PUT    /api/profile/                                Update profile
PATCH  /api/profile/                                Partial update profile
POST   /api/change-password/                        Change password
POST   /api/change-pin/                             Change student PIN
GET    /api/sessions/                               List active sessions
POST   /api/sessions/{id}/terminate/                Terminate session
GET    /api/stats/                                  Get user statistics
GET    /api/schools/                                List schools (public)
```

### 📚 3. Content Management (15 endpoints)

```
GET    /api/subjects/                               List subjects (filter: grade_level)
GET    /api/subjects/{id}/                          Get subject details
GET    /api/chapters/                               List chapters (filter: subject)
GET    /api/chapters/{id}/                          Get chapter details
GET    /api/lessons/                                List lessons (filter: chapter)
GET    /api/lessons/{id}/                           Get lesson details
GET    /api/search/                                 Search content
POST   /api/ratings/                                Rate content
GET    /api/bookmarks/                              List bookmarks
POST   /api/bookmarks/                              Create bookmark
DELETE /api/bookmarks/{id}/                         Remove bookmark
GET    /api/offline/                                Get offline content
POST   /api/lessons/{id}/request-access/            Request premium access
POST   /api/lessons/{id}/media/                     Upload lesson media
GET    /api/stats/                                  Content statistics
```

### 🎯 4. Quiz System (11 endpoints)

```
GET    /api/quizzes/                                List quizzes (filter: subject, grade)
GET    /api/quizzes/{id}/                           Get quiz details
GET    /api/quizzes/{id}/analytics/                 Quiz analytics
GET    /api/attempts/                               List user attempts
POST   /api/attempts/start/                         Start quiz attempt
GET    /api/sessions/{session_key}/                 Get session details
POST   /api/sessions/{session_key}/submit-answer/   Submit answer
POST   /api/sessions/{session_key}/complete/        Complete quiz
POST   /api/sessions/{session_key}/abandon/         Abandon quiz
POST   /api/feedback/                               Submit feedback
GET    /api/stats/                                  Quiz statistics
```

### 📊 5. Progress Tracking (11 endpoints)

```
GET    /api/progress/                               List all progress (filter: status)
GET    /api/progress/{id}/                          Get progress details
POST   /api/progress/lessons/{id}/update/           Update lesson progress
GET    /api/progress/streak/                        Get learning streak
GET    /api/progress/subjects/                      Get subject progress
GET    /api/progress/grade/                         Get grade progress
GET    /api/progress/milestones/                    List milestones
GET    /api/progress/stats/                         Progress statistics
GET    /api/progress/weekly/                        Weekly progress
GET    /api/progress/monthly/                       Monthly progress
GET    /api/progress/parent-dashboard/{child_id}/   Parent dashboard
```

### 📈 6. Analytics (5 endpoints)

```
GET    /api/analytics/                              List analytics data
GET    /api/analytics/reports/                      List reports
GET    /api/analytics/reports/{id}/                 Get report details
GET    /api/analytics/dashboard/                    Analytics dashboard
POST   /api/analytics/export/                       Export analytics
```

### 🔔 7. Notifications (12 endpoints)

```
GET    /api/notifications/                          List notifications
GET    /api/notifications/{id}/                     Get notification
POST   /api/notifications/{id}/mark-read/           Mark as read
POST   /api/notifications/mark-all-read/            Mark all read
GET    /api/notifications/unread-count/             Unread count
GET    /api/notifications/preferences/              Get preferences
POST   /api/notifications/preferences/              Update preferences
GET    /api/notifications/templates/                List templates (admin)
GET    /api/notifications/templates/{id}/           Get template (admin)
GET    /api/notifications/campaigns/                List campaigns (admin)
GET    /api/notifications/campaigns/{id}/           Get campaign (admin)
POST   /api/notifications/campaigns/{id}/send/      Send campaign (admin)
```

### 🔗 8. Webhooks (6 endpoints)

```
POST   /webhooks/payment/                           Payment webhook
POST   /webhooks/content/                           Content webhook
POST   /webhooks/{type}/                            Generic webhook
POST   /webhooks/register/                          Register webhook
GET    /webhooks/list/                              List webhooks
DELETE /webhooks/unregister/{id}/                   Unregister webhook
```

## 🚀 Quick Start

### Step 1: Start Server
```bash
python manage.py runserver
```

### Step 2: Open Swagger
```
http://localhost:8000/api/docs/
```

### Step 3: Authenticate
1. Get a token from `/api/auth/student-login/`
2. Click "Authorize" in Swagger UI
3. Enter: `Bearer <your-token>`

### Step 4: Test Endpoints
- Expand any endpoint
- Click "Try it out"
- Fill parameters
- Click "Execute"

## 🔑 Common Query Parameters

### Pagination
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Filtering
- `grade_level`: Filter by grade (1-4)
- `subject`: Filter by subject ID
- `chapter`: Filter by chapter ID
- `status`: Filter by status (e.g., "completed", "in_progress")
- `is_read`: Filter notifications (true/false)

### Search
- `search`: Text search across relevant fields

### Ordering
- `ordering`: Sort by field(s) (e.g., "-created_at", "title")

## 📝 Example Requests

### Student Login
```bash
curl -X POST http://localhost:8000/api/auth/student-login/ \
  -H "Content-Type: application/json" \
  -d '{"student_id": "12345", "pin": "1234"}'
```

### Get Subjects for Grade 1
```bash
curl -X GET "http://localhost:8000/api/subjects/?grade_level=1" \
  -H "Authorization: Bearer <token>"
```

### Update Lesson Progress
```bash
curl -X POST http://localhost:8000/api/progress/lessons/123/update/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action": "complete", "time_spent": 900, "score": 95}'
```

## 🎨 Features in Swagger UI

✅ Interactive testing  
✅ Request/Response schemas  
✅ Authentication support  
✅ Try it out functionality  
✅ Example values  
✅ Parameter validation  
✅ Export API spec  

## ⚡ Rate Limits

- Authentication: 5 req/min
- General API: 1000 req/hour
- Analytics: 10 req/min

## 📚 Additional Resources

- **Complete Guide**: `SWAGGER_ENDPOINTS_GUIDE.md`
- **Quick Start**: `start_swagger.md`
- **API Docs**: `API_DOCUMENTATION.md`
- **README**: `README.md`

---

**Total: 76+ Endpoints | All Documented in Swagger** 🎉


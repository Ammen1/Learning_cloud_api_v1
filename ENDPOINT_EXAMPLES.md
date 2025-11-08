# 🚀 API Endpoint Examples - Ready to Use!

## Quick Access

**Base URL**: `http://localhost:8000/api/`

**Documentation**:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- API Info: http://localhost:8000/api/

---

## 🔐 Authentication Endpoints

### 1. Student Login
```bash
POST /api/auth/student-login/
Content-Type: application/json

{
  "student_id": "12345",
  "pin": "1234"
}
```

**Response**:
```json
{
  "token": "your_access_token_here",
  "refresh_token": "your_refresh_token_here",
  "user": {
    "id": "user_id",
    "username": "student123",
    "role": "STUDENT"
  }
}
```

### 2. Teacher Login
```bash
POST /api/auth/teacher-login/
Content-Type: application/json

{
  "email": "teacher@school.com",
  "password": "password123"
}
```

### 3. Parent Login
```bash
POST /api/auth/parent-login/
Content-Type: application/json

{
  "email": "parent@email.com",
  "password": "password123"
}
```

### 4. Register New User
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "STUDENT"
}
```

### 5. Get OAuth2 Token
```bash
POST /api/auth/token/
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=student_id&password=pin&client_id=your_client_id&client_secret=your_client_secret
```

---

## 👤 Account Management

### 6. Get User Profile
```bash
GET /api/profile/
Authorization: Bearer your_access_token_here
```

### 7. Update Profile
```bash
PATCH /api/profile/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "first_name": "Updated Name",
  "last_name": "Updated Lastname",
  "email": "newemail@example.com"
}
```

### 8. List All Schools (Public - No Auth Required)
```bash
GET /api/schools/
```

**Response**:
```json
{
  "count": 10,
  "results": [
    {
      "id": "school_id",
      "name": "School Name",
      "city": "Addis Ababa",
      "country": "Ethiopia"
    }
  ]
}
```

### 9. Get User Statistics
```bash
GET /api/stats/
Authorization: Bearer your_access_token_here
```

### 10. Change Password
```bash
POST /api/change-password/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "old_password": "oldpass123",
  "new_password": "newpass123"
}
```

### 11. Change Student PIN
```bash
POST /api/change-pin/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "old_pin": "1234",
  "new_pin": "5678"
}
```

### 12. List Active Sessions
```bash
GET /api/sessions/
Authorization: Bearer your_access_token_here
```

---

## 📚 Content Management

### 13. List All Subjects
```bash
GET /api/subjects/
```

**With filters**:
```bash
GET /api/subjects/?grade_level=1
GET /api/subjects/?search=math
```

### 14. Get Subject Details
```bash
GET /api/subjects/1/
```

### 15. List Chapters
```bash
GET /api/chapters/
GET /api/chapters/?subject_id=1
```

### 16. Get Chapter Details
```bash
GET /api/chapters/1/
```

### 17. List Lessons
```bash
GET /api/lessons/
GET /api/lessons/?chapter_id=1
GET /api/lessons/?grade_level=1
```

### 18. Get Lesson Details
```bash
GET /api/lessons/1/
Authorization: Bearer your_access_token_here
```

### 19. Search Content
```bash
GET /api/search/?q=mathematics&grade_level=1
```

**Response**:
```json
{
  "subjects": [...],
  "chapters": [...],
  "lessons": [...]
}
```

### 20. Rate a Lesson
```bash
POST /api/ratings/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "lesson_id": 1,
  "rating": 5,
  "comment": "Great lesson!"
}
```

### 21. Get Bookmarks
```bash
GET /api/bookmarks/
Authorization: Bearer your_access_token_here
```

### 22. Create Bookmark
```bash
POST /api/bookmarks/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "lesson_id": 1
}
```

### 23. Remove Bookmark
```bash
DELETE /api/bookmarks/1/
Authorization: Bearer your_access_token_here
```

### 24. Get Content Statistics
```bash
GET /api/content/stats/
```

---

## 🎯 Quiz System

### 25. List All Quizzes
```bash
GET /api/quizzes/
GET /api/quizzes/?subject_id=1
GET /api/quizzes/?grade_level=1
```

### 26. Get Quiz Details
```bash
GET /api/quizzes/1/
Authorization: Bearer your_access_token_here
```

### 27. Get Quiz Analytics
```bash
GET /api/quizzes/1/analytics/
Authorization: Bearer your_access_token_here
```

### 28. List Quiz Attempts
```bash
GET /api/attempts/
Authorization: Bearer your_access_token_here
```

### 29. Start Quiz Attempt
```bash
POST /api/attempts/start/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "quiz_id": 1
}
```

**Response**:
```json
{
  "session_key": "session_key_123",
  "quiz": {...},
  "started_at": "2024-01-01T10:00:00Z"
}
```

### 30. Get Quiz Session
```bash
GET /api/sessions/session_key_123/
Authorization: Bearer your_access_token_here
```

### 31. Submit Answer
```bash
POST /api/sessions/session_key_123/submit-answer/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "question_id": 1,
  "answer": "Option A"
}
```

### 32. Complete Quiz
```bash
POST /api/sessions/session_key_123/complete/
Authorization: Bearer your_access_token_here
```

### 33. Abandon Quiz
```bash
POST /api/sessions/session_key_123/abandon/
Authorization: Bearer your_access_token_here
```

### 34. Submit Quiz Feedback
```bash
POST /api/feedback/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "quiz_id": 1,
  "rating": 4,
  "comment": "Good quiz!"
}
```

---

## 📊 Progress Tracking

### 35. List Progress Records
```bash
GET /api/progress/
Authorization: Bearer your_access_token_here
```

### 36. Get Progress Detail
```bash
GET /api/progress/1/
Authorization: Bearer your_access_token_here
```

### 37. Update Lesson Progress
```bash
POST /api/progress/lessons/1/update/
Authorization: Bearer your_access_token_here
Content-Type: application/json

{
  "status": "COMPLETED",
  "time_spent": 300,
  "score": 95.5
}
```

### 38. Get Learning Streak
```bash
GET /api/progress/streak/
Authorization: Bearer your_access_token_here
```

### 39. Get Progress by Subject
```bash
GET /api/progress/subjects/
Authorization: Bearer your_access_token_here
```

### 40. Get Grade Progress
```bash
GET /api/progress/grade/
Authorization: Bearer your_access_token_here
```

### 41. Get Progress Statistics
```bash
GET /api/progress/stats/
Authorization: Bearer your_access_token_here
```

### 42. Get Weekly Progress
```bash
GET /api/progress/weekly/
Authorization: Bearer your_access_token_here
```

---

## 📈 Analytics

### 43. Get Analytics Data
```bash
GET /api/analytics/
Authorization: Bearer your_access_token_here
```

### 44. Get Analytics Reports
```bash
GET /api/analytics/reports/
Authorization: Bearer your_access_token_here
```

### 45. Get Analytics Dashboard
```bash
GET /api/analytics/dashboard/
Authorization: Bearer your_access_token_here
```

### 46. Export Analytics
```bash
GET /api/analytics/export/?format=csv
Authorization: Bearer your_access_token_here
```

---

## 🔔 Notifications

### 47. List Notifications
```bash
GET /api/notifications/
Authorization: Bearer your_access_token_here
```

### 48. Get Notification Detail
```bash
GET /api/notifications/1/
Authorization: Bearer your_access_token_here
```

### 49. Mark Notification as Read
```bash
POST /api/notifications/1/mark-read/
Authorization: Bearer your_access_token_here
```

### 50. Mark All Notifications as Read
```bash
POST /api/notifications/mark-all-read/
Authorization: Bearer your_access_token_here
```

### 51. Get Unread Count
```bash
GET /api/notifications/unread-count/
Authorization: Bearer your_access_token_here
```

### 52. Get Notification Preferences
```bash
GET /api/notifications/preferences/
Authorization: Bearer your_access_token_here
```

---

## 🧪 Testing with cURL

### Example: Get All Subjects
```bash
curl -X GET http://localhost:8000/api/subjects/
```

### Example: Login and Get Profile
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/student-login/ \
  -H "Content-Type: application/json" \
  -d '{"student_id": "12345", "pin": "1234"}'

# 2. Use the token to get profile
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Example: Get Quizzes
```bash
curl -X GET http://localhost:8000/api/quizzes/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🧪 Testing with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 1. Login
response = requests.post(
    f"{BASE_URL}/auth/student-login/",
    json={"student_id": "12345", "pin": "1234"}
)
token = response.json()["token"]

# 2. Get Profile
headers = {"Authorization": f"Bearer {token}"}
profile = requests.get(f"{BASE_URL}/profile/", headers=headers)
print(profile.json())

# 3. Get Subjects
subjects = requests.get(f"{BASE_URL}/subjects/")
print(subjects.json())

# 4. Get Quizzes
quizzes = requests.get(f"{BASE_URL}/quizzes/", headers=headers)
print(quizzes.json())

# 5. Get Progress
progress = requests.get(f"{BASE_URL}/progress/", headers=headers)
print(progress.json())
```

---

## 🧪 Testing with JavaScript (Fetch API)

```javascript
const BASE_URL = "http://localhost:8000/api";

// 1. Login
async function login() {
  const response = await fetch(`${BASE_URL}/auth/student-login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      student_id: '12345',
      pin: '1234'
    })
  });
  const data = await response.json();
  return data.token;
}

// 2. Get Profile
async function getProfile(token) {
  const response = await fetch(`${BASE_URL}/profile/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
}

// 3. Get Subjects
async function getSubjects() {
  const response = await fetch(`${BASE_URL}/subjects/`);
  return await response.json();
}

// Usage
const token = await login();
const profile = await getProfile(token);
const subjects = await getSubjects();
console.log({ profile, subjects });
```

---

## 📝 Important Notes

1. **Authentication**: Most endpoints require a Bearer token in the Authorization header
2. **Public Endpoints**: Some endpoints like `/api/schools/` and `/api/subjects/` don't require authentication
3. **Pagination**: List endpoints support pagination with `?page=1&page_size=10`
4. **Filtering**: Many endpoints support filtering, e.g., `?grade_level=1&subject_id=1`
5. **Search**: Use the search endpoint for full-text search: `/api/search/?q=keyword`

---

## 🔗 Quick Links

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **API Info**: http://localhost:8000/api/
- **Health Check**: http://localhost:8000/health/

---

**Happy Coding! 🚀**


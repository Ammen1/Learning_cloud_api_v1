# API Endpoints Quick Reference Guide

## 🔍 Important: All endpoints require `/api/` prefix!

If you're getting 404 errors, make sure you're using the full path with `/api/` prefix.

## ✅ Correct Endpoint URLs

### Authentication
- ✅ `POST /api/auth/register/`
- ✅ `POST /api/auth/student-login/`
- ✅ `POST /api/auth/teacher-login/`
- ✅ `POST /api/auth/parent-login/`
- ✅ `POST /api/auth/logout/`

### Account Management
- ✅ `GET /api/profile/`
- ✅ `GET /api/schools/` (List schools)
- ✅ `GET /api/stats/` (User statistics)
- ✅ `GET /api/sessions/`

### Content Management
- ✅ `GET /api/subjects/` (List subjects)
- ✅ `GET /api/subjects/<id>/` (Subject details)
- ✅ `GET /api/chapters/` (List chapters)
- ✅ `GET /api/lessons/` (List lessons)
- ✅ `GET /api/search/` (Search content)
- ✅ `GET /api/content/stats/` (Content statistics)

### Quizzes
- ✅ `GET /api/quizzes/` (List quizzes)
- ✅ `GET /api/quizzes/<id>/` (Quiz details)
- ✅ `GET /api/attempts/` (Quiz attempts)

### Progress
- ✅ `GET /api/progress/` (Progress records)
- ✅ `GET /api/progress/streak/` (Learning streak)

### Analytics
- ✅ `GET /api/analytics/` (Analytics data)
- ✅ `GET /api/analytics/reports/` (Reports)

## ❌ Common Mistakes (Will return 404)

- ❌ `GET /schools/` → Should be `GET /api/schools/`
- ❌ `GET /stats/` → Should be `GET /api/stats/`
- ❌ `GET /subjects/` → Should be `GET /api/subjects/`
- ❌ `GET /` → Redirects to `/api/docs/`

## 📚 Access API Documentation

1. **Swagger UI**: http://localhost:8000/api/docs/
2. **ReDoc**: http://localhost:8000/api/redoc/
3. **API Info**: http://localhost:8000/api/ (Shows all available endpoints)
4. **Schema**: http://localhost:8000/api/schema/

## 🧪 Testing Endpoints

### Using curl:
```bash
# List schools
curl http://localhost:8000/api/schools/

# List subjects
curl http://localhost:8000/api/subjects/

# Get API info
curl http://localhost:8000/api/
```

### Using Swagger UI:
1. Go to http://localhost:8000/api/docs/
2. Find the endpoint you want to test
3. Click "Try it out"
4. Click "Execute"
5. Check the response

## 🔑 Authentication

Most endpoints require authentication. Get a token first:

```bash
# Student login
curl -X POST http://localhost:8000/api/auth/student-login/ \
  -H "Content-Type: application/json" \
  -d '{"student_id": "12345", "pin": "1234"}'
```

Then use the token:
```bash
curl http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 💡 Tips

1. **Always use `/api/` prefix** - All endpoints are under `/api/`
2. **Check Swagger docs** - Most accurate source of endpoint URLs
3. **Use `/api/` endpoint** - Visit http://localhost:8000/api/ to see all available endpoints
4. **Check server logs** - If you get 404, check what URL was requested


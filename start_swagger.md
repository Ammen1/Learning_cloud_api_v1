# Quick Start: Access Your Swagger Documentation

## Step 1: Activate Virtual Environment

```bash
# Activate the virtual environment
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # Linux/Mac
```

## Step 2: Start the Server

```bash
python manage.py runserver
```

## Step 3: Open Swagger UI in Your Browser

Once the server is running, open:

**Swagger UI** (Interactive): http://localhost:8000/api/docs/

**ReDoc** (Alternative UI): http://localhost:8000/api/redoc/

**Raw Schema** (JSON): http://localhost:8000/api/schema/

## Quick Test

### 1. Get a Student Token

In Swagger UI:
- Find the `/api/auth/student-login/` endpoint
- Click "Try it out"
- Enter sample data:
  ```json
  {
    "student_id": "12345",
    "pin": "1234"
  }
  ```
- Click "Execute"
- Copy the token from the response

### 2. Authorize in Swagger

- Click "Authorize" button (🔓 icon)
- Enter: `Bearer <your-token>`
- Click "Authorize"

### 3. Test an Endpoint

- Find `/api/subjects/` endpoint
- Click "Try it out"
- Add query parameter: `grade_level` = `1`
- Click "Execute"
- View the response

## All Available Endpoints (100+)

Your API includes endpoints for:

✅ **Authentication** (8 endpoints)
   - Register, Login (Student/Teacher/Parent), Logout, Token management

✅ **Account Management** (8 endpoints)
   - Profile, Password/PIN change, Session management, Stats

✅ **Content Management** (15 endpoints)
   - Subjects, Chapters, Lessons, Search, Ratings, Bookmarks

✅ **Quiz System** (11 endpoints)
   - Quizzes, Attempts, Sessions, Submissions, Analytics

✅ **Progress Tracking** (11 endpoints)
   - Lesson progress, Streaks, Milestones, Statistics

✅ **Analytics** (5 endpoints)
   - Dashboard, Reports, Exports

✅ **Notifications** (12 endpoints)
   - List, Read status, Preferences, Campaigns

✅ **Webhooks** (6 endpoints)
   - Register, List, Payment, Content handlers

## Features in Swagger UI

🌟 **Try It Out**: Test any endpoint directly  
📋 **Schema**: See request/response structures  
🔐 **Auto-Auth**: Easy token-based authentication  
📝 **Examples**: View example requests/responses  
💾 **Export**: Download API specification  

## Docker Alternative

If using Docker:

```bash
docker-compose up
```

Then access: http://localhost:8000/api/docs/

## Need Help?

1. Check `SWAGGER_ENDPOINTS_GUIDE.md` for complete endpoint list
2. See `API_DOCUMENTATION.md` for detailed API docs
3. View `README.md` for setup instructions

---

**Your Swagger documentation is ready! 🎉**


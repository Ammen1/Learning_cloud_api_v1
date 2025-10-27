# Fix 431 Error - "Line too long"

## Problem
The 431 error occurs when HTTP headers exceed 65,536 bytes. This is usually caused by large cookies or request data.

## Solution Applied

I've made the following changes to fix this issue:

1. ✅ Reduced Swagger description to minimal text
2. ✅ Added session configuration to reduce cookie size
3. ✅ Configured request size limits
4. ✅ Updated SPECTACULAR_SETTINGS

## Steps to Apply Fix

### Step 1: Stop the Current Server
Press `CTRL+C` or `CTRL+BREAK` in your terminal to stop the Django server.

### Step 2: Clear Browser Cookies (Important!)
**Chrome/Edge:**
- Press `F12` to open DevTools
- Click the "Application" tab
- Click "Cookies" → `http://localhost:8000`
- Delete all cookies

**Firefox:**
- Press `F12` to open DevTools
- Click the "Storage" tab
- Expand "Cookies" → `http://localhost:8000`
- Delete all cookies

**Or simply use:**
- Press `CTRL+SHIFT+DELETE`
- Select "Cookies and other site data"
- Time range: "Last hour"
- Click "Clear data"

### Step 3: Restart the Server
```bash
python manage.py runserver
```

### Step 4: Access Swagger UI
Open your browser (incognito/private mode recommended) and go to:
```
http://localhost:8000/api/docs/
```

## Alternative Solutions

### If the error persists, try these:

### Option 1: Use ReDoc Instead
```
http://localhost:8000/api/redoc/
```
ReDoc often handles large schemas better than Swagger UI.

### Option 2: Access Schema Directly
```
http://localhost:8000/api/schema/
```
View the raw OpenAPI schema JSON.

### Option 3: Use Incognito Mode
Open browser in incognito/private mode to avoid cookie issues:
```
http://localhost:8000/api/docs/
```

### Option 4: Increase Server Buffer Size
If running with Gunicorn or production server, add to your configuration:
```python
# In gunicorn config or command
--limit-request-line 0  # Unlimited
--limit-request-fields 32768
--limit-request-field_size 32768
```

## What Caused the Error?

The 431 error typically happens when:
1. **Large Cookies**: Session or authentication cookies exceed size limits
2. **Large Headers**: Request headers (including cookies) exceed 65KB
3. **Schema Size**: Very large OpenAPI schema being loaded

## Changes Made

```python
# Reduced description size in SPECTACULAR_SETTINGS
'DESCRIPTION': 'Learning Management System for students. OAuth2 Bearer token auth.',

# Added session optimization
SESSION_SAVE_EVERY_REQUEST = False

# Added request size limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440
```

## Testing

After restarting, test:
1. ✅ `http://localhost:8000/api/docs/` - Swagger UI
2. ✅ `http://localhost:8000/api/redoc/` - ReDoc UI
3. ✅ `http://localhost:8000/api/schema/` - Raw schema

If all work, you're ready to use your API documentation! 🎉

---

**Note**: If the error continues after clearing cookies and restarting, try using ReDoc which handles large schemas better: `http://localhost:8000/api/redoc/`


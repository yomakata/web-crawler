# URGENT: Backend Restart Required

## Problem
The backend is not running or needs to be restarted to apply the current_url changes.

## Quick Fix - Restart Backend

### Option 1: Using CMD (Recommended for Windows)

```cmd
REM 1. Navigate to backend directory
cd c:\Projects\web-crawler\backend

REM 2. Activate virtual environment
call venv\Scripts\activate.bat

REM 3. Start Flask API server
set FLASK_APP=api/app.py
set FLASK_ENV=development
python -m flask run --port=3000 --host=0.0.0.0
```

### Option 2: Using Docker (if you have Docker)

```cmd
cd c:\Projects\web-crawler
docker-compose down
docker-compose up --build
```

### Option 3: Using the setup script

```cmd
cd c:\Projects\web-crawler\backend
call venv\Scripts\activate.bat
set FLASK_APP=api/app.py
flask run --port=3000
```

## After Restarting Backend

1. **Hard refresh the frontend in your browser**:
   - Press `Ctrl + Shift + R` (Windows/Linux)
   - Or `Cmd + Shift + R` (Mac)
   - This clears the cached JavaScript

2. **Clear browser console** (F12):
   - Click the clear icon in console
   - This helps see fresh logs

3. **Try a new crawl**:
   - Upload a CSV or enter a single URL
   - Start the crawl
   - Watch for the "Processing: [URL]" text

## What to Check

### In Backend Terminal:
You should see:
```
* Running on http://127.0.0.1:3000
* Running on http://[::1]:3000
```

### In Browser Console (F12):
You should see debug logs like:
```
Job status received: {status: "running", current_url: "https://..."}
Current URL set to: https://...
ProgressBar props: {currentUrl: "https://...", ...}
```

### In Browser Network Tab:
1. Open DevTools > Network
2. Filter by "status"
3. Click on a status request
4. Check Response - should have `"current_url": "https://..."`

## If Backend Won't Start

Check the error message in the terminal. Common issues:

1. **Port 3000 already in use**:
   ```cmd
   netstat -ano | findstr :3000
   taskkill //F //PID <pid_number>
   ```

2. **Missing dependencies**:
   ```cmd
   cd backend
   call venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

3. **Python version issues**:
   ```cmd
   python --version
   REM Should be Python 3.7+
   ```

## Manual Test After Backend Starts

Test if the API returns current_url:

```bash
# Start a crawl first, then run:
curl http://localhost:3000/api/job/<job-id>/status

# Should return JSON with:
# "current_url": "https://example.com/..."
```

## Summary of Changes Made

✅ Backend:
- Added `current_url` field to Job model
- Added `set_current_url()` method
- Updated tasks.py to set URL during processing
- Updated routes.py to return current_url in API

✅ Frontend:
- Added currentUrl state
- Updated polling to capture current_url
- Updated ProgressBar to display URL
- Added debug console.log statements

🔴 **NEXT STEP**: Restart the backend using one of the options above!

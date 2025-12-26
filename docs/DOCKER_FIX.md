# Docker Setup Fix

## Issue
The original `docker-compose.yml` included a frontend service that doesn't exist yet, causing this error:
```
unable to prepare context: path "C:\\Projects\\web-crawler\\frontend" not found
```

## Solution Applied
The `docker-compose.yml` has been updated to comment out the frontend service. The backend and Redis services will run without issues.

## Current Docker Services

### Active Services
1. **backend** - Python/Flask API (Port 5000)
2. **redis** - Redis cache (Port 6379)

### Commented Out (for future)
- **frontend** - React application (will be uncommented when implemented)

## How to Use Docker Now

### Start Services
```bash
docker-compose up -d
```

This will start:
- Backend API at http://localhost:5000
- Redis at localhost:6379

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Redis only
docker-compose logs -f redis
```

### Stop Services
```bash
docker-compose down
```

### Rebuild (if you make code changes)
```bash
docker-compose up -d --build
```

## Test the Backend API

Once Docker is running, test the API:

```bash
# Health check
curl http://localhost:5000/health

# API info
curl http://localhost:5000/

# Crawl a URL
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "formats": ["txt"]}'
```

## Alternative: Run Backend Without Docker

If you prefer not to use Docker:

```bash
# Navigate to backend
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run API
python -m flask --app api.app run

# Or use CLI directly
python main.py --url https://example.com
```

## When Frontend is Implemented

Once the React frontend is created, you can uncomment the frontend service in `docker-compose.yml`:

```yaml
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: webcrawler-frontend
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:${BACKEND_PORT:-5000}/api
    depends_on:
      - backend
    networks:
      - webcrawler-network
    restart: unless-stopped
```

Then rebuild:
```bash
docker-compose up -d --build
```

## Recommended Workflow

For now, the **easiest way** to use the web crawler is:

### Option 1: CLI (No Docker Needed)
```bash
cd backend
python main.py --url https://example.com
```

### Option 2: Docker API
```bash
docker-compose up -d
# Wait for services to start
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "formats": ["txt", "md"]}'
```

### Option 3: Local API (No Docker)
```bash
cd backend
python -m flask --app api.app run
# In another terminal, use curl or test via browser
```

## Summary

✅ **Fixed**: docker-compose.yml now works with backend only  
✅ **Active**: Backend API + Redis services  
⏳ **Future**: Frontend will be added later  

**You can now use Docker or run the backend directly!**

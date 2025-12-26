# Web Crawler - Getting Started Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend - to be implemented)
- **Docker & Docker Compose** (optional, for containerized deployment)
- **Git** (for version control)

## 🚀 Quick Start (3 Methods)

### Method 1: Using Setup Scripts (Recommended for Development)

#### Windows
```bash
setup.bat
```

#### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

### Method 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Verify setup:**
```bash
python test_setup.py
```

### Method 3: Using Docker

1. **Copy environment file:**
```bash
cp .env.example .env
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Check status:**
```bash
docker-compose ps
```

## 🎯 Usage

### Command Line Interface (CLI)

The CLI is the quickest way to start crawling websites.

#### Basic Examples

**1. Crawl a webpage (content mode - default):**
```bash
python main.py --url https://example.com
```

**2. Get multiple formats:**
```bash
python main.py --url https://example.com --format txt,md,html
```

**3. Extract specific section:**
```bash
python main.py --url https://example.com --scope-class article-body
```

**4. Download images:**
```bash
python main.py --url https://example.com --download-images
```

**5. Extract links (link mode):**
```bash
python main.py --url https://example.com --mode link --format json
```

**6. Process CSV file (bulk mode):**
```bash
python main.py --csv urls.csv
```

#### Interactive Mode

Simply run without arguments:
```bash
python main.py
```

The interactive mode will guide you through the options.

#### All CLI Options

```bash
python main.py --help
```

**Available options:**
- `--url URL` - URL to crawl
- `--csv FILE` - CSV file for bulk processing
- `--mode {content,link}` - Crawling mode (default: content)
- `--format FORMATS` - Output formats (comma-separated)
- `--output DIR` - Output directory (default: ./output)
- `--scope-class CLASS` - CSS class for scoped extraction
- `--scope-id ID` - Element ID for scoped extraction
- `--download-images` - Download images (content mode)
- `--link-type {all,internal,external}` - Link type filter (link mode)
- `--exclude-anchors` - Exclude anchor fragments (link mode)
- `--timeout SECONDS` - Request timeout (default: 30)

### REST API

#### Starting the API Server

**Development mode:**
```bash
cd backend
python -m flask --app api.app run
```

**With custom port:**
```bash
python -m flask --app api.app run --port 8000
```

**Production mode (Docker):**
```bash
docker-compose up -d
```

The API will be available at:
- Local: http://localhost:5000
- Docker: http://localhost:5000

#### API Endpoints

**1. Health Check**
```bash
curl http://localhost:5000/health
```

**2. Crawl Single URL (Content Mode)**
```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "content",
    "formats": ["txt", "md"],
    "scope_class": "main-content",
    "download_images": true
  }'
```

**3. Crawl Single URL (Link Mode)**
```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "link",
    "formats": ["json"],
    "link_type": "internal"
  }'
```

**4. Bulk Crawl (CSV Upload)**
```bash
curl -X POST http://localhost:5000/api/crawl/bulk \
  -F "file=@urls.csv"
```

**5. Check Job Status**
```bash
curl http://localhost:5000/api/job/{job_id}/status
```

**6. Get Job Results**
```bash
curl http://localhost:5000/api/job/{job_id}/results
```

**7. Download File**
```bash
curl -O http://localhost:5000/api/download/{job_id}/{filename}
```

**8. Get History**
```bash
curl http://localhost:5000/api/history
```

**9. Delete Job**
```bash
curl -X DELETE http://localhost:5000/api/job/{job_id}
```

## 📁 CSV Format for Bulk Crawling

Create a CSV file with the following columns:

```csv
url,mode,scope_class,format,download_images,link_type
https://example.com,content,main-content,txt md,false,
https://example.com/about,content,,txt,false,
https://example.com,link,,,false,internal
```

**Column descriptions:**
- `url` (required) - URL to crawl
- `mode` (optional) - "content" or "link" (default: content)
- `scope_class` (optional) - CSS class for scoped extraction
- `scope_id` (optional) - Element ID for scoped extraction
- `format` (optional) - Space or comma-separated formats (default: txt)
- `download_images` (optional) - true/false (default: false)
- `link_type` (optional) - "all", "internal", "external" (default: all)

**Example:**
```bash
# Save the example
cp urls.csv.example urls.csv

# Edit urls.csv with your URLs

# Run bulk crawl
python main.py --csv urls.csv
```

## 🧪 Testing

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test File
```bash
pytest tests/test_parser.py
```

### Run with Coverage
```bash
pytest --cov=crawler --cov=api --cov-report=html
```

### Quick Verification
```bash
python test_setup.py
```

## 📦 Output Structure

All crawled content is saved in organized folders:

### Content Mode Output
```
output/
└── example_com_blog_20231215_1430/
    ├── example_com_blog_20231215_1430.txt
    ├── example_com_blog_20231215_1430.md
    ├── example_com_blog_20231215_1430.html
    ├── extraction_details.json
    ├── extraction_summary.txt
    ├── image_001.jpg
    └── image_002.png
```

### Link Mode Output
```
output/
└── example_com_20231215_1430/
    ├── example_com_20231215_1430.txt
    ├── example_com_20231215_1430.json
    ├── extraction_details.json
    └── extraction_summary.txt
```

## 🔧 Configuration

### Environment Variables

Edit the `.env` file to customize settings:

```bash
# Backend API
BACKEND_PORT=5000
OUTPUT_DIRECTORY=./output

# Crawler Settings
DEFAULT_TIMEOUT=30
MAX_RETRIES=3
MAX_IMAGE_SIZE_MB=10

# File Upload Limits
MAX_CSV_SIZE_MB=10
MAX_URLS_PER_CSV=1000

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Custom User Agent

Set your custom user agent in `.env`:
```bash
USER_AGENT=MyBot/1.0 (Contact: email@example.com)
```

## 🐛 Troubleshooting

### Issue: Module not found errors

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Permission denied on output directory

**Solution:**
```bash
mkdir output
chmod 755 output
```

### Issue: Port already in use

**Solution:**
```bash
# Use different port
python -m flask --app api.app run --port 8000

# Or kill existing process
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Issue: Docker container fails to start

**Solution:**
```bash
# Check logs
docker-compose logs backend

# Rebuild containers
docker-compose down
docker-compose up --build
```

## 📚 Common Use Cases

### 1. Extract Blog Articles

```bash
python main.py \
  --url https://blog.example.com/article \
  --scope-class article-content \
  --format md html \
  --download-images
```

### 2. Get All Links from a Website

```bash
python main.py \
  --url https://example.com \
  --mode link \
  --format json \
  --link-type all
```

### 3. Extract Multiple Articles

Create `articles.csv`:
```csv
url,mode,scope_class,format,download_images
https://blog.example.com/post1,content,article,md,true
https://blog.example.com/post2,content,article,md,true
https://blog.example.com/post3,content,article,md,true
```

Run:
```bash
python main.py --csv articles.csv
```

### 4. Build a Sitemap

```bash
python main.py \
  --url https://example.com \
  --mode link \
  --link-type internal \
  --format json
```

## 🔐 Best Practices

1. **Respect robots.txt** - Check the website's robots.txt before crawling
2. **Rate Limiting** - Don't overwhelm servers with too many requests
3. **User Agent** - Always identify your crawler
4. **Legal Compliance** - Ensure you have permission to crawl
5. **Error Handling** - Use try-except in custom scripts
6. **Storage** - Monitor disk space for image downloads
7. **Timeouts** - Adjust timeout for slow websites

## 🆘 Getting Help

### View Documentation
- Main README: `README.md`
- Development Spec: `dev-spec.md`
- API Docs: http://localhost:5000/api/docs

### Check Logs
```bash
# CLI logs appear in terminal

# API logs
docker-compose logs -f backend

# Or if running locally
tail -f logs/crawler.log
```

### Run Diagnostics
```bash
python test_setup.py
```

## 📈 Performance Tips

1. **Bulk Processing** - Use CSV for multiple URLs instead of individual calls
2. **Format Selection** - Only request formats you need
3. **Image Downloads** - Skip images if not needed (much faster)
4. **Scoping** - Use scope_class/scope_id to extract only what you need
5. **Timeout** - Adjust timeout based on target website speed

## 🔄 Next Steps

1. ✅ Backend implementation complete
2. 🚧 Frontend (React + Tailwind) - Coming next
3. 🚧 Advanced features (Celery, Redis, database)

Stay tuned for the frontend implementation!

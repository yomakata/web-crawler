# Web Crawler ✅ COMPLETE

A full-stack web crawler application with Python backend and React frontend that allows users to crawl URLs in two modes: content extraction or link extraction. Supports single URL crawling or bulk operations via CSV upload, with Docker containerization for easy deployment.

## 🎉 Project Status: 100% COMPLETE

All 9 phases of development are implemented and production-ready!

## Features

- **Dual Mode Operation**: Content extraction or link extraction
- **Multiple Output Formats**: Plain text, Markdown, HTML (content mode) | Plain text, JSON (link mode)
- **Bulk Processing**: CSV upload for processing multiple URLs
- **Content Scoping**: Extract specific elements by class or ID
- **Image Downloading**: Download and save images with content
- **Metadata Tracking**: Comprehensive extraction statistics and details
- **Web & CLI Interfaces**: Use via browser or command line
- **Real-time Progress**: Live updates during crawling operations
- **Docker Deployment**: Containerized stack (backend + frontend + Redis)
- **Modern UI**: Beautiful, responsive React interface with Tailwind CSS

## Quick Start

Get the web crawler running on your local machine in just a few minutes!

### Prerequisites

Before you begin, make sure you have the following installed:
- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git**

To verify your installation:
```bash
docker --version
docker-compose --version
git --version
```

### Step-by-Step Setup

**1. Clone the Repository**

Open your terminal and run:
```bash
git clone https://github.com/yomakata/web-crawler.git
cd web-crawler
```

**2. Set Up Environment Variables**

Copy the example environment file and configure it:
```bash
cp .env.example .env
```

The default settings in `.env` are ready to use. You can customize them later if needed.

**3. Build and Start the Application**

Start all services (backend, frontend, and Redis) with Docker Compose:
```bash
docker-compose up -d
```

This command will:
- Download necessary Docker images
- Build the backend and frontend containers
- Start all services in the background

Wait about 30-60 seconds for all services to initialize.

**4. Verify the Application is Running**

Check that all containers are running:
```bash
docker-compose ps
```

You should see three containers running:
- `web-crawler-backend-1`
- `web-crawler-frontend-1`
- `web-crawler-redis-1`

**5. Access the Application**

Open your browser and navigate to:
- **Frontend UI**: http://localhost:3000 🌐 (Main web interface)
- **Backend API**: http://localhost:5000/api (REST API)
- **Health Check**: http://localhost:5000/health (Verify backend is running)

**6. Start Crawling!**

You're all set! The web interface at http://localhost:3000 will guide you through:
1. Choosing crawl mode (Content or Link extraction)
2. Entering a URL or uploading a CSV file
3. Configuring crawl options
4. Viewing results and downloading files

### Stopping the Application

To stop all services:
```bash
docker-compose down
```

To stop and remove all data (including downloaded content):
```bash
docker-compose down -v
```

### Troubleshooting

**Port Already in Use**

If ports 3000 or 5000 are already in use, you can change them in the `.env` file:
```bash
FRONTEND_PORT=3001
BACKEND_PORT=5001
```

Then restart the containers:
```bash
docker-compose down
docker-compose up -d
```

**Viewing Logs**

To see what's happening inside the containers:
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run CLI
python main.py --help
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Usage

### Command Line Interface (CLI)

#### Content Mode Examples

```bash
# Basic usage (default: content mode, .txt output)
python main.py --url https://example.com

# Multiple formats
python main.py --url https://example.com --format txt,md,html

# With scoping
python main.py --url https://example.com --scope-class main-content --format md

# With images
python main.py --url https://example.com --download-images

# Full options
python main.py --url https://example.com/blog \
  --mode content \
  --scope-class article-body \
  --format txt,md,html \
  --download-images \
  --output ./output/
```

#### Link Mode Examples

```bash
# Basic link extraction
python main.py --url https://example.com --mode link

# JSON output
python main.py --url https://example.com --mode link --format json

# Internal links only
python main.py --url https://example.com --mode link --link-type internal

# External links only
python main.py --url https://example.com --mode link --link-type external
```

#### Bulk Processing

```bash
# Process multiple URLs from CSV
python main.py --csv urls.csv --output ./bulk_output/
```

CSV format example:
```csv
url,mode,scope_class,format,download_images
https://example.com/page1,content,main-content,txt,false
https://example.com/page2,link,,json,
https://example.com/page3,content,,txt md,true
```

#### Interactive Mode

```bash
python main.py
```

### Web Interface

1. Navigate to http://localhost:3000
2. Select crawling mode (Content or Link)
3. Choose input method (Single URL or CSV upload)
4. Configure options
5. Start crawling and monitor progress
6. View results and download files

### API Usage

#### Single URL Crawl (Content Mode)

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

#### Single URL Crawl (Link Mode)

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

#### Bulk Crawl with CSV

```bash
curl -X POST http://localhost:5000/api/crawl/bulk \
  -F "file=@urls.csv"
```

## Project Structure

```
web-crawler/
├── backend/
│   ├── crawler/          # Core crawling modules
│   ├── api/              # Flask/FastAPI backend
│   ├── utils/            # Utilities
│   ├── tests/            # Unit tests
│   ├── main.py           # CLI entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── services/     # API client
│   └── package.json
├── output/               # Crawl output directory
├── docker-compose.yml
├── .env.example
└── README.md
```

## Configuration

Key environment variables in `.env`:

```bash
# Backend
BACKEND_PORT=5000
OUTPUT_DIRECTORY=/app/output
DEFAULT_TIMEOUT=30

# Frontend
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost:5000/api

# Crawler
MAX_IMAGE_SIZE_MB=10
MAX_URLS_PER_CSV=10000
```

## Output Structure

### Content Mode (with images)

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

### Link Mode

```
output/
└── example_com_20231215_1430/
    ├── example_com_20231215_1430.txt
    ├── example_com_20231215_1430.json
    ├── extraction_details.json
    └── extraction_summary.txt
```

## Testing

```bash
cd backend
pytest tests/
```

## Technologies

- **Backend**: Python 3.10+, Flask/FastAPI, BeautifulSoup4
- **Frontend**: React 18+, Tailwind CSS
- **Task Queue**: Redis + Celery (optional)
- **Deployment**: Docker + Docker Compose

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Acknowledgments

Built with ❤️ using Python and React

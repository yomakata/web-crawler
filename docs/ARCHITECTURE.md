# Web Crawler - System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         WEB CRAWLER SYSTEM                          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACES                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐         ┌──────────────────┐                │
│  │   CLI Interface  │         │   REST API       │                │
│  │   (main.py)      │         │   (Flask)        │                │
│  │                  │         │                  │                │
│  │ - Interactive    │         │ - POST /crawl    │                │
│  │ - Arguments      │         │ - GET /status    │                │
│  │ - CSV Bulk       │         │ - GET /results   │                │
│  └────────┬─────────┘         └────────┬─────────┘                │
│           │                            │                           │
└───────────┼────────────────────────────┼───────────────────────────┘
            │                            │
            └────────────┬───────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       CRAWLER ENGINE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  FETCHER (fetcher.py)                                        │  │
│  │  - HTTP requests with retry                                  │  │
│  │  - URL validation                                            │  │
│  │  - Error handling                                            │  │
│  └─────────────────────────┬────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PARSER (parser.py)                                          │  │
│  │  - HTML parsing (BeautifulSoup + lxml)                       │  │
│  │  - Content extraction                                        │  │
│  │  - Scoping (class/ID)                                        │  │
│  │  - Metadata extraction                                       │  │
│  └───────────┬─────────────────────────┬────────────────────────┘  │
│              ↓                         ↓                            │
│  ┌───────────────────────┐  ┌──────────────────────────────────┐  │
│  │  CONTENT MODE         │  │  LINK MODE                       │  │
│  ├───────────────────────┤  ├──────────────────────────────────┤  │
│  │                       │  │                                  │  │
│  │ ┌─────────────────┐   │  │ ┌────────────────────────────┐ │  │
│  │ │ CONVERTERS      │   │  │ │ LINK EXTRACTOR             │ │  │
│  │ │ (converters.py) │   │  │ │ (link_extractor.py)        │ │  │
│  │ │                 │   │  │ │                            │ │  │
│  │ │ - Text          │   │  │ │ - Extract all links        │ │  │
│  │ │ - Markdown      │   │  │ │ - Filter internal/external │ │  │
│  │ │ - HTML+CSS      │   │  │ │ - Link metadata            │ │  │
│  │ └─────────────────┘   │  │ │ - JSON/Text output         │ │  │
│  │                       │  │ └────────────────────────────┘ │  │
│  │ ┌─────────────────┐   │  │                                  │  │
│  │ │ IMAGE DOWNLOADER│   │  │                                  │  │
│  │ │ (image_down.py) │   │  │                                  │  │
│  │ │                 │   │  │                                  │  │
│  │ │ - Download imgs │   │  │                                  │  │
│  │ │ - Local paths   │   │  │                                  │  │
│  │ │ - Path mapping  │   │  │                                  │  │
│  │ └─────────────────┘   │  │                                  │  │
│  └───────────────────────┘  └──────────────────────────────────┘  │
│              ↓                         ↓                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  WRITER (writer.py)                                          │  │
│  │  - File output (.txt, .md, .html, .json)                     │  │
│  │  - Folder structure                                          │  │
│  │  - Metadata files (extraction_details.json, summary.txt)     │  │
│  │  - Timestamp naming                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                          UTILITIES                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │   VALIDATORS    │  │  CSV PROCESSOR  │  │     LOGGER       │   │
│  │  (validators.py)│  │ (csv_proc.py)   │  │   (logger.py)    │   │
│  │                 │  │                 │  │                  │   │
│  │ - URL check     │  │ - Parse CSV     │  │ - Setup logging  │   │
│  │ - Input check   │  │ - Validate      │  │ - Console/File   │   │
│  │ - Format check  │  │ - Bulk process  │  │ - Colored output │   │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT STORAGE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  output/                                                            │
│  └── example_com_blog_20231215_1430/                               │
│      ├── example_com_blog_20231215_1430.txt                        │
│      ├── example_com_blog_20231215_1430.md                         │
│      ├── example_com_blog_20231215_1430.html                       │
│      ├── extraction_details.json                                   │
│      ├── extraction_summary.txt                                    │
│      ├── image_001.jpg                                             │
│      └── image_002.png                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      API LAYER (Flask)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ROUTES (routes.py)                                          │  │
│  │                                                              │  │
│  │  POST   /api/crawl/single         - Single URL crawl        │  │
│  │  POST   /api/crawl/bulk           - Bulk CSV crawl          │  │
│  │  GET    /api/job/{id}/status      - Job status              │  │
│  │  GET    /api/job/{id}/results     - Job results             │  │
│  │  GET    /api/job/{id}/metadata    - Extraction metadata     │  │
│  │  GET    /api/download/{id}/{file} - Download file           │  │
│  │  GET    /api/history              - Crawl history           │  │
│  │  DELETE /api/job/{id}             - Delete job              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  MODELS (models.py)                                          │  │
│  │  - CrawlRequest: Request validation                          │  │
│  │  - Job: Job tracking and state                              │  │
│  │  - JobStore: In-memory job storage                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                            ↓                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  TASKS (tasks.py)                                            │  │
│  │  - crawl_single_url(): Execute single crawl                  │  │
│  │  - crawl_bulk_urls(): Execute bulk crawl                     │  │
│  │  - Job state management                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     DEPLOYMENT (Docker)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐      │
│  │    Backend     │  │    Frontend    │  │     Redis       │      │
│  │    (Python)    │  │    (React)     │  │   (Optional)    │      │
│  │                │  │                │  │                 │      │
│  │  Port: 5000    │  │  Port: 3000    │  │  Port: 6379     │      │
│  └────────────────┘  └────────────────┘  └─────────────────┘      │
│                                                                     │
│  Orchestrated by: docker-compose.yml                               │
│  Configuration: .env                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. User Input (CLI/API) → URL/CSV                                 │
│  2. Validation → Check URL format, parameters                      │
│  3. Fetch → HTTP request to target URL                             │
│  4. Parse → Extract HTML content                                   │
│  5. Process:                                                        │
│     ├─ Content Mode: Extract text → Convert formats → Download imgs│
│     └─ Link Mode: Extract links → Filter → Format output           │
│  6. Write → Save files with metadata                               │
│  7. Return → Results with statistics                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      KEY TECHNOLOGIES                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Backend:     Python 3.10+, Flask 3.0, BeautifulSoup4, lxml        │
│  HTTP:        requests library with retry logic                    │
│  Parsing:     BeautifulSoup4 + lxml parser                         │
│  Conversion:  html2text (Markdown), Custom HTML formatter          │
│  Data:        pandas (CSV), JSON (metadata)                        │
│  Testing:     pytest, pytest-cov                                   │
│  Deployment:  Docker, Docker Compose                               │
│  Optional:    Redis (caching), Celery (async tasks)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        FEATURES                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✅ Dual Mode (Content & Link extraction)                          │
│  ✅ Multiple Formats (txt, md, html, json)                         │
│  ✅ Content Scoping (by CSS class or ID)                           │
│  ✅ Image Downloading (with local path mapping)                    │
│  ✅ Bulk Processing (CSV input)                                    │
│  ✅ Metadata Tracking (JSON + text summaries)                      │
│  ✅ CLI Interface (interactive & argument-based)                   │
│  ✅ REST API (full CRUD operations)                                │
│  ✅ Error Handling (graceful failures)                             │
│  ✅ Docker Support (containerized deployment)                      │
│  ✅ Comprehensive Tests (unit + integration)                       │
│  ✅ Full Documentation (guides + examples)                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Architecture Highlights

### Modular Design
Each component is independent and can be tested/modified separately:
- **Fetcher**: Only handles HTTP operations
- **Parser**: Only handles HTML parsing
- **Converters**: Only handle format conversion
- **Writer**: Only handles file I/O

### Separation of Concerns
- **CLI** (`main.py`): User interaction
- **API** (`api/`): HTTP interface
- **Core** (`crawler/`): Business logic
- **Utils** (`utils/`): Shared utilities

### Scalability
- Job-based architecture (async-ready)
- Redis integration prepared
- Docker containerization
- Horizontal scaling possible

### Extensibility
- Easy to add new output formats
- Easy to add new extraction modes
- Plugin architecture for validators
- Customizable processing pipeline

### Reliability
- Retry logic for network errors
- Comprehensive error handling
- Validation at every step
- Detailed logging and metrics

## System Requirements

**Minimum:**
- Python 3.8+
- 512MB RAM
- 100MB disk space

**Recommended:**
- Python 3.10+
- 2GB RAM
- 1GB disk space (for outputs)

**For Production:**
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 10GB+ disk space

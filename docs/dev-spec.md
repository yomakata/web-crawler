# Web Crawler - Development Specification

**Last Updated**: December 26, 2025

## Project Overview
A full-stack web crawler application with Python backend and React frontend that allows users to crawl URLs in two modes: content extraction or link extraction. Supports single URL crawling or bulk operations via CSV upload, with Docker containerization for easy deployment.

### Key Capabilities
- **Dual Mode Operation**: Content extraction or link extraction
- **Multiple Output Formats**: Plain text, Markdown, HTML, JSON
- **Bulk Processing**: CSV upload for processing multiple URLs
- **Content Scoping**: Extract specific elements by class or ID
- **Image Downloading**: Download and save images with content
- **ZIP Download**: Automatic ZIP compression when images are downloaded
- **Metadata Tracking**: Comprehensive extraction statistics and details
- **Web & CLI Interfaces**: Use via browser or command line
- **Real-time Progress**: Live updates during crawling operations
- **Docker Deployment**: Containerized stack (backend + frontend + Redis)
- **RESTful API**: Programmatic access to all features
- **Authentication Support**: Cookies, headers, and basic auth for protected content
- **Page Preview**: Test authentication and scope selectors before extraction
- **Saved Jobs**: Save and reuse crawling configurations
- **Enhanced Error Handling**: User-friendly error messages with actionable suggestions
- **Inline Text Handling**: Proper formatting for inline elements (spans, links) within paragraphs
- **Job History**: Track all extraction jobs with full metadata and results
- **Advanced UI**: Modern, responsive interface with modals, toasts, and visual feedback

## Features

### 1. Crawling Modes
Users must select one of two crawling modes:

#### Content Mode (Default)
- Extract and save webpage content in multiple formats
- Supports text, markdown, and HTML output
- Optional image downloading
- Content scoping by class name or element ID

#### Link Mode
- Extract and output only hyperlinks from the webpage
- Supports internal links, external links, or both
- Output as plain text list or structured JSON
- Optional link metadata (link text, URL, type)
- Filter options (same domain only, exclude anchors, etc.)

### 2. Web Crawling
- Crawl content from single URL or multiple URLs (bulk mode)
- Handle HTTP/HTTPS protocols
- Support for different content types (HTML, text)
- Error handling for invalid URLs, network errors, and timeout scenarios
- User-agent configuration to identify the crawler

### 3. Content Scoping (Scope Element - Content Mode Only)
- Allow users to specify a target element by class name or element ID
- **Targeted Extraction**: When a class name or element ID is provided:
  - If the element is found, extract content only from that specific element
  - If the element is not found, cancel and exit script
- Enables focused content extraction from specific sections of a webpage
- Supports both single element targeting and multiple element extraction

### 4. Image Downloading (Content Mode Only)
- Download images referenced in the extracted content
- Save images alongside the extracted content in a dedicated folder
- **Output Structure**:
  - Each crawled page creates its own folder
  - Folder contains: extracted content files (.txt, .md, .html) + downloaded images
  - Images maintain their original format (jpg, png, gif, svg, webp, etc.)
- Update image references in extracted content to point to local files
- Handle image download errors gracefully (log failures, continue extraction)
- **ZIP Download**: When images are downloaded, all output files (content + images) are automatically packaged into a ZIP archive for convenient download

### 5. File Download System
The application provides two download methods based on whether images were downloaded:

#### Individual File Downloads
- **When**: No images were downloaded (text/markdown/HTML only)
- **Behavior**: Each output file gets its own download button
- **UI**: List of files with individual "Download" buttons
- **Use Case**: Quick access to single text files

#### ZIP Archive Download
- **When**: Images were downloaded with the content
- **Behavior**: All files (content + images) compressed into a single ZIP
- **UI**: Single prominent "Download All (ZIP)" button replacing individual downloads
- **Advantages**: 
  - Maintains folder structure
  - Preserves image references in HTML/Markdown
  - Convenient one-click download for all assets
  - Reduces UI clutter when many files present
- **Implementation**: Backend flag `has_images` triggers conditional UI rendering

**Technical Details**:
- Backend creates ZIP archives on-the-fly using Python's `zipfile` module
- ZIP contains proper folder structure: `[job_id]/[filename]`
- Frontend conditionally renders based on `result.has_images` flag
- API endpoints:
  - `/download/<job_id>/<filename>` - Individual file download
  - `/download/<job_id>` - ZIP archive download (all files)

### 6. Bulk URL Processing
- Upload CSV file containing multiple URLs
- Process all URLs in batch mode
- Generate individual output folders for each URL
- Aggregate summary report for all processed URLs
- Progress tracking for bulk operations
- CSV format: columns for URL, mode (optional), scope_class (optional), scope_id (optional)

### 7. Job History & Management (NEW)
Track and manage all extraction jobs with comprehensive history:

#### History Features
- **Job List**: View all past extraction jobs with key metadata
- **Job Details**: Full results, statistics, and metadata for each job
- **Search & Filter**: Find jobs by URL, status, or date range
- **Delete Jobs**: Remove unwanted job records
- **Persistent Storage**: Jobs stored in JSON file (`jobs.json`)
- **Status Tracking**: pending, running, completed, failed
- **Progress Indicators**: Real-time progress for bulk jobs

#### Job Data Structure
```json
{
  "job_id": "uuid",
  "status": "completed" | "failed" | "running" | "pending",
  "created_at": timestamp,
  "started_at": timestamp,
  "completed_at": timestamp,
  "total_urls": number,
  "completed_urls": number,
  "failed_urls": number,
  "progress": number,  // 0-100%
  "results": [{
    "url": string,
    "status": "success" | "failed",
    "output_folder": string,
    "output_files": [string],
    "has_images": boolean,  // NEW: Triggers ZIP download
    "statistics": {...},
    "metadata": {...},
    "failure_info": {...}  // If failed
  }],
  "errors": [string]
}
```

#### History Page UI
- **Job Cards**: Visual cards showing job summary
  - URL (truncated with tooltip)
  - Status badge (color-coded)
  - Timestamp (relative time: "2 hours ago")
  - Statistics preview (files created, execution time)
  - Action buttons (View Results, Delete)
- **Results Modal**: Detailed view when clicking "View Results"
  - Full extraction metadata
  - Content statistics
  - Download buttons (individual or ZIP)
  - Error details if failed
- **Empty State**: Helpful message when no jobs exist
- **Auto-refresh**: Polling for running jobs (optional)

### 8. Home Page Dashboard (NEW)
Improved landing page with quick access to key features:

#### Dashboard Sections
- **Quick Actions**: Large buttons for primary actions
  - "Start New Extraction" → Navigate to Crawler page
  - "View History" → Navigate to History page  
  - "Manage Saved Jobs" → Navigate to Saved Jobs page
- **Recent History**: Last 5 extraction jobs with status
  - Non-clickable display cards (view-only)
  - Status icons and timestamps
  - Quick overview without navigation
- **Saved Jobs Preview**: Last 3 saved configurations
  - Non-clickable display cards (view-only)
  - Job name and description
  - "Manage" link to full Saved Jobs page
- **Statistics Summary**: Quick stats at a glance
  - Total extractions performed
  - Success rate percentage
  - Total files downloaded
  - Average execution time

#### UI Design
- **Clean Layout**: Removed excessive sections (Platform Features removed)
- **Proper Spacing**: Fixed footer spacing issues
- **Visual Hierarchy**: Clear sections with headers
- **Responsive Grid**: Cards adapt to screen size
- **Modern Styling**: Gradient backgrounds, shadows, hover effects

### 9. Extraction Metadata & Results Display
- Generate extraction detail and summary files alongside content
- **Display metadata in frontend** after extraction completes:
  - Real-time results card/modal showing extraction summary
  - Visual statistics dashboard (charts/cards for metrics)
  - Color-coded status indicators (success/warning/error)
  - Expandable sections for detailed information
  - **Smart Download UI**: Shows ZIP button when images downloaded, individual buttons otherwise
  - Link to view full extraction details
- **extraction_details.json**: Complete extraction metadata including:
  - Source URL, timestamp, execution time
  - Extraction parameters (scope class/ID, formats requested)
  - HTTP response details (status code, headers, content-type)
  - Images downloaded (count, list of URLs, success/failure status)
  - Content statistics (word count, character count, image count)
  - Any errors or warnings encountered
  - **has_images flag**: Boolean indicating if images were successfully downloaded (triggers ZIP UI)
  - **Failure Information** (if extraction failed):
    - `extraction_status`: "failed"
    - `failure_reason`: Specific error message
    - `error_type`: Category (e.g., "network_error", "http_error", "parsing_error", "validation_error")
    - `error_code`: HTTP status code or error code if applicable
    - `error_timestamp`: When the error occurred
    - `retry_possible`: Boolean indicating if retry might succeed
    - `suggestions`: Array of actionable troubleshooting steps
- **extraction_summary.txt**: Human-readable summary including:
  - URL and extraction timestamp
  - Content extraction status
  - Number of images downloaded
  - Output files generated
  - Any issues encountered

### 10. Output Options

#### Content Mode Outputs

**Default Output:**
- **Plain Text (.txt)**: Extract and save clean text content without HTML tags

**Optional Outputs:**
- **Markdown (.md)**: Convert HTML content to Markdown format, preserving structure (headings, lists, links, etc.)
- **HTML (.html)**: Save formatted HTML with proper styling and structure
  - Preserve original formatting
  - Include inline CSS or reference external stylesheets
  - Maintain responsive design elements

#### Link Mode Outputs

**Default Output:**
- **Plain Text (.txt)**: Simple list of URLs, one per line

**Optional Outputs:**
- **JSON (.json)**: Structured link data including:
  - URL
  - Link text/anchor text
  - Link type (internal/external)
  - Parent section/context
  - HTTP status (if validation enabled)

### 11. User Interface

### 12. Authentication Support
The crawler now supports three authentication methods for accessing protected content:

#### Cookie-Based Authentication
- **Format**: Standard cookie string format (`name1=value1; name2=value2`)
- **Use Case**: Session-based authentication, logged-in content
- **Frontend**: Multi-line textarea for cookie input
- **Backend**: Parses cookie string and includes in requests

#### Header-Based Authentication  
- **Format**: JSON object with custom headers (`{"Authorization": "Bearer token", "X-Custom-Header": "value"}`)
- **Use Case**: API tokens, custom auth headers
- **Frontend**: JSON editor with validation
- **Backend**: Merges custom headers with request headers

#### Basic Authentication
- **Format**: Username and password fields
- **Use Case**: HTTP Basic Auth protected sites
- **Frontend**: Separate username/password inputs
- **Backend**: Generates `Authorization: Basic` header automatically

**Implementation Details**:
- Authentication method selector (radio buttons/dropdown)
- Conditional form fields based on selected method
- Validation for JSON format (headers) and required fields
- Credentials stored with saved jobs (⚠️ plaintext - documented security consideration)
- Authentication included in preview and extraction requests

### 13. Page Preview
Before running full extraction, users can preview the page to:

#### Preview Capabilities
- **Authentication Testing**: Verify cookies/headers work before extraction
- **Page Load Verification**: Confirm URL is accessible and returns content
- **Scope Element Validation**: Check if specified class/ID exists on page
- **Content Preview**: See first ~200 characters of scoped content
- **Available Classes**: List of CSS classes found on page (top 20) for debugging
- **Page Statistics**: Word count, image count, link count, paragraph count

#### Preview Response
```json
{
  "success": boolean,
  "url": string,
  "title": string,
  "has_scope_element": boolean,  // null if no scope specified
  "scope_element_info": {
    "tag": string,
    "text_length": number
  },
  "scope_element_preview": string,  // First ~200 chars
  "available_classes": [string],  // Top 20 classes on page
  "statistics": {
    "content_length": number,
    "text_length": number,
    "total_links": number,
    "total_images": number,
    "total_paragraphs": number
  },
  "error": string  // If failed
}
```

**UI Components**:
- "Preview Page" button in crawler form
- Modal/panel showing preview results with color-coded status
- Green badge if scope element found, yellow warning if not found
- Resizable textarea for content preview
- List of available classes for easy reference
- "Continue with Extraction" button if preview succeeds

### 14. Saved Jobs
Users can save crawling configurations for reuse:

#### Saved Job Features
- **Save Configuration**: Save all form settings as a named job
- **Job Metadata**: Name, description, creation date, last used date
- **Stored Settings**: URL, mode, formats, scope, auth method, all form values
- **Job List View**: Dedicated page showing all saved jobs
- **Load Job**: One-click to populate form with saved settings
- **Delete Job**: Remove unwanted saved configurations
- **Update Job**: Re-save with same name to update (future enhancement)

#### Saved Job Data Structure
```json
{
  "saved_job_id": "uuid",
  "name": string,
  "description": string,
  "input_method": "single" | "bulk",
  "mode": "content" | "link",
  "url": string,
  "csv_filename": string,
  "formats": [string],
  "scope_class": string,
  "scope_id": string,
  "download_images": boolean,
  "link_type": "all" | "internal" | "external",
  "auth_method": "cookies" | "headers" | "basic" | null,
  "cookies": string,  // ⚠️ Stored in plaintext
  "auth_headers": object,  // ⚠️ Stored in plaintext
  "basic_auth_username": string,  // ⚠️ Stored in plaintext
  "basic_auth_password": string,  // ⚠️ Stored in plaintext
  "created_at": timestamp,
  "last_used_at": timestamp
}
```

**Storage**: JSON file (`saved_jobs.json`) in backend `/app` directory

**Security Note**: Credentials are stored in plaintext. Documented in README with recommendation to use environment-specific credentials and not commit sensitive data.

### 15. Enhanced Error Handling
User-friendly error messages with actionable suggestions:

#### Error Categories
- **Network Errors**: Timeout, connection refused, too many redirects
- **HTTP Errors**: 400, 401, 403, 404, 408, 429, 500-504 with specific suggestions
- **Content Errors**: Empty content, element not found, encoding errors
- **Validation Errors**: Invalid URL format, missing parameters
- **Permission Errors**: File system errors, disk full, permission denied

#### Error Response Structure
```json
{
  "failure_reason": string,  // Human-readable error message
  "error_type": string,  // Category: network_error, http_error, etc.
  "error_code": number | string | null,  // HTTP status or error code
  "retry_possible": boolean,  // Whether retry might succeed
  "suggestions": [string]  // Actionable troubleshooting steps
}
```

#### Example Error Messages
- **404 Not Found**: "Check if the URL is correct and complete. The page may have been moved or deleted."
- **401 Unauthorized**: "The page requires authentication. Check if you have the necessary credentials."
- **Connection Timeout**: "Check your internet connection. The target server may be slow or experiencing issues."
- **Element Not Found**: "Verify the class name or ID is correct. Try extracting without scope restrictions first."

**Implementation**:
- `error_handler.py` module with `handle_extraction_failure()` function
- Maps Python exceptions to user-friendly failure_info
- HTTP status code specific suggestions via `get_http_error_suggestions()`
- Displayed in results modal with error icon and red status badge

### 16. Improved Text Formatting
Enhanced HTML-to-text conversion with proper inline element handling:

#### Text Extraction Algorithm
- **Recursive Traversal**: Custom recursive function processes HTML tree
- **Block vs Inline Elements**: Distinguishes between block (p, div, h1-h6) and inline (span, a, strong, b, em)
- **Block Elements**: Create new lines (paragraphs, divs, headings separated)
- **Inline Elements**: Stay on same line (spans, links, bold text don't break)
- **Space Joining**: Inline elements joined with spaces, not newlines

#### Supported Element Types
**Block Elements**: `p`, `div`, `h1-h6`, `section`, `article`, `header`, `footer`, `nav`, `aside`, `main`, `blockquote`, `pre`, `ul`, `ol`, `li`, `table`, `tr`, `td`, `th`, `dl`, `dt`, `dd`, `form`, `fieldset`, `figure`, `figcaption`

**Inline Elements**: All other elements (automatically stay inline)

#### Example
**HTML**:
```html
<p><span>MQDC </span><span>จัด </span><span>'</span><span>โปร ปิด ปี</span><span>' </span><span>สุดพิเศษส่งท้ายปี </span><span>2025</span></p>
```

**Output**:
```
MQDC จัด ' โปร ปิด ปี ' สุดพิเศษส่งท้ายปี 2025
```

**Previous Behavior**: Each span created a new line (❌ incorrect)
**Current Behavior**: All spans stay on one line (✅ correct)

This fix ensures proper formatting for:
- Thai text with styling spans
- Links with nested spans
- Bold/italic text within paragraphs
- Any inline formatting elements

### 17. User Interface

#### Command-Line Interface (CLI)
- Traditional CLI for direct script execution
- Full access to all features via command-line arguments
- Support for automation and scripting

#### Web Interface (React Frontend)
- Modern, responsive web interface built with Tailwind CSS
- Single URL or CSV bulk upload options
- Real-time crawling progress indicators
- Download results directly from browser
- Mode selection (Content/Link)
- Interactive form for all options:
  - Output format selection
  - Scope element configuration
  - Image download toggle
  - Link filtering options
- **Extraction Results Display**:
  - Immediate results modal/card upon completion
  - Visual metadata presentation with statistics
  - Content preview (first 500 chars)
  - Word count, character count, image count badges
  - Success/warning/error status indicators
  - List of generated output files with download buttons
  - Execution time and timestamp
  - Errors and warnings displayed prominently
  - **Failure Reason Display**: If extraction fails, show:
    - "Extraction Failed" status badge (red/error color)
    - Specific failure reason in clear language
    - Error type icon/indicator
    - Suggested actions or troubleshooting steps
    - Option to retry extraction
    - **Implementation Note**: Use optional chaining (`?.`) and fallback values to ensure failure reasons are always displayed, even if data structure varies. Fallback chain: `failure_info?.failure_reason` → `error` → "An unknown error occurred"
  - Image download status (X of Y successful)
  - Option to view full extraction_details.json
- Results dashboard showing:
  - Extraction history with metadata previews
  - Success/failure statistics charts
  - Download links for all output files
  - Filter and search capabilities

## Technical Requirements

### Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | Python 3.10+ with Flask or FastAPI | REST API server |
| **Frontend** | React 18+ with Tailwind CSS | Web user interface |
| **Web Scraping** | BeautifulSoup4 + lxml | HTML parsing |
| **Data Processing** | pandas | CSV handling |
| **Task Queue** | Redis + Celery (optional) | Async job processing |
| **Containerization** | Docker + Docker Compose | Deployment |
| **Charts** | Recharts or Chart.js | Data visualization |
| **State Management** | React Query or SWR | API data caching |
| **File Upload** | React Dropzone | CSV file handling |
| **HTTP Client** | requests (backend), Axios (frontend) | Network requests |

### Backend (Python)

#### Core Dependencies
- **Flask** or **FastAPI**: REST API framework for backend
- **requests** or **httpx**: HTTP client for fetching web pages
- **beautifulsoup4**: HTML parsing and content extraction
- **html2text** or **markdownify**: HTML to Markdown conversion
- **argparse**: CLI argument parsing
- **pathlib**: File system path handling
- **pandas**: CSV file processing for bulk uploads
- **python-dotenv**: Environment variable management
- **Flask-CORS** or **fastapi-cors**: Cross-origin resource sharing

#### Python Version
- Python 3.10 or higher (recommended)
- Minimum: Python 3.8

#### Optional Dependencies
- **lxml**: Faster HTML parsing (optional, falls back to html.parser)
- **colorama**: Colored terminal output for better CLI UX
- **validators**: URL validation
- **celery**: Async task queue for bulk processing (optional)
- **redis-py**: Redis client (required if using Celery)

### Frontend (React)

#### Core Dependencies
- **React 18+**: Frontend framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Headless UI** or **Radix UI**: Unstyled accessible components (to use with Tailwind)
- **React Dropzone**: File upload component for CSV
- **React Query** or **SWR**: Data fetching and caching
- **Recharts** or **Chart.js**: Data visualization for statistics
- **React Icons**: Icon library for UI elements

#### Node Version
- Node.js 18 or higher (recommended)
- Minimum: Node.js 16
- npm (v8+) or yarn (v1.22+) package manager

### Deployment

#### Docker Requirements
- **Docker**: Container runtime
- **Docker Compose**: Multi-container orchestration
- **docker-compose.yml**: Service definitions for:
  - Backend API service (Python/Flask or FastAPI)
  - Frontend service (React/Node)
  - Optional: Redis service (for task queue)
  - Optional: PostgreSQL service (for job history)

#### Environment Variables (.env)
All sensitive configuration stored in `.env`:
- API keys (if any)
- Database credentials (if using database)
- Redis connection string (if using task queue)
- Secret keys for session management
- CORS allowed origins
- File upload limits
- Output directory paths

## Architecture

### Module Structure
```
web-crawler/
├── backend/
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── fetcher.py          # URL fetching logic
│   │   ├── parser.py           # HTML parsing and content extraction
│   │   ├── converters.py       # Format conversion (txt, md, html)
│   │   ├── image_downloader.py # Image downloading and management
│   │   ├── link_extractor.py   # Link extraction for link mode
│   │   └── writer.py           # File output handling
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py              # Flask/FastAPI application
│   │   ├── routes.py           # API endpoints
│   │   ├── models.py           # Data models/schemas
│   │   └── tasks.py            # Background tasks (if using Celery)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py       # URL and input validation
│   │   ├── csv_processor.py    # CSV file handling
│   │   ├── error_handler.py    # User-friendly error handling (NEW)
│   │   └── logger.py           # Logging configuration
│   ├── tests/
│   │   ├── test_fetcher.py
│   │   ├── test_parser.py
│   │   ├── test_converters.py
│   │   ├── test_link_extractor.py
│   │   ├── test_image_downloader.py
│   │   └── test_api.py
│   ├── main.py                 # CLI entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── CrawlForm.jsx       # Main crawl configuration form
│   │   │   ├── ModeSelector.jsx    # Content/Link mode selection
│   │   │   ├── URLInput.jsx        # Single URL input
│   │   │   ├── CSVUpload.jsx       # CSV file upload component
│   │   │   ├── ProgressBar.jsx     # Crawling progress indicator
│   │   │   ├── ResultsTable.jsx    # Results table display
│   │   │   ├── ResultsModal.jsx    # Metadata display modal after extraction
│   │   │   ├── PreviewModal.jsx    # Page preview modal (NEW)
│   │   │   ├── SaveJobModal.jsx    # Save job configuration modal (NEW)
│   │   │   ├── AuthSection.jsx     # Authentication method selector (NEW)
│   │   │   ├── MetadataCard.jsx    # Visual metadata statistics card
│   │   │   ├── StatsChart.jsx      # Charts for statistics visualization
│   │   │   └── DownloadButton.jsx  # Download output files
│   │   ├── pages/
│   │   │   ├── Home.jsx            # Landing page
│   │   │   ├── Crawler.jsx         # Main crawler interface
│   │   │   ├── SavedJobs.jsx       # Saved jobs list page (NEW)
│   │   │   └── History.jsx         # Extraction history
│   │   ├── services/
│   │   │   └── api.js              # API client functions
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── App.css
│   ├── package.json
│   ├── package-lock.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .env
├── .gitignore
├── dev-spec.md
└── README.md
```

### Core Components

#### 1. Fetcher Module (`fetcher.py`)
```python
class WebFetcher:
    - fetch(url: str, cookies: dict = None, headers: dict = None, auth: tuple = None) -> Response  # NEW: Auth params
    - validate_url(url: str) -> bool
    - set_headers(custom_headers: dict = None) -> dict  # NEW: Merge custom headers
    - handle_errors()
    - parse_cookies(cookie_string: str) -> dict  # NEW: Parse cookie string to dict
```

#### 2. Parser Module (`parser.py`)
```python
class ContentParser:
    - parse_html(html: str) -> BeautifulSoup
    - extract_text() -> str  # NEW: Recursive extraction with inline/block element handling
    - extract_title() -> str
    - extract_metadata() -> dict
    - clean_content() -> str
    - extract_by_scope(class_name: str = None, element_id: str = None) -> str
    - find_scoped_element(soup: BeautifulSoup, class_name: str, element_id: str) -> BeautifulSoup
    - extract_image_urls(soup: BeautifulSoup) -> list[str]
    - extract_text_recursive(elem, in_block: bool = False) -> str  # NEW: Recursive helper
```

**Text Extraction Implementation (NEW)**:
- Recursive tree traversal distinguishing block vs inline elements
- Block elements (p, div, h1-h6, etc.) create newlines
- Inline elements (span, a, strong, etc.) stay on same line
- Properly handles nested inline elements (e.g., `<p><a><span>text</span></a></p>`)
- Fixes Thai text formatting issues with multiple spans in paragraphs

#### 2b. Link Extractor Module (`link_extractor.py`)
```python
class LinkExtractor:
    - extract_all_links(soup: BeautifulSoup, base_url: str) -> list[dict]
    - filter_links(links: list, link_type: str = 'all') -> list
      # link_type options: 'all', 'internal', 'external'
    - get_link_metadata(link_element) -> dict
    - is_internal_link(url: str, base_url: str) -> bool
    - normalize_url(url: str, base_url: str) -> str
    - remove_anchors(url: str) -> str
    - validate_link(url: str) -> bool
    - format_links_as_text(links: list) -> str
    - format_links_as_json(links: list) -> str
```

#### 3. Converters Module (`converters.py`)
```python
class TextConverter:
    - to_plain_text(soup: BeautifulSoup) -> str

class MarkdownConverter:
    - to_markdown(html: str) -> str
    - update_image_paths(content: str, image_mapping: dict) -> str

class HTMLConverter:
    - format_html(soup: BeautifulSoup) -> str
    - add_styling() -> str
    - update_image_paths(soup: BeautifulSoup, image_mapping: dict) -> str
```

#### 4. Image Downloader Module (`image_downloader.py`)
```python
class ImageDownloader:
    - download_image(url: str, save_path: str) -> bool
    - download_all_images(image_urls: list[str], output_dir: str) -> dict
    - resolve_image_url(base_url: str, img_src: str) -> str
    - sanitize_filename(url: str) -> str
    - get_image_extension(url: str, content_type: str) -> str
```

#### 5. Writer Module (`writer.py`)
```python
class FileWriter:
    - write_file(content: str, filename: str, format: str)
    - generate_filename(url: str, format: str) -> str
    - generate_folder_name(url: str) -> str
    - extract_domain_and_path(url: str) -> tuple[str, str]
    - format_timestamp() -> str  # Returns YYYYMMDD_HHMM format
    - ensure_directory(path: str)
    - create_output_folder(base_dir: str, folder_name: str) -> str
    - write_extraction_details(details: dict, output_path: str)
    - write_extraction_summary(summary: dict, output_path: str)
    - generate_extraction_metadata(url: str, extraction_data: dict) -> dict
```

#### 6. API Module (`api/routes.py`)
```python
# REST API Endpoints

POST /api/crawl/single
    - Crawl a single URL
    - Body: {url, mode, scope_class, scope_id, formats, download_images, link_filters, 
             auth_method, cookies, auth_headers, basic_auth_username, basic_auth_password}  # NEW: Auth params
    - Returns: {job_id, status}

POST /api/crawl/bulk
    - Upload CSV and crawl multiple URLs
    - Body: multipart/form-data with CSV file
    - Returns: {job_id, total_urls, status}

POST /api/preview  # NEW: Page preview endpoint
    - Preview page with authentication and scope validation
    - Body: {url, scope_class, scope_id, auth_method, cookies, auth_headers, 
             basic_auth_username, basic_auth_password}
    - Returns: {
        success: boolean,
        url: string,
        title: string,
        has_scope_element: boolean | null,
        scope_element_info: {tag, text_length},
        scope_element_preview: string,
        available_classes: [string],
        statistics: {content_length, text_length, total_links, total_images, total_paragraphs},
        error: string | null
      }

POST /api/jobs/saved  # NEW: Create saved job
    - Save crawling configuration
    - Body: {name, description, ...all form fields}
    - Returns: {saved_job_id, name, created_at}

GET /api/jobs/saved  # NEW: List all saved jobs
    - Get all saved job configurations
    - Returns: [{saved_job_id, name, description, created_at, last_used_at, ...fields}]

GET /api/jobs/saved/{job_id}  # NEW: Get specific saved job
    - Get saved job configuration by ID
    - Returns: {saved_job_id, name, description, ...all fields}

PUT /api/jobs/saved/{job_id}  # NEW: Update saved job
    - Update existing saved job configuration
    - Body: {name, description, ...fields to update}
    - Returns: {saved_job_id, name, updated_at}

DELETE /api/jobs/saved/{job_id}  # NEW: Delete saved job
    - Delete saved job configuration
    - Returns: {success: true}

GET /api/job/{job_id}/status
    - Get crawling job status
    - Returns: {job_id, status, progress, completed, total}

GET /api/job/{job_id}/results
    - Get job results with full metadata
    - Returns: {
        job_id,
        results: [{
          url,
          status,  # "success", "failed", "pending"
          output_files,
          errors,  # Array of error messages (legacy, may contain single string)
          failure_info: {  # Present only if status == "failed" - PREFERRED for detailed error information (NEW)
            failure_reason: "Specific error message",  # Human-readable, always present
            error_type: "network_error|http_error|parsing_error|validation_error|content_error|permission_error|unknown_error",
            error_code: 404,  # HTTP status or error code (may be null)
            retry_possible: true,  # Boolean indicating if retry might succeed
            suggestions: ["Action 1", "Action 2"]  # Array of actionable suggestions (may be empty)
          },
          metadata: {
            execution_time,
            content_statistics,
            images_info,
            extraction_parameters
          }
        }]
      }
    - **Frontend Note**: When displaying errors, use fallback chain:
      - `result.failure_info?.failure_reason` (preferred, most specific)
      - `result.error` (fallback, generic message)
      - Default message (last resort)
    - Always use optional chaining (`?.`) when accessing `failure_info` properties

GET /api/job/{job_id}/metadata
    - Get detailed extraction metadata for display
    - Returns: extraction_details.json content formatted for frontend display

GET /api/download/{job_id}/{filename}
    - Download specific output file
    - Returns: File download

GET /api/history
    - Get extraction history
    - Returns: [{job_id, timestamp, mode, urls_count, status}]

DELETE /api/job/{job_id}
    - Delete job and its output files
    - Returns: {success: true}
```

#### 7. Error Handler Module (`utils/error_handler.py`) - NEW
```python
class ExtractionError(Exception):
    """Base exception for extraction errors"""
    - __init__(message, error_type, error_code, retry_possible)

def handle_extraction_failure(url: str, exception: Exception) -> dict:
    """Map exceptions to user-friendly failure information"""
    - Returns: {
        extraction_status: "failed",
        url: string,
        failure_reason: string,
        error_type: string,
        error_code: number | string | null,
        error_timestamp: ISO timestamp,
        retry_possible: boolean,
        suggestions: [string]
      }

def get_http_error_suggestions(status_code: int) -> list[str]:
    """Get actionable suggestions for HTTP status codes"""
    - Handles: 400, 401, 403, 404, 408, 429, 500-504
    - Returns: List of specific troubleshooting steps

def format_failure_for_api(failure_info: dict) -> dict:
    """Format failure information for API response"""

def create_failed_extraction_details(url: str, failure_info: dict) -> dict:
    """Create extraction_details.json for failed extractions"""
```

**Error Handling Flow**:
1. Exception occurs during crawling/extraction
2. `handle_extraction_failure()` catches and categorizes exception
3. Maps to user-friendly error message and suggestions
4. Returns structured failure_info
5. Frontend displays with color-coded status and actionable steps
```python
class CSVProcessor:
    - validate_csv(file_path: str) -> bool
    - parse_csv(file_path: str) -> list[dict]
    - validate_url_column(df: DataFrame) -> bool
    - get_crawl_parameters(row: dict) -> dict
    - generate_bulk_summary(results: list) -> dict
    - export_results_to_csv(results: list, output_path: str)
```

## Usage Examples

### Command Line Interface (CLI)

#### Content Mode Examples

##### Basic usage (default: content mode, .txt output)
```bash
python main.py --url https://example.com
```

##### Content mode with multiple formats
```bash
python main.py --url https://example.com --mode content --format txt,md,html
```

##### Content mode with scoping
```bash
python main.py --url https://example.com --mode content --class main-content --format md
```

##### Content mode with images
```bash
python main.py --url https://example.com --mode content --download-images
```

##### Full content mode options
```bash
python main.py --url https://example.com/blog/article \
  --mode content \
  --class main-content \
  --format txt,md,html \
  --download-images \
  --output ./output/
```

#### Link Mode Examples

##### Basic link extraction (text output)
```bash
python main.py --url https://example.com --mode link
```

##### Link extraction with JSON output
```bash
python main.py --url https://example.com --mode link --format json
```

##### Extract only internal links
```bash
python main.py --url https://example.com --mode link --link-type internal
```

##### Extract only external links
```bash
python main.py --url https://example.com --mode link --link-type external
```

##### Link extraction with filtering
```bash
python main.py --url https://example.com --mode link --format json --exclude-anchors
```

#### Bulk Processing (CSV)

##### Process multiple URLs from CSV
```bash
python main.py --csv urls.csv --output ./bulk_output/
```

CSV format example (`urls.csv`):
```csv
url,mode,scope_class,format,download_images
https://example.com/page1,content,main-content,txt,false
https://example.com/page2,link,,json,
https://example.com/page3,content,,txt md,true
```

#### Interactive Mode
```bash
python main.py
# Prompts:
# Select mode [content/link] (default: content): content
# Enter URL: https://example.com
# Select output format(s) [txt,md,html] (default: txt): md
# Enter scope class (optional): main-content
# Download images? [y/n]: n
```

### Web Interface (React Frontend)

#### Starting the application with Docker Compose
```bash
# Start all services
docker-compose up -d

# Access the web interface
# Open browser to http://localhost:3000

# Access the API directly
# API endpoint: http://localhost:5000/api
```

#### Web Interface Workflow

1. **Navigate to the web interface** at `http://localhost:3000`
2. **Select crawling mode**: Content or Link
3. **Choose input method**:
   - Single URL input
   - CSV file upload for bulk processing
4. **Configure options** based on selected mode:
   - Content Mode: formats, scope, image download
   - Link Mode: link type filters, output format
5. **Start crawling** and monitor real-time progress
6. **View extraction results** in interactive modal/card:
   - Extraction summary with visual statistics
   - Content preview and metadata
   - Success/warning/error indicators
   - Download buttons for each output file
7. **Download results** - individual files or zip archive
8. **View history** of past extractions with metadata previews

#### API Usage Examples

##### Single URL crawl (Content Mode)
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

##### Single URL crawl (Link Mode)
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

##### Bulk crawl with CSV
```bash
curl -X POST http://localhost:5000/api/crawl/bulk \
  -F "file=@urls.csv"
```

##### Check job status
```bash
curl http://localhost:5000/api/job/{job_id}/status
```

##### Download results
```bash
curl -O http://localhost:5000/api/download/{job_id}/example_com_20231215_1430.txt
```

## Implementation Plan

### Phase 1: Core Backend Functionality
1. Set up project structure (backend/frontend separation)
2. Implement URL fetching with error handling
3. Implement HTML parsing and text extraction (Content Mode)
4. Create plain text output functionality
5. Basic CLI interface
6. Implement folder-based output structure

### Phase 2: Format Conversion & Content Scoping
1. Implement Markdown conversion
2. Implement formatted HTML output
3. Add file writing with naming conventions
4. Handle special characters and encoding
5. Implement scope element feature (class/ID targeting)
6. Add extraction metadata generation (JSON and text summary)

### Phase 3: Link Mode & Image Downloading
1. Implement link extraction module (Link Mode)
2. Add link filtering (internal/external/all)
3. Link metadata collection and JSON output
4. Implement image URL extraction from HTML (Content Mode)
5. Create image downloader module
6. Update content files to reference local images

### Phase 4: Backend API Development
1. Set up Flask/FastAPI application
2. Implement REST API endpoints
3. Add request validation and error handling
4. Implement job queue system (sync or async)
5. Add file download endpoints
6. Implement job history tracking

### Phase 5: CSV Bulk Processing
1. Implement CSV parser and validator
2. Add bulk processing logic
3. Generate aggregate reports for bulk jobs
4. Add progress tracking for bulk operations
5. Handle errors per URL in bulk mode

### Phase 6: React Frontend Development
1. Set up React application structure with Tailwind CSS
2. Configure Tailwind CSS with custom theme and colors
3. Create mode selector component (Content/Link)
4. Build single URL input form with Tailwind styling
5. Implement CSV upload component with drag-and-drop
6. Add progress indicators and real-time updates
7. Create extraction results modal with metadata display:
   - Visual statistics cards (word count, images, etc.)
   - Charts for data visualization
   - Color-coded status badges
   - Expandable sections for details
   - **Failed extraction display**: Show "Extraction Failed" message with specific failure reason
   - Display error type icon and actionable suggestions
   - Include retry button for failed extractions
8. Build results table with metadata previews
9. Implement download interface with file management
10. Build history/dashboard page with filtering
11. Integrate with backend API
12. Add responsive design for mobile devices

### Phase 7: Docker & Deployment
1. Create Dockerfile for backend
2. Create Dockerfile for frontend
3. Write docker-compose.yml configuration
4. Set up .env file structure
5. Configure volume mounts for persistent data
6. Add health checks and logging
7. Document deployment process

### Phase 8: Enhanced CLI Features
1. Add mode selection to CLI
2. Implement link mode CLI arguments
3. Add CSV processing to CLI
4. Enhance interactive mode with new features
5. Add colored output for status messages

### Phase 9: Testing & Documentation
1. Write unit tests for all backend modules
2. Write unit tests for React components
3. Integration testing (API + Frontend)
4. End-to-end testing
5. Create comprehensive README
6. Add inline documentation and docstrings
7. Create API documentation
8. Write deployment guide

## Configuration Options

### Environment Variables (.env)
```bash
# Application Settings
APP_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key-here

# Backend API
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
API_PREFIX=/api

# Frontend
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost:5000/api

# Crawler Settings
DEFAULT_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=Mozilla/5.0 (Web Crawler Bot)
OUTPUT_DIRECTORY=/app/output
MAX_IMAGE_SIZE_MB=10
IMAGE_TIMEOUT=10

# File Upload Limits
MAX_CSV_SIZE_MB=10
MAX_URLS_PER_CSV=10000  # Increased from 1000 to support larger bulk operations

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# Optional: Task Queue (if using Celery)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Optional: Database (if storing job history)
DATABASE_URL=postgresql://user:password@db:5432/webcrawler
```

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: webcrawler-backend
    ports:
      - "${BACKEND_PORT:-5000}:5000"
    volumes:
      - ./output:/app/output
      - ./backend:/app
    environment:
      - FLASK_APP=api/app.py
      - FLASK_ENV=${APP_ENV:-production}
      - SECRET_KEY=${SECRET_KEY}
      - OUTPUT_DIRECTORY=/app/output
      - CORS_ORIGINS=${CORS_ORIGINS}
    env_file:
      - .env
    depends_on:
      - redis
    networks:
      - webcrawler-network
    restart: unless-stopped

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

  redis:
    image: redis:7-alpine
    container_name: webcrawler-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - webcrawler-network
    restart: unless-stopped

  # Optional: PostgreSQL for job history
  # db:
  #   image: postgres:15-alpine
  #   container_name: webcrawler-db
  #   environment:
  #     POSTGRES_USER: webcrawler
  #     POSTGRES_PASSWORD: ${DB_PASSWORD}
  #     POSTGRES_DB: webcrawler
  #   volumes:
  #     - postgres-data:/var/lib/postgresql/data
  #   networks:
  #     - webcrawler-network
  #   restart: unless-stopped

volumes:
  redis-data:
  # postgres-data:

networks:
  webcrawler-network:
    driver: bridge
```

### Backend Dockerfile Example
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /app/output

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
```

### Frontend Dockerfile Example
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

### Default Settings (Python Config)
```python
DEFAULT_CONFIG = {
    # Crawling Mode
    'mode': 'content',  # Options: 'content' or 'link'

    # Output Settings
    'output_formats': ['txt'],  # Default: txt only. Options: ['txt', 'md', 'html'] for content, ['txt', 'json'] for link
    'output_directory': './output/',

    # HTTP Settings
    'timeout': 30,  # Request timeout in seconds
    'user_agent': 'Mozilla/5.0 (Web Crawler Bot)',
    'encoding': 'utf-8',
    'max_retries': 3,  # Retry failed requests

    # Content Mode Settings
    'scope_class': None,  # Target CSS class for scoped extraction
    'scope_id': None,  # Target element ID for scoped extraction
    'download_images': False,  # Download images from the page
    'image_timeout': 10,  # Image download timeout in seconds
    'max_image_size': 10,  # Maximum image size in MB

    # Link Mode Settings
    'link_type': 'all',  # Options: 'all', 'internal', 'external'
    'exclude_anchors': False,  # Exclude anchor links (#section)
    'validate_links': False,  # Check HTTP status of extracted links

    # Bulk Processing Settings
    'max_concurrent_jobs': 5,  # Maximum parallel crawling jobs
    'job_timeout': 300,  # Job timeout in seconds (5 minutes)
}
```

## Error Handling

### Expected Errors
- Invalid URL format
- Network connectivity issues
- HTTP errors (404, 403, 500, etc.)
- Timeout errors
- Encoding issues
- File write permission errors
- Image download failures (404, timeout, invalid format)
- Disk space issues when downloading large images

### Error Messages
- Clear, user-friendly error messages
- Suggestions for resolution
- Logging for debugging purposes
- **Failed Extraction Display**: When extraction fails, display both:
  - "Extraction Failed" message prominently
  - Specific failure reason (e.g., "Network timeout", "404 Not Found", "Invalid URL format", "Element not found", "Permission denied")
  - Include error details in extraction_details.json for programmatic access
  - Show error timestamp and affected URL
  - Provide actionable suggestions when possible (e.g., "Check URL spelling", "Verify network connection", "Ensure element exists")

### Frontend Error Handling Best Practices

When displaying extraction failures in the UI (especially in ResultsModal component):

1. **Use Optional Chaining**: Always use optional chaining (`?.`) when accessing nested error properties
   - Example: `result.failure_info?.failure_reason` instead of `result.failure_info.failure_reason`
   - Prevents runtime errors if the data structure is incomplete

2. **Implement Fallback Chain**: Provide multiple fallback options for error messages
   - Primary: `result.failure_info?.failure_reason` (most specific, from backend error handler)
   - Secondary: `result.error` (generic error message)
   - Tertiary: `"An unknown error occurred"` (last resort default)
   - Example: `{result.failure_info?.failure_reason || result.error || 'An unknown error occurred'}`

3. **Conditional Rendering**: Only render optional error details if they exist
   - Check existence before rendering: `{result.failure_info?.error_type && <ErrorTypeBadge />}`
   - Show suggestions only if array has items: `{result.failure_info?.suggestions?.length > 0 && ...}`
   - Display retry button based on availability: `{(result.failure_info?.retry_possible || !result.failure_info) && ...}`

4. **Safe Array Iteration**: Always check array existence before mapping
   - Example: `{result.failure_info?.suggestions?.map(...)}`
   - Prevents "Cannot read property 'map' of undefined" errors

5. **Provide Defaults**: Use fallback values for missing optional data
   - Error code: `{result.failure_info?.error_code || 'N/A'}`
   - Error type: `{result.failure_info?.error_type || 'Unknown'}`
   - Retry possible: `{result.failure_info?.retry_possible ? 'Yes' : 'No'}`

6. **Debug Logging**: Include console logging for debugging (can be removed in production)
   ```javascript
   console.log('ResultsModal - Full results:', results);
   console.log('ResultsModal - Failure info:', result?.failure_info);
   ```

7. **Graceful Degradation**: UI should work even if backend error structure changes
   - Don't rely on exact property names being present
   - Show as much information as available
   - Never break the UI due to missing error details

**Example Implementation** (ResultsModal.jsx):
```jsx
{result.status === 'failed' && (
  <>
    <p className="text-sm text-error-700 mt-1 font-medium">
      {result.failure_info?.failure_reason || result.error || 'An unknown error occurred'}
    </p>
    {result.failure_info?.error_type && (
      <span className="inline-block mt-2 px-2 py-1 text-xs font-medium rounded-md bg-error-100 text-error-800">
        {result.failure_info.error_type.replace('_', ' ').toUpperCase()}
      </span>
    )}
  </>
)}
```

This ensures users always see meaningful error messages, even if:
- Backend error handling evolves
- Network issues prevent complete error data transmission
- Unexpected error types occur
- Error structure varies between different failure scenarios

## Output Structure and Naming Convention

### Output Structure

#### Content Mode Output (without images):
```
output/
└── example_com_blog_20231215_1430/
    ├── example_com_blog_20231215_1430.txt
    ├── example_com_blog_20231215_1430.md
    ├── extraction_details.json
    └── extraction_summary.txt
```

#### Content Mode Output (with images):
```
output/
└── example_com_blog_20231215_1430/
    ├── example_com_blog_20231215_1430.txt
    ├── example_com_blog_20231215_1430.md
    ├── example_com_blog_20231215_1430.html
    ├── extraction_details.json
    ├── extraction_summary.txt
    ├── image_001.jpg
    ├── image_002.png
    └── logo.svg
```

#### Link Mode Output:
```
output/
└── example_com_20231215_1430/
    ├── example_com_20231215_1430.txt        # Plain text list of URLs
    ├── example_com_20231215_1430.json       # JSON with link metadata (if requested)
    ├── extraction_details.json
    └── extraction_summary.txt
```

### File Naming Pattern:
```
{domain}_{first_url_path_if_exist}_{timestamp}.{extension}
Examples:
- https://example.com → example_com_20231215_1430.txt
- https://example.com/blog/article → example_com_blog_20231215_1430.md
- https://docs.site.org/guide/intro → docs_site_org_guide_20231215_1430.html

Timestamp format: YYYYMMDD_HHMM
```

### Image Naming Pattern:
```
Original filename preserved when possible, with sanitization
Fallback: image_{sequential_number}.{extension}
Examples: logo.png, banner.jpg, image_001.png
```

### User-specified names:
```
{user_input}.{extension}
Example: my_article.md
```

### Metadata Files Examples:

#### extraction_details.json (Content Mode):
```json
{
  "source_url": "https://example.com/blog/article",
  "timestamp": "2023-12-15T14:30:00Z",
  "execution_time_seconds": 3.45,
  "extraction_parameters": {
    "scope_class": "main-content",
    "scope_id": null,
    "output_formats": ["txt", "md", "html"],
    "download_images": true
  },
  "http_response": {
    "status_code": 200,
    "content_type": "text/html; charset=utf-8",
    "final_url": "https://example.com/blog/article"
  },
  "content_statistics": {
    "word_count": 1250,
    "character_count": 7850,
    "image_count": 5,
    "title": "Example Article Title"
  },
  "images": {
    "total_found": 5,
    "successfully_downloaded": 4,
    "failed": 1,
    "image_list": [
      {"url": "https://example.com/img1.jpg", "local_path": "image_001.jpg", "status": "success"},
      {"url": "https://example.com/img2.png", "local_path": "image_002.png", "status": "success"},
      {"url": "https://broken.com/img.jpg", "local_path": null, "status": "failed", "error": "404 Not Found"}
    ]
  },
  "output_files": [
    "example_com_blog_20231215_1430.txt",
    "example_com_blog_20231215_1430.md",
    "example_com_blog_20231215_1430.html"
  ],
  "errors": [],
  "warnings": ["One image failed to download"]
}
```

#### extraction_summary.txt:
```
Extraction Summary
==================

URL: https://example.com/blog/article
Date: 2023-12-15 14:30:00
Execution Time: 3.45 seconds

Extraction Parameters:
- Scope: class="main-content"
- Formats: txt, md, html
- Download Images: Yes

Results:
✓ Content extracted successfully
✓ 1,250 words extracted
✓ 4 of 5 images downloaded successfully
✓ 3 output files generated

Output Files:
- example_com_blog_20231215_1430.txt
- example_com_blog_20231215_1430.md
- example_com_blog_20231215_1430.html

Images:
- image_001.jpg (from https://example.com/img1.jpg)
- image_002.png (from https://example.com/img2.png)

Issues:
⚠ 1 image failed to download: https://broken.com/img.jpg (404 Not Found)

Status: SUCCESS
```

#### extraction_details.json (Link Mode):
```json
{
  "source_url": "https://example.com",
  "timestamp": "2023-12-15T14:35:00Z",
  "execution_time_seconds": 1.23,
  "extraction_parameters": {
    "mode": "link",
    "link_type": "all",
    "exclude_anchors": false,
    "output_formats": ["txt", "json"]
  },
  "http_response": {
    "status_code": 200,
    "content_type": "text/html; charset=utf-8",
    "final_url": "https://example.com"
  },
  "link_statistics": {
    "total_links": 127,
    "internal_links": 89,
    "external_links": 38,
    "unique_domains": 15
  },
  "links": [
    {"url": "https://example.com/about", "text": "About Us", "type": "internal"},
    {"url": "https://example.com/contact", "text": "Contact", "type": "internal"},
    {"url": "https://external-site.com", "text": "External Link", "type": "external"}
  ],
  "output_files": [
    "example_com_20231215_1435.txt",
    "example_com_20231215_1435.json"
  ],
  "errors": [],
  "warnings": []
}
```

#### extraction_summary.txt (Link Mode):
```
Extraction Summary
==================

URL: https://example.com
Date: 2023-12-15 14:35:00
Execution Time: 1.23 seconds
Mode: Link Extraction

Extraction Parameters:
- Link Type: all (internal + external)
- Exclude Anchors: No
- Formats: txt, json

Results:
✓ Links extracted successfully
✓ 127 total links found
✓ 89 internal links
✓ 38 external links
✓ 15 unique external domains
✓ 2 output files generated

Output Files:
- example_com_20231215_1435.txt
- example_com_20231215_1435.json

Status: SUCCESS
```

## Future Enhancements (Optional)
- **Recursive crawling**: Follow links and crawl related pages automatically
- **Advanced content filtering**: Include/exclude specific HTML elements or patterns
- **PDF output format**: Export extracted content as PDF files
- **Database persistence**: Store job history and results in PostgreSQL
- **Authentication & user management**: Multi-user support with login system
- **Scheduled crawling**: Cron-like scheduling for automated recurring crawls
- **Webhook notifications**: Notify external systems when crawling completes
- **Advanced rate limiting**: Configurable delays between requests per domain
- **Robots.txt compliance**: Automatic checking and respecting of robots.txt rules
- **JavaScript rendering**: Use Puppeteer/Playwright for SPA and JS-heavy sites
- **Background image extraction**: Extract images from CSS background-image properties
- **Lazy-loaded image handling**: Detect and download lazy-loaded images
- **Image optimization**: Compress and resize downloaded images
- **Content deduplication**: Detect and skip duplicate content across crawls
- **Export to cloud storage**: Upload results directly to S3, Google Drive, etc.
- **API rate limiting**: Implement API key system with usage quotas
- **Browser extension**: Chrome/Firefox extension for one-click crawling
- **Sitemap generation**: Create XML sitemaps from crawled URLs

## Success Criteria

### Backend & Core Functionality
1. Successfully crawl and extract content from any valid URL in both Content and Link modes
2. Generate clean, readable output in all supported formats:
   - Content Mode: txt (default), md, html (optional)
   - Link Mode: txt (default), json (optional)
3. Accurately extract content from scoped elements (class/ID targeting) in Content Mode
4. Successfully extract and filter links (internal/external/all) in Link Mode
5. Successfully download and save images alongside content (Content Mode)
6. Generate comprehensive extraction metadata (JSON details + text summary)
7. Create organized folder structure for each extraction
8. Process CSV files with multiple URLs in bulk mode
9. Generate aggregate reports for bulk processing jobs
10. Handle errors gracefully without crashes for both single and bulk operations

### API & Integration
11. Fully functional REST API with all endpoints working correctly
12. Real-time job status updates and progress tracking
13. Secure file download endpoints with proper access control
14. CSV upload validation and error reporting
15. Job history tracking and retrieval
16. Proper CORS configuration for frontend-backend communication

### Frontend
17. Intuitive React web interface with responsive Tailwind CSS design
18. Mode selection (Content/Link) working correctly
19. Single URL and CSV bulk upload both functional
20. Real-time progress indicators during crawling
21. **Extraction metadata displayed in frontend immediately after completion**:
    - Visual statistics cards showing content metrics
    - Charts/graphs for data visualization
    - Color-coded status indicators
    - File download buttons for each output
    - Expandable details for full metadata
22. Results display with download functionality
23. Extraction history dashboard showing past jobs with metadata previews
24. Error handling and user-friendly error messages in UI
25. Mobile-responsive design across all screen sizes

### Deployment & Configuration
26. Docker Compose successfully orchestrates all services
27. All sensitive configuration properly stored in .env file
28. Environment variables correctly used in docker-compose.yml
29. Frontend and backend containers communicate properly
30. Persistent data storage for outputs via volume mounts
31. Services start and stop cleanly with proper health checks

### CLI & Developer Experience
32. Intuitive CLI interface with all feature flags (mode, formats, scope, etc.)
33. Interactive CLI mode with guided prompts
34. CSV processing available through CLI
35. Comprehensive documentation (README, API docs, deployment guide)
36. Code coverage > 80% with unit tests for all modules
37. Integration tests for API endpoints
38. End-to-end tests for critical workflows

### Performance & Reliability
39. Execution time < 10 seconds for typical web pages (excluding large image downloads)
40. Bulk processing handles at least 100 URLs without issues
41. Proper error recovery and continuation in bulk mode
42. Rate limiting to avoid overwhelming target servers

## Notes
- Respect robots.txt and website terms of service
- Implement rate limiting to avoid overwhelming servers
- Follow ethical web scraping practices
- Include proper attribution and user-agent identification

## Quick Reference

### Common Commands

#### Docker Operations
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up -d --build

# Check service status
docker-compose ps
```

#### CLI Usage
```bash
# Content mode (default)
python main.py --url https://example.com

# Link mode
python main.py --url https://example.com --mode link --format json

# With scoping and images
python main.py --url https://example.com --class main-content --download-images

# Bulk processing
python main.py --csv urls.csv --output ./results/
```

#### API Endpoints Quick Reference
```
POST   /api/crawl/single          - Start single URL crawl
POST   /api/crawl/bulk            - Start bulk CSV crawl
POST   /api/preview               - Preview page before extraction
GET    /api/job/{id}/status       - Get job status
GET    /api/job/{id}/results      - Get results with metadata
GET    /api/job/{id}/metadata     - Get detailed metadata
GET    /api/download/{id}/{file}  - Download individual output file
GET    /api/download/{id}         - Download all files as ZIP
GET    /api/history               - Get crawl history
DELETE /api/job/{id}              - Delete job and outputs
POST   /api/jobs/saved            - Create saved job
GET    /api/jobs/saved            - List all saved jobs
GET    /api/jobs/saved/{id}       - Get specific saved job
PUT    /api/jobs/saved/{id}       - Update saved job
DELETE /api/jobs/saved/{id}       - Delete saved job
```

### Project URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **Redis**: localhost:6379

### File Locations
- **Output Directory**: `./output/` (host) or `/app/output` (container)
- **Backend Code**: `./backend/`
- **Frontend Code**: `./frontend/`
- **Environment Config**: `.env`
- **Docker Compose**: `docker-compose.yml`

### Key Configuration Files
```
.env                     # Environment variables
docker-compose.yml       # Service orchestration
backend/requirements.txt # Python dependencies
frontend/package.json    # Node dependencies
```

---

## Recent Enhancements (December 2025)

### Phase 6 Improvements
The following major enhancements were added in December 2025:

#### 1. **ZIP Download System** ✨
- Automatic ZIP compression when images are downloaded
- Smart UI that shows single "Download All (ZIP)" button instead of multiple file downloads
- Backend flag `has_images` triggers conditional rendering
- Maintains folder structure in ZIP archives
- Seamless integration with existing download infrastructure

#### 2. **Job History & Management** 📊
- Complete job tracking system with persistent storage
- History page showing all past extractions
- Status indicators (pending, running, completed, failed)
- Progress tracking for bulk operations
- Delete functionality for cleanup
- Results modal for detailed view of each job

#### 3. **Improved Home Page** 🏠
- Dashboard with quick action buttons
- Recent history preview (last 5 jobs)
- Saved jobs preview (last 3 configs)
- Statistics summary at a glance
- Cleaned up UI (removed Platform Features section)
- Fixed spacing and layout issues

#### 4. **Enhanced Results Display** 📈
- Expandable sections for better organization
- Visual statistics cards with icons
- Color-coded status badges
- Smart download UI based on content type
- Execution time tracking
- Comprehensive error display with suggestions

#### 5. **Advanced Error Handling** 🛡️
- User-friendly error messages for all failure types
- Actionable troubleshooting suggestions
- HTTP status code specific guidance
- Retry possibility indicators
- Error categorization (network, HTTP, content, validation, permission)
- Fallback error display chain for robustness

#### 6. **Text Formatting Improvements** 📝
- Proper inline element handling (spans, links)
- Block vs inline element distinction
- Correct Thai text formatting
- Space joining for inline elements
- Preserved paragraph structure

### Key Technical Decisions

#### Why ZIP for Images?
- **UX**: Single click download instead of 10+ individual buttons
- **Organization**: Maintains folder structure and file relationships
- **Practicality**: Necessary for bulk image downloads
- **Simplicity**: Reduces UI clutter in results modal

#### Job Storage Strategy
- JSON file storage for simplicity (`jobs.json`, `saved_jobs.json`)
- No database dependency (easier deployment)
- File-based persistence suitable for single-user scenarios
- Future: Can migrate to SQLite/PostgreSQL if needed

#### Conditional UI Patterns
- Check `has_images` flag to determine download UI
- Fallback chains for error display (`failure_info?.failure_reason ?? error ?? "Unknown"`)
- Optional chaining throughout for robustness
- Console logging for debugging without user exposure

### Future Enhancement Ideas
- [ ] Bulk edit/delete for history items
- [ ] Export history as CSV/JSON
- [ ] Schedule recurring crawls
- [ ] Email notifications for completed jobs
- [ ] Advanced search/filter in history
- [ ] Database migration for multi-user support
- [ ] Image thumbnail previews in results
- [ ] Content diff tracking for re-crawled URLs
- [ ] API key authentication for programmatic access
- [ ] Webhook support for job completion events

---

## Latest Updates (December 26, 2025 - Evening)

### Individual Result ZIP Downloads & Image Authentication 📦🔐

#### 1. **Individual URL Result ZIP Downloads**
- **New Feature**: Each URL result can be downloaded as a complete ZIP package
- **Location**:
  - Backend: [routes.py:440-479](backend/api/routes.py#L440-L479)
  - Frontend: [ResultsModal.jsx:114-126](frontend/src/components/ResultsModal.jsx#L114-L126)
- **Endpoint**: `GET /api/download/<job_id>/<folder_name>/zip`
- **Behavior**:
  - Downloads entire result folder (content + images) as ZIP
  - Files added to ZIP root (not in subfolder)
  - Proper error handling for missing folders
- **Use Cases**:
  - Bulk crawl results - each URL gets its own "Download ZIP" button
  - Ensures all related files (content + images) stay together
  - Single-click download for complete result package

**API Endpoint Details:**
```python
@api_bp.route('/download/<job_id>/<folder_name>/zip', methods=['GET'])
def download_result_folder_zip(job_id, folder_name):
    """Download a specific result folder as zip archive"""
    # 1. Validate job exists
    # 2. Find result folder by name
    # 3. Create temporary ZIP file
    # 4. Add all files from folder to ZIP (at root level)
    # 5. Return ZIP as download
```

**Frontend Implementation:**
```javascript
// ResultsModal.jsx - Bulk crawl result download
<button onClick={() => {
  const folderName = result.output_folder.split(/[/\\]/).pop();
  window.open(`http://localhost:5000/api/download/${jobId}/${folderName}/zip`, '_blank');
}}>
  Download ZIP
</button>
```

#### 2. **Authentication for Image Downloads** 🔐
- **Problem Fixed**: Images on authenticated domains were failing to download
- **Root Cause**: Authentication credentials (cookies/headers) were used for HTML fetch but NOT passed to ImageDownloader
- **Solution**: Modified ImageDownloader to accept and use authentication credentials
- **Location**:
  - ImageDownloader: [image_downloader.py:13-22](backend/crawler/image_downloader.py#L13-L22)
  - Integration: [tasks.py:269-273](backend/api/tasks.py#L269-L273)

**Changes Made:**

**Before:**
```python
class ImageDownloader:
    def __init__(self, timeout: int = 10, max_size_mb: int = 10):
        self.session = requests.Session()
```

**After:**
```python
class ImageDownloader:
    def __init__(self, timeout: int = 10, max_size_mb: int = 10,
                 cookies: dict = None, auth_headers: dict = None):
        self.session = requests.Session()

        # Set up authentication
        if cookies:
            self.session.cookies.update(cookies)
        if auth_headers:
            self.session.headers.update(auth_headers)
```

**Integration in tasks.py:**
```python
# Download images if requested
if crawl_request.download_images and image_urls:
    # Pass authentication to image downloader
    downloader = ImageDownloader(
        cookies=crawl_request.cookies,
        auth_headers=crawl_request.auth_headers
    )
    image_info = downloader.download_all_images(image_urls, output_path, crawl_request.url)
```

**Impact:**
- Images from authenticated domains (like `image-intranet.dtgsiam.com`) now download successfully
- Same authentication used for HTML is applied to image downloads
- Fixes "0 images downloaded" issue for protected content

#### 3. **Enhanced Image Status Display** 📊
- **Improvement**: Frontend now shows successful vs failed image counts
- **Location**: [ResultsModal.jsx:106-114, 371-394](frontend/src/components/ResultsModal.jsx#L106-L114)
- **Features**:
  - **Bulk Results**: Shows `🖼️ 2/3 images` or `⚠️ 3 images (failed)`
  - **Single Results**:
    - Image count card shows `0/1` or `2/3` format
    - Color-coded: Green (success), Orange (failed), Gray (none)
    - Status text: "Images Downloaded" vs "Images (Failed)"
  - **Images Section**: Always shows `X/Y` format (successful/total)

**UI Changes:**

**Bulk Crawl Result Card:**
```jsx
{result.statistics.image_count > 0 && (
  <span>
    {result.metadata?.images?.successful > 0 ? (
      `🖼️ ${result.metadata.images.successful}/${result.statistics.image_count} images`
    ) : (
      `⚠️ ${result.statistics.image_count} images (failed)`
    )}
  </span>
)}
```

**Single Crawl Statistics Card:**
```jsx
<div className={`rounded-lg p-4 border ${
  images.successfully_downloaded > 0
    ? 'bg-success-50 border-success-200'
    : images.total_found > 0
    ? 'bg-warning-50 border-warning-200'
    : 'bg-gray-50 border-gray-200'
}`}>
  <FiImage className={/* color based on status */} />
  <p className="text-2xl font-bold text-gray-900">
    {images.successfully_downloaded || 0}
    {images.total_found > 0 && `/${images.total_found}`}
  </p>
  <p className="text-sm text-gray-600">
    {images.successfully_downloaded > 0
      ? 'Images Downloaded'
      : images.total_found > 0
      ? 'Images (Failed)'
      : 'Images'}
  </p>
</div>
```

#### 4. **API Documentation Update** 📖
- **Updated**: [routes.py:20-36](backend/api/routes.py#L20-L36)
- **New Endpoints Documented**:
  - `GET /api/download/<job_id>/<folder_name>/zip` - Download result folder as ZIP
  - `GET /api/download/<job_id>` - Download all results as ZIP
- **Endpoint Summary**:
  ```
  GET /api/download/{job_id}/{filename}        - Download individual file
  GET /api/download/{job_id}/{folder_name}/zip - Download folder as ZIP (NEW)
  GET /api/download/{job_id}                   - Download all job results as ZIP
  ```

### Technical Implementation Details

#### ZIP Archive Creation Pattern
```python
# backend/api/routes.py
import tempfile
import zipfile

temp_dir = Path(tempfile.gettempdir())
zip_path = temp_dir / f'{folder_name}.zip'

with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in target_folder.iterdir():
        if file.is_file():
            # Add files directly to root of zip (not in subfolder)
            zipf.write(str(file), file.name)

return send_file(
    str(zip_path),
    as_attachment=True,
    download_name=f'{folder_name}.zip',
    mimetype='application/zip'
)
```

#### Authentication Flow for Images
```
1. User submits crawl with cookies/headers
2. HTML fetched with authentication ✓
3. Images extracted from HTML
4. ImageDownloader created WITH same cookies/headers
5. Each image downloaded with authentication ✓
6. Images saved to output folder
7. Image list added to output_files array
8. ZIP includes both content and images
```

#### Frontend Download Logic
```javascript
// Extract folder name from output_folder path
const folderName = result.output_folder.split(/[/\\]/).pop();

// Call ZIP download endpoint
window.open(`http://localhost:5000/api/download/${jobId}/${folderName}/zip`, '_blank');
```

### User Experience Improvements

#### Before These Changes:
**Problem 1 - Bulk Results Download:**
- ❌ Error: "File not found" when downloading
- ❌ Frontend was passing folder name instead of filename
- ❌ Backend couldn't find file

**Problem 2 - Image Downloads:**
- ❌ Images from authenticated domains failed (0/1 downloaded)
- ❌ ZIP was empty (no images included)
- ❌ Misleading UI showed "1 images" but none downloaded

#### After These Changes:
**Solution 1 - Individual ZIP Downloads:**
- ✅ Each URL result has "Download ZIP" button
- ✅ ZIP contains ALL files (content + images)
- ✅ One-click download for complete package
- ✅ Works for both single and bulk crawl results

**Solution 2 - Authenticated Image Downloads:**
- ✅ Images download successfully with authentication
- ✅ ZIP includes all downloaded images
- ✅ Clear status display: "2/3 images" (2 succeeded, 1 failed)
- ✅ Color-coded indicators (green=success, orange=failed)

### Configuration & Deployment

**No configuration changes required** - works out of the box with existing setup.

**Backward Compatibility:**
- ✅ Existing download endpoints unchanged
- ✅ Old jobs/results still work
- ✅ No database migration needed
- ✅ Frontend gracefully handles missing data

**Testing Checklist:**
- [x] Individual URL ZIP download works
- [x] ZIP contains all content files
- [x] ZIP contains all successfully downloaded images
- [x] Authentication passed to image downloads
- [x] Images from authenticated domains download
- [x] UI shows correct success/failed counts
- [x] Color-coded image status cards
- [x] Bulk crawl results show download buttons
- [x] Single crawl results work correctly

### File Structure in ZIP

**Example ZIP Contents:**
```
7244_intranet_dtgo_com_Whats-New_20251226_1346.zip
├── intranet_dtgo_com_Whats-New_20251226_1346.txt
├── extraction_details.json
├── extraction_summary.txt
├── news-sep-23-2016.jpg          (if downloaded successfully)
└── logo.png                       (if downloaded successfully)
```

**Note**: Files are at ZIP root level, not in a subfolder for convenience.

### Related Endpoints

**Download Endpoints Summary:**
```python
# Single file download (unchanged)
GET /api/download/<job_id>/<filename>
→ Returns: Single file (content.txt, content.md, etc.)

# Individual folder ZIP (NEW)
GET /api/download/<job_id>/<folder_name>/zip
→ Returns: ZIP of all files in specific result folder

# All job results ZIP (unchanged)
GET /api/download/<job_id>
→ Returns: ZIP of all folders and files for entire job
```

### Future Enhancement Ideas

- [ ] Progress indicator for large ZIP creation
- [ ] Selective file inclusion in ZIP (user picks files)
- [ ] ZIP compression level configuration
- [ ] Background ZIP creation for very large result sets
- [ ] Email notification when ZIP is ready
- [ ] Download queue for multiple concurrent ZIP requests
- [ ] ZIP preview before download (file list)
- [ ] Automatic cleanup of temporary ZIP files

---

## Recent Improvements (December 26, 2025)

### Bulk Crawling Enhancements 🚀

#### 1. **Increased URL Limit**
- **Changed**: MAX_URLS_PER_CSV from 1,000 to 10,000 URLs
- **Location**: [.env](.env#L25) and [.env.example](.env.example#L25)
- **Reason**: Support larger bulk crawling operations (e.g., 7,244 URLs)
- **Impact**: Users can now process significantly larger CSV files
- **Configurable**: Administrators can adjust limit via environment variable

#### 2. **Comprehensive Error Alerting System** 🛡️
- **New Feature**: Prominent error alert banner with actionable guidance
- **Location**: [Crawler.jsx](frontend/src/pages/Crawler.jsx#L218-L274)
- **Components**:
  - Red alert box with warning icon
  - Clear "Cannot Start Crawl" heading
  - Specific error message display
  - Context-aware help sections for common errors:
    - **Too many URLs**: Shows current limit and how to increase it
    - **Invalid file type**: Explains CSV requirement
    - **Empty CSV**: Reminds to include URLs
  - Dismissible with button
  - Auto-clears on new crawl attempt

#### 3. **Enhanced Backend Error Messages** 📝
- **Improved**: All bulk crawl error messages now include detailed context
- **Location**: [routes.py](backend/api/routes.py#L120-L205)
- **Examples**:
  - Old: `"Too many URLs"`
  - New: `"Too many URLs: Your CSV contains 7,244 URLs, but the maximum allowed is 10,000. Please reduce the number of URLs or contact your administrator to increase the limit."`
  - Old: `"File must be a CSV"`
  - New: `"Invalid file type: \"intranet_bulk_content.xlsx\". Only CSV files (.csv) are supported."`
- **Benefits**: Users understand exactly what went wrong and how to fix it

#### 4. **CSV Format Help Tooltip** 💡
- **Feature**: CSV examples hidden behind help icon (?) with hover tooltip
- **Location**: [CSVUpload.jsx](frontend/src/components/CSVUpload.jsx)
- **UI Changes**:
  - Previously: All CSV examples always visible (cluttered UI)
  - Now: Clean label with help icon → hover to see examples
  - Tooltip features:
    - 600px wide popup with all CSV format examples
    - Scrollable content (max 400px height)
    - Text selection enabled for copying examples
    - 200ms hover delay prevents accidental closing
    - Stays open when moving mouse to tooltip content
- **Benefits**: Cleaner interface, examples available when needed

#### 5. **Detailed Backend Logging** 🔍
- **Enhancement**: Comprehensive logging throughout bulk crawl process
- **Location**: [routes.py](backend/api/routes.py#L120-L210)
- **Log Points**:
  - File reception and validation
  - CSV parsing progress
  - Global authentication application
  - URL limit checking
  - Job creation
  - Each step success/failure
- **Format**: Emoji-prefixed logs for easy scanning (📁 📋 🔐 ✅ ❌)
- **Purpose**: Easier debugging of bulk crawl issues

#### 6. **Git Security Hardening** 🔒
- **Updated**: [.gitignore](.gitignore) with comprehensive exclusions
- **Protected Files/Directories**:
  - **Secrets**: `.env`, `.env.local`, `.env.*.local`
  - **Output**: `output/`, `bulk_output/` (crawled content)
  - **Uploads**: `temp_uploads/`, `backend/temp_uploads/` (CSV files)
  - **Job Data**: `*.json` job history files (contain URLs)
  - **Build**: `node_modules/`, `frontend/build/`
  - **Logs**: `*.log`, `logs/`
- **Safe to Commit**: `.env.example`, source code, Docker configs
- **Documentation**: Pre-commit checklist in .gitignore comments

### Technical Implementation Details

#### Error Alert State Management
```javascript
// Crawler.jsx
const [errorAlert, setErrorAlert] = useState(null);

// Structure:
{
  message: string,      // Main error message
  details: object,      // Optional additional details
  type: 'error'         // Alert type
}
```

#### CSV Tooltip Component Pattern
```javascript
// CSVUpload.jsx
const [showTooltip, setShowTooltip] = useState(false);
const [hideTimeout, setHideTimeout] = useState(null);

// 200ms delay before hiding allows mouse movement to tooltip
const handleMouseLeave = () => {
  const timeout = setTimeout(() => {
    setShowTooltip(false);
  }, 200);
  setHideTimeout(timeout);
};
```

#### Backend Logging Pattern
```python
# routes.py
logger.info(f"📁 Received file: {file.filename}")
logger.info(f"✅ Parsed {len(crawl_params)} URLs from CSV")
logger.error(f"❌ CSV validation failed: {error}")
```

### Configuration Changes

#### Environment Variables (.env)
```bash
# Before:
MAX_URLS_PER_CSV=1000

# After:
MAX_URLS_PER_CSV=10000
```

#### Git Ignore Additions
```gitignore
# Added protection for:
temp_uploads/              # CSV file uploads
backend/temp_uploads/
job_history.json          # Job tracking data
backend/job_history.json
```

### User Experience Improvements

#### Before vs After

**Bulk Crawl with 7,244 URLs:**
- **Before**:
  - Error: "400 Bad Request"
  - User confused, no guidance
  - Generic console error

- **After**:
  - Prominent red alert: "Cannot Start Crawl"
  - Specific message: "Your CSV contains 7,244 URLs, but the maximum allowed is 10,000"
  - Help section: "How to fix this..."
  - Clear action items

**CSV Format Help:**
- **Before**:
  - 8 example boxes always visible
  - Takes up ~40% of form space
  - Overwhelming for experienced users

- **After**:
  - Single help icon (?)
  - Hover to see all examples
  - Clean, minimal UI
  - Copy-paste friendly

### Migration Notes

**For Existing Deployments:**

1. **Update .env**:
   ```bash
   # Edit .env file
   MAX_URLS_PER_CSV=10000  # Or your preferred limit
   ```

2. **Restart Backend**:
   ```bash
   docker compose restart backend
   ```

3. **Clear Browser Cache** (if needed):
   - Frontend changes require browser refresh
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

4. **Verify .gitignore**:
   ```bash
   # Check that sensitive files are ignored
   git status
   # Should NOT show: .env, output/, temp_uploads/, *.json
   ```

### Testing Checklist

- [x] Bulk crawl with 7,244 URLs succeeds
- [x] Error alert displays for invalid CSV
- [x] Error alert displays for file > URL limit
- [x] CSV help tooltip shows on hover
- [x] Tooltip stays open when mouse moves to it
- [x] Backend logs show detailed progress
- [x] .env is excluded from git
- [x] output/ directory excluded from git
- [x] temp_uploads/ excluded from git
- [x] Job history files excluded from git

### Performance Considerations

**URL Limit Increase:**
- **Memory**: ~10KB per URL in CSV (negligible for 10K URLs)
- **Processing**: Linear time complexity (acceptable for 10K)
- **Recommendation**: Monitor memory usage if increasing beyond 50K URLs

**Error Alert:**
- **Render Cost**: Minimal (single conditional render)
- **State Updates**: One setState call per error
- **Performance**: No noticeable impact

**CSV Tooltip:**
- **Render**: Only when shown (no constant overhead)
- **Memory**: ~2KB for tooltip content
- **Performance**: Negligible impact

### Future Enhancement Ideas

- [ ] Configurable URL limit via UI (admin panel)
- [ ] Bulk crawl progress indicator (X of Y URLs)
- [ ] CSV validation before upload (client-side)
- [ ] Error log export feature
- [ ] Batch retry for failed URLs
- [ ] CSV template download button
- [ ] URL limit warning at 80% threshold
- [ ] Compression for large CSV uploads

---

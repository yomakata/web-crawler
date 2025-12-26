"""API routes and endpoints"""
import os
import json
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import shutil

from api.models import CrawlRequest, job_store, saved_job_store
from api.tasks import crawl_single_url, crawl_bulk_urls
from utils.validators import URLValidator
from utils.csv_processor import CSVProcessor
from utils.logger import get_logger

logger = get_logger('routes')

api_bp = Blueprint('api', __name__)


@api_bp.route('/docs')
def api_docs():
    """API documentation"""
    return {
        'endpoints': {
            'POST /api/crawl/single': 'Crawl a single URL',
            'POST /api/crawl/bulk': 'Upload CSV and crawl multiple URLs',
            'GET /api/job/<job_id>/status': 'Get job status',
            'GET /api/job/<job_id>/results': 'Get job results',
            'GET /api/job/<job_id>/metadata': 'Get extraction metadata',
            'GET /api/download/<job_id>/<filename>': 'Download output file',
            'GET /api/download/<job_id>/<folder_name>/zip': 'Download result folder as ZIP',
            'GET /api/download/<job_id>': 'Download all results as ZIP',
            'GET /api/history': 'Get crawling history',
            'DELETE /api/job/<job_id>': 'Delete job and outputs'
        }
    }


@api_bp.route('/crawl/single', methods=['POST'])
def crawl_single():
    """
    Crawl a single URL
    
    Request body:
    {
        "url": "https://example.com",
        "mode": "content",  // or "link"
        "formats": ["txt", "md"],
        "scope_class": "main-content",  // optional
        "scope_id": null,  // optional
        "download_images": true,  // optional
        "link_type": "all",  // optional: "all", "internal", "external"
        "exclude_anchors": false,  // optional
        "cookies": {"session_id": "abc123"},  // optional: cookies for authentication
        "auth_headers": {"Authorization": "Bearer token"},  // optional: custom auth headers
        "basic_auth_username": "user",  // optional: HTTP Basic Auth username
        "basic_auth_password": "pass"  // optional: HTTP Basic Auth password
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Create crawl request
        crawl_req = CrawlRequest(
            url=data.get('url', ''),
            mode=data.get('mode', 'content'),
            formats=data.get('formats', ['txt']),
            scope_class=data.get('scope_class'),
            scope_id=data.get('scope_id'),
            download_images=data.get('download_images', False),
            link_type=data.get('link_type', 'all'),
            exclude_anchors=data.get('exclude_anchors', False),
            cookies=data.get('cookies'),
            auth_headers=data.get('auth_headers'),
            basic_auth_username=data.get('basic_auth_username'),
            basic_auth_password=data.get('basic_auth_password')
        )
        
        # Validate request
        is_valid, errors = crawl_req.validate()
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Validate URL
        if not URLValidator.is_http_url(crawl_req.url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Create job
        job = job_store.create_job(total_urls=1, crawl_type='single')
        
        # Execute crawl
        output_dir = os.getenv('OUTPUT_DIRECTORY', './output')
        result = crawl_single_url(crawl_req, output_dir, job)
        
        return jsonify({
            'job_id': job.job_id,
            'status': job.status,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/crawl/bulk', methods=['POST'])
def crawl_bulk():
    """
    Upload CSV and crawl multiple URLs
    
    Form data:
    - file: CSV file with columns: url, mode, scope_class, format, download_images
    - global_auth_enabled: Whether to apply global authentication (optional)
    - auth_method: 'cookies', 'headers', or 'basic' (optional)
    - cookies: Cookie string for authentication (optional)
    - auth_headers: JSON string of auth headers (optional)
    - basic_auth_username: HTTP Basic Auth username (optional)
    - basic_auth_password: HTTP Basic Auth password (optional)
    """
    try:
        if 'file' not in request.files:
            logger.error("❌ Bulk crawl error: No file in request.files")
            return jsonify({'error': 'No file provided. Please select a CSV file to upload.'}), 400

        file = request.files['file']
        logger.info(f"📁 Received file: {file.filename}")

        if file.filename == '':
            logger.error("❌ Bulk crawl error: Empty filename")
            return jsonify({'error': 'No file selected. Please choose a CSV file to upload.'}), 400

        if not file.filename.endswith('.csv'):
            logger.error(f"❌ Bulk crawl error: Invalid file type - {file.filename}")
            return jsonify({'error': f'Invalid file type: "{file.filename}". Only CSV files (.csv) are supported.'}), 400

        # Get bulk crawl options from form data
        combine_results = request.form.get('combine_results', 'false').lower() == 'true'
        global_auth_enabled = request.form.get('global_auth_enabled', 'false').lower() == 'true'
        global_auth = None

        logger.info(f"🔍 Bulk crawl - combine_results: {combine_results}")
        logger.info(f"🔍 Bulk crawl - global_auth_enabled: {global_auth_enabled}")

        if global_auth_enabled:
            auth_method = request.form.get('auth_method', 'cookies')
            cookies_raw = request.form.get('cookies')
            auth_headers_raw = request.form.get('auth_headers')

            logger.info(f"🔍 Bulk crawl - auth_method: {auth_method}")
            logger.info(f"🔍 Bulk crawl - cookies_raw: {cookies_raw[:100] if cookies_raw else 'None'}...")
            logger.info(f"🔍 Bulk crawl - auth_headers_raw: {auth_headers_raw[:100] if auth_headers_raw else 'None'}...")

            global_auth = {
                'auth_method': auth_method,
                'cookies': cookies_raw,
                'auth_headers': auth_headers_raw,
                'basic_auth_username': request.form.get('basic_auth_username'),
                'basic_auth_password': request.form.get('basic_auth_password')
            }

        # Save uploaded file temporarily
        upload_dir = Path('./temp_uploads')
        upload_dir.mkdir(exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = upload_dir / filename
        logger.info(f"💾 Saving file to: {filepath}")
        file.save(str(filepath))
        logger.info(f"✅ File saved successfully, size: {filepath.stat().st_size} bytes")

        # Validate CSV
        processor = CSVProcessor()
        logger.info(f"🔍 Validating CSV file...")
        is_valid, error = processor.validate_csv(str(filepath))

        if not is_valid:
            logger.error(f"❌ CSV validation failed: {error}")
            filepath.unlink()  # Delete temp file
            return jsonify({'error': error}), 400

        logger.info(f"✅ CSV validation passed")

        # Parse CSV
        logger.info(f"📋 Parsing CSV file...")
        crawl_params = processor.parse_csv(str(filepath))
        logger.info(f"✅ Parsed {len(crawl_params)} URLs from CSV")

        # Apply global authentication if enabled
        if global_auth:
            logger.info(f"🔐 Applying global authentication to {len(crawl_params)} URLs...")
            for params in crawl_params:
                # Only apply global auth if row doesn't have auth_enabled
                if not params.get('auth_enabled'):
                    params['global_auth'] = global_auth
            logger.info(f"✅ Global authentication applied")

        # Check URL limit
        max_urls = int(os.getenv('MAX_URLS_PER_CSV', 1000))
        logger.info(f"🔍 Checking URL limit: {len(crawl_params)} / {max_urls}")
        if len(crawl_params) > max_urls:
            logger.error(f"❌ Too many URLs: {len(crawl_params)} > {max_urls}")
            filepath.unlink()
            return jsonify({
                'error': f'Too many URLs: Your CSV contains {len(crawl_params):,} URLs, but the maximum allowed is {max_urls:,}. Please reduce the number of URLs or contact your administrator to increase the limit.'
            }), 400

        # Create job
        logger.info(f"📝 Creating job for {len(crawl_params)} URLs...")
        job = job_store.create_job(total_urls=len(crawl_params), crawl_type='bulk', csv_filename=filename)
        logger.info(f"✅ Job created: {job.job_id}")

        # Execute bulk crawl in background thread
        output_dir = os.getenv('OUTPUT_DIRECTORY', './output')

        import threading
        def background_crawl():
            try:
                crawl_bulk_urls(crawl_params, output_dir, job, combine_results=combine_results)
            finally:
                # Clean up temp file after crawling
                try:
                    filepath.unlink()
                except:
                    pass

        thread = threading.Thread(target=background_crawl, daemon=True)
        thread.start()

        # Return immediately with job_id so frontend can start polling
        return jsonify({
            'job_id': job.job_id,
            'status': 'running',  # Job is now running in background
            'total_urls': len(crawl_params),
            'message': f'Processing {len(crawl_params)} URLs'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Bulk crawl error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@api_bp.route('/job/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get job status and progress"""
    job = job_store.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'job_id': job.job_id,
        'status': job.status,
        'progress': round((job.completed_urls / job.total_urls * 100)) if job.total_urls > 0 else 0,
        'completed': job.completed_urls,
        'failed': job.failed_urls,
        'total': job.total_urls,
        'current_url': job.current_url,
        'created_at': job.created_at.isoformat(),
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None
    }), 200


@api_bp.route('/job/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """Get job results with metadata"""
    job = job_store.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job.to_dict()), 200


@api_bp.route('/job/<job_id>/metadata', methods=['GET'])
def get_job_metadata(job_id):
    """Get detailed extraction metadata for display"""
    job = job_store.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if not job.results:
        return jsonify({'error': 'No results available yet'}), 404
    
    # Load extraction_details.json for first result
    first_result = job.results[0]
    output_folder = first_result.get('output_folder')
    
    if not output_folder:
        return jsonify({'error': 'Output folder not found'}), 404
    
    details_file = Path(output_folder) / 'extraction_details.json'
    
    if not details_file.exists():
        return jsonify({'error': 'Metadata file not found'}), 404
    
    with open(details_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    return jsonify(metadata), 200


@api_bp.route('/download/<job_id>/<filename>', methods=['GET'])
def download_file(job_id, filename):
    """Download specific output file"""
    job = job_store.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Find the output folder
    output_folder = None
    for result in job.results:
        if result.get('output_folder'):
            folder_path = Path(result['output_folder'])
            file_path = folder_path / filename
            
            if file_path.exists():
                output_folder = folder_path
                break
    
    if not output_folder:
        return jsonify({'error': 'File not found'}), 404
    
    file_path = output_folder / filename
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(str(file_path), as_attachment=True, download_name=filename)


@api_bp.route('/output/<path:filepath>', methods=['GET'])
def serve_output_file(filepath):
    """Serve output files for viewing (e.g., debug HTML)"""
    from flask import current_app, request
    import os
    
    # Get output directory from environment or use default
    output_dir = os.environ.get('OUTPUT_DIRECTORY', '/app/output')
    file_path = Path(output_dir) / filepath
    
    # Security check: ensure the file is within output directory
    try:
        file_path = file_path.resolve()
        output_dir_resolved = Path(output_dir).resolve()
        if not str(file_path).startswith(str(output_dir_resolved)):
            return jsonify({'error': 'Invalid file path'}), 403
    except:
        return jsonify({'error': 'Invalid file path'}), 400
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    # Check if raw mode is requested (HTML source view)
    raw_mode = request.args.get('raw', 'false').lower() == 'true'
    
    # For HTML files in raw mode, show source code with syntax highlighting
    if file_path.suffix == '.html' and raw_mode:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Escape HTML to show as plain text with basic styling
        import html
        escaped_html = html.escape(html_content)
        
        # Wrap in a simple viewer with syntax highlighting
        viewer_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML Source - {file_path.name}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
        }}
        .header {{
            background-color: #252526;
            padding: 15px 20px;
            margin: -20px -20px 20px -20px;
            border-bottom: 1px solid #3e3e42;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header h1 {{
            margin: 0;
            font-size: 16px;
            color: #cccccc;
            font-weight: 500;
        }}
        .header .info {{
            margin-top: 5px;
            font-size: 12px;
            color: #858585;
        }}
        pre {{
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .line-numbers {{
            display: inline-block;
            width: 50px;
            color: #858585;
            text-align: right;
            padding-right: 15px;
            border-right: 1px solid #3e3e42;
            margin-right: 15px;
            user-select: none;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 HTML Source Code</h1>
        <div class="info">File: {file_path.name} | Size: {len(html_content):,} bytes</div>
    </div>
    <pre><code>{escaped_html}</code></pre>
</body>
</html>"""
        
        return viewer_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    
    # Determine mime type for normal preview mode
    mime_type = 'text/html' if file_path.suffix == '.html' else 'application/octet-stream'
    
    return send_file(str(file_path), mimetype=mime_type)



@api_bp.route('/download/<job_id>/<folder_name>/zip', methods=['GET'])
def download_result_folder_zip(job_id, folder_name):
    """Download a specific result folder as zip archive"""
    job = job_store.get_job(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    # Find the result with matching folder name
    target_folder = None
    for result in job.results:
        output_folder = result.get('output_folder')
        if output_folder:
            folder_path = Path(output_folder)
            if folder_path.name == folder_name and folder_path.exists():
                target_folder = folder_path
                break

    if not target_folder:
        return jsonify({'error': 'Result folder not found'}), 404

    # Create zip archive
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


@api_bp.route('/download/<job_id>', methods=['GET'])
def download_job_archive(job_id):
    """Download all job outputs as zip archive"""
    job = job_store.get_job(job_id)

    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if not job.results:
        return jsonify({'error': 'No results to download'}), 404

    # Create zip archive
    import tempfile
    import zipfile

    temp_dir = Path(tempfile.gettempdir())
    zip_path = temp_dir / f'job_{job_id}.zip'

    with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
        for result in job.results:
            output_folder = result.get('output_folder')
            if output_folder and Path(output_folder).exists():
                folder_path = Path(output_folder)
                for file in folder_path.iterdir():
                    if file.is_file():
                        arcname = f"{folder_path.name}/{file.name}"
                        zipf.write(str(file), arcname)

    return send_file(
        str(zip_path),
        as_attachment=True,
        download_name=f'crawl_results_{job_id}.zip',
        mimetype='application/zip'
    )


@api_bp.route('/history', methods=['GET'])
def get_history():
    """Get extraction history"""
    limit = request.args.get('limit', 100, type=int)
    
    jobs = job_store.get_all_jobs(limit=limit)
    
    history = []
    for job in jobs:
        # Get first result to extract info
        first_result = job.results[0] if job.results else {}
        
        # Get failure reason if job failed
        failure_reason = None
        if job.status == 'failed' and job.results:
            for result in job.results:
                if result.get('status') == 'failed':
                    # Try to get detailed failure reason
                    failure_info = result.get('failure_info', {})
                    failure_reason = failure_info.get('failure_reason') or result.get('error', 'Unknown error')
                    break
        
        history.append({
            'job_id': job.job_id,
            'status': job.status,
            'timestamp': job.created_at.isoformat(),  # Frontend expects 'timestamp'
            'mode': first_result.get('mode', 'content'),
            'urls_count': job.total_urls,
            'failure_reason': failure_reason,  # Add failure reason for display
            'crawl_type': job.crawl_type,  # Add crawl type (single/bulk)
            'csv_filename': job.csv_filename  # Add CSV filename for bulk crawls
        })
    
    # Return array directly, not wrapped in object
    return jsonify(history), 200


@api_bp.route('/job/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete job and its output files"""
    job = job_store.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Delete output folders
    for result in job.results:
        output_folder = result.get('output_folder')
        if output_folder and Path(output_folder).exists():
            try:
                shutil.rmtree(output_folder)
            except Exception as e:
                print(f"Error deleting folder {output_folder}: {e}")
    
    # Delete job from store
    job_store.delete_job(job_id)
    
    return jsonify({
        'success': True,
        'message': f'Job {job_id} deleted successfully'
    }), 200


@api_bp.route('/preview', methods=['POST'])
def preview_page():
    """
    Preview a page before extraction
    
    Request body:
    {
        "url": "https://example.com",
        "scope_class": "main-content",  // optional
        "scope_id": null,  // optional
        "cookies": {"session_id": "abc123"},  // optional
        "auth_headers": {"Authorization": "Bearer token"},  // optional
        "basic_auth_username": "user",  // optional
        "basic_auth_password": "pass"  // optional
    }
    
    Returns:
    {
        "success": true,
        "url": "https://example.com",
        "title": "Page Title",
        "status_code": 200,
        "content_length": 12345,
        "has_scope_element": true,
        "scope_element_preview": "First 500 chars of scoped content...",
        "available_classes": ["class1", "class2", ...],
        "page_preview": "First 1000 chars of full page..."
    }
    """
    try:
        from crawler.fetcher import WebFetcher
        from bs4 import BeautifulSoup
        
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data.get('url')
        scope_class = data.get('scope_class')
        scope_id = data.get('scope_id')
        cookies = data.get('cookies')
        auth_headers = data.get('auth_headers')
        basic_auth_username = data.get('basic_auth_username')
        basic_auth_password = data.get('basic_auth_password')
        
        # Validate URL
        if not URLValidator.is_http_url(url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Set up authentication
        basic_auth = None
        if basic_auth_username:
            basic_auth = (basic_auth_username, basic_auth_password or '')
        
        # Fetch the page
        fetcher = WebFetcher(cookies=cookies, auth_headers=auth_headers)
        response = fetcher.fetch(url, basic_auth=basic_auth)
        
        if not response or not response.text:
            return jsonify({'error': 'Failed to fetch page - empty response'}), 400
        
        html = response.text
        
        # Parse the page
        soup = BeautifulSoup(html, 'lxml')
        
        # Get page title
        title = soup.title.string if soup.title else 'No title'
        
        # Get available classes (top 50 most common)
        all_classes = []
        for element in soup.find_all(class_=True):
            all_classes.extend(element.get('class', []))
        
        from collections import Counter
        class_counts = Counter(all_classes)
        available_classes = [cls for cls, _ in class_counts.most_common(50)]
        
        # Check if scope element exists
        has_scope_element = False
        scope_element_preview = None
        scope_element_info = None
        
        if scope_class:
            scope_element = soup.find(class_=scope_class)
            if scope_element:
                has_scope_element = True
                # Use ContentParser to get properly formatted text
                from crawler.parser import ContentParser
                parser = ContentParser(html, url)
                scope_text = parser.extract_text(scope_element)
                scope_element_preview = scope_text[:500] + ('...' if len(scope_text) > 500 else '')
                scope_element_info = {
                    'tag': scope_element.name,
                    'text_length': len(scope_text),
                    'has_children': len(list(scope_element.children)) > 1
                }
        elif scope_id:
            scope_element = soup.find(id=scope_id)
            if scope_element:
                has_scope_element = True
                # Use ContentParser to get properly formatted text
                from crawler.parser import ContentParser
                parser = ContentParser(html, url)
                scope_text = parser.extract_text(scope_element)
                scope_element_preview = scope_text[:500] + ('...' if len(scope_text) > 500 else '')
                scope_element_info = {
                    'tag': scope_element.name,
                    'text_length': len(scope_text),
                    'has_children': len(list(scope_element.children)) > 1
                }
        
        # Get full page HTML for preview
        # We'll send the full HTML so it can be rendered in an iframe
        page_html = html
        
        # Also get text preview for fallback
        body = soup.body if soup.body else soup
        page_text = body.get_text(strip=True)
        page_text_preview = page_text[:1000] + ('...' if len(page_text) > 1000 else '')
        
        # Get page statistics
        stats = {
            'total_elements': len(soup.find_all()),
            'total_links': len(soup.find_all('a')),
            'total_images': len(soup.find_all('img')),
            'total_paragraphs': len(soup.find_all('p')),
            'content_length': len(html),
            'text_length': len(page_text)
        }
        
        return jsonify({
            'success': True,
            'url': url,
            'title': title,
            'status_code': 200,
            'has_scope_element': has_scope_element,
            'scope_element_preview': scope_element_preview,
            'scope_element_info': scope_element_info,
            'available_classes': available_classes,
            'page_html': page_html,  # Full HTML for rendering
            'page_text_preview': page_text_preview,  # Text fallback
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500


@api_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'message': f'Maximum file size is {os.getenv("MAX_CSV_SIZE_MB", 10)}MB'
    }), 413


# ==================== Saved Jobs Endpoints ====================

@api_bp.route('/jobs/saved', methods=['POST'])
def create_saved_job():
    """
    Save a job configuration for reuse
    
    Request body:
    {
        "name": "My Intranet Crawler",
        "description": "Daily news extraction",
        "input_method": "single",
        "mode": "content",
        "url": "https://example.com",
        "formats": ["txt", "md"],
        "scope_class": "content-section",
        "auth_method": "cookies",
        "cookies": "session=abc123",
        "force_update": false,  // optional: set to true to update existing job
        ...
    }
    """
    try:
        data = request.get_json()
        print(f"=== Received saved job data ===")
        print(f"Name: {data.get('name')}")
        print(f"Description: {data.get('description')}")
        print(f"URL: {data.get('url')}")
        print(f"Mode: {data.get('mode')}")
        print(f"Formats: {data.get('formats')}")
        print(f"Scope class: {data.get('scope_class')}")
        print(f"Auth method: {data.get('auth_method')}")
        print(f"Full data keys: {list(data.keys())}")
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Job name is required'
            }), 400
        
        # Check for duplicate name
        existing_job = saved_job_store.find_by_name(data['name'])
        force_update = data.pop('force_update', False)
        
        if existing_job and not force_update:
            return jsonify({
                'success': False,
                'error': 'duplicate_name',
                'message': f'A job with name "{data["name"]}" already exists',
                'existing_job_id': existing_job.saved_job_id,
                'existing_job': existing_job.to_dict()
            }), 409  # 409 Conflict
        
        # If force_update is true and job exists, update it
        if existing_job and force_update:
            updated_job = saved_job_store.update_job(existing_job.saved_job_id, data)
            return jsonify({
                'success': True,
                'message': 'Job updated successfully',
                'saved_job': updated_job.to_dict(),
                'updated': True
            }), 200
        
        # Create new job
        saved_job = saved_job_store.create_job(data)
        
        return jsonify({
            'success': True,
            'message': 'Job saved successfully',
            'saved_job': saved_job.to_dict(),
            'updated': False
        }), 201
        
    except Exception as e:
        print(f"Error saving job: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/jobs/saved', methods=['GET'])
def list_saved_jobs():
    """Get all saved jobs"""
    try:
        jobs = saved_job_store.get_all_jobs()
        return jsonify({
            'success': True,
            'saved_jobs': [job.to_dict() for job in jobs],
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/jobs/saved/<saved_job_id>', methods=['GET'])
def get_saved_job(saved_job_id):
    """Get a specific saved job"""
    try:
        job = saved_job_store.get_job(saved_job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Saved job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'saved_job': job.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/jobs/saved/<saved_job_id>', methods=['PUT'])
def update_saved_job(saved_job_id):
    """Update a saved job"""
    try:
        data = request.get_json()
        job = saved_job_store.update_job(saved_job_id, data)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Saved job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Job updated successfully',
            'saved_job': job.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/jobs/saved/<saved_job_id>', methods=['DELETE'])
def delete_saved_job(saved_job_id):
    """Delete a saved job"""
    try:
        success = saved_job_store.delete_job(saved_job_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Saved job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Job deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

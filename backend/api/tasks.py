"""Background tasks for crawling operations"""
import time
from datetime import datetime

from crawler.fetcher import WebFetcher
from crawler.parser import ContentParser
from crawler.converters import TextConverter, MarkdownConverter, HTMLConverter
from crawler.link_extractor import LinkExtractor
from crawler.image_downloader import ImageDownloader
from crawler.writer import FileWriter
from utils.validators import URLValidator
from utils.logger import get_logger
from utils.error_handler import handle_extraction_failure, format_failure_for_api, create_failed_extraction_details
from pathlib import Path
from api.models import job_store

logger = get_logger('tasks')


def crawl_single_url(crawl_request, output_dir: str, job, bulk_index: int = None) -> dict:
    """
    Execute single URL crawl
    
    Args:
        crawl_request: CrawlRequest object
        output_dir: Output directory
        job: Job object
        bulk_index: Optional index for bulk crawl (to ensure unique folder names)
        
    Returns:
        Result dictionary
    """
    # Only start job in single mode (bulk mode handles this)
    if bulk_index is None:
        job.start()
        job.set_current_url(crawl_request.url)
        job_store.update_job(job)  # Persist job start
    start_time = time.time()
    response = None  # Initialize to track if fetch succeeded
    
    try:
        # Initialize components with authentication
        cookies = crawl_request.cookies or {}
        auth_headers = crawl_request.auth_headers or {}
        basic_auth = None
        
        # Log authentication details for debugging
        logger.info(f"🔍 Crawling {crawl_request.url}")
        logger.info(f"🍪 Cookies: {list(cookies.keys()) if cookies else 'None'}")
        logger.info(f"🔑 Auth headers: {list(auth_headers.keys()) if auth_headers else 'None'}")
        
        if crawl_request.basic_auth_username and crawl_request.basic_auth_password:
            basic_auth = (crawl_request.basic_auth_username, crawl_request.basic_auth_password)
            logger.info(f"🔐 Using basic auth")
        
        fetcher = WebFetcher(cookies=cookies, auth_headers=auth_headers)
        writer = FileWriter(output_dir)
        
        logger.info(f"Crawling URL: {crawl_request.url}")
        
        # Fetch page with authentication
        response = fetcher.fetch(crawl_request.url, basic_auth=basic_auth)
        
        # Log HTTP status for debugging
        logger.info(f"HTTP {response.status_code} - Authentication: {'Success' if response.status_code == 200 else 'May have issues'}")
        
        # Parse HTML
        parser = ContentParser(response.text, crawl_request.url)
        
        # Execute based on mode
        try:
            if crawl_request.mode == 'content':
                result = _crawl_content_mode(
                    crawl_request,
                    parser,
                    response,
                    writer,
                    output_dir,
                    bulk_index
                )
            else:  # link mode
                result = _crawl_link_mode(
                    crawl_request,
                    parser,
                    response,
                    writer,
                    output_dir,
                    bulk_index
                )
        except ValueError as ve:
            # Enhanced error message for scoped element errors
            if 'Scoped element not found' in str(ve):
                auth_status = "✓ Authentication successful" if response.status_code == 200 else f"⚠ HTTP {response.status_code}"
                enhanced_error = f"{auth_status} - {str(ve)}"
                
                # Save the fetched HTML for debugging
                debug_html_url = None
                try:
                    writer = FileWriter(output_dir)
                    folder_name = writer.generate_folder_name(crawl_request.url)
                    output_path = writer.create_output_folder(output_dir, folder_name)
                    debug_html_path = Path(output_path) / "debug_fetched.html"
                    with open(debug_html_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    debug_html_url = f"{folder_name}/debug_fetched.html"
                    enhanced_error += f"\n\n💡 Debug: Fetched HTML saved to {debug_html_path.name} for inspection"
                    logger.info(f"Saved debug HTML to {debug_html_path}")
                except Exception as debug_error:
                    logger.warning(f"Could not save debug HTML: {debug_error}")
                
                # Get failure info
                failure_info = handle_extraction_failure(crawl_request.url, ValueError(enhanced_error))
                
                # Create extraction_details.json for failed extraction
                extraction_details = create_failed_extraction_details(crawl_request.url, failure_info)
                try:
                    writer.write_extraction_details(extraction_details, output_path)
                except:
                    pass
                
                # Return failure result with debug HTML URL
                result = {
                    'status': 'failed',
                    'url': crawl_request.url,
                    'error': enhanced_error,
                    'failure_info': format_failure_for_api(failure_info),
                    'debug_html_url': debug_html_url
                }
                
                job.add_result(result)

                # Only fail job in single mode (bulk mode handles job completion)
                if bulk_index is None:
                    job.fail(enhanced_error)
                    job_store.update_job(job)
                else:
                    # In bulk mode, just persist the result
                    job_store.update_job(job)

                return result
            raise
        
        execution_time = time.time() - start_time
        result['execution_time'] = execution_time
        result['mode'] = crawl_request.mode
        
        job.add_result(result)

        # Only complete job in single mode (bulk mode handles job completion)
        if bulk_index is None:
            job.set_current_url(None)  # Clear current URL on completion
            job.complete()
            job_store.update_job(job)  # Persist job completion
        else:
            # In bulk mode, just persist the result
            job_store.update_job(job)

        logger.info(f"Crawl completed in {execution_time:.2f}s")
        
        return result
        
    except Exception as e:
        logger.error(f"Error crawling {crawl_request.url}: {e}")
        
        # Get detailed failure information
        failure_info = handle_extraction_failure(crawl_request.url, e)
        
        # Create extraction_details.json for failed extraction
        extraction_details = create_failed_extraction_details(crawl_request.url, failure_info)
        
        # Try to save failure details and debug HTML if possible
        debug_html_url = None
        try:
            writer = FileWriter(output_dir)
            folder_name = writer.generate_folder_name(crawl_request.url)
            output_path = writer.create_output_folder(output_dir, folder_name)
            writer.write_extraction_details(extraction_details, output_path)
            
            # Save debug HTML if we have a response
            if response is not None and hasattr(response, 'text'):
                debug_html_path = Path(output_path) / "debug_fetched.html"
                with open(debug_html_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                # Make path relative to output directory for frontend access
                debug_html_url = f"{folder_name}/debug_fetched.html"
                logger.info(f"Saved debug HTML to {debug_html_path}")
        except Exception as write_error:
            logger.error(f"Failed to write error details: {write_error}")
        
        result = {
            'status': 'failed',
            'url': crawl_request.url,
            'error': str(e),
            'failure_info': format_failure_for_api(failure_info),
            'debug_html_url': debug_html_url  # Add debug HTML URL to result
        }
        
        job.add_result(result)

        # Only fail job in single mode (bulk mode handles job completion)
        if bulk_index is None:
            job.fail(str(e))
            job_store.update_job(job)  # Persist job failure
        else:
            # In bulk mode, just persist the result
            job_store.update_job(job)

        return result


def _crawl_content_mode(crawl_request, parser, response, writer, output_dir, bulk_index=None):
    """Execute content mode crawl"""
    # Extract content with optional scoping
    try:
        scoped_soup = parser.extract_by_scope(
            crawl_request.scope_class,
            crawl_request.scope_id
        )
    except ValueError as e:
        # Save debug HTML for scoped element errors
        debug_html_url = None
        try:
            folder_name = writer.generate_folder_name(crawl_request.url)
            output_path = writer.create_output_folder(output_dir, folder_name)
            debug_html_path = Path(output_path) / "debug_fetched.html"
            with open(debug_html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            debug_html_url = f"{folder_name}/debug_fetched.html"
            logger.info(f"Saved debug HTML to {debug_html_path}")
        except Exception as debug_error:
            logger.warning(f"Could not save debug HTML: {debug_error}")
        
        # Get failure info
        auth_status = "✓ Authentication successful" if response.status_code == 200 else f"⚠ HTTP {response.status_code}"
        enhanced_error = f"{auth_status} - {str(e)}"
        
        from utils.error_handler import handle_extraction_failure, format_failure_for_api
        failure_info = handle_extraction_failure(crawl_request.url, e)
        
        return {
            'status': 'failed',
            'url': crawl_request.url,
            'error': enhanced_error,
            'failure_info': format_failure_for_api(failure_info),
            'debug_html_url': debug_html_url
        }
    
    # Extract text
    text_content = parser.extract_text(scoped_soup)
    
    # Handle images
    image_urls = parser.extract_image_urls(scoped_soup) if crawl_request.download_images else []
    stats = parser.get_content_statistics(text_content, len(image_urls))
    
    # Create output folder with bulk index prefix if provided
    folder_name = writer.generate_folder_name(crawl_request.url, bulk_index)
    output_path = writer.create_output_folder(output_dir, folder_name)
    
    # Generate base filename
    base_filename = writer.generate_filename(crawl_request.url, 'txt')
    base_name = base_filename.rsplit('.', 1)[0]
    
    output_files = []
    image_info = None
    image_mapping = {}
    
    # Download images if requested
    if crawl_request.download_images and image_urls:
        downloader = ImageDownloader()
        image_info = downloader.download_all_images(image_urls, output_path, crawl_request.url)
        image_mapping = image_info['mapping']
        
        # Add downloaded images to output_files list
        for downloaded_filename in image_mapping.values():
            output_files.append(downloaded_filename)
    
    # Write content in requested formats
    for fmt in crawl_request.formats:
        if fmt == 'txt':
            filepath = Path(output_path) / f"{base_name}.txt"
            writer.write_file(text_content, str(filepath))
            output_files.append(filepath.name)
        
        elif fmt == 'md':
            converter = MarkdownConverter()
            md_content = converter.to_markdown(str(scoped_soup))
            
            if image_mapping:
                md_content = converter.update_image_paths(md_content, image_mapping)
            
            filepath = Path(output_path) / f"{base_name}.md"
            writer.write_file(md_content, str(filepath))
            output_files.append(filepath.name)
        
        elif fmt == 'html':
            if image_mapping:
                scoped_soup = HTMLConverter.update_image_paths(scoped_soup, image_mapping)
            
            html_content = HTMLConverter.format_html(scoped_soup)
            html_content = HTMLConverter.add_styling(html_content, stats['title'])
            
            filepath = Path(output_path) / f"{base_name}.html"
            writer.write_file(html_content, str(filepath))
            output_files.append(filepath.name)
    
    # Prepare metadata
    extraction_data = {
        'url': crawl_request.url,
        'mode': 'content',
        'execution_time': 0,  # Will be set by caller
        'parameters': {
            'scope_class': crawl_request.scope_class,
            'scope_id': crawl_request.scope_id,
            'output_formats': crawl_request.formats,
            'download_images': crawl_request.download_images
        },
        'http_response': {
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type'),
            'final_url': response.url
        },
        'statistics': stats,
        'images': image_info or {
            'total_found': 0,
            'successfully_downloaded': 0,
            'failed': 0,
            'image_list': []
        },
        'output_files': output_files,
        'errors': [],
        'warnings': []
    }
    
    if crawl_request.download_images and image_info and image_info['failed'] > 0:
        extraction_data['warnings'].append(f"{image_info['failed']} images failed to download")
    
    # Write metadata files
    details = writer.generate_extraction_metadata(crawl_request.url, extraction_data)
    writer.write_extraction_details(details, output_path)
    
    summary_data = {**extraction_data, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    writer.write_extraction_summary(summary_data, output_path)
    
    return {
        'status': 'success',
        'url': crawl_request.url,
        'output_folder': output_path,
        'output_files': output_files,
        'statistics': stats,
        'has_images': crawl_request.download_images and image_info and image_info['successful'] > 0
    }


def _crawl_link_mode(crawl_request, parser, response, writer, output_dir, bulk_index=None):
    """Execute link mode crawl"""
    # Extract links with optional scoping
    try:
        scoped_soup = parser.extract_by_scope(
            crawl_request.scope_class,
            crawl_request.scope_id
        )
    except ValueError as e:
        # Get failure info
        auth_status = "✓ Authentication successful" if response.status_code == 200 else f"⚠ HTTP {response.status_code}"
        enhanced_error = f"{auth_status} - {str(e)}"

        from utils.error_handler import handle_extraction_failure, format_failure_for_api
        failure_info = handle_extraction_failure(crawl_request.url, e)

        return {
            'status': 'failed',
            'url': crawl_request.url,
            'error': enhanced_error,
            'failure_info': format_failure_for_api(failure_info)
        }

    # Extract links from scoped element
    extractor = LinkExtractor(crawl_request.url)
    all_links = extractor.extract_all_links(scoped_soup, crawl_request.url)
    
    # Filter links
    filtered_links = extractor.filter_links(
        all_links,
        link_type=crawl_request.link_type,
        exclude_anchors=crawl_request.exclude_anchors
    )
    
    # Calculate statistics
    from urllib.parse import urlparse
    internal_count = sum(1 for link in filtered_links if link['type'] == 'internal')
    external_count = sum(1 for link in filtered_links if link['type'] == 'external')
    unique_domains = len(set(
        urlparse(link['url']).netloc 
        for link in filtered_links 
        if link['type'] == 'external'
    ))
    
    stats = {
        'total_links': len(filtered_links),
        'internal_links': internal_count,
        'external_links': external_count,
        'unique_domains': unique_domains
    }
    
    # Create output folder with bulk index prefix if provided
    folder_name = writer.generate_folder_name(crawl_request.url, bulk_index)
    output_path = writer.create_output_folder(output_dir, folder_name)
    
    # Generate base filename
    base_filename = writer.generate_filename(crawl_request.url, 'txt')
    base_name = base_filename.rsplit('.', 1)[0]
    
    output_files = []
    
    # Write links in requested formats
    for fmt in crawl_request.formats:
        if fmt == 'txt':
            content = extractor.format_links_as_text(filtered_links)
            filepath = Path(output_path) / f"{base_name}.txt"
            writer.write_file(content, str(filepath))
            output_files.append(filepath.name)
        
        elif fmt == 'json':
            content = extractor.format_links_as_json(filtered_links)
            filepath = Path(output_path) / f"{base_name}.json"
            writer.write_file(content, str(filepath))
            output_files.append(filepath.name)
    
    # Prepare metadata
    extraction_data = {
        'url': crawl_request.url,
        'mode': 'link',
        'execution_time': 0,  # Will be set by caller
        'parameters': {
            'link_type': crawl_request.link_type,
            'exclude_anchors': crawl_request.exclude_anchors,
            'formats': crawl_request.formats,
            'scope_class': crawl_request.scope_class,
            'scope_id': crawl_request.scope_id
        },
        'http_response': {
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type'),
            'final_url': response.url
        },
        'statistics': stats,
        'output_files': output_files,
        'errors': [],
        'warnings': []
    }
    
    # Write metadata files
    details = writer.generate_extraction_metadata(crawl_request.url, extraction_data)
    writer.write_extraction_details(details, output_path)
    
    summary_data = {**extraction_data, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    writer.write_extraction_summary(summary_data, output_path)
    
    return {
        'status': 'success',
        'url': crawl_request.url,
        'output_folder': output_path,
        'output_files': output_files,
        'statistics': stats
    }


def crawl_bulk_urls(crawl_params_list, output_dir: str, job, combine_results: bool = False):
    """
    Execute bulk URL crawl

    Args:
        crawl_params_list: List of crawl parameter dictionaries
        output_dir: Output directory
        job: Job object
        combine_results: Whether to combine all results into a single file
    """
    job.start()
    job_store.update_job(job)  # Persist job start

    # Track all results for combining
    all_results = []
    
    for index, params in enumerate(crawl_params_list, start=1):
        # Set current URL being processed
        job.set_current_url(params['url'])
        job_store.update_job(job)  # Persist current URL
        logger.info(f"📍 Bulk crawl [{index}/{len(crawl_params_list)}] - Set current URL: {params['url']}")
        logger.info(f"📊 Job state before processing: completed={job.completed_urls}, failed={job.failed_urls}, current_url={job.current_url}")
        
        # Validate URL
        if not URLValidator.is_http_url(params['url']):
            result = {
                'status': 'failed',
                'url': params['url'],
                'error': 'Invalid URL format'
            }
            job.add_result(result)
            job_store.update_job(job)  # Persist after each result
            continue
        
        # Parse authentication from CSV or global auth
        cookies = None
        auth_headers = None
        basic_auth_username = None
        basic_auth_password = None
        
        # Check if row has its own authentication
        if params.get('auth_enabled'):
            auth_type = params.get('auth_type', 'cookies')
            if auth_type == 'cookies' and params.get('cookies'):
                # Parse cookie string to dict
                cookies = _parse_cookies_string(params['cookies'])
            elif auth_type == 'headers' and params.get('auth_headers'):
                # Parse JSON headers
                import json
                try:
                    auth_headers = json.loads(params['auth_headers'])
                except:
                    pass
            elif auth_type == 'basic':
                basic_auth_username = params.get('basic_auth_username')
                basic_auth_password = params.get('basic_auth_password')
        
        # Apply global authentication if no row-specific auth
        elif params.get('global_auth'):
            global_auth = params['global_auth']
            auth_method = global_auth.get('auth_method', 'cookies')
            
            if auth_method == 'cookies' and global_auth.get('cookies'):
                cookies = _parse_cookies_string(global_auth['cookies'])
                logger.info(f"🍪 Bulk crawl - Parsed cookies for {params['url']}: {list(cookies.keys()) if cookies else 'None'}")
            elif auth_method == 'headers' and global_auth.get('auth_headers'):
                import json
                try:
                    auth_headers = json.loads(global_auth['auth_headers'])
                    logger.info(f"🔑 Bulk crawl - Using auth headers for {params['url']}: {list(auth_headers.keys())}")
                except:
                    pass
            elif auth_method == 'basic':
                basic_auth_username = global_auth.get('basic_auth_username')
                basic_auth_password = global_auth.get('basic_auth_password')
                logger.info(f"🔐 Bulk crawl - Using basic auth for {params['url']}")
        
        # Create crawl request
        from api.models import CrawlRequest
        crawl_req = CrawlRequest(
            url=params['url'],
            mode=params.get('mode', 'content'),
            formats=params.get('formats', ['txt']),
            scope_class=params.get('scope_class'),
            scope_id=params.get('scope_id'),
            download_images=params.get('download_images', False),
            link_type=params.get('link_type', 'all'),
            exclude_anchors=params.get('exclude_anchors', False),
            cookies=cookies,
            auth_headers=auth_headers,
            basic_auth_username=basic_auth_username,
            basic_auth_password=basic_auth_password
        )
        
        # Execute crawl with bulk index for unique folder names
        result = crawl_single_url(crawl_req, output_dir, job, bulk_index=index)
        logger.info(f"✅ Bulk crawl [{index}/{len(crawl_params_list)}] - Completed URL: {params['url']} - Status: {result.get('status')}")
        logger.info(f"📊 Job state after processing: completed={job.completed_urls}, failed={job.failed_urls}, progress={job.completed_urls/job.total_urls*100:.1f}%")

        # Track successful results for combining
        if combine_results and result.get('status') == 'success':
            all_results.append(result)

    # Combine results if requested
    if combine_results and all_results:
        logger.info(f"📦 Combining {len(all_results)} results into a single file...")
        _combine_bulk_results(all_results, output_dir, job)

    # Clear current URL when done
    job.set_current_url(None)
    job.complete()
    job_store.update_job(job)  # Persist job completion


def _parse_cookies_string(cookie_str: str) -> dict:
    """Parse cookie string to dictionary"""
    if not cookie_str:
        return {}
    
    # If it's JSON, parse it
    if cookie_str.strip().startswith('{'):
        import json
        try:
            return json.loads(cookie_str)
        except:
            pass
    
    # Parse Chrome DevTools format: "key1=value1; key2=value2"
    cookies = {}
    pairs = cookie_str.split(';')
    for pair in pairs:
        pair = pair.strip()
        if '=' in pair:
            key, value = pair.split('=', 1)
            cookies[key.strip()] = value.strip()

    return cookies


def _combine_bulk_results(results: list, output_dir: str, job):
    """
    Combine all bulk crawl results into a single file

    Args:
        results: List of successful crawl results
        output_dir: Output directory
        job: Job object
    """
    try:
        from pathlib import Path

        # Create combined folder
        combined_folder = Path(output_dir) / "combined_results"
        combined_folder.mkdir(exist_ok=True)

        # Generate timestamp for filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Combine text content
        txt_content = []
        md_content = []

        for i, result in enumerate(results, 1):
            if 'output_folder' not in result or 'output_files' not in result:
                continue

            output_folder = Path(result['output_folder'])

            # Read and combine TXT files
            for filename in result['output_files']:
                if filename.endswith('.txt'):
                    txt_file = output_folder / filename
                    if txt_file.exists():
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Only add content, no separators
                            txt_content.append(content)

                # Read and combine MD files
                elif filename.endswith('.md'):
                    md_file = output_folder / filename
                    if md_file.exists():
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Only add content, no separators
                            md_content.append(content)

        # Write combined files
        output_files = []

        if txt_content:
            combined_txt = combined_folder / f"combined_{timestamp}.txt"
            with open(combined_txt, 'w', encoding='utf-8') as f:
                f.write(''.join(txt_content))
            output_files.append(combined_txt.name)
            logger.info(f"📝 Created combined TXT file: {combined_txt.name}")

        if md_content:
            combined_md = combined_folder / f"combined_{timestamp}.md"
            with open(combined_md, 'w', encoding='utf-8') as f:
                # Write only the content, no header
                f.write(''.join(md_content))
            output_files.append(combined_md.name)
            logger.info(f"📝 Created combined MD file: {combined_md.name}")

        logger.info(f"✅ Successfully combined {len(results)} results into {len(output_files)} file(s)")

        # Add combined result to job so it appears in the results modal
        if output_files:
            combined_result = {
                'status': 'success',
                'url': f'📦 Combined Results ({len(results)} URLs)',
                'output_folder': str(combined_folder),
                'output_files': output_files,
                'statistics': {
                    'total_urls_combined': len(results),
                    'files_created': len(output_files)
                }
            }
            job.add_result(combined_result)
            job_store.update_job(job)
            logger.info(f"📋 Added combined results to job")

    except Exception as e:
        logger.error(f"❌ Error combining results: {e}")
        import traceback
        traceback.print_exc()

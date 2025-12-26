"""Main CLI entry point for web crawler"""
import argparse
import sys
from pathlib import Path
import time
from datetime import datetime
from urllib.parse import urlparse

from crawler.fetcher import WebFetcher
from crawler.parser import ContentParser
from crawler.converters import TextConverter, MarkdownConverter, HTMLConverter
from crawler.link_extractor import LinkExtractor
from crawler.image_downloader import ImageDownloader
from crawler.writer import FileWriter
from utils.validators import URLValidator, InputValidator
from utils.csv_processor import CSVProcessor
from utils.logger import setup_logger

try:
    from colorama import init, Fore, Style
    init()
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False


class WebCrawlerCLI:
    """Command-line interface for web crawler"""
    
    def __init__(self):
        self.logger = setup_logger()
        self.fetcher = None
        self.writer = None
    
    def print_success(self, message: str):
        """Print success message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        else:
            print(f"✓ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
        else:
            print(f"✗ {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
        else:
            print(f"⚠ {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        if COLORS_AVAILABLE:
            print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
        else:
            print(f"ℹ {message}")
    
    def crawl_url_content_mode(self, url: str, formats: list, scope_class: str = None,
                              scope_id: str = None, download_images: bool = False,
                              output_dir: str = './output') -> dict:
        """
        Crawl URL in content mode
        
        Returns:
            Result dictionary
        """
        start_time = time.time()
        
        try:
            self.print_info(f"Fetching: {url}")
            
            # Fetch page
            response = self.fetcher.fetch(url)
            
            # Parse HTML
            parser = ContentParser(response.text, url)
            
            # Extract content (with optional scoping)
            try:
                scoped_soup = parser.extract_by_scope(scope_class, scope_id)
            except ValueError as e:
                return {
                    'status': 'failed',
                    'error': str(e),
                    'url': url
                }
            
            # Extract text
            text_content = parser.extract_text(scoped_soup)
            
            # Get statistics
            image_urls = parser.extract_image_urls(scoped_soup) if download_images else []
            stats = parser.get_content_statistics(text_content, len(image_urls))
            
            # Create output folder
            folder_name = self.writer.generate_folder_name(url)
            output_path = self.writer.create_output_folder(output_dir, folder_name)
            
            self.print_info(f"Saving to: {output_path}")
            
            # Generate base filename
            base_filename = self.writer.generate_filename(url, 'txt')
            base_name = base_filename.rsplit('.', 1)[0]
            
            output_files = []
            image_info = None
            image_mapping = {}
            
            # Download images if requested
            if download_images and image_urls:
                self.print_info(f"Downloading {len(image_urls)} images...")
                downloader = ImageDownloader()
                image_info = downloader.download_all_images(image_urls, output_path, url)
                image_mapping = image_info['mapping']
                
                # Add downloaded images to output_files list
                for downloaded_filename in image_mapping.values():
                    output_files.append(downloaded_filename)
                
                self.print_success(f"Downloaded {image_info['successful']}/{image_info['total']} images")
            
            # Write content in requested formats
            for fmt in formats:
                if fmt == 'txt':
                    filepath = Path(output_path) / f"{base_name}.txt"
                    self.writer.write_file(text_content, str(filepath))
                    output_files.append(filepath.name)
                
                elif fmt == 'md':
                    converter = MarkdownConverter()
                    md_content = converter.to_markdown(str(scoped_soup))
                    
                    # Update image paths
                    if image_mapping:
                        md_content = converter.update_image_paths(md_content, image_mapping)
                    
                    filepath = Path(output_path) / f"{base_name}.md"
                    self.writer.write_file(md_content, str(filepath))
                    output_files.append(filepath.name)
                
                elif fmt == 'html':
                    # Update image paths in HTML
                    if image_mapping:
                        scoped_soup = HTMLConverter.update_image_paths(scoped_soup, image_mapping)
                    
                    html_content = HTMLConverter.format_html(scoped_soup)
                    html_content = HTMLConverter.add_styling(html_content, stats['title'])
                    
                    filepath = Path(output_path) / f"{base_name}.html"
                    self.writer.write_file(html_content, str(filepath))
                    output_files.append(filepath.name)
            
            execution_time = time.time() - start_time
            
            # Prepare metadata
            extraction_data = {
                'url': url,
                'mode': 'content',
                'execution_time': execution_time,
                'parameters': {
                    'scope_class': scope_class,
                    'scope_id': scope_id,
                    'output_formats': formats,
                    'download_images': download_images
                },
                'http_response': {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type'),
                    'final_url': response.url
                },
                'statistics': stats,
                'images': image_info or {'total_found': 0, 'successfully_downloaded': 0, 'failed': 0, 'image_list': []},
                'output_files': output_files,
                'errors': [],
                'warnings': []
            }
            
            if download_images and image_info and image_info['failed'] > 0:
                extraction_data['warnings'].append(f"{image_info['failed']} images failed to download")
            
            # Write metadata files
            details = self.writer.generate_extraction_metadata(url, extraction_data)
            self.writer.write_extraction_details(details, output_path)
            
            summary_data = {**extraction_data, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            self.writer.write_extraction_summary(summary_data, output_path)
            
            self.print_success(f"Extraction completed in {execution_time:.2f}s")
            self.print_success(f"Output saved to: {output_path}")
            
            return {
                'status': 'success',
                'url': url,
                'output_folder': output_path,
                'output_files': output_files,
                'statistics': stats,
                'execution_time': execution_time
            }
            
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")
            self.print_error(f"Failed to crawl {url}: {e}")
            
            return {
                'status': 'failed',
                'url': url,
                'error': str(e)
            }
    
    def crawl_url_link_mode(self, url: str, formats: list, link_type: str = 'all',
                           exclude_anchors: bool = False, output_dir: str = './output') -> dict:
        """
        Crawl URL in link mode
        
        Returns:
            Result dictionary
        """
        start_time = time.time()
        
        try:
            self.print_info(f"Fetching: {url}")
            
            # Fetch page
            response = self.fetcher.fetch(url)
            
            # Parse HTML
            parser = ContentParser(response.text, url)
            
            # Extract links
            extractor = LinkExtractor(url)
            all_links = extractor.extract_all_links(parser.soup, url)
            
            # Filter links
            filtered_links = extractor.filter_links(
                all_links,
                link_type=link_type,
                exclude_anchors=exclude_anchors
            )
            
            self.print_info(f"Found {len(filtered_links)} links")
            
            # Calculate statistics
            internal_count = sum(1 for link in filtered_links if link['type'] == 'internal')
            external_count = sum(1 for link in filtered_links if link['type'] == 'external')
            unique_domains = len(set(urlparse(link['url']).netloc for link in filtered_links if link['type'] == 'external'))
            
            stats = {
                'total_links': len(filtered_links),
                'internal_links': internal_count,
                'external_links': external_count,
                'unique_domains': unique_domains
            }
            
            # Create output folder
            folder_name = self.writer.generate_folder_name(url)
            output_path = self.writer.create_output_folder(output_dir, folder_name)
            
            self.print_info(f"Saving to: {output_path}")
            
            # Generate base filename
            base_filename = self.writer.generate_filename(url, 'txt')
            base_name = base_filename.rsplit('.', 1)[0]
            
            output_files = []
            
            # Write links in requested formats
            for fmt in formats:
                if fmt == 'txt':
                    content = extractor.format_links_as_text(filtered_links)
                    filepath = Path(output_path) / f"{base_name}.txt"
                    self.writer.write_file(content, str(filepath))
                    output_files.append(filepath.name)
                
                elif fmt == 'json':
                    content = extractor.format_links_as_json(filtered_links)
                    filepath = Path(output_path) / f"{base_name}.json"
                    self.writer.write_file(content, str(filepath))
                    output_files.append(filepath.name)
            
            execution_time = time.time() - start_time
            
            # Prepare metadata
            extraction_data = {
                'url': url,
                'mode': 'link',
                'execution_time': execution_time,
                'parameters': {
                    'link_type': link_type,
                    'exclude_anchors': exclude_anchors,
                    'formats': formats
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
            details = self.writer.generate_extraction_metadata(url, extraction_data)
            self.writer.write_extraction_details(details, output_path)
            
            summary_data = {**extraction_data, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            self.writer.write_extraction_summary(summary_data, output_path)
            
            self.print_success(f"Extraction completed in {execution_time:.2f}s")
            self.print_success(f"Output saved to: {output_path}")
            
            return {
                'status': 'success',
                'url': url,
                'output_folder': output_path,
                'output_files': output_files,
                'statistics': stats,
                'execution_time': execution_time
            }
            
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")
            self.print_error(f"Failed to crawl {url}: {e}")
            
            return {
                'status': 'failed',
                'url': url,
                'error': str(e)
            }
    
    def run(self, args):
        """Run crawler with parsed arguments"""
        # Initialize components
        self.fetcher = WebFetcher(timeout=args.timeout)
        self.writer = FileWriter(args.output)
        
        # Bulk CSV mode
        if args.csv:
            return self.run_bulk_mode(args)
        
        # Single URL mode
        if args.url:
            return self.run_single_mode(args)
        
        # Interactive mode
        return self.run_interactive_mode()
    
    def run_single_mode(self, args):
        """Run single URL crawl"""
        # Validate URL
        if not URLValidator.is_http_url(args.url):
            self.print_error(f"Invalid URL: {args.url}")
            return 1
        
        # Validate mode
        if args.mode not in ['content', 'link']:
            self.print_error(f"Invalid mode: {args.mode}. Must be 'content' or 'link'")
            return 1
        
        # Parse formats
        formats = [f.strip() for f in args.format.split(',')]
        
        # Validate formats
        if not InputValidator.validate_formats(formats, args.mode):
            self.print_error(f"Invalid formats for {args.mode} mode: {formats}")
            return 1
        
        # Crawl based on mode
        if args.mode == 'content':
            result = self.crawl_url_content_mode(
                args.url,
                formats,
                args.scope_class,
                args.scope_id,
                args.download_images,
                args.output
            )
        else:  # link mode
            result = self.crawl_url_link_mode(
                args.url,
                formats,
                args.link_type,
                args.exclude_anchors,
                args.output
            )
        
        return 0 if result['status'] == 'success' else 1
    
    def run_bulk_mode(self, args):
        """Run bulk CSV crawl"""
        processor = CSVProcessor()
        
        # Validate CSV
        is_valid, error = processor.validate_csv(args.csv)
        if not is_valid:
            self.print_error(error)
            return 1
        
        # Parse CSV
        crawl_params = processor.parse_csv(args.csv)
        
        self.print_info(f"Processing {len(crawl_params)} URLs from CSV")
        
        results = []
        for idx, params in enumerate(crawl_params, 1):
            self.print_info(f"\n[{idx}/{len(crawl_params)}] Processing: {params['url']}")
            
            # Validate URL
            if not URLValidator.is_http_url(params['url']):
                self.print_error(f"Invalid URL (row {params['row_number']}): {params['url']}")
                results.append({
                    'status': 'failed',
                    'url': params['url'],
                    'error': 'Invalid URL format'
                })
                continue
            
            # Crawl based on mode
            if params['mode'] == 'content':
                result = self.crawl_url_content_mode(
                    params['url'],
                    params['formats'],
                    params['scope_class'],
                    params['scope_id'],
                    params['download_images'],
                    args.output
                )
            else:  # link mode
                result = self.crawl_url_link_mode(
                    params['url'],
                    params['formats'],
                    params['link_type'],
                    params['exclude_anchors'],
                    args.output
                )
            
            results.append(result)
        
        # Generate summary
        summary = processor.generate_bulk_summary(results)
        
        self.print_info(f"\n{'='*50}")
        self.print_info("Bulk Crawl Summary")
        self.print_info(f"{'='*50}")
        self.print_success(f"Total URLs: {summary['total_urls']}")
        self.print_success(f"Successful: {summary['successful']}")
        self.print_error(f"Failed: {summary['failed']}")
        self.print_info(f"Success Rate: {summary['success_rate']:.1f}%")
        
        # Export results
        results_csv = Path(args.output) / 'bulk_results.csv'
        processor.export_results_to_csv(results, str(results_csv))
        self.print_info(f"Results exported to: {results_csv}")
        
        return 0 if summary['failed'] == 0 else 1
    
    def run_interactive_mode(self):
        """Run interactive CLI mode"""
        print("\n=== Web Crawler - Interactive Mode ===\n")
        
        # Get mode
        mode = input("Select mode [content/link] (default: content): ").strip().lower() or 'content'
        if mode not in ['content', 'link']:
            self.print_error("Invalid mode. Using 'content'")
            mode = 'content'
        
        # Get URL
        url = input("Enter URL: ").strip()
        if not URLValidator.is_http_url(url):
            self.print_error("Invalid URL")
            return 1
        
        # Mode-specific options
        if mode == 'content':
            formats_input = input("Select output format(s) [txt,md,html] (default: txt): ").strip() or 'txt'
            formats = [f.strip() for f in formats_input.split(',')]
            
            scope_class = input("Enter scope class (optional): ").strip() or None
            scope_id = input("Enter scope ID (optional): ").strip() or None
            
            download_images_input = input("Download images? [y/n] (default: n): ").strip().lower()
            download_images = download_images_input in ['y', 'yes']
            
            output = input("Output directory (default: ./output): ").strip() or './output'
            
            self.fetcher = WebFetcher()
            self.writer = FileWriter(output)
            
            result = self.crawl_url_content_mode(url, formats, scope_class, scope_id, download_images, output)
        
        else:  # link mode
            formats_input = input("Select output format(s) [txt,json] (default: txt): ").strip() or 'txt'
            formats = [f.strip() for f in formats_input.split(',')]
            
            link_type = input("Link type [all/internal/external] (default: all): ").strip() or 'all'
            
            exclude_anchors_input = input("Exclude anchor fragments? [y/n] (default: n): ").strip().lower()
            exclude_anchors = exclude_anchors_input in ['y', 'yes']
            
            output = input("Output directory (default: ./output): ").strip() or './output'
            
            self.fetcher = WebFetcher()
            self.writer = FileWriter(output)
            
            result = self.crawl_url_link_mode(url, formats, link_type, exclude_anchors, output)
        
        return 0 if result['status'] == 'success' else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Web Crawler - Extract content or links from websites',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('--url', type=str, help='URL to crawl')
    input_group.add_argument('--csv', type=str, help='CSV file with URLs for bulk processing')
    
    # Mode selection
    parser.add_argument('--mode', type=str, default='content', choices=['content', 'link'],
                       help='Crawling mode (default: content)')
    
    # Output options
    parser.add_argument('--format', type=str, default='txt',
                       help='Output format(s) comma-separated (content: txt,md,html | link: txt,json)')
    parser.add_argument('--output', '-o', type=str, default='./output',
                       help='Output directory (default: ./output)')
    
    # Content mode options
    parser.add_argument('--scope-class', '--class', type=str, dest='scope_class',
                       help='CSS class name for scoped extraction (content mode)')
    parser.add_argument('--scope-id', '--id', type=str, dest='scope_id',
                       help='Element ID for scoped extraction (content mode)')
    parser.add_argument('--download-images', action='store_true',
                       help='Download images (content mode)')
    
    # Link mode options
    parser.add_argument('--link-type', type=str, default='all', choices=['all', 'internal', 'external'],
                       help='Type of links to extract (link mode, default: all)')
    parser.add_argument('--exclude-anchors', action='store_true',
                       help='Exclude anchor fragments from URLs (link mode)')
    
    # HTTP options
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # If no arguments, run interactive mode
    if len(sys.argv) == 1:
        cli = WebCrawlerCLI()
        return cli.run_interactive_mode()
    
    # Run with arguments
    cli = WebCrawlerCLI()
    return cli.run(args)


if __name__ == '__main__':
    sys.exit(main())

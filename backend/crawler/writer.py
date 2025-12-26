"""File Writer Module - Handle file output operations"""
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import json
import re


class FileWriter:
    """Write extracted content and metadata to files"""
    
    def __init__(self, base_output_dir: str = './output'):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
    
    def format_timestamp(self) -> str:
        """
        Generate timestamp string in YYYYMMDD_HHMM format
        
        Returns:
            Formatted timestamp string
        """
        return datetime.now().strftime('%Y%m%d_%H%M')
    
    def extract_domain_and_path(self, url: str) -> tuple:
        """
        Extract domain and path from URL for filename
        
        Args:
            url: URL to parse
            
        Returns:
            Tuple of (domain, path_segment)
        """
        parsed = urlparse(url)
        
        # Clean domain (remove www, dots, etc)
        domain = parsed.netloc.replace('www.', '').replace('.', '_')
        
        # Get first path segment (if exists)
        path = parsed.path.strip('/')
        path_parts = [p for p in path.split('/') if p]
        
        # Take first path segment and sanitize
        path_segment = ''
        if path_parts:
            path_segment = '_' + path_parts[0]
            path_segment = re.sub(r'[^\w\-_]', '_', path_segment)
            # Limit length
            if len(path_segment) > 50:
                path_segment = path_segment[:50]
        
        return domain, path_segment
    
    def generate_folder_name(self, url: str, bulk_index: int = None) -> str:
        """
        Generate folder name for output files
        
        Args:
            url: Source URL
            bulk_index: Optional index for bulk crawl (prefixes folder name)
            
        Returns:
            Folder name string
        """
        domain, path = self.extract_domain_and_path(url)
        timestamp = self.format_timestamp()
        
        # Add bulk index prefix if provided
        if bulk_index is not None:
            folder_name = f"{bulk_index:03d}_{domain}{path}_{timestamp}"
        else:
            folder_name = f"{domain}{path}_{timestamp}"
        
        # Sanitize
        folder_name = re.sub(r'[<>:"/\\|?*]', '_', folder_name)
        
        return folder_name
    
    def generate_filename(self, url: str, format: str) -> str:
        """
        Generate filename for output file
        
        Args:
            url: Source URL
            format: File format (txt, md, html, json)
            
        Returns:
            Filename string
        """
        domain, path = self.extract_domain_and_path(url)
        timestamp = self.format_timestamp()
        
        filename = f"{domain}{path}_{timestamp}.{format}"
        
        # Sanitize
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        return filename
    
    def create_output_folder(self, base_dir: str, folder_name: str) -> str:
        """
        Create output folder for extraction
        
        Args:
            base_dir: Base output directory
            folder_name: Name of folder to create
            
        Returns:
            Absolute path to created folder
        """
        folder_path = Path(base_dir) / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        return str(folder_path)
    
    def ensure_directory(self, path: str):
        """
        Ensure directory exists
        
        Args:
            path: Directory path
        """
        Path(path).mkdir(parents=True, exist_ok=True)
    
    def write_file(self, content: str, filepath: str, mode: str = 'w'):
        """
        Write content to file
        
        Args:
            content: Content to write
            filepath: Full file path
            mode: File open mode (default 'w')
        """
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(content)
    
    def write_extraction_details(self, details: dict, output_path: str):
        """
        Write extraction_details.json file
        
        Args:
            details: Extraction details dictionary
            output_path: Output directory path
        """
        filepath = Path(output_path) / 'extraction_details.json'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(details, indent=2, ensure_ascii=False, fp=f)
    
    def write_extraction_summary(self, summary_data: dict, output_path: str):
        """
        Write extraction_summary.txt file
        
        Args:
            summary_data: Summary data dictionary
            output_path: Output directory path
        """
        filepath = Path(output_path) / 'extraction_summary.txt'
        
        # Format summary text
        summary_text = self._format_summary_text(summary_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary_text)
    
    def _format_summary_text(self, data: dict) -> str:
        """Format summary data as readable text"""
        mode = data.get('mode', 'content')
        
        if mode == 'link':
            return self._format_link_summary(data)
        else:
            return self._format_content_summary(data)
    
    def _format_content_summary(self, data: dict) -> str:
        """Format content mode summary"""
        lines = [
            "Extraction Summary",
            "=" * 50,
            "",
            f"URL: {data.get('url', 'N/A')}",
            f"Date: {data.get('timestamp', 'N/A')}",
            f"Execution Time: {data.get('execution_time', 0):.2f} seconds",
            "",
            "Extraction Parameters:",
        ]
        
        params = data.get('parameters', {})
        if params.get('scope_class'):
            lines.append(f"- Scope: class=\"{params['scope_class']}\"")
        elif params.get('scope_id'):
            lines.append(f"- Scope: id=\"{params['scope_id']}\"")
        else:
            lines.append("- Scope: Full page")
        
        lines.append(f"- Formats: {', '.join(params.get('formats', ['txt']))}")
        lines.append(f"- Download Images: {'Yes' if params.get('download_images') else 'No'}")
        lines.append("")
        lines.append("Results:")
        
        stats = data.get('statistics', {})
        lines.append(f"✓ Content extracted successfully")
        lines.append(f"✓ {stats.get('word_count', 0):,} words extracted")
        
        if params.get('download_images'):
            img_info = data.get('images', {})
            total = img_info.get('total_found', 0)
            success = img_info.get('successfully_downloaded', 0)
            lines.append(f"✓ {success} of {total} images downloaded successfully")
        
        lines.append(f"✓ {len(data.get('output_files', []))} output files generated")
        lines.append("")
        lines.append("Output Files:")
        
        for file in data.get('output_files', []):
            lines.append(f"- {file}")
        
        if data.get('images', {}).get('image_list'):
            lines.append("")
            lines.append("Images:")
            for img in data['images']['image_list']:
                if img['status'] == 'success':
                    lines.append(f"- {img['local_path']} (from {img['url']})")
        
        errors = data.get('errors', [])
        warnings = data.get('warnings', [])
        
        if errors or warnings:
            lines.append("")
            lines.append("Issues:")
            for warning in warnings:
                lines.append(f"⚠ {warning}")
            for error in errors:
                lines.append(f"✗ {error}")
        
        lines.append("")
        lines.append(f"Status: {'SUCCESS' if not errors else 'COMPLETED WITH ERRORS'}")
        
        return '\n'.join(lines)
    
    def _format_link_summary(self, data: dict) -> str:
        """Format link mode summary"""
        lines = [
            "Extraction Summary",
            "=" * 50,
            "",
            f"URL: {data.get('url', 'N/A')}",
            f"Date: {data.get('timestamp', 'N/A')}",
            f"Execution Time: {data.get('execution_time', 0):.2f} seconds",
            f"Mode: Link Extraction",
            "",
            "Extraction Parameters:",
        ]
        
        params = data.get('parameters', {})
        lines.append(f"- Link Type: {params.get('link_type', 'all')} (internal + external)")
        lines.append(f"- Exclude Anchors: {'Yes' if params.get('exclude_anchors') else 'No'}")
        lines.append(f"- Formats: {', '.join(params.get('formats', ['txt']))}")
        lines.append("")
        lines.append("Results:")
        
        stats = data.get('statistics', {})
        lines.append(f"✓ Links extracted successfully")
        lines.append(f"✓ {stats.get('total_links', 0)} total links found")
        lines.append(f"✓ {stats.get('internal_links', 0)} internal links")
        lines.append(f"✓ {stats.get('external_links', 0)} external links")
        
        if stats.get('unique_domains'):
            lines.append(f"✓ {stats['unique_domains']} unique external domains")
        
        lines.append(f"✓ {len(data.get('output_files', []))} output files generated")
        lines.append("")
        lines.append("Output Files:")
        
        for file in data.get('output_files', []):
            lines.append(f"- {file}")
        
        lines.append("")
        lines.append("Status: SUCCESS")
        
        return '\n'.join(lines)
    
    def generate_extraction_metadata(self, url: str, extraction_data: dict) -> dict:
        """
        Generate complete extraction metadata
        
        Args:
            url: Source URL
            extraction_data: Dict with extraction results
            
        Returns:
            Complete metadata dictionary
        """
        return {
            'source_url': url,
            'timestamp': datetime.now().isoformat(),
            'execution_time_seconds': extraction_data.get('execution_time', 0),
            'extraction_parameters': extraction_data.get('parameters', {}),
            'http_response': extraction_data.get('http_response', {}),
            'content_statistics': extraction_data.get('statistics', {}),
            'images': extraction_data.get('images', {}),
            'output_files': extraction_data.get('output_files', []),
            'errors': extraction_data.get('errors', []),
            'warnings': extraction_data.get('warnings', [])
        }

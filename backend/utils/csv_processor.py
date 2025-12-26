"""CSV file processing utilities"""
import pandas as pd
from pathlib import Path
from typing import List, Dict


class CSVProcessor:
    """Process CSV files for bulk crawling"""
    
    def __init__(self):
        self.required_columns = ['url']
        self.optional_columns = [
            'mode', 'scope_class', 'scope_id', 'format', 'download_images',
            'auth_enabled', 'auth_type', 'cookies', 'auth_headers',
            'basic_auth_username', 'basic_auth_password'
        ]
    
    def validate_csv(self, file_path: str) -> tuple:
        """
        Validate CSV file structure
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            df = pd.read_csv(file_path)
            
            # Check if URL column exists
            if 'url' not in df.columns:
                return False, "CSV must contain a 'url' column"
            
            # Check if there are any rows
            if len(df) == 0:
                return False, "CSV file is empty"
            
            return True, None
            
        except Exception as e:
            return False, f"Error reading CSV: {str(e)}"
    
    def parse_csv(self, file_path: str) -> List[Dict]:
        """
        Parse CSV file and extract crawl parameters
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of crawl parameter dictionaries
        """
        df = pd.read_csv(file_path)
        
        # Fill NaN with None
        df = df.where(pd.notnull(df), None)
        
        crawl_params = []
        
        for idx, row in df.iterrows():
            params = self.get_crawl_parameters(row.to_dict())
            params['row_number'] = idx + 2  # +2 for header and 0-indexing
            crawl_params.append(params)
        
        return crawl_params
    
    def get_crawl_parameters(self, row: Dict) -> Dict:
        """
        Extract and normalize crawl parameters from CSV row
        
        Args:
            row: Dictionary representing CSV row
            
        Returns:
            Normalized parameters dictionary
        """
        params = {
            'url': self._safe_strip(row.get('url', '')),
            'mode': self._safe_strip(row.get('mode', 'content')).lower() or 'content',
            'scope_class': self._safe_strip(row.get('scope_class', '')) or None,
            'scope_id': self._safe_strip(row.get('scope_id', '')) or None,
            'formats': self._parse_formats(row.get('format', 'txt')),
            'download_images': self._parse_boolean(row.get('download_images', False)),
            'link_type': self._safe_strip(row.get('link_type', 'all')).lower() or 'all',
            'exclude_anchors': self._parse_boolean(row.get('exclude_anchors', False))
        }
        
        # Parse authentication parameters from CSV
        auth_enabled = self._parse_boolean(row.get('auth_enabled', False))
        if auth_enabled:
            auth_type = self._safe_strip(row.get('auth_type', '')).lower() or 'cookies'
            params['auth_enabled'] = True
            params['auth_type'] = auth_type
            
            if auth_type == 'cookies':
                params['cookies'] = self._safe_strip(row.get('cookies', '')) or None
            elif auth_type == 'headers':
                params['auth_headers'] = self._safe_strip(row.get('auth_headers', '')) or None
            elif auth_type == 'basic':
                params['basic_auth_username'] = self._safe_strip(row.get('basic_auth_username', '')) or None
                params['basic_auth_password'] = self._safe_strip(row.get('basic_auth_password', '')) or None
        
        # Clean up empty strings to None (already handled by "or None" above)
        return params
    
    def _parse_formats(self, format_str) -> List[str]:
        """Parse format string to list"""
        if not format_str or pd.isna(format_str):
            return ['txt']
        
        if isinstance(format_str, str):
            # Split by comma or space
            formats = [f.strip().lower() for f in format_str.replace(',', ' ').split()]
            return [f for f in formats if f]
        
        return ['txt']
    
    def _safe_strip(self, value) -> str:
        """Safely strip a value, handling NaN and non-string types"""
        if value is None or pd.isna(value):
            return ''
        return str(value).strip()
    
    def _parse_boolean(self, value) -> bool:
        """Parse boolean value from CSV"""
        if pd.isna(value):
            return False
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 'y']
        
        return bool(value)
    
    def validate_url_column(self, df: pd.DataFrame) -> tuple:
        """
        Validate URLs in dataframe
        
        Returns:
            Tuple of (valid_count, invalid_rows)
        """
        from .validators import URLValidator
        
        invalid_rows = []
        valid_count = 0
        
        for idx, row in df.iterrows():
            url = row.get('url', '')
            if not URLValidator.is_http_url(url):
                invalid_rows.append({
                    'row': idx + 2,  # +2 for header and 0-indexing
                    'url': url,
                    'error': 'Invalid URL format'
                })
            else:
                valid_count += 1
        
        return valid_count, invalid_rows
    
    def generate_bulk_summary(self, results: List[Dict]) -> Dict:
        """
        Generate summary for bulk crawl results
        
        Args:
            results: List of crawl result dictionaries
            
        Returns:
            Summary dictionary
        """
        total = len(results)
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        
        return {
            'total_urls': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'results': results
        }
    
    def export_results_to_csv(self, results: List[Dict], output_path: str):
        """
        Export bulk crawl results to CSV
        
        Args:
            results: List of crawl result dictionaries
            output_path: Path to save CSV
        """
        # Flatten results for CSV
        rows = []
        for result in results:
            row = {
                'url': result.get('url'),
                'status': result.get('status'),
                'output_folder': result.get('output_folder'),
                'execution_time': result.get('execution_time'),
                'word_count': result.get('statistics', {}).get('word_count', 0),
                'error': result.get('error', '')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)

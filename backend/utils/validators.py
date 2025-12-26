"""URL and input validators"""
import validators
from urllib.parse import urlparse
from pathlib import Path


class URLValidator:
    """Validate URLs and URL-related inputs"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        if not url or not isinstance(url, str):
            return False
        return validators.url(url) is True
    
    @staticmethod
    def is_http_url(url: str) -> bool:
        """Check if URL uses HTTP or HTTPS"""
        if not URLValidator.is_valid_url(url):
            return False
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https']
    
    @staticmethod
    def validate_url_list(urls: list) -> tuple:
        """
        Validate list of URLs
        
        Returns:
            Tuple of (valid_urls, invalid_urls)
        """
        valid = []
        invalid = []
        
        for url in urls:
            if URLValidator.is_http_url(url):
                valid.append(url)
            else:
                invalid.append(url)
        
        return valid, invalid


class InputValidator:
    """Validate user inputs"""
    
    @staticmethod
    def validate_mode(mode: str) -> bool:
        """Validate crawling mode"""
        return mode in ['content', 'link']
    
    @staticmethod
    def validate_formats(formats: list, mode: str = 'content') -> bool:
        """Validate output formats for given mode"""
        if mode == 'content':
            valid_formats = ['txt', 'md', 'html']
        else:  # link mode
            valid_formats = ['txt', 'json']
        
        return all(fmt in valid_formats for fmt in formats)
    
    @staticmethod
    def validate_link_type(link_type: str) -> bool:
        """Validate link type"""
        return link_type in ['all', 'internal', 'external']
    
    @staticmethod
    def validate_file_path(filepath: str) -> bool:
        """Check if file path exists"""
        return Path(filepath).exists()
    
    @staticmethod
    def validate_csv_file(filepath: str) -> bool:
        """Validate CSV file"""
        path = Path(filepath)
        return path.exists() and path.suffix.lower() == '.csv'

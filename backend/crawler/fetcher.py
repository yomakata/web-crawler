"""URL Fetcher Module - Handles HTTP requests and URL validation"""
import requests
from typing import Optional, Dict
from urllib.parse import urlparse
import validators


class WebFetcher:
    """Fetches web pages and handles HTTP operations"""
    
    def __init__(self, timeout: int = 30, user_agent: str = None, max_retries: int = 3,
                 cookies: Dict[str, str] = None, auth_headers: Dict[str, str] = None):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or "Mozilla/5.0 (Web Crawler Bot)"
        self.session = requests.Session()
        self.auth_headers = auth_headers or {}
        
        # Set cookies if provided
        if cookies:
            self.session.cookies.update(cookies)
        
    def set_headers(self) -> dict:
        """Set HTTP headers for requests"""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        # Merge with authentication headers
        headers.update(self.auth_headers)
        return headers
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format and scheme"""
        if not url or not isinstance(url, str):
            return False
        
        # Check if URL is valid
        if not validators.url(url):
            return False
        
        # Check if scheme is HTTP or HTTPS
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        
        return True
    
    def fetch(self, url: str, basic_auth: tuple = None) -> requests.Response:
        """
        Fetch content from URL with retry logic and authentication support
        
        Args:
            url: The URL to fetch
            basic_auth: Optional tuple of (username, password) for HTTP Basic Auth
            
        Returns:
            Response object
            
        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If fetch fails after retries
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        headers = self.set_headers()
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    auth=basic_auth  # Add basic auth support
                )
                response.raise_for_status()
                return response
                
            except requests.Timeout as e:
                last_exception = e
                if attempt == self.max_retries - 1:
                    raise requests.RequestException(f"Timeout after {self.max_retries} attempts: {url}") from e
                    
            except requests.RequestException as e:
                last_exception = e
                if attempt == self.max_retries - 1:
                    raise
        
        raise requests.RequestException(f"Failed to fetch URL after {self.max_retries} attempts") from last_exception
    
    def handle_errors(self, error: Exception) -> dict:
        """Convert exceptions to user-friendly error messages"""
        error_map = {
            requests.Timeout: "Request timed out. The server took too long to respond.",
            requests.ConnectionError: "Failed to connect to the server. Please check your internet connection.",
            requests.HTTPError: "HTTP error occurred.",
            ValueError: "Invalid URL format.",
        }
        
        error_type = type(error)
        message = error_map.get(error_type, str(error))
        
        return {
            "error": error_type.__name__,
            "message": message,
            "details": str(error)
        }

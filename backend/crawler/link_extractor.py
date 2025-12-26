"""Link Extractor Module - Extract and filter links from HTML"""
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin, urlparse, urlunparse
import json


class LinkExtractor:
    """Extract and filter hyperlinks from web pages"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
    
    def normalize_url(self, url: str, base_url: str = None) -> str:
        """
        Normalize and resolve relative URLs
        
        Args:
            url: URL to normalize
            base_url: Base URL for resolving relative URLs
            
        Returns:
            Normalized absolute URL
        """
        base = base_url or self.base_url
        
        # Handle protocol-relative URLs
        if url.startswith('//'):
            parsed_base = urlparse(base)
            return f"{parsed_base.scheme}:{url}"
        
        # Resolve relative URLs
        if not url.startswith(('http://', 'https://')):
            url = urljoin(base, url)
        
        return url
    
    def remove_anchors(self, url: str) -> str:
        """Remove anchor/fragment from URL"""
        parsed = urlparse(url)
        return urlunparse(parsed._replace(fragment=''))
    
    def is_internal_link(self, url: str, base_url: str = None) -> bool:
        """
        Check if URL is internal (same domain)
        
        Args:
            url: URL to check
            base_url: Base URL for comparison
            
        Returns:
            True if internal, False if external
        """
        base_domain = urlparse(base_url or self.base_url).netloc
        url_domain = urlparse(url).netloc
        
        return url_domain == base_domain
    
    def get_link_metadata(self, link_element) -> Dict:
        """
        Extract metadata from link element
        
        Args:
            link_element: BeautifulSoup link element
            
        Returns:
            Dict with link metadata
        """
        href = link_element.get('href', '')
        text = link_element.get_text(strip=True)
        title = link_element.get('title', '')
        rel = link_element.get('rel', [])
        
        return {
            'text': text or href,
            'title': title,
            'rel': rel if isinstance(rel, list) else [rel]
        }
    
    def extract_all_links(self, soup: BeautifulSoup, base_url: str = None) -> List[Dict]:
        """
        Extract all links from HTML
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of link dictionaries
        """
        base = base_url or self.base_url
        links = []
        seen_urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Skip empty hrefs, mailto, tel, javascript, etc.
            if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue
            
            # Normalize URL
            try:
                normalized_url = self.normalize_url(href, base)
            except Exception:
                continue
            
            # Skip duplicates
            if normalized_url in seen_urls:
                continue
            
            seen_urls.add(normalized_url)
            
            # Determine link type
            link_type = 'internal' if self.is_internal_link(normalized_url, base) else 'external'
            
            # Get metadata
            metadata = self.get_link_metadata(link)
            
            links.append({
                'url': normalized_url,
                'type': link_type,
                'text': metadata['text'],
                'title': metadata['title'],
                'rel': metadata['rel']
            })
        
        return links
    
    def filter_links(self, links: List[Dict], link_type: str = 'all', 
                    exclude_anchors: bool = False, same_domain_only: bool = False) -> List[Dict]:
        """
        Filter links by type and options
        
        Args:
            links: List of link dictionaries
            link_type: 'all', 'internal', or 'external'
            exclude_anchors: Remove anchor fragments from URLs
            same_domain_only: Only include same-domain links
            
        Returns:
            Filtered list of links
        """
        filtered = links
        
        # Filter by type
        if link_type == 'internal':
            filtered = [link for link in filtered if link['type'] == 'internal']
        elif link_type == 'external':
            filtered = [link for link in filtered if link['type'] == 'external']
        
        # Apply same domain filter
        if same_domain_only:
            filtered = [link for link in filtered if link['type'] == 'internal']
        
        # Remove anchors if requested
        if exclude_anchors:
            for link in filtered:
                link['url'] = self.remove_anchors(link['url'])
            
            # Remove duplicates after anchor removal
            seen = set()
            unique_links = []
            for link in filtered:
                if link['url'] not in seen:
                    seen.add(link['url'])
                    unique_links.append(link)
            filtered = unique_links
        
        return filtered
    
    def validate_link(self, url: str) -> bool:
        """
        Basic URL validation
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def format_links_as_text(self, links: List[Dict]) -> str:
        """
        Format links as plain text list
        
        Args:
            links: List of link dictionaries
            
        Returns:
            Plain text string with one URL per line
        """
        return '\n'.join([link['url'] for link in links])
    
    def format_links_as_json(self, links: List[Dict]) -> str:
        """
        Format links as JSON
        
        Args:
            links: List of link dictionaries
            
        Returns:
            JSON string
        """
        return json.dumps(links, indent=2, ensure_ascii=False)

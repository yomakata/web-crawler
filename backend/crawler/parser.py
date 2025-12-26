"""HTML Parser Module - Extracts content and metadata from HTML"""
from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urljoin, urlparse


class ContentParser:
    """Parses HTML content and extracts text, metadata, and images"""
    
    def __init__(self, html: str, url: str = None):
        self.html = html
        self.url = url
        self.soup = self.parse_html(html)
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML string into BeautifulSoup object"""
        return BeautifulSoup(html, 'lxml')
    
    def find_scoped_element(self, class_name: str = None, element_id: str = None) -> Optional[BeautifulSoup]:
        """
        Find element by class name or ID
        
        Args:
            class_name: CSS class name to search for
            element_id: Element ID to search for
            
        Returns:
            BeautifulSoup element or None if not found
        """
        if element_id:
            element = self.soup.find(id=element_id)
            if element:
                return element
        
        if class_name:
            # Try multiple methods to find the element
            # Method 1: Exact class match
            element = self.soup.find(class_=class_name)
            if element:
                return element
            
            # Method 2: Find element where class_name is one of multiple classes
            element = self.soup.find(attrs={"class": lambda x: x and class_name in x.split()})
            if element:
                return element
            
            # Method 3: CSS selector (more flexible)
            element = self.soup.select_one(f".{class_name}")
            if element:
                return element
        
        return None
    
    def extract_by_scope(self, class_name: str = None, element_id: str = None) -> BeautifulSoup:
        """
        Extract content from scoped element or full page
        
        Args:
            class_name: CSS class name to scope extraction
            element_id: Element ID to scope extraction
            
        Returns:
            BeautifulSoup element (scoped or full soup)
            
        Raises:
            ValueError: If scope is specified but element not found
        """
        if class_name or element_id:
            scoped_element = self.find_scoped_element(class_name, element_id)
            if scoped_element is None:
                scope_desc = f"class='{class_name}'" if class_name else f"id='{element_id}'"
                
                # Add diagnostic information
                all_classes = set()
                for tag in self.soup.find_all(class_=True):
                    classes = tag.get('class', [])
                    if isinstance(classes, list):
                        all_classes.update(classes)
                    else:
                        all_classes.add(classes)
                
                # Check if it's a JavaScript-rendered page
                scripts = self.soup.find_all('script')
                has_js_frameworks = any(
                    keyword in str(script) for script in scripts 
                    for keyword in ['React', 'Vue', 'Angular', 'botframework', 'webchat']
                )
                
                error_msg = f"Scoped element not found: {scope_desc}"
                
                # Check if the class name appears anywhere in the HTML (even as substring)
                if class_name:
                    html_text = str(self.soup)
                    if class_name in html_text:
                        error_msg += f"\n⚠ Note: '{class_name}' found in HTML source but not as a complete class attribute"
                        error_msg += "\n   This could mean:"
                        error_msg += "\n   - The element is inside a <script> or <style> tag"
                        error_msg += "\n   - The class is part of a longer class name"
                        error_msg += "\n   - The content is loaded dynamically via JavaScript"
                
                if has_js_frameworks:
                    error_msg += "\n⚠ Page appears to use JavaScript frameworks - content may be dynamically loaded"
                
                # Show available classes for debugging (limit to 20)
                available_classes = sorted(list(all_classes))[:20]
                if available_classes:
                    error_msg += f"\n\nAvailable classes in HTML: {', '.join(available_classes)}"
                
                raise ValueError(error_msg)
            return scoped_element
        
        return self.soup
    
    def extract_text(self, scope_element: BeautifulSoup = None) -> str:
        """
        Extract clean text from HTML with proper formatting
        
        Rules:
        - Block elements (p, div, h1-h6, etc.) create new lines
        - Inline elements (span, a, strong, etc.) stay on the same line
        """
        element = scope_element or self.soup
        
        # Remove script and style elements
        for script in element(["script", "style", "noscript"]):
            script.decompose()
        
        # Define block and inline elements
        block_elements = {
            'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'section', 'article', 'header', 'footer', 'nav', 'aside', 'main',
            'blockquote', 'pre', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th',
            'dl', 'dt', 'dd', 'form', 'fieldset', 'figure', 'figcaption'
        }
        
        def extract_text_recursive(elem, in_block=False, inside_p=False):
            """Recursively extract text, adding newlines for block elements and spans outside <p>"""
            result = []
            
            for child in elem.children:
                if isinstance(child, str):
                    # Plain text - just add it
                    text = child.strip()
                    if text:
                        result.append(text)
                elif hasattr(child, 'name'):
                    # It's a tag
                    if child.name in block_elements:
                        # Block element - add its text and a newline
                        # Track if we're inside a <p> tag
                        is_p_tag = child.name == 'p'
                        child_text = extract_text_recursive(child, in_block=True, inside_p=is_p_tag)
                        if child_text:
                            result.append(child_text)
                            if in_block:
                                result.append('\n')
                    elif child.name == 'span' and not inside_p:
                        # Span tag NOT inside <p> - add text with newline after
                        child_text = extract_text_recursive(child, in_block=in_block, inside_p=inside_p)
                        if child_text:
                            result.append(child_text)
                            result.append('\n')
                    else:
                        # Other inline element - just extract its text without newline
                        child_text = extract_text_recursive(child, in_block=in_block, inside_p=inside_p)
                        if child_text:
                            result.append(child_text)
            
            return ' '.join(result) if result else ''
        
        # Extract text
        text = extract_text_recursive(element)
        
        # Clean up: split by newlines, strip each line, remove empty lines
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    def extract_title(self) -> str:
        """Extract page title"""
        title_tag = self.soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = self.soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Untitled"
    
    def extract_metadata(self) -> dict:
        """Extract page metadata"""
        metadata = {
            'title': self.extract_title(),
            'description': '',
            'keywords': '',
            'author': '',
        }
        
        # Extract meta tags
        for meta in self.soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_name = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description' or property_name == 'og:description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
        
        return metadata
    
    def clean_content(self, text: str) -> str:
        """Additional content cleaning"""
        # Remove excessive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text.strip()
    
    def extract_image_urls(self, scope_element: BeautifulSoup = None) -> List[dict]:
        """
        Extract all image URLs from HTML
        
        Args:
            scope_element: Optional scoped element to extract images from
            
        Returns:
            List of dicts with image info (url, alt, src)
        """
        element = scope_element or self.soup
        images = []
        
        for img in element.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            
            # Resolve relative URLs
            if self.url and not src.startswith(('http://', 'https://', '//')):
                src = urljoin(self.url, src)
            elif src.startswith('//'):
                src = 'https:' + src
            
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        return images
    
    def get_content_statistics(self, text: str, image_count: int = 0) -> dict:
        """Calculate content statistics"""
        words = text.split()
        
        return {
            'word_count': len(words),
            'character_count': len(text),
            'image_count': image_count,
            'title': self.extract_title()
        }

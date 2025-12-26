"""Content Converters Module - Convert HTML to different formats"""
from bs4 import BeautifulSoup
import html2text
import re


class TextConverter:
    """Convert HTML to plain text"""
    
    @staticmethod
    def to_plain_text(soup: BeautifulSoup) -> str:
        """
        Convert BeautifulSoup to plain text
        
        Args:
            soup: BeautifulSoup element
            
        Returns:
            Plain text string
        """
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)


class MarkdownConverter:
    """Convert HTML to Markdown"""
    
    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_emphasis = False
        self.converter.body_width = 0  # Don't wrap lines
        self.converter.single_line_break = False
    
    def to_markdown(self, html: str) -> str:
        """
        Convert HTML to Markdown
        
        Args:
            html: HTML string or BeautifulSoup
            
        Returns:
            Markdown formatted string
        """
        if isinstance(html, BeautifulSoup):
            html = str(html)
        
        markdown = self.converter.handle(html)
        return markdown.strip()
    
    def update_image_paths(self, content: str, image_mapping: dict) -> str:
        """
        Update image URLs in markdown to local paths
        
        Args:
            content: Markdown content
            image_mapping: Dict mapping original URLs to local filenames
            
        Returns:
            Updated markdown content
        """
        for original_url, local_path in image_mapping.items():
            # Match markdown image syntax: ![alt](url)
            pattern = re.escape(original_url)
            content = re.sub(
                rf'!\[(.*?)\]\({pattern}\)',
                rf'![\1]({local_path})',
                content
            )
        
        return content


class HTMLConverter:
    """Convert and format HTML"""
    
    @staticmethod
    def format_html(soup: BeautifulSoup) -> str:
        """
        Format HTML with proper structure
        
        Args:
            soup: BeautifulSoup element
            
        Returns:
            Formatted HTML string
        """
        # Add basic HTML structure if not present
        if not soup.find('html'):
            html_soup = BeautifulSoup('<!DOCTYPE html><html><head></head><body></body></html>', 'lxml')
            body = html_soup.find('body')
            body.append(soup)
            soup = html_soup
        
        return soup.prettify()
    
    @staticmethod
    def add_styling(html: str, title: str = "Extracted Content") -> str:
        """
        Add CSS styling to HTML
        
        Args:
            html: HTML string
            title: Page title
            
        Returns:
            HTML with embedded CSS
        """
        css = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 20px 0;
            }
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
            }
            code {
                background-color: #f6f8fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            pre {
                background-color: #f6f8fa;
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
            }
            a {
                color: #0366d6;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
        """
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Add or update head section
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)
        
        # Add title
        title_tag = soup.find('title')
        if not title_tag:
            title_tag = soup.new_tag('title')
            title_tag.string = title
            head.append(title_tag)
        
        # Add CSS
        style_tag = BeautifulSoup(css, 'lxml').find('style')
        head.append(style_tag)
        
        return str(soup)
    
    @staticmethod
    def update_image_paths(soup: BeautifulSoup, image_mapping: dict) -> BeautifulSoup:
        """
        Update image src attributes to local paths
        
        Args:
            soup: BeautifulSoup element
            image_mapping: Dict mapping original URLs to local filenames
            
        Returns:
            Updated BeautifulSoup element
        """
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and src in image_mapping:
                img['src'] = image_mapping[src]
        
        return soup

"""Image Downloader Module - Download and manage images"""
import requests
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse, unquote
import mimetypes
import re


class ImageDownloader:
    """Download images and manage image files"""
    
    def __init__(self, timeout: int = 10, max_size_mb: int = 10):
        self.timeout = timeout
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.session = requests.Session()
    
    def sanitize_filename(self, url: str) -> str:
        """
        Create safe filename from URL
        
        Args:
            url: Image URL
            
        Returns:
            Sanitized filename
        """
        # Get filename from URL
        parsed = urlparse(url)
        path = unquote(parsed.path)
        filename = Path(path).name
        
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Ensure filename is not empty
        if not filename or filename == '_':
            filename = 'image'
        
        # Limit filename length
        name, ext = Path(filename).stem, Path(filename).suffix
        if len(name) > 100:
            name = name[:100]
        
        return f"{name}{ext}" if ext else name
    
    def get_image_extension(self, url: str, content_type: str = None) -> str:
        """
        Determine image file extension
        
        Args:
            url: Image URL
            content_type: HTTP Content-Type header
            
        Returns:
            File extension (e.g., '.jpg')
        """
        # Try to get extension from URL
        parsed = urlparse(url)
        path_ext = Path(parsed.path).suffix.lower()
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico']
        if path_ext in valid_extensions:
            return path_ext
        
        # Try to get extension from content type
        if content_type:
            ext = mimetypes.guess_extension(content_type.split(';')[0])
            if ext and ext in valid_extensions:
                return ext
        
        # Default to .jpg
        return '.jpg'
    
    def resolve_image_url(self, base_url: str, img_src: str) -> str:
        """
        Resolve relative image URL
        
        Args:
            base_url: Base page URL
            img_src: Image source attribute
            
        Returns:
            Absolute image URL
        """
        from urllib.parse import urljoin
        
        if img_src.startswith('//'):
            return 'https:' + img_src
        elif img_src.startswith(('http://', 'https://')):
            return img_src
        else:
            return urljoin(base_url, img_src)
    
    def download_image(self, url: str, save_path: str) -> bool:
        """
        Download single image
        
        Args:
            url: Image URL
            save_path: Path to save image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                stream=True,
                headers={'User-Agent': 'Mozilla/5.0 (Web Crawler Bot)'}
            )
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_size_bytes:
                return False
            
            # Ensure directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download image
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"Failed to download image {url}: {e}")
            return False
    
    def download_all_images(self, image_urls: List[str], output_dir: str, 
                          base_url: str = None) -> Dict:
        """
        Download all images from list
        
        Args:
            image_urls: List of image URLs
            output_dir: Directory to save images
            base_url: Base URL for resolving relative URLs
            
        Returns:
            Dict with download results and mapping
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            'total': len(image_urls),
            'successful': 0,
            'failed': 0,
            'mapping': {},  # Original URL -> local filename
            'details': []
        }
        
        used_filenames = set()
        
        for idx, img_data in enumerate(image_urls):
            # Handle both string URLs and dict with image info
            if isinstance(img_data, dict):
                img_url = img_data.get('src')
            else:
                img_url = img_data
            
            if not img_url:
                continue
            
            # Resolve URL if needed
            if base_url:
                img_url = self.resolve_image_url(base_url, img_url)
            
            try:
                # Generate filename
                base_filename = self.sanitize_filename(img_url)
                filename = base_filename
                
                # Handle duplicate filenames
                counter = 1
                while filename in used_filenames:
                    name, ext = Path(base_filename).stem, Path(base_filename).suffix
                    filename = f"{name}_{counter}{ext}"
                    counter += 1
                
                used_filenames.add(filename)
                
                # Ensure extension
                if not Path(filename).suffix:
                    filename += '.jpg'
                
                save_path = output_path / filename
                
                # Download image
                success = self.download_image(img_url, str(save_path))
                
                if success:
                    results['successful'] += 1
                    results['mapping'][img_url] = filename
                    results['details'].append({
                        'url': img_url,
                        'local_path': filename,
                        'status': 'success'
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'url': img_url,
                        'local_path': None,
                        'status': 'failed',
                        'error': 'Download failed'
                    })
                    
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'url': img_url,
                    'local_path': None,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results

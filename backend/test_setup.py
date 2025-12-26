#!/usr/bin/env python
"""Quick test script to verify setup"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from crawler.fetcher import WebFetcher
        print("✓ fetcher module imported")
        
        from crawler.parser import ContentParser
        print("✓ parser module imported")
        
        from crawler.converters import TextConverter, MarkdownConverter, HTMLConverter
        print("✓ converters module imported")
        
        from crawler.link_extractor import LinkExtractor
        print("✓ link_extractor module imported")
        
        from crawler.image_downloader import ImageDownloader
        print("✓ image_downloader module imported")
        
        from crawler.writer import FileWriter
        print("✓ writer module imported")
        
        from utils.validators import URLValidator
        print("✓ validators module imported")
        
        from utils.csv_processor import CSVProcessor
        print("✓ csv_processor module imported")
        
        from api.app import create_app
        print("✓ Flask app module imported")
        
        from api.models import CrawlRequest, Job
        print("✓ API models module imported")
        
        print("\n✓ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        return False


def test_url_validation():
    """Test URL validation"""
    print("\nTesting URL validation...")
    
    from utils.validators import URLValidator
    
    assert URLValidator.is_http_url('https://example.com') == True
    assert URLValidator.is_http_url('http://example.com') == True
    assert URLValidator.is_http_url('invalid-url') == False
    assert URLValidator.is_http_url('ftp://example.com') == False
    
    print("✓ URL validation tests passed!")


def test_file_writer():
    """Test file writer"""
    print("\nTesting file writer...")
    
    from crawler.writer import FileWriter
    
    writer = FileWriter()
    
    # Test folder name generation
    folder = writer.generate_folder_name('https://example.com/blog/post')
    assert 'example_com' in folder
    assert 'blog' in folder
    
    # Test filename generation
    filename = writer.generate_filename('https://example.com', 'txt')
    assert filename.endswith('.txt')
    assert 'example_com' in filename
    
    print("✓ File writer tests passed!")


def test_flask_app():
    """Test Flask app creation"""
    print("\nTesting Flask app creation...")
    
    from api.app import create_app
    
    app = create_app()
    assert app is not None
    assert app.name == 'api.app'
    
    print("✓ Flask app creation successful!")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Web Crawler - Setup Verification")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    try:
        test_url_validation()
        test_file_writer()
        test_flask_app()
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        success = False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! Setup is complete.")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Run CLI: python main.py --help")
        print("2. Start API: python -m flask --app api.app run")
        print("3. Or use Docker: docker-compose up")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("=" * 50)
        return 1


if __name__ == '__main__':
    sys.exit(main())

"""Unit tests for parser module"""
import pytest
from crawler.parser import ContentParser
from bs4 import BeautifulSoup


def test_parse_html():
    """Test HTML parsing"""
    html = '<html><body><h1>Test</h1></body></html>'
    parser = ContentParser(html)
    
    assert parser.soup is not None
    assert parser.soup.find('h1').text == 'Test'


def test_extract_title():
    """Test title extraction"""
    html = '<html><head><title>Test Title</title></head><body></body></html>'
    parser = ContentParser(html)
    
    assert parser.extract_title() == 'Test Title'


def test_extract_title_fallback():
    """Test title fallback to h1"""
    html = '<html><body><h1>H1 Title</h1></body></html>'
    parser = ContentParser(html)
    
    assert parser.extract_title() == 'H1 Title'


def test_find_scoped_element_by_class():
    """Test finding element by class"""
    html = '''
    <html><body>
        <div class="content">Target content</div>
        <div class="other">Other content</div>
    </body></html>
    '''
    parser = ContentParser(html)
    
    element = parser.find_scoped_element(class_name='content')
    assert element is not None
    assert 'Target content' in element.text


def test_find_scoped_element_by_id():
    """Test finding element by ID"""
    html = '''
    <html><body>
        <div id="main">Main content</div>
        <div id="sidebar">Sidebar</div>
    </body></html>
    '''
    parser = ContentParser(html)
    
    element = parser.find_scoped_element(element_id='main')
    assert element is not None
    assert 'Main content' in element.text


def test_extract_text():
    """Test text extraction"""
    html = '''
    <html><body>
        <h1>Title</h1>
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
    </body></html>
    '''
    parser = ContentParser(html)
    text = parser.extract_text()
    
    assert 'Title' in text
    assert 'Paragraph 1' in text
    assert 'Paragraph 2' in text


def test_extract_image_urls():
    """Test image URL extraction"""
    html = '''
    <html><body>
        <img src="https://example.com/image1.jpg" alt="Image 1">
        <img src="/path/image2.png" alt="Image 2">
    </body></html>
    '''
    parser = ContentParser(html, 'https://example.com')
    images = parser.extract_image_urls()
    
    assert len(images) == 2
    assert images[0]['src'] == 'https://example.com/image1.jpg'
    assert images[0]['alt'] == 'Image 1'

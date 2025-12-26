"""Unit tests for link extractor module"""
import pytest
from crawler.link_extractor import LinkExtractor
from bs4 import BeautifulSoup


def test_normalize_url():
    """Test URL normalization"""
    extractor = LinkExtractor('https://example.com')
    
    # Relative URL
    normalized = extractor.normalize_url('/path/to/page')
    assert normalized == 'https://example.com/path/to/page'
    
    # Protocol-relative URL
    normalized = extractor.normalize_url('//cdn.example.com/image.jpg')
    assert normalized == 'https://cdn.example.com/image.jpg'
    
    # Absolute URL
    normalized = extractor.normalize_url('https://other.com/page')
    assert normalized == 'https://other.com/page'


def test_is_internal_link():
    """Test internal link detection"""
    extractor = LinkExtractor('https://example.com')
    
    assert extractor.is_internal_link('https://example.com/page') == True
    assert extractor.is_internal_link('https://example.com/') == True
    assert extractor.is_internal_link('https://other.com/page') == False


def test_remove_anchors():
    """Test anchor removal"""
    extractor = LinkExtractor('https://example.com')
    
    url = extractor.remove_anchors('https://example.com/page#section')
    assert url == 'https://example.com/page'
    
    url = extractor.remove_anchors('https://example.com/page')
    assert url == 'https://example.com/page'


def test_extract_all_links():
    """Test link extraction"""
    html = '''
    <html><body>
        <a href="/page1">Page 1</a>
        <a href="https://example.com/page2">Page 2</a>
        <a href="https://other.com/page">External</a>
        <a href="#section">Anchor</a>
        <a href="mailto:test@example.com">Email</a>
    </body></html>
    '''
    soup = BeautifulSoup(html, 'lxml')
    extractor = LinkExtractor('https://example.com')
    
    links = extractor.extract_all_links(soup)
    
    # Should extract 3 links (excluding anchor and mailto)
    assert len(links) == 3
    
    # Check internal/external classification
    internal = [l for l in links if l['type'] == 'internal']
    external = [l for l in links if l['type'] == 'external']
    
    assert len(internal) == 2
    assert len(external) == 1


def test_filter_links():
    """Test link filtering"""
    links = [
        {'url': 'https://example.com/page1', 'type': 'internal', 'text': 'Page 1'},
        {'url': 'https://example.com/page2', 'type': 'internal', 'text': 'Page 2'},
        {'url': 'https://other.com/page', 'type': 'external', 'text': 'External'},
    ]
    
    extractor = LinkExtractor('https://example.com')
    
    # Filter internal only
    internal = extractor.filter_links(links, link_type='internal')
    assert len(internal) == 2
    
    # Filter external only
    external = extractor.filter_links(links, link_type='external')
    assert len(external) == 1
    
    # All links
    all_links = extractor.filter_links(links, link_type='all')
    assert len(all_links) == 3


def test_format_links_as_text():
    """Test text formatting"""
    links = [
        {'url': 'https://example.com/page1', 'type': 'internal'},
        {'url': 'https://example.com/page2', 'type': 'internal'},
    ]
    
    extractor = LinkExtractor('https://example.com')
    text = extractor.format_links_as_text(links)
    
    assert 'https://example.com/page1' in text
    assert 'https://example.com/page2' in text
    assert text.count('\n') == 1  # One newline between two links

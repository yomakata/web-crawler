"""Unit tests for fetcher module"""
import pytest
from crawler.fetcher import WebFetcher
import requests


def test_validate_url():
    """Test URL validation"""
    fetcher = WebFetcher()
    
    # Valid URLs
    assert fetcher.validate_url('https://example.com') == True
    assert fetcher.validate_url('http://example.com') == True
    assert fetcher.validate_url('https://example.com/path') == True
    
    # Invalid URLs
    assert fetcher.validate_url('') == False
    assert fetcher.validate_url('not-a-url') == False
    assert fetcher.validate_url('ftp://example.com') == False
    assert fetcher.validate_url(None) == False


def test_set_headers():
    """Test header generation"""
    fetcher = WebFetcher(user_agent='Test Agent')
    headers = fetcher.set_headers()
    
    assert 'User-Agent' in headers
    assert headers['User-Agent'] == 'Test Agent'
    assert 'Accept' in headers


def test_handle_errors():
    """Test error handling"""
    fetcher = WebFetcher()
    
    error = requests.Timeout('Request timed out')
    result = fetcher.handle_errors(error)
    
    assert 'error' in result
    assert 'message' in result
    assert result['error'] == 'Timeout'

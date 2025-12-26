"""
Test script for error_handler module
Run this to verify the error handler functionality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from utils.error_handler import handle_extraction_failure, format_failure_for_api
import requests


def test_timeout_error():
    """Test timeout error handling"""
    print("\n=== Testing Timeout Error ===")
    exception = requests.Timeout("Connection timed out after 30 seconds")
    failure_info = handle_extraction_failure("https://example.com", exception)
    
    print(f"Failure Reason: {failure_info['failure_reason']}")
    print(f"Error Type: {failure_info['error_type']}")
    print(f"Retry Possible: {failure_info['retry_possible']}")
    print(f"Suggestions: {len(failure_info['suggestions'])}")
    for suggestion in failure_info['suggestions']:
        print(f"  - {suggestion}")
    
    assert failure_info['error_type'] == 'network_error'
    assert failure_info['retry_possible'] == True
    print("✓ Timeout error test passed")


def test_http_404_error():
    """Test 404 HTTP error handling"""
    print("\n=== Testing 404 HTTP Error ===")
    
    # Create a mock response
    class MockResponse:
        status_code = 404
        reason = "Not Found"
    
    exception = requests.HTTPError()
    exception.response = MockResponse()
    
    failure_info = handle_extraction_failure("https://example.com/notfound", exception)
    
    print(f"Failure Reason: {failure_info['failure_reason']}")
    print(f"Error Type: {failure_info['error_type']}")
    print(f"Error Code: {failure_info['error_code']}")
    print(f"Retry Possible: {failure_info['retry_possible']}")
    print(f"Suggestions: {len(failure_info['suggestions'])}")
    for suggestion in failure_info['suggestions']:
        print(f"  - {suggestion}")
    
    assert failure_info['error_type'] == 'http_error'
    assert failure_info['error_code'] == 404
    assert failure_info['retry_possible'] == False
    print("✓ 404 error test passed")


def test_invalid_url_error():
    """Test invalid URL error handling"""
    print("\n=== Testing Invalid URL Error ===")
    exception = ValueError("Invalid URL format")
    failure_info = handle_extraction_failure("not-a-valid-url", exception)
    
    print(f"Failure Reason: {failure_info['failure_reason']}")
    print(f"Error Type: {failure_info['error_type']}")
    print(f"Retry Possible: {failure_info['retry_possible']}")
    print(f"Suggestions: {len(failure_info['suggestions'])}")
    for suggestion in failure_info['suggestions']:
        print(f"  - {suggestion}")
    
    assert failure_info['error_type'] == 'validation_error'
    assert failure_info['retry_possible'] == False
    print("✓ Invalid URL error test passed")


def test_connection_error():
    """Test connection refused error handling"""
    print("\n=== Testing Connection Error ===")
    exception = requests.ConnectionError("Connection refused")
    failure_info = handle_extraction_failure("https://unreachable-server.com", exception)
    
    print(f"Failure Reason: {failure_info['failure_reason']}")
    print(f"Error Type: {failure_info['error_type']}")
    print(f"Retry Possible: {failure_info['retry_possible']}")
    print(f"Suggestions: {len(failure_info['suggestions'])}")
    for suggestion in failure_info['suggestions']:
        print(f"  - {suggestion}")
    
    assert failure_info['error_type'] == 'network_error'
    assert failure_info['retry_possible'] == True
    print("✓ Connection error test passed")


def test_format_for_api():
    """Test API response formatting"""
    print("\n=== Testing API Response Formatting ===")
    exception = requests.Timeout("Connection timed out")
    failure_info = handle_extraction_failure("https://example.com", exception)
    
    api_response = format_failure_for_api(failure_info)
    
    print(f"API Response Keys: {list(api_response.keys())}")
    
    required_keys = ['failure_reason', 'error_type', 'error_code', 'retry_possible', 'suggestions']
    for key in required_keys:
        assert key in api_response, f"Missing key: {key}"
    
    print("✓ API formatting test passed")


def main():
    """Run all tests"""
    print("=" * 60)
    print("ERROR HANDLER TEST SUITE")
    print("=" * 60)
    
    try:
        test_timeout_error()
        test_http_404_error()
        test_invalid_url_error()
        test_connection_error()
        test_format_for_api()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

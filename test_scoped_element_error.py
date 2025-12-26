"""Test script to verify scoped element error handling"""
import sys
sys.path.insert(0, 'backend')

from utils.error_handler import handle_extraction_failure

# Simulate the error from parser.py
test_url = "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer"
exception = ValueError("Scoped element not found: class='content-section'")

# Test the error handler
result = handle_extraction_failure(test_url, exception)

print("=" * 60)
print("SCOPED ELEMENT ERROR HANDLER TEST")
print("=" * 60)
print(f"\nURL: {test_url}")
print(f"\nException: {exception}")
print("\n" + "-" * 60)
print("FAILURE INFO RETURNED:")
print("-" * 60)
print(f"\nExtraction Status: {result['extraction_status']}")
print(f"Failure Reason: {result['failure_reason']}")
print(f"Error Type: {result['error_type']}")
print(f"Error Code: {result['error_code']}")
print(f"Retry Possible: {result['retry_possible']}")
print(f"\nSuggestions:")
for i, suggestion in enumerate(result['suggestions'], 1):
    print(f"  {i}. {suggestion}")
print("\n" + "=" * 60)

# Verify the correct error type is returned
assert result['error_type'] == 'content_error', f"Expected 'content_error', got '{result['error_type']}'"
assert result['error_code'] == 'ELEMENT_NOT_FOUND', f"Expected 'ELEMENT_NOT_FOUND', got '{result['error_code']}'"
assert result['retry_possible'] == False, f"Expected False, got {result['retry_possible']}"
assert "Scoped element not found" in result['failure_reason'], f"Expected scoped element message in failure_reason"

print("\n✓ All assertions passed! Error handling is working correctly.")
print("=" * 60)

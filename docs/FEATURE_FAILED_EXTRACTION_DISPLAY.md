# Feature Addition: Enhanced Failed Extraction Display

## Feature Overview
Enhanced error reporting for failed extractions with detailed failure reasons displayed alongside the "Extraction Failed" message.

## Implementation Date
December 24, 2025

## Specification Location
`dev-spec.md` - Updated sections:
- Error Handling (lines ~920-930)
- Extraction Results Display (lines ~142-150)
- API Response Format (lines ~410-430)
- extraction_details.json metadata (lines ~75-90)
- Phase 6 Implementation Tasks (line ~677)

## Feature Description

### User Experience
When an extraction fails, users will see:
1. **Clear Status**: "Extraction Failed" message with red/error styling
2. **Specific Reason**: Detailed failure reason in clear, user-friendly language
3. **Error Context**: Error type indicator (icon/badge)
4. **Actionable Guidance**: Suggested troubleshooting steps or resolution actions
5. **Retry Option**: Button to retry the failed extraction

### Error Types Displayed
- **Network Errors**: "Network timeout", "Connection refused", "DNS resolution failed"
- **HTTP Errors**: "404 Not Found", "403 Forbidden", "500 Internal Server Error"
- **Validation Errors**: "Invalid URL format", "Missing required parameters"
- **Content Errors**: "Element not found", "Empty content", "Invalid HTML structure"
- **Permission Errors**: "Access denied", "File write failed", "Disk space full"
- **Parsing Errors**: "Unable to parse HTML", "Encoding error", "Malformed content"

### Implementation Components

#### 1. Frontend Display (ResultsModal.jsx)
```jsx
// Failed extraction display section
{status === 'failed' && (
  <div className="failed-extraction-banner">
    <div className="error-icon">❌</div>
    <div className="error-content">
      <h3>Extraction Failed</h3>
      <p className="failure-reason">{failureInfo.failure_reason}</p>
      <span className="error-type-badge">{failureInfo.error_type}</span>
    </div>
    <div className="error-actions">
      {failureInfo.retry_possible && (
        <button onClick={handleRetry}>Retry Extraction</button>
      )}
      <button onClick={showTroubleshooting}>Help & Troubleshooting</button>
    </div>
  </div>
)}
```

#### 2. API Response Format
```json
{
  "job_id": "abc123",
  "results": [{
    "url": "https://example.com",
    "status": "failed",
    "output_files": [],
    "failure_info": {
      "failure_reason": "404 Not Found - The requested page does not exist",
      "error_type": "http_error",
      "error_code": 404,
      "error_timestamp": "2025-12-24T15:30:00Z",
      "retry_possible": false,
      "suggestions": [
        "Check if the URL is correct",
        "Verify the page still exists",
        "Try accessing the page in a browser"
      ]
    }
  }]
}
```

#### 3. extraction_details.json Format
```json
{
  "url": "https://example.com",
  "extraction_status": "failed",
  "failure_reason": "Connection timeout after 30 seconds",
  "error_type": "network_error",
  "error_code": "TIMEOUT",
  "error_timestamp": "2025-12-24T15:30:00Z",
  "retry_possible": true,
  "suggestions": [
    "Check your internet connection",
    "Try again in a few moments",
    "The target server may be experiencing issues"
  ],
  "http_response": null,
  "execution_time": "30.5s"
}
```

#### 4. Backend Error Handling
```python
def handle_extraction_failure(url, exception):
    """Map exceptions to user-friendly failure information"""
    failure_info = {
        'extraction_status': 'failed',
        'failure_reason': '',
        'error_type': '',
        'error_code': None,
        'error_timestamp': datetime.now().isoformat(),
        'retry_possible': False,
        'suggestions': []
    }
    
    if isinstance(exception, requests.Timeout):
        failure_info.update({
            'failure_reason': 'Connection timeout - Server took too long to respond',
            'error_type': 'network_error',
            'error_code': 'TIMEOUT',
            'retry_possible': True,
            'suggestions': [
                'Check your internet connection',
                'Try again in a few moments',
                'The target server may be slow or down'
            ]
        })
    elif isinstance(exception, requests.HTTPError):
        status_code = exception.response.status_code
        failure_info.update({
            'failure_reason': f'{status_code} {exception.response.reason}',
            'error_type': 'http_error',
            'error_code': status_code,
            'retry_possible': status_code >= 500,
            'suggestions': get_http_error_suggestions(status_code)
        })
    # ... more exception types
    
    return failure_info
```

### Error Message Examples

| Scenario | Display Message | Error Type | Retry Possible |
|----------|----------------|------------|----------------|
| Network timeout | "Connection timeout - Server took too long to respond" | network_error | Yes |
| 404 Not Found | "404 Not Found - The requested page does not exist" | http_error | No |
| Invalid URL | "Invalid URL format - Please check the URL syntax" | validation_error | No |
| Element not found | "Target element not found - The specified class or ID does not exist on the page" | content_error | No |
| Connection refused | "Connection refused - Unable to reach the server" | network_error | Yes |
| 500 Server Error | "500 Internal Server Error - The server encountered an error" | http_error | Yes |
| Disk full | "Disk space full - Unable to save extracted content" | permission_error | No |
| Encoding error | "Text encoding error - Unable to decode page content" | parsing_error | Yes |

### Benefits

1. **Improved User Experience**: Users understand exactly what went wrong
2. **Faster Troubleshooting**: Clear error messages reduce support requests
3. **Better Debugging**: Developers can track common failure patterns
4. **Actionable Feedback**: Users know what steps to take next
5. **Enhanced Reliability**: Retry functionality for transient errors

### Related Files to Update

1. **Backend**:
   - `backend/core/crawler.py` - Add failure reason capture
   - `backend/core/extractor.py` - Enhanced error handling
   - `backend/api/routes.py` - Update response format
   - `backend/utils/error_handler.py` - Error categorization logic

2. **Frontend**:
   - `frontend/src/components/ResultsModal.jsx` - Failed state display
   - `frontend/src/services/api.js` - Handle failure_info in responses
   - `frontend/src/pages/Crawler.jsx` - Pass failure data to modal
   - `frontend/src/pages/History.jsx` - Show failure reasons in history

3. **Documentation**:
   - `dev-spec.md` - Updated (completed)
   - `backend/README.md` - Document error response format
   - `frontend/README.md` - Document failure state handling

### Testing Scenarios

1. **Network timeout simulation**: Force timeout and verify message
2. **404 error**: Test with non-existent URL
3. **Invalid URL format**: Test URL validation
4. **Element not found**: Test scope element that doesn't exist
5. **Permission errors**: Test with read-only output directory
6. **Server errors (500)**: Mock server error responses
7. **Retry functionality**: Verify retry button works correctly
8. **Multiple failures**: Test bulk mode with mixed successes/failures

## Next Steps

1. Implement backend error mapping in `error_handler.py`
2. Update API responses to include `failure_info`
3. Create `ResultsModal` failed state UI component
4. Add retry functionality to frontend
5. Update extraction_details.json generation
6. Add error type icons/badges to UI
7. Write unit tests for error handling
8. Update user documentation with error resolution guide

## Acceptance Criteria

✅ Failed extractions show "Extraction Failed" message prominently
✅ Specific failure reason is displayed in clear language
✅ Error type is categorized and indicated with appropriate styling
✅ Actionable suggestions are provided for common errors
✅ Retry button appears when retry is possible
✅ extraction_details.json includes all failure information
✅ API responses include failure_info object for failed extractions
✅ History page shows failure reasons in job list
✅ All error types are properly mapped and tested

---

**Status**: Specification Complete - Ready for Implementation
**Priority**: High - Improves user experience significantly
**Estimated Effort**: 1-2 days for full implementation

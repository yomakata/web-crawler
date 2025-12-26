# Failed Extraction Display Feature - README

## Overview

This feature provides detailed, user-friendly error information when web page extractions fail, helping users understand what went wrong and how to fix it.

## Features

### 1. **Detailed Error Messages**
When an extraction fails, users see:
- Clear "Extraction Failed" status
- Specific failure reason (e.g., "Connection timeout", "404 Not Found")
- Error type categorization
- Error code (when applicable)

### 2. **Actionable Suggestions**
Every error includes specific troubleshooting steps:
- Check URL format
- Verify network connection
- Confirm page exists
- Wait and retry for temporary errors

### 3. **Smart Retry Logic**
The system determines if retrying might succeed:
- **Retry Possible**: Network timeouts, server errors (500+)
- **No Retry**: Invalid URLs, 404 errors, validation failures

### 4. **Visual Error Display**
Professional, color-coded error UI:
- Red error banners
- Error type badges
- Warning icons
- Expandable details

## Usage

### For End Users

#### Viewing Error Details in Results Modal

When extraction fails:
1. A red banner appears with "Extraction Failed"
2. The specific error reason is shown
3. Suggestions list provides steps to resolve
4. Click "Retry Extraction" if available
5. Expand "View Troubleshooting Tips" for more details

#### Checking Failed Jobs in History

In the History page:
1. Failed jobs show with red "Failed" badge
2. Compact error message appears below job details
3. Click "View Results" to see full error information

### For Developers

#### Backend: Handling Errors

```python
from utils.error_handler import handle_extraction_failure, format_failure_for_api

try:
    # Your extraction code here
    result = perform_extraction(url)
except Exception as e:
    # Get detailed failure information
    failure_info = handle_extraction_failure(url, e)
    
    # Format for API response
    api_response = format_failure_for_api(failure_info)
    
    # Return to frontend
    return {
        'status': 'failed',
        'url': url,
        'failure_info': api_response
    }
```

#### Frontend: Displaying Errors

```jsx
// In ResultsModal component
{result.status === 'failed' && result.failure_info && (
  <div className="bg-error-50 border border-error-200 rounded-lg p-4">
    <p className="font-semibold text-error-900">
      {result.failure_info.failure_reason}
    </p>
    <ul className="mt-2">
      {result.failure_info.suggestions.map((suggestion, idx) => (
        <li key={idx}>• {suggestion}</li>
      ))}
    </ul>
    {result.failure_info.retry_possible && (
      <button onClick={handleRetry}>Retry</button>
    )}
  </div>
)}
```

## Error Types

### Network Errors (`network_error`)
- Connection timeout
- Connection refused
- Too many redirects
- DNS resolution failed

**Retry**: Usually possible

### HTTP Errors (`http_error`)
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 429 Too Many Requests
- 500-504 Server Errors

**Retry**: Only for 5xx errors

### Validation Errors (`validation_error`)
- Invalid URL format
- Missing required parameters
- Invalid parameter values

**Retry**: Not possible without fixing input

### Content Errors (`content_error`)
- Element not found (wrong class/ID)
- Empty page content
- Malformed HTML

**Retry**: Usually not helpful

### Parsing Errors (`parsing_error`)
- Encoding detection failed
- Character encoding issues

**Retry**: Sometimes possible

### Permission Errors (`permission_error`)
- File write permission denied
- Disk space full
- Invalid output path

**Retry**: Not possible without fixing system issues

## Error Response Format

### API Response
```json
{
  "status": "failed",
  "url": "https://example.com",
  "error": "Connection timeout",
  "failure_info": {
    "failure_reason": "Connection timeout - Server took too long to respond",
    "error_type": "network_error",
    "error_code": "TIMEOUT",
    "retry_possible": true,
    "suggestions": [
      "Check your internet connection",
      "Try again in a few moments",
      "The target server may be slow or experiencing issues"
    ]
  }
}
```

### extraction_details.json
```json
{
  "source_url": "https://example.com",
  "timestamp": "2025-12-24T16:30:00Z",
  "extraction_status": "failed",
  "failure_reason": "Connection timeout - Server took too long to respond",
  "error_type": "network_error",
  "error_code": "TIMEOUT",
  "retry_possible": true,
  "suggestions": [...],
  "execution_time": null,
  "http_response": null,
  "extraction_parameters": {},
  "content_statistics": null,
  "images": null,
  "output_files": [],
  "errors": ["Connection timeout"],
  "warnings": []
}
```

## Testing

### Run Error Handler Tests

```bash
cd /c/Projects/web-crawler
python test_error_handler.py
```

### Manual Testing Scenarios

1. **Test Timeout**:
   - Use a very slow website or set low timeout
   - Should show timeout error with retry button

2. **Test 404 Error**:
   - Use URL: `https://example.com/this-page-does-not-exist`
   - Should show 404 error with suggestions, no retry

3. **Test Invalid URL**:
   - Use: `not-a-valid-url`
   - Should show validation error

4. **Test Connection Error**:
   - Use unreachable domain: `https://this-domain-definitely-does-not-exist-12345.com`
   - Should show connection error with retry

5. **Test Element Not Found**:
   - Use valid URL with wrong class: `--class wrong-class-name`
   - Should show content error

## Configuration

### Backend Configuration

In `backend/utils/error_handler.py`, you can customize:
- Error messages per exception type
- Suggestions per HTTP status code
- Retry possibility logic
- Error categorization

### Frontend Configuration

In `frontend/src/components/ResultsModal.jsx`:
- Error banner styling
- Suggestion display format
- Retry button behavior
- Troubleshooting section content

## Troubleshooting

### Error Not Showing in Frontend

1. Check API response includes `failure_info`
2. Verify frontend expects `status: 'failed'` not `status: 'error'`
3. Check browser console for JavaScript errors

### Wrong Error Message Displayed

1. Check exception type in `error_handler.py`
2. Verify mapping logic in `handle_extraction_failure()`
3. Test with `test_error_handler.py`

### Retry Button Not Appearing

1. Check `retry_possible` is `true` in API response
2. Verify condition in ResultsModal component
3. Test error type logic in error_handler

## Files Modified

### Backend
- `backend/utils/error_handler.py` (NEW)
- `backend/api/tasks.py` (MODIFIED)

### Frontend
- `frontend/src/components/ResultsModal.jsx` (MODIFIED)
- `frontend/src/pages/History.jsx` (MODIFIED)

### Documentation
- `dev-spec.md` (UPDATED)
- `FEATURE_FAILED_EXTRACTION_DISPLAY.md` (NEW)
- `FAILED_EXTRACTION_IMPLEMENTATION.md` (NEW)

### Tests
- `test_error_handler.py` (NEW)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in browser console
3. Check backend logs for detailed error traces
4. Run `test_error_handler.py` to verify error handler

## Future Enhancements

Potential improvements:
- Error analytics dashboard
- Automatic retry with exponential backoff
- Email notifications for critical failures
- Error pattern detection
- Machine learning for error resolution suggestions
- Integration with external error tracking services

---

**Version**: 1.0  
**Last Updated**: December 24, 2025  
**Status**: Production Ready ✅

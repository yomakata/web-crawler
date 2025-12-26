# Enhanced Error Messages for Authentication & Content Extraction

## Feature Overview
Enhanced error messages that clearly distinguish between authentication problems and content extraction problems, making it easier to debug issues.

## Problem Solved
Previously, when a scoped element error occurred (e.g., "Scoped element not found: class='content-section'"), it was unclear whether:
- The authentication failed and you got a login page instead
- The authentication succeeded but the CSS class doesn't exist
- The page has a different structure than expected

## Solution Implemented

### Enhanced Error Messages

#### Before:
```
Extraction Failed
Scoped element not found: class='content-section'
Available classes in HTML: button, buttonleft, contentbox, ...
```
**Problem**: Can't tell if authentication worked or not!

#### After:
```
Extraction Failed
✓ Authentication successful - Scoped element not found: class='content-section'
Available classes in HTML: button, buttonleft, contentbox, ...
```
**Clear**: Authentication worked! The issue is just the CSS class name.

Or if authentication failed:
```
Extraction Failed
⚠ HTTP 401 - Scoped element not found: class='content-section'
Available classes in HTML: username, password, login-form, ...
```
**Clear**: Authentication problem! You're seeing a login page.

## Implementation Details

### 1. Enhanced `tasks.py` (Lines 48-74)

**HTTP Status Logging:**
```python
# Fetch page with authentication
response = fetcher.fetch(crawl_request.url, basic_auth=basic_auth)

# Log HTTP status for debugging
logger.info(f"HTTP {response.status_code} - Authentication: {'Success' if response.status_code == 200 else 'May have issues'}")
```

**Enhanced ValueError Handling:**
```python
try:
    if crawl_request.mode == 'content':
        result = _crawl_content_mode(...)
    else:
        result = _crawl_link_mode(...)
except ValueError as ve:
    # Enhanced error message for scoped element errors
    if 'Scoped element not found' in str(ve):
        auth_status = "✓ Authentication successful" if response.status_code == 200 else f"⚠ HTTP {response.status_code}"
        enhanced_error = f"{auth_status} - {str(ve)}"
        raise ValueError(enhanced_error)
    raise
```

### 2. Enhanced `error_handler.py` (Lines 175-196)

**Smart Suggestions Based on Authentication Status:**
```python
if 'Scoped element not found' in str(exception):
    error_msg = str(exception)
    
    # Check if authentication was successful
    auth_successful = '✓ Authentication successful' in error_msg
    
    if auth_successful:
        suggestions = [
            '✓ Page was fetched successfully with authentication',
            '✗ The specified CSS class or ID does not exist on this page',
            'Verify the class name or ID is correct',
            'Try extracting without scope restrictions to see full page content',
            'Use Preview feature to inspect the actual page structure'
        ]
    else:
        suggestions = [
            'Verify the class name or ID is correct',
            'Check if the page structure has changed',
            'If using authentication, verify credentials are correct',
            'Try extracting without scope restrictions first',
            'Inspect the page HTML to confirm the element exists'
        ]
```

## Error Message Interpretation Guide

### HTTP Status Codes in Error Messages

| Status | Meaning | What to Check |
|--------|---------|---------------|
| **✓ Authentication successful** | HTTP 200 OK | ✅ Authentication worked<br>❌ CSS selector is wrong |
| **⚠ HTTP 401** | Unauthorized | ❌ Missing or invalid credentials<br>Check cookies/headers/basic auth |
| **⚠ HTTP 403** | Forbidden | ❌ Credentials provided but access denied<br>Check permissions |
| **⚠ HTTP 404** | Not Found | ❌ Wrong URL or page moved<br>Check URL spelling |
| **⚠ HTTP 302/303** | Redirect | ⚠️ Possibly redirected to login<br>Check authentication |

### Example Scenarios

#### Scenario 1: Successful Auth, Wrong CSS Class
```
✓ Authentication successful - Scoped element not found: class='content-section'
Available classes: button, contentbox, formstyle, wrapper
```
**Diagnosis**: Authentication is working fine. Just use the correct class name.
**Solution**: Change `content-section` to `contentbox` or remove scope entirely.

#### Scenario 2: Authentication Failed
```
⚠ HTTP 401 - Scoped element not found: class='content-section'
Available classes: username, password, login-form, submit-button
```
**Diagnosis**: You're seeing a login page, not the actual content.
**Solution**: Check/fix your cookies, auth headers, or basic auth credentials.

#### Scenario 3: Redirected to Login
```
⚠ HTTP 302 - Scoped element not found: class='content-section'
Available classes: signin, email, password, remember-me
```
**Diagnosis**: Server redirected you to a login page.
**Solution**: Your session may have expired. Get fresh cookies.

#### Scenario 4: No Element Scope Needed
```
✓ Authentication successful - Scoped element not found: class='main-content'
Available classes: container, row, col-md-8, article-body
```
**Diagnosis**: Page structure is different than expected.
**Solution**: Try with an empty scope class to extract the full page first.

## Benefits

### ✅ **Faster Debugging**
Know immediately whether you have an authentication problem or a CSS selector problem.

### ✅ **Better Error Context**
See HTTP status codes and available classes in one message.

### ✅ **Actionable Suggestions**
Get different suggestions based on whether authentication succeeded or failed.

### ✅ **Bulk CSV Clarity**
When crawling 100 URLs, quickly identify which failed due to auth vs CSS issues.

## User Workflow

### When You See an Error:

1. **Check the Status Icon**
   - `✓ Authentication successful` → Focus on CSS selector
   - `⚠ HTTP XXX` → Focus on authentication or URL

2. **Read Available Classes**
   - If you see login-related classes (username, password, signin) → Auth problem
   - If you see content classes (article, content, main) → Selector problem

3. **Follow Suggestions**
   - Each error type provides specific actionable steps
   - Suggestions are prioritized by likelihood

4. **Use Preview Feature**
   - Preview button shows actual page structure
   - See exact HTML and classes before crawling

## Testing

### Test Case 1: Valid Auth + Wrong Selector
```
URL: https://intranet.company.com/news
Auth: Valid cookies
Scope: class='content-section' (doesn't exist)
Expected: "✓ Authentication successful - Scoped element not found..."
```

### Test Case 2: Invalid Auth
```
URL: https://intranet.company.com/news
Auth: Expired/invalid cookies
Scope: class='article-body'
Expected: "⚠ HTTP 401 - Scoped element not found..."
Available classes should show login form elements
```

### Test Case 3: No Auth Needed + Wrong Selector
```
URL: https://public-site.com/page
Auth: None
Scope: class='wrong-class'
Expected: "✓ Authentication successful - Scoped element not found..."
(200 OK even without auth)
```

## Files Modified

- ✅ `backend/api/tasks.py` - Enhanced ValueError handling with HTTP status
- ✅ `backend/utils/error_handler.py` - Smart suggestions based on auth status

## Date
December 25, 2025

## Status
✅ Complete and Ready for Testing

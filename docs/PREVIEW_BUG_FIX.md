# Preview Feature Bug Fixes

## Date: December 25, 2025

## Issues Fixed

### 1. Response Object Handling Error
**Problem:** Preview endpoint was treating `Response` object as string
**Error Message:** `AttributeError: 'Response' object has no attribute` or type errors when trying to parse HTML

**Root Cause:**
```python
# WRONG - returns Response object
html = fetcher.fetch(url, basic_auth=basic_auth)
```

**Fix Applied:**
```python
# CORRECT - extract .text from Response
response = fetcher.fetch(url, basic_auth=basic_auth)
html = response.text
```

**File Modified:** `backend/api/routes.py` (lines 403-411)

---

### 2. Cookie String Sanitization Error
**Problem:** User could paste "cookie:" header name along with values, causing newline characters in cookie string
**Error Message:** `Invalid header value b'.ASPXAUTH=...\\ncookie\\nASP.NET_SessionId=...'`

**Root Cause:**
When copying from Chrome DevTools, users might accidentally copy:
```
cookie: .ASPXAUTH=value1; ASP.NET_SessionId=value2
```

This includes the "cookie:" prefix and may include newline characters.

**Fix Applied:**
Enhanced cookie parser to sanitize input:
```javascript
const parseCookieString = (cookieStr) => {
  // Sanitize input: remove "cookie:" prefix, newlines, carriage returns
  let trimmed = cookieStr.trim()
    .replace(/^cookie[:\s]+/i, '')  // Remove "cookie:" or "Cookie:" prefix
    .replace(/\n/g, '; ')           // Replace newlines with semicolons
    .replace(/\r/g, '')             // Remove carriage returns
    .trim();
  
  // ... rest of parsing logic
}
```

**File Modified:** `frontend/src/components/CrawlForm.jsx` (lines 28-66)

---

## Testing Instructions

### 1. Test with Proper Cookie Format
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Find request to your intranet site
4. In Request Headers, find `cookie:` header
5. **Copy ONLY the cookie values** (everything after "cookie:")
6. Paste into the "Cookies" field in the crawler
7. Click "Preview Page"

### 2. Test with Messy Input (Now Handled)
The parser now handles:
- `cookie: value1=a; value2=b` (includes "cookie:" prefix)
- Multi-line cookie strings with `\n` characters
- Extra whitespace and carriage returns
- Both Chrome DevTools format and JSON format

### 3. Expected Results
✅ **Success Case:** Green banner showing "Page loaded successfully!", element status, and page info
❌ **Auth Failed:** Yellow/red banner showing error, but with helpful diagnostic info

---

## What Got Fixed

### Backend Changes
1. ✅ Fixed `response.text` extraction in preview endpoint
2. ✅ Preview now properly handles Response object from fetcher

### Frontend Changes
1. ✅ Cookie parser removes "cookie:" prefix (case-insensitive)
2. ✅ Cookie parser converts newlines to semicolons
3. ✅ Cookie parser removes carriage returns
4. ✅ Better handling of messy copy-paste from DevTools

### Deployment
1. ✅ Backend container rebuilt and restarted
2. ✅ Frontend container rebuilt and restarted
3. ✅ All containers running (backend:5000, frontend:3000, redis:6379)

---

## How to Copy Cookies Correctly

### Method 1: Copy Just Values (Recommended)
```
# In Chrome DevTools Network tab, find your request
# Look at Request Headers section
# Find: cookie: .ASPXAUTH=ABC123; ASP.NET_SessionId=XYZ789
# Copy: .ASPXAUTH=ABC123; ASP.NET_SessionId=XYZ789
# (Everything AFTER "cookie:")
```

### Method 2: Copy Everything (Now Works!)
```
# Even if you copy:
cookie: .ASPXAUTH=ABC123; ASP.NET_SessionId=XYZ789

# The parser will automatically strip "cookie:" and clean it up
```

---

## Next Steps

1. **Test Preview**: Click "Preview Page" button with your cookies
2. **Verify Element**: Check if scoped element (class="content-section") is found
3. **Continue Extraction**: If preview succeeds, click "Continue with Extraction"
4. **Download Results**: Review extracted content in your chosen format

---

## Technical Details

### Files Modified
1. `backend/api/routes.py` - Fixed Response.text extraction (lines 403-411)
2. `frontend/src/components/CrawlForm.jsx` - Enhanced cookie parser (lines 28-66)

### Containers Rebuilt
- `webcrawler-backend` - Running on port 5000
- `webcrawler-frontend` - Running on port 3000
- `webcrawler-redis` - Running on port 6379

### Related Documentation
- [COOKIE_PARSER_GUIDE.md](./COOKIE_PARSER_GUIDE.md) - How to use cookie authentication
- [PAGE_PREVIEW_GUIDE.md](./PAGE_PREVIEW_GUIDE.md) - How to use preview feature
- [PREVIEW_FEATURE_COMPLETE.md](./PREVIEW_FEATURE_COMPLETE.md) - Complete feature overview

---

## Status: ✅ FIXED AND DEPLOYED

Both issues are now resolved. The preview feature should work correctly with authenticated pages.

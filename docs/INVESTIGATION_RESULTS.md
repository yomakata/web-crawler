# Investigation Results: Scoped Element Not Found Issue

## Executive Summary

The class `content-section` **DOES exist** on the page (confirmed from your browser screenshot), but the web crawler **cannot access the page** because it's an **intranet URL** that requires special network access.

## Root Cause Analysis

### The Real Problem: Network Access

**URL**: `https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer`

This is an **intranet/internal company URL**, which means:

1. ✅ **Your browser CAN access it** - You're logged into your company network/VPN
2. ❌ **The Docker container CANNOT access it** - It's isolated from your internal network
3. ❌ **The crawler fails to fetch** the HTML, so it never sees the `content-section` class

### Why the Error Message is Misleading

When the crawler cannot fetch the page OR fetches an error page:
- The fetcher might return a login page, error page, or empty HTML
- The parser correctly doesn't find `content-section` (because it's not in the error HTML)
- Error message says "Scoped element not found" when it should say "Cannot access intranet URL"

## Evidence

From your screenshot:
- ✅ The page **does** have `<div id="content-section">` with class `content-section`
- ✅ The page uses Botframework WebChat (visible in scripts)
- ✅ Your browser can see and render the page

From our tests:
- ❌ Docker container times out trying to reach `intranet.dtgo.com`
- ❌ No HTTP response received (connection timeout)

## Solutions

### Solution 1: Use VPN/Network Bridge (Recommended for Docker)

If you need to crawl intranet pages from Docker, configure network access:

```yaml
# docker-compose.yml
services:
  backend:
    network_mode: "host"  # Use host network to access intranet
    # ... rest of config
```

**Pros**: Allows Docker to access your company intranet  
**Cons**: Reduces container isolation

### Solution 2: Run Crawler Locally (Not in Docker)

For intranet URLs, run the Python crawler **directly on your machine** instead of Docker:

```bash
# Install dependencies locally
cd backend
pip install -r requirements.txt

# Run crawler directly
python main.py --url https://intranet.dtgo.com/... --mode content --class content-section
```

**Pros**: Direct access to your network/VPN  
**Cons**: Requires local Python setup

### Solution 3: Add Proxy Support (For Corporate Proxy)

If your company uses a proxy for intranet access:

**Modify `fetcher.py`:**
```python
def fetch(self, url: str, proxies: dict = None) -> requests.Response:
    # ...
    response = self.session.get(
        url,
        headers=headers,
        timeout=self.timeout,
        proxies=proxies  # Add proxy support
    )
```

**Usage:**
```python
proxies = {
    'http': 'http://proxy.company.com:8080',
    'https': 'http://proxy.company.com:8080',
}
fetcher.fetch(url, proxies=proxies)
```

### Solution 4: Better Error Detection (What I've Already Fixed)

I've improved the error handling and diagnostics:

**Enhanced `parser.py`:**
- ✅ Tries 3 different methods to find elements (more flexible)
- ✅ Lists available classes when element not found (helps debug)
- ✅ Detects JavaScript frameworks (identifies dynamic content)
- ✅ Provides better error messages with diagnostic info

**Enhanced `error_handler.py`:**
- ✅ Properly categorizes "element not found" as `content_error`
- ✅ Shows actionable suggestions
- ✅ Distinguishes between network errors and parsing errors

## For Your Specific Case

Since you're crawling an **intranet URL**:

### Option A: Test with Docker using host network

```bash
# Edit docker-compose.yml temporarily
# Add under backend service:
#   network_mode: "host"

docker-compose down
docker-compose up -d
```

### Option B: Use the API/Web interface from your local machine

If your local machine (where the browser runs) can access the intranet:
- The browser at `localhost:3000` can send the URL to backend
- Backend in Docker might still fail (network issue)
- **Solution**: Run backend locally too, or use network_mode: host

### Option C: Test with a public URL first

To verify the crawler works correctly, test with a public URL:

```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "mode": "content",
    "formats": ["txt"],
    "scope_class": "content-section"
  }'
```

This will prove whether:
- ✅ The crawler works fine for accessible URLs
- ❌ The issue is specifically network/intranet access

## Updated Error Messages

With my improvements, you'll now see better diagnostics:

### Before
```
Error: Scoped element not found: class='content-section'
Error Type: Unknown
```

### After (if network fails)
```
Error: Connection timeout - Server took too long to respond
Error Type: NETWORK_ERROR
Suggestions:
  - Check your internet connection
  - The server may be down or unreachable
  - VPN may be required for intranet URLs
```

### After (if element genuinely missing)
```
Error: Scoped element not found: class='content-section'
Available classes in HTML: wrapper, header, footer, nav, main-content, ...
Error Type: CONTENT_ERROR
Suggestions:
  - Verify the class name or ID is correct
  - Check if the page structure has changed
```

## Recommended Next Steps

1. **Test with a public URL** to verify the crawler works
2. **Check network access** - Can Docker reach intranet.dtgo.com?
3. **Consider running backend locally** for intranet crawling
4. **Or use Docker host networking** for intranet access
5. **Check if VPN is required** and ensure Docker can use it

## Additional Improvements Made

Even though the root cause is network access, I've made the crawler more robust:

1. ✅ **Multiple element finding strategies** - tries 3 different BeautifulSoup methods
2. ✅ **Better error diagnostics** - shows available classes when element not found
3. ✅ **JavaScript detection** - warns if page uses dynamic rendering
4. ✅ **Network error handling** - properly categorizes timeout vs element not found
5. ✅ **Diagnostic tool** - `diagnose_fetch.py` to debug fetch issues

## Files Modified

1. ✅ `backend/crawler/parser.py` - Enhanced element finding with 3 methods
2. ✅ `backend/utils/error_handler.py` - Better error categorization (previous fix)
3. 📄 `diagnose_fetch.py` - New diagnostic tool
4. 📄 `INVESTIGATION_RESULTS.md` - This document

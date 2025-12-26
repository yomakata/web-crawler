# Authentication Guide - Crawling Intranet/Protected Sites

## Overview

The web crawler now supports **authenticated sessions** for crawling intranet sites and protected pages that require login. Three authentication methods are supported:

1. **🍪 Cookie-based Authentication** (Recommended for intranet sites)
2. **🔑 HTTP Basic Authentication**
3. **🎫 Token/Header-based Authentication**

---

## Method 1: Cookie-based Authentication (Recommended)

This is the **best method for intranet sites** where you log in through a web browser.

### Step 1: Extract Cookies from Your Browser

After logging into the intranet site in your browser:

#### Using Chrome/Edge Developer Tools:
1. Open the intranet site in your browser
2. Log in successfully
3. Press `F12` to open Developer Tools
4. Go to **Application** tab
5. Expand **Cookies** in the left sidebar
6. Click on your domain (e.g., `intranet.dtgo.com`)
7. Find the authentication cookies (usually named `session`, `auth_token`, `ASP.NET_SessionId`, etc.)
8. Copy the **Name** and **Value** of each cookie

#### Using Firefox:
1. Open Developer Tools (`F12`)
2. Go to **Storage** tab
3. Expand **Cookies**
4. Copy cookie names and values

### Step 2: Use Cookies in API Request

```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer",
    "mode": "content",
    "formats": ["txt"],
    "scope_class": "content-section",
    "cookies": {
      "ASP.NET_SessionId": "your-session-id-here",
      "AuthToken": "your-auth-token-here"
    }
  }'
```

### Step 3: Test in Frontend (React)

Update `frontend/src/services/api.js` or use the form:

```javascript
const response = await crawlAPI.crawlSingle({
  url: 'https://intranet.dtgo.com/...',
  mode: 'content',
  formats: ['txt'],
  scope_class: 'content-section',
  cookies: {
    'ASP.NET_SessionId': 'your-session-id',
    'AuthToken': 'your-token'
  }
});
```

---

## Method 2: HTTP Basic Authentication

For sites using HTTP Basic Auth (popup username/password).

### API Request Example:

```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://intranet.example.com/page",
    "mode": "content",
    "formats": ["txt"],
    "basic_auth_username": "your-username",
    "basic_auth_password": "your-password"
  }'
```

### JavaScript Example:

```javascript
const response = await crawlAPI.crawlSingle({
  url: 'https://intranet.example.com/page',
  mode: 'content',
  basic_auth_username: 'your-username',
  basic_auth_password: 'your-password'
});
```

---

## Method 3: Token/Header-based Authentication

For APIs or sites using Bearer tokens, API keys, or custom headers.

### API Request Example:

```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.example.com/data",
    "mode": "content",
    "formats": ["txt"],
    "auth_headers": {
      "Authorization": "Bearer your-jwt-token-here",
      "X-API-Key": "your-api-key-here"
    }
  }'
```

### JavaScript Example:

```javascript
const response = await crawlAPI.crawlSingle({
  url: 'https://api.example.com/data',
  mode: 'content',
  auth_headers: {
    'Authorization': 'Bearer ' + jwtToken,
    'X-API-Key': apiKey
  }
});
```

---

## Complete Example: Crawling Your Intranet Site

### Your Specific Case (intranet.dtgo.com)

```bash
# 1. Log into https://intranet.dtgo.com in your browser
# 2. Open Developer Tools (F12) → Application → Cookies
# 3. Copy the session cookies
# 4. Use them in the API request:

curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer",
    "mode": "content",
    "formats": ["txt"],
    "scope_class": "content-section",
    "cookies": {
      "ASP.NET_SessionId": "paste-your-session-id-here",
      ".AspNet.ApplicationCookie": "paste-cookie-value-if-exists"
    }
  }'
```

---

## Adding Cookie Support to Frontend UI

### Option A: Add Authentication Fields to CrawlForm

Update `frontend/src/components/CrawlForm.jsx`:

```jsx
import { useState } from 'react';

export default function CrawlForm() {
  const [showAuthOptions, setShowAuthOptions] = useState(false);
  const [cookies, setCookies] = useState('');
  
  return (
    <form>
      {/* ...existing fields... */}
      
      {/* Authentication Section */}
      <div className="mt-4">
        <button
          type="button"
          onClick={() => setShowAuthOptions(!showAuthOptions)}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          {showAuthOptions ? '− Hide' : '+ Show'} Authentication Options
        </button>
        
        {showAuthOptions && (
          <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cookies (JSON format)
              </label>
              <textarea
                value={cookies}
                onChange={(e) => setCookies(e.target.value)}
                placeholder='{"session_id": "abc123", "auth_token": "xyz789"}'
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows="3"
              />
              <p className="text-xs text-gray-500 mt-1">
                For intranet sites: Copy cookies from browser Developer Tools
              </p>
            </div>
            
            {/* Add more auth options here */}
          </div>
        )}
      </div>
    </form>
  );
}
```

### Option B: Create a Browser Extension Helper

Create a simple bookmarklet to extract cookies:

```javascript
javascript:(function(){
  const cookies = document.cookie.split(';').reduce((acc, cookie) => {
    const [name, value] = cookie.trim().split('=');
    acc[name] = value;
    return acc;
  }, {});
  const json = JSON.stringify(cookies, null, 2);
  prompt('Copy these cookies to the crawler:', json);
})();
```

**Usage:**
1. Bookmark this code
2. Log into your intranet site
3. Click the bookmarklet
4. Copy the displayed cookies
5. Paste into the crawler form

---

## Security Considerations

### ⚠️ Important Security Notes:

1. **Never commit credentials to Git**
   - Add `.env` to `.gitignore`
   - Store cookies/tokens in environment variables

2. **Cookie Expiration**
   - Session cookies expire when you close your browser
   - You may need to refresh cookies periodically

3. **Token Rotation**
   - Tokens may expire (typically 1-24 hours)
   - Refresh tokens before making new requests

4. **HTTPS Only**
   - Only use authentication over HTTPS
   - Cookies/tokens sent over HTTP are insecure

5. **Backend Security**
   ```python
   # In .env file:
   INTRANET_SESSION_COOKIE=your-session-cookie
   INTRANET_AUTH_TOKEN=your-auth-token
   
   # In code:
   import os
   cookies = {
       'session': os.getenv('INTRANET_SESSION_COOKIE')
   }
   ```

---

## Troubleshooting

### Problem: Still getting "401 Unauthorized" or "403 Forbidden"

**Solutions:**
1. Check cookie names are correct (case-sensitive)
2. Verify cookies haven't expired
3. Try copying ALL cookies, not just session ones
4. Check if site requires multiple cookies to work together

### Problem: Cookies work in browser but not in crawler

**Solutions:**
1. Check if site validates User-Agent header
2. Try copying more cookies (some sites check multiple)
3. Verify no CSRF token is required
4. Check if site uses JavaScript to set additional cookies

### Problem: Content still shows login page

**Solutions:**
1. The session may have expired - log in again and get new cookies
2. Check if site requires specific headers (Referer, Origin)
3. Some sites detect automated access - try adding more browser-like headers

---

## Testing Authentication

### Quick Test Script

Save as `test_auth.sh`:

```bash
#!/bin/bash

# Replace with your actual cookies
SESSION_ID="your-session-id"
AUTH_TOKEN="your-auth-token"

curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer\",
    \"mode\": \"content\",
    \"formats\": [\"txt\"],
    \"scope_class\": \"content-section\",
    \"cookies\": {
      \"ASP.NET_SessionId\": \"$SESSION_ID\",
      \"AuthToken\": \"$AUTH_TOKEN\"
    }
  }" | jq .
```

Run: `bash test_auth.sh`

---

## Next Steps

1. ✅ **Log into your intranet site**
2. ✅ **Extract session cookies** from browser
3. ✅ **Test with curl** to verify authentication works
4. ✅ **Integrate into your frontend** if needed
5. ✅ **Set up environment variables** for production

---

## API Reference

### Request Schema with Authentication

```json
{
  "url": "string (required)",
  "mode": "content|link",
  "formats": ["txt", "md", "html"],
  "scope_class": "string (optional)",
  "scope_id": "string (optional)",
  "download_images": boolean,
  
  // Authentication (all optional)
  "cookies": {
    "cookie_name": "cookie_value"
  },
  "auth_headers": {
    "Authorization": "Bearer token",
    "X-Custom-Header": "value"
  },
  "basic_auth_username": "string",
  "basic_auth_password": "string"
}
```

---

For more help, see:
- `INVESTIGATION_RESULTS.md` - Why authentication was needed
- `QUICK_FIX_SUMMARY.md` - Network access issues
- Backend API documentation: http://localhost:5000/api/docs

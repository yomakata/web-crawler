# Quick Start: Crawl Your Intranet Site with Authentication

## Your Specific URL
`https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer`

## 🎯 Solution: Use Session Cookies

Since this is an intranet site that requires login, you need to **extract your session cookies** from your browser and pass them to the crawler.

---

## Step-by-Step Instructions

### Step 1: Get Your Session Cookies

1. **Open your browser** (Chrome, Edge, or Firefox)

2. **Navigate to** and **log into** your intranet site:
   ```
   https://intranet.dtgo.com
   ```

3. **Open Developer Tools**:
   - Press `F12` or
   - Right-click → Inspect → Application tab

4. **Find Cookies**:
   - In the left sidebar, expand **Cookies**
   - Click on `https://intranet.dtgo.com`

5. **Copy ALL cookie names and values** you see, especially:
   - `ASP.NET_SessionId` (or similar session cookie)
   - `.AspNet.ApplicationCookie` (if exists)
   - Any other authentication-related cookies

   Example:
   ```
   Name: ASP.NET_SessionId
   Value: 5wxyz123abc456def789ghi012jkl345
   
   Name: .AspNet.ApplicationCookie  
   Value: longbase64encodedvalue==
   ```

### Step 2: Test with curl

Replace the cookie values with yours:

```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer",
    "mode": "content",
    "formats": ["txt"],
    "scope_class": "content-section",
    "cookies": {
      "ASP.NET_SessionId": "PASTE_YOUR_SESSION_ID_HERE",
      ".AspNet.ApplicationCookie": "PASTE_YOUR_COOKIE_VALUE_HERE"
    }
  }'
```

### Step 3: Check the Result

The response should show:
```json
{
  "job_id": "abc-123-xyz",
  "status": "completed",
  "result": {
    "status": "success",
    "url": "https://intranet.dtgo.com/...",
    "output_files": ["intranet_dtgo_com_...txt"]
  }
}
```

✅ **Success!** The crawler can now access your intranet page.

---

## Alternative: Use the Web Interface

### Option 1: Simple curl with saved cookies

Create a file `my_cookies.json`:
```json
{
  "ASP.NET_SessionId": "your-session-id-here",
  ".AspNet.ApplicationCookie": "your-cookie-value-here"
}
```

Then use:
```bash
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "url": "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer",
  "mode": "content",
  "formats": ["txt"],
  "scope_class": "content-section",
  "cookies": $(cat my_cookies.json)
}
EOF
```

### Option 2: Use Postman

1. Open Postman
2. Create POST request to: `http://localhost:5000/api/crawl/single`
3. Set Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "url": "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer",
  "mode": "content",
  "formats": ["txt"],
  "scope_class": "content-section",
  "cookies": {
    "ASP.NET_SessionId": "paste-here",
    ".AspNet.ApplicationCookie": "paste-here"
  }
}
```

---

## Troubleshooting

### ❌ Still getting "Scoped element not found"?

**Possible causes:**

1. **Cookies expired** → Log in again and get fresh cookies
2. **Wrong cookie names** → Copy ALL cookies from browser
3. **Site requires multiple cookies** → Make sure you copied all of them
4. **CSRF protection** → Some sites need additional headers

### ✅ How to verify cookies are working:

The crawler should now:
- ✅ Successfully fetch the page (no timeout)
- ✅ See the `content-section` class in the HTML
- ✅ Extract content successfully
- ✅ Create output files

If you still see "element not found" but NO timeout, it means:
- ✅ Authentication works (page is loading)
- ❌ The class name might be wrong (check spelling: `content-section` vs `content_section`)

---

## Security Reminder

⚠️ **Never share your session cookies publicly!** They give full access to your intranet account.

- Cookies are like temporary passwords
- They expire when you log out or after some time
- Keep them secret and secure

---

## Need More Help?

### Check if authentication is working:

```bash
# Test 1: Without cookies (should fail or show login page)
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer",
    "mode": "content",
    "formats": ["txt"]
  }'

# Test 2: With cookies (should succeed)
curl -X POST http://localhost:5000/api/crawl/single \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer",
    "mode": "content",
    "formats": ["txt"],
    "cookies": {"ASP.NET_SessionId": "your-session-id"}
  }'
```

Compare the results - Test 2 should succeed!

---

## Full Documentation

- 📄 **AUTHENTICATION_GUIDE.md** - Complete authentication documentation
- 📄 **INVESTIGATION_RESULTS.md** - Why this was needed
- 📄 **QUICK_FIX_SUMMARY.md** - Network issues explained

---

## Summary

**Problem**: Intranet site requires login  
**Solution**: Pass session cookies from your browser to the crawler  
**Method**: Extract cookies using F12 Developer Tools  
**Result**: Crawler can now access authenticated pages ✅

Happy crawling! 🎉

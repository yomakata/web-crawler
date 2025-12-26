# Using the Frontend with Authentication

## ✅ YES, You Can Crawl Intranet Sites via Frontend!

The frontend now has **built-in authentication support** for crawling protected/intranet sites.

---

## How to Use (Step by Step)

### Step 1: Access the Web Interface

Open your browser and go to:
```
http://localhost:3000
```

### Step 2: Fill in the Basic Fields

1. **Input Method**: Select "Single URL"
2. **Mode**: Choose "Content" (or "Link")
3. **URL**: Paste your intranet URL
   ```
   https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer
   ```
4. **Scope Class**: Enter `content-section`
5. **Output Formats**: Check "txt" (or any format you want)

### Step 3: Add Authentication (NEW! 🔐)

1. **Click "Show Authentication Options"** at the bottom of the form

2. **Extract your cookies** from the browser:
   - Stay logged into your intranet site
   - Press **F12** (Developer Tools)
   - Go to **Application** tab → **Cookies**
   - Copy the cookie names and values

3. **Paste cookies in JSON format**:
   ```json
   {
     "ASP.NET_SessionId": "your-session-id-here",
     ".AspNet.ApplicationCookie": "your-cookie-value-here"
   }
   ```

### Step 4: Start Crawling

Click the **"Start Crawling"** button!

---

## What the Form Looks Like Now

```
┌─────────────────────────────────────────────┐
│  Web Crawler                                │
├─────────────────────────────────────────────┤
│  Input Method: [Single URL] [Bulk CSV]     │
│                                             │
│  Mode: [Content] [Link]                     │
│                                             │
│  URL: https://intranet.dtgo.com/...        │
│                                             │
│  Scope Class: content-section               │
│                                             │
│  Output Formats: ☑ txt ☐ md ☐ html        │
│                                             │
│  🔐 Show Authentication Options ▼           │
│  ┌───────────────────────────────────────┐ │
│  │ 🔐 For Intranet/Protected Sites       │ │
│  │ If crawling a site that requires      │ │
│  │ login, extract cookies from browser.  │ │
│  │                                        │ │
│  │ Cookies (JSON):                        │ │
│  │ {"ASP.NET_SessionId": "abc123"}       │ │
│  │                                        │ │
│  │ Auth Headers (JSON): [Optional]        │ │
│  │ {"Authorization": "Bearer token"}     │ │
│  │                                        │ │
│  │ HTTP Basic Auth: [Optional]            │ │
│  │ Username: ___________                  │ │
│  │ Password: ___________                  │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [▶ Start Crawling]                        │
└─────────────────────────────────────────────┘
```

---

## Authentication Methods Available

### Method 1: Cookies (BEST for Intranet Sites) 🍪

**When to use**: Company intranet, SharePoint, any site where you log in via browser

**Format**:
```json
{
  "ASP.NET_SessionId": "your-session-cookie",
  ".AspNet.ApplicationCookie": "your-auth-cookie"
}
```

**How to get cookies**:
1. Log into your intranet in the browser
2. F12 → Application → Cookies → intranet.dtgo.com
3. Copy all cookie names and values
4. Format as JSON
5. Paste into "Cookies" field

### Method 2: Authentication Headers 🎫

**When to use**: APIs with Bearer tokens, custom auth headers

**Format**:
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "X-API-Key": "your-api-key-here"
}
```

### Method 3: HTTP Basic Auth 🔑

**When to use**: Sites with popup username/password prompt

**How to use**:
- Enter username in "HTTP Basic Auth Username" field
- Enter password in "HTTP Basic Auth Password" field

---

## Complete Example: Your Intranet Site

### What You Need:

1. ✅ **URL**: `https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer`
2. ✅ **Scope Class**: `content-section`
3. ✅ **Cookies**: From your browser after logging in

### Step-by-Step:

1. **Log into** `https://intranet.dtgo.com` in Chrome/Edge

2. **Keep that tab open**, press F12, go to Application → Cookies

3. **Copy cookies** - you'll see something like:
   ```
   Name: ASP.NET_SessionId
   Value: 5wxyz123abc456def789ghi012jkl345
   
   Name: .AspNet.ApplicationCookie
   Value: very_long_base64_encoded_string_here==
   ```

4. **Format as JSON**:
   ```json
   {
     "ASP.NET_SessionId": "5wxyz123abc456def789ghi012jkl345",
     ".AspNet.ApplicationCookie": "very_long_base64_encoded_string_here=="
   }
   ```

5. **Go to** `http://localhost:3000`

6. **Fill the form**:
   - URL: `https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer`
   - Mode: Content
   - Scope Class: `content-section`
   - Click "Show Authentication Options"
   - Paste your JSON cookies

7. **Click "Start Crawling"** ✅

8. **View results** in the modal that appears!

---

## Troubleshooting

### ❌ Error: "Invalid JSON format for cookies"

**Problem**: JSON syntax error

**Solution**: Check your JSON:
- ✅ Use double quotes: `"key": "value"`
- ✅ Separate with commas: `{"key1": "val1", "key2": "val2"}`
- ❌ Don't use single quotes
- ❌ No trailing commas

**Valid**:
```json
{"session": "abc123", "token": "xyz789"}
```

**Invalid**:
```json
{'session': 'abc123', 'token': 'xyz789',}
```

### ❌ Still getting "Scoped element not found"

**Possible causes**:

1. **Cookies expired** → Log in again and get fresh cookies
2. **Wrong cookies** → Make sure you copied ALL cookies
3. **Missing cookies** → Some sites need multiple cookies to work

**How to fix**: Copy ALL cookies from the Application tab, not just one

### ❌ Shows login page instead of content

**Problem**: Authentication not working

**Solution**:
1. Verify you're still logged in on the intranet tab
2. Copy cookies again (they may have expired)
3. Make sure cookie names match exactly (case-sensitive)
4. Try copying ALL cookies, not just session ones

---

## Security Tips 🔒

### ⚠️ Important:

1. **Never share your cookies** - they're like temporary passwords
2. **Cookies expire** - you may need to refresh them periodically
3. **Use HTTPS only** - never send cookies over HTTP
4. **Close browser when done** - to invalidate session cookies

### For Production:

If you're using this regularly:
1. Consider storing cookies in environment variables
2. Set up automatic cookie refresh
3. Use a secrets management system

---

## Summary

✅ **YES, you CAN use the frontend** to crawl intranet sites!

**Just**:
1. Open http://localhost:3000
2. Fill in your URL and scope class
3. Click "Show Authentication Options"
4. Paste your browser cookies (F12 → Application → Cookies)
5. Click "Start Crawling"

**That's it!** 🎉

---

## Need Help?

- See `AUTHENTICATION_GUIDE.md` for detailed auth documentation
- See `INTRANET_QUICKSTART.md` for curl examples
- Check backend logs: `docker-compose logs backend`

Happy crawling! 🚀

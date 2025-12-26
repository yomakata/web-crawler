# Cookie Parser Guide

## Overview
The crawler now supports **two formats** for entering cookies:

1. **Chrome DevTools Format** (Recommended - Easy Copy/Paste)
2. **JSON Format** (Manual Entry)

## Method 1: Chrome DevTools Format (Easiest)

### Step 1: Open DevTools
Press `F12` or right-click → Inspect

### Step 2: Go to Network Tab
1. Click on the **Network** tab
2. Refresh the page (F5) if no requests appear
3. Click on **any request** to your intranet site

### Step 3: Copy Cookie Value
1. Scroll down to **Request Headers** section
2. Find the `cookie:` field
3. **Copy the entire value** (everything after "cookie:")

### Example of what you'll copy:
```
ASP.NET_SessionId=0nefhpyqznpqqdxphy5doz3g; _gid=GA1.2.1610841898.1766569092; .ASPXAUTH=58F6D585724E1F7026C5C10525E7201D6819F60236F0624122BF5834BE068ADCB6971523AAF4915A4EA917AB37493F564ABC92E254F89B1AB6F2DCBD5C125DD318199F55DB63489960B84D87B96EA56C0429004129151E64B033192568A9847B72D16311; _ga=GA1.2.2036924830.1766569092
```

### Step 4: Paste Into Crawler
1. Go to http://localhost:3000
2. Click **"Show Authentication Options"**
3. Make sure **"Cookies"** method is selected
4. **Paste the entire string** into the Cookies field
5. Click **"Start Crawling"**

✅ **The parser automatically converts it to the correct format!**

---

## Method 2: JSON Format (Manual)

If you prefer to manually format cookies as JSON:

```json
{
  "ASP.NET_SessionId": "0nefhpyqznpqqdxphy5doz3g",
  ".ASPXAUTH": "58F6D585724E1F7026C5C10525E7201D6819F60236F0624122BF5834BE068ADCB6971523AAF4915A4EA917AB37493F564ABC92E254F89B1AB6F2DCBD5C125DD318199F55DB63489960B84D87B96EA56C0429004129151E64B033192568A9847B72D16311",
  "_ga": "GA1.2.2036924830.1766569092"
}
```

---

## How The Parser Works

The `parseCookieString()` function automatically detects which format you're using:

### If it starts with `{` → Parses as JSON
```javascript
{ "cookie1": "value1", "cookie2": "value2" }
```

### Otherwise → Parses as semicolon-separated format
```javascript
cookie1=value1; cookie2=value2; cookie3=value3
```

The parser:
1. Splits on semicolons (`;`)
2. Finds the first `=` in each pair
3. Extracts key and value
4. Builds a JSON object
5. Sends to backend

---

## Common Cookies for Intranet Sites

### ASP.NET Sites (Most Company Intranets)
You need these cookies:
- `ASP.NET_SessionId` - Session identifier
- `.ASPXAUTH` - Authentication token

### PHP Sites
- `PHPSESSID` - Session identifier

### Other Frameworks
- `sessionid` - Generic session ID
- `auth_token` - Authentication token
- `jwt` - JSON Web Token

---

## Troubleshooting

### Error: "Invalid cookie format"
- Make sure you copied the entire cookie value
- Check there are no extra spaces or quotes
- Verify cookies are separated by semicolons (`;`)

### Error: "No valid cookies found"
- The string must contain at least one `key=value` pair
- Check you didn't copy just the cookie names without values

### Cookies Not Working
- Cookies may have expired - log in again and get fresh cookies
- You might need additional cookies - copy ALL cookies from the request
- The site might require specific headers too (use Headers method)

---

## Best Practices

1. ✅ **Always copy from Network tab** (not Application/Storage tab)
   - Network tab shows the exact cookies sent with requests
   
2. ✅ **Copy from a successful authenticated request**
   - Make sure you're logged in first
   - The request should return 200 OK, not redirect to login

3. ✅ **Include all cookies** if unsure
   - The parser will accept all cookies
   - The backend will send them all to the target site

4. ✅ **Refresh cookies if they expire**
   - Many session cookies expire after 20-60 minutes
   - Just copy new ones from DevTools

---

## Examples

### Example 1: Copy/Paste from Chrome
**What you copy from DevTools:**
```
ASP.NET_SessionId=abc123; .ASPXAUTH=xyz789
```

**What gets sent to backend:**
```json
{
  "ASP.NET_SessionId": "abc123",
  ".ASPXAUTH": "xyz789"
}
```

### Example 2: Already JSON
**What you paste:**
```json
{"sessionid": "abc123", "token": "xyz789"}
```

**What gets sent to backend:**
```json
{
  "sessionid": "abc123",
  "token": "xyz789"
}
```

Both formats work perfectly! 🎉

---

## Quick Reference

| Action | Location | What to Copy |
|--------|----------|-------------|
| Open DevTools | `F12` | - |
| Go to Network | Top tabs | Click Network |
| Pick a request | Left panel | Any request to your site |
| Find cookies | Request Headers | `cookie:` field |
| Copy value | After "cookie:" | Everything on that line |
| Paste in form | Cookies field | Ctrl+V |

---

## Video Tutorial Equivalent

1. F12 → Network tab
2. Refresh page (F5)
3. Click any request
4. Scroll to "Request Headers"
5. Find "cookie:"
6. Triple-click to select entire line
7. Copy (Ctrl+C)
8. Paste into crawler (Ctrl+V)
9. Click "Start Crawling"

Done! ✅

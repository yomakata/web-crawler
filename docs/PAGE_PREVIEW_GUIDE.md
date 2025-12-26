# Page Preview Feature Guide

## Overview
The **Page Preview** feature lets you verify that authentication worked and the target element exists BEFORE starting the actual extraction. This saves time and helps you debug authentication and scope issues.

## How to Use

### Step 1: Fill in the Form
1. **Enter URL**: https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer
2. **Select Mode**: Content
3. **Enter Scope Class**: content-section
4. **Add Authentication** (if needed):
   - Click "Show Authentication Options"
   - Select "Cookies" method
   - Paste your cookies from DevTools

### Step 2: Click "Preview Page"
Instead of "Start Crawling", click the **"Preview Page"** button.

### Step 3: Review the Preview
The preview modal will show you:

#### ✅ Success Indicators
- **Green banner**: "Page loaded successfully!"
- **Authentication worked**: You're seeing the actual page content
- **Status code**: 200 OK

#### Page Information
- **Title**: The page's `<title>` tag
- **URL**: Confirms which page was loaded
- **Content Size**: Total HTML size in KB
- **Text Length**: Amount of extractable text

#### Scoped Element Check
This is the MOST IMPORTANT section:

**✅ If scoped element is FOUND:**
```
Scoped Element Found ✓
Tag: <div>
Text Length: 1,234 characters

Content Preview:
[First 500 characters of the scoped content]
```

**❌ If scoped element is NOT FOUND:**
```
Scoped Element NOT Found
The specified class/ID was not found on this page.

Available classes (top 20):
button buttonleft contentbox effect-10 
formstyle hidden icon...
```

#### Page Statistics
- **Links**: Number of `<a>` tags
- **Images**: Number of `<img>` tags
- **Paragraphs**: Number of `<p>` tags

### Step 4: Decision
Based on the preview:

**✅ If Element Found** → Click **"Continue with Extraction"**
- This will immediately start the crawl
- No need to re-enter information

**❌ If Element NOT Found** → Click "Close" and fix the issue:
1. Check the "Available classes" list
2. Update your Scope Class to match one of them
3. Click "Preview Page" again

---

## Common Scenarios

### Scenario 1: Authentication Failed
**Preview shows:**
- Error: "Failed to load page"
- Or: Page loads but shows login form content

**Solution:**
1. Get fresh cookies from browser (F12 → Network tab)
2. Make sure you're logged in
3. Copy the entire cookie string from a successful request
4. Try preview again

---

### Scenario 2: Wrong Scope Class
**Preview shows:**
```
✓ Page loaded successfully
❌ Scoped element NOT found
Available classes: button, contentbox, news-article, main-content...
```

**Solution:**
1. Look at the "Available classes" list
2. Find the correct class name (e.g., `news-article` instead of `content-section`)
3. Update "Scope Class" field
4. Click "Preview Page" again

---

### Scenario 3: Element Exists But Different Tag
**Preview shows:**
```
✓ Scoped Element Found
Tag: <section>
Text Length: 89 characters
Content Preview: Lorem ipsum...
```

**What this means:**
- The element exists and has the class name you specified
- But it's a `<section>` not a `<div>` (doesn't matter for extraction)
- **Text Length is very short** (89 chars) - might be the wrong element

**Solution:**
1. Read the "Content Preview" carefully
2. If it's not the right content, try a different class name
3. Look for classes with more specific names

---

### Scenario 4: Perfect Match
**Preview shows:**
```
✓ Page loaded successfully
✓ Scoped Element Found
Tag: <div>
Text Length: 3,456 characters

Content Preview:
Don't Miss MQDC Special Year-End Offer
Get ready for an amazing opportunity...
```

**Action:**
✅ Click **"Continue with Extraction"** immediately!

---

## Benefits of Preview

### 1. **Verify Authentication**
- See if cookies/headers work BEFORE starting extraction
- Saves time vs. waiting for crawl to fail

### 2. **Find Correct Element**
- See list of available classes on the page
- Copy/paste the exact class name

### 3. **Debug Scope Issues**
- See if element exists but contains unexpected content
- Check text length to verify you have the right element

### 4. **Fast Iteration**
- Preview → Adjust → Preview again
- Much faster than running full extractions

---

## Technical Details

### What Preview Does
1. Fetches the page with your authentication
2. Parses the HTML with BeautifulSoup
3. Searches for your specified class/ID
4. Returns first 500 chars of scoped content (if found)
5. Lists top 50 most common classes on the page

### What Preview Does NOT Do
- Does NOT save any files
- Does NOT download images
- Does NOT extract links
- Does NOT create a job or history entry
- Does NOT count against any limits

### Preview API Endpoint
```
POST /api/preview
Content-Type: application/json

{
  "url": "https://example.com",
  "scope_class": "content-section",
  "cookies": {"session": "abc123"},
  "auth_headers": {"Authorization": "Bearer token"}
}
```

---

## Troubleshooting

### Preview Button Disabled
- **Cause**: No URL entered
- **Solution**: Enter a valid URL first

### "Failed to load page"
**Possible causes:**
1. **Network issue**: Can't reach the server
2. **Authentication failed**: Cookies expired or incorrect
3. **Invalid URL**: Typo in URL
4. **Server error**: Target server is down

**Solutions:**
- Check URL is correct
- Get fresh cookies
- Try accessing URL in browser first
- Wait and try again if server is down

### Preview Works But Extraction Fails
**Possible causes:**
1. Different scope class was used
2. Preview doesn't test image downloads (but extraction does)
3. Server responded differently on second request

**Solutions:**
- Verify you used same scope class in both preview and extraction
- Disable image downloads if causing issues
- Try extraction immediately after successful preview

---

## Example Workflow

### For Intranet Site (with Authentication)

```
1. Enter URL:
   https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer

2. Set Mode: Content

3. Set Scope Class: content-section

4. Show Authentication Options
   → Select "Cookies"
   → Paste: ASP.NET_SessionId=xxx; .ASPXAUTH=yyy

5. Click "Preview Page" 🔍

6. Review Preview:
   ❌ "Scoped element NOT found"
   Available classes: contentbox, news-article, main-content...

7. Update Scope Class: contentbox

8. Click "Preview Page" again 🔍

9. Review Preview:
   ✅ "Scoped Element Found"
   ✅ Content preview looks correct

10. Click "Continue with Extraction" ▶️

11. Wait for extraction to complete

12. Download results ✅
```

---

## Quick Reference

| Button | What It Does | When to Use |
|--------|--------------|-------------|
| **Preview Page** | Fetches page, checks element, shows preview | Before extraction to verify setup |
| **Start Crawling** | Skips preview, starts extraction immediately | When you're confident everything is correct |
| **Continue with Extraction** | (In preview modal) Starts extraction with current settings | After successful preview |

---

## Tips for Success

1. ✅ **Always preview first** when crawling authenticated sites
2. ✅ **Check the Content Preview** text - does it match what you expect?
3. ✅ **Use available classes list** to find correct class names
4. ✅ **Get fresh cookies** if preview shows login page
5. ✅ **Preview multiple times** until you find the right scope class
6. ❌ **Don't skip preview** for important crawls - it saves time in the long run

---

## Success Criteria

Before clicking "Continue with Extraction", verify:

- ✅ Green "Page loaded successfully" banner
- ✅ Green "Scoped Element Found" banner  
- ✅ Content Preview shows expected text (not "Login" or "Error")
- ✅ Text Length is reasonable (not 0 or suspiciously small)
- ✅ Page Title matches expected page

If all checkmarks are green → **Click "Continue with Extraction"** with confidence! 🚀

---

## Video Tutorial (Conceptual)

```
1. [00:00] Open http://localhost:3000
2. [00:05] Fill in URL and scope class
3. [00:15] Click "Show Authentication Options"
4. [00:20] Paste cookies from DevTools
5. [00:25] Click "Preview Page" button
6. [00:30] Wait for preview modal to appear
7. [00:35] Check if scoped element found (green checkmark)
8. [00:40] Review content preview text
9. [00:45] Click "Continue with Extraction"
10. [00:50] Wait for extraction to complete
11. [01:00] Download results - SUCCESS! ✅
```

---

**Remember**: Preview is your friend! Use it to save time and avoid failed extractions. 🎯

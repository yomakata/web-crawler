# ✅ Authentication Form - Where to Find It

## The "Show Authentication Options" button is there!

I just rebuilt the frontend with the authentication support. Here's where to find it:

## 📍 Location in the Form

The authentication section appears **at the bottom of the form**, just **above the "Start Crawling" button**.

### Visual Guide:

```
┌─────────────────────────────────────────┐
│                                         │
│  Mode: [Content] [Link]                 │
│                                         │
│  URL: _____________________________     │
│                                         │
│  Scope Class: ___________________       │
│  Scope ID: ______________________       │
│                                         │
│  Output Formats: ☐ txt ☐ md ☐ html    │
│                                         │
│  ☐ Download images from the page        │
│                                         │
│  ─────────────────────────────────────  │  ← Border line
│                                         │
│  🔒 Show Authentication Options ▼       │  ← CLICK HERE!
│                                         │
│  [▶ Start Crawling]                    │
└─────────────────────────────────────────┘
```

## 🔍 How to Access It

### Step 1: Open the Web Interface
```
http://localhost:3000
```

### Step 2: Scroll Down

The authentication options are **below** the main form fields. You need to:

1. **Select "Single URL"** (not "Bulk CSV")
2. **Scroll down** past the scope class/ID fields
3. **Look for a border line** (thin horizontal line)
4. **Below the border** you'll see: 
   ```
   🔒 Show Authentication Options ▼
   ```

### Step 3: Click the Button

Click on **"Show Authentication Options"** to expand the authentication section.

## 🎨 What It Looks Like When Expanded

After clicking, you'll see:

```
🔒 Hide Authentication Options ▲

┌─────────────────────────────────────────────┐
│ 🔐 For Intranet/Protected Sites              │
│ If crawling a site that requires login      │
│ (like your company intranet), extract       │
│ cookies from your browser after logging in  │
│ (F12 → Application → Cookies).              │
├─────────────────────────────────────────────┤
│                                             │
│ Cookies (JSON format)                       │
│ ┌─────────────────────────────────────────┐ │
│ │ {"ASP.NET_SessionId": "abc123"}         │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
│ Example: {session_id: "...", ...}          │
│                                             │
│ Authentication Headers (JSON format)        │
│ ┌─────────────────────────────────────────┐ │
│ │ {"Authorization": "Bearer token"}       │ │
│ └─────────────────────────────────────────┘ │
│ For Bearer tokens or API keys              │
│                                             │
│ HTTP Basic Auth Username                    │
│ [________________]                          │
│                                             │
│ HTTP Basic Auth Password                    │
│ [________________]                          │
└─────────────────────────────────────────────┘
```

## ⚠️ Troubleshooting

### "I still don't see it!"

**Possible reasons:**

1. **You're on "Bulk CSV" mode**
   - Authentication only shows for "Single URL" mode
   - Switch to "Single URL" at the top

2. **Browser cache**
   - The frontend was just rebuilt
   - Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
   - Or clear browser cache

3. **Need to scroll**
   - The button is at the **bottom** of the form
   - Scroll down past all the form fields

4. **Frontend not updated**
   - Check if the rebuild completed
   - Run: `docker ps` to verify containers are running
   - Try: `docker-compose restart frontend`

### Quick Test

1. Open `http://localhost:3000`
2. Press `Ctrl+F` (Find in page)
3. Search for: "Authentication"
4. You should see the text highlighted on the page

If you still don't see it, the page might be cached. Try:

```bash
# Force rebuild and restart
cd /c/Projects/web-crawler
docker-compose down
docker-compose up -d --build
```

Then refresh your browser with `Ctrl + Shift + R`

## 📸 Screenshots Guide

If you still can't find it, here's what to look for:

1. **Icon**: 🔒 (lock icon)
2. **Text**: "Show Authentication Options"
3. **Color**: Blue text (primary-600 color)
4. **Location**: Above the green "Start Crawling" button
5. **Condition**: Only visible when "Single URL" is selected

## ✅ Verification

To verify it's working:

1. Open browser console (F12)
2. Type: `document.querySelector('button').textContent`
3. You should see button texts including "Show Authentication Options"

Or check the page source:
1. Right-click → "View Page Source"
2. Search for "Authentication"
3. You should find the authentication section in the HTML

---

**The form IS there and working!** Just need to:
1. ✅ Ensure you're on "Single URL" mode
2. ✅ Scroll to the bottom of the form
3. ✅ Click the blue "Show Authentication Options" button
4. ✅ If needed, hard refresh with Ctrl+Shift+R

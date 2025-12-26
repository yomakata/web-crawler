# Bulk CSV Authentication Feature

## Overview
Implemented comprehensive authentication support for bulk CSV crawling with two modes:
1. **Global Authentication** - Apply same credentials to all URLs in the CSV
2. **Per-URL Authentication** - Specify different credentials for each URL in CSV columns

## Problem Solved
Previously, bulk CSV crawling had no authentication support, making it impossible to crawl protected/authenticated sites using CSV uploads. Users could only crawl public URLs in bulk.

## Solution Implemented

### Two Authentication Modes

#### Mode 1: Global Authentication (Apply to All URLs)
- User checks a checkbox to enable global authentication
- Enters authentication credentials once
- Same credentials are applied to every URL in the CSV
- **Best for**: Multiple URLs on the same site/domain requiring same login

#### Mode 2: Per-URL Authentication (CSV Columns)
- User leaves global authentication unchecked
- Includes authentication columns in the CSV file
- Each URL can have different authentication
- **Best for**: Multiple sites with different credentials

## Backend Implementation

### 1. CSV Processor (`backend/utils/csv_processor.py`)

**Added Authentication Columns:**
```python
self.optional_columns = [
    'mode', 'scope_class', 'scope_id', 'format', 'download_images',
    'auth_enabled',           # NEW: Enable auth for this row
    'auth_type',              # NEW: 'cookies', 'headers', or 'basic'
    'cookies',                # NEW: Cookie string
    'auth_headers',           # NEW: JSON headers
    'basic_auth_username',    # NEW: Basic auth username
    'basic_auth_password'     # NEW: Basic auth password
]
```

**Updated `get_crawl_parameters()` Method:**
- Parses `auth_enabled` column (boolean)
- Reads `auth_type` column (cookies/headers/basic)
- Extracts authentication data based on type
- Returns authentication parameters with crawl params

### 2. API Routes (`backend/api/routes.py`)

**Updated `/crawl/bulk` Endpoint:**

**New Form Parameters:**
- `global_auth_enabled` (boolean) - Enable global authentication
- `auth_method` (string) - 'cookies', 'headers', or 'basic'
- `cookies` (string) - Cookie string
- `auth_headers` (string) - JSON auth headers
- `basic_auth_username` (string) - Basic auth username
- `basic_auth_password` (string) - Basic auth password

**Logic:**
```python
if global_auth_enabled:
    global_auth = {
        'auth_method': auth_method,
        'cookies': cookies,
        'auth_headers': auth_headers,
        'basic_auth_username': username,
        'basic_auth_password': password
    }
    
    # Apply to rows without auth_enabled
    for params in crawl_params:
        if not params.get('auth_enabled'):
            params['global_auth'] = global_auth
```

### 3. Crawl Tasks (`backend/api/tasks.py`)

**Updated `crawl_bulk_urls()` Function:**

**Authentication Priority:**
1. **Per-URL Auth** (if `auth_enabled=true` in CSV) - Highest priority
2. **Global Auth** (if enabled and no per-URL auth)
3. **No Auth** (default)

**Cookie Parsing:**
- Handles JSON format: `{"session": "abc123"}`
- Handles Chrome DevTools format: `session=abc123; token=xyz`
- Added `_parse_cookies_string()` helper function

**Header Parsing:**
- Parses JSON auth headers
- Supports custom header names

**Basic Auth:**
- Extracts username and password
- Passes as tuple to fetcher

## Frontend Implementation

### 1. CSV Upload Component (`frontend/src/components/CSVUpload.jsx`)

**Enhanced CSV Format Examples:**

Shows 4 different format examples:
1. **Basic Format** (no authentication)
2. **With Per-URL Cookies**
3. **With Per-URL Basic Auth**
4. **With Per-URL Auth Headers**

**Example Display:**
```jsx
<div className="bg-gray-100 p-2 rounded">
  <p className="font-semibold mb-1">With Per-URL Authentication:</p>
  <code className="block text-xs">
    url,mode,format,auth_enabled,auth_type,cookies<br/>
    https://example.com,content,txt,true,cookies,"session=abc123; token=xyz"
  </code>
</div>
```

**Tip Box:**
Shows blue info box explaining users can choose between global auth or per-URL auth

### 2. Crawl Form Component (`frontend/src/components/CrawlForm.jsx`)

**New State:**
```javascript
const [bulkGlobalAuth, setBulkGlobalAuth] = useState(false);
```

**New UI Section - Bulk CSV Global Authentication:**

Located after CSV upload, includes:

1. **Checkbox** - "Apply authentication to all URLs in CSV"
2. **Info Text** - Explains global vs per-URL authentication
3. **Collapsible Auth Section** (when checked):
   - Blue info banner: "Global Authentication for All URLs"
   - Authentication method selector (Cookies/Headers/Basic Auth)
   - Appropriate input fields based on method

**Visual Hierarchy:**
```
┌─────────────────────────────────────────────────┐
│ Upload CSV File                                 │
│ [CSV Upload Component with examples]            │
└─────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────┐
│ ☑ Apply authentication to all URLs in CSV      │
│ 💡 Enable this to use same auth for all URLs...│
│                                                  │
│ ┌─────────────────────────────────────────────┐ │
│ │ 🔐 Global Authentication for All URLs      │ │
│ │ These credentials will be applied to every │ │
│ │ URL in your CSV file.                      │ │
│ │                                             │ │
│ │ Authentication Method:                      │ │
│ │ [Cookies] [Headers] [Basic Auth]            │ │
│ │                                             │ │
│ │ [Authentication input fields...]            │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**Updated `buildRequestData()` Function:**
- Includes `bulkGlobalAuth` flag
- Includes `authMethod` when global auth enabled
- Processes cookies, headers, or basic auth accordingly

### 3. API Service (`frontend/src/services/api.js`)

**Updated `crawlBulk()` Method:**
```javascript
crawlBulk: async (file, authData = null) => {
  const formData = new FormData();
  formData.append('file', file);
  
  if (authData && authData.global_auth_enabled) {
    formData.append('global_auth_enabled', 'true');
    formData.append('auth_method', authData.auth_method);
    // ... append auth credentials
  }
  
  return await api.post('/crawl/bulk', formData);
}
```

### 4. Crawler Page (`frontend/src/pages/Crawler.jsx`)

**Updated `handleSubmit()` Function:**
```javascript
if (formData.bulkGlobalAuth) {
  authData = {
    global_auth_enabled: true,
    auth_method: formData.authMethod,
    cookies: formData.cookies,
    auth_headers: formData.auth_headers,
    basic_auth_username: formData.basic_auth_username,
    basic_auth_password: formData.basic_auth_password,
  };
}
response = await crawlAPI.crawlBulk(formData.file, authData);
```

## CSV Format Examples

### Example 1: Basic (No Authentication)
```csv
url,mode,format
https://example.com,content,txt
https://another.com,content,md
```

### Example 2: Global Authentication
**CSV:**
```csv
url,mode,format
https://intranet.company.com/page1,content,txt
https://intranet.company.com/page2,content,md
```

**UI:** Check "Apply authentication to all URLs" and enter credentials once

### Example 3: Per-URL Cookies
```csv
url,mode,scope_class,format,download_images,auth_enabled,auth_type,cookies
https://site1.com,content,main-content,txt,false,true,cookies,"session=abc123; token=xyz"
https://site2.com,content,main-content,txt,false,true,cookies,"auth_token=different_token"
https://public.com,content,main-content,txt,false,false,,
```

### Example 4: Per-URL Basic Auth
```csv
url,mode,scope_class,format,download_images,auth_enabled,auth_type,basic_auth_username,basic_auth_password
https://site1.com,content,main-content,txt,false,true,basic,user1,pass1
https://site2.com,content,main-content,txt,false,true,basic,user2,pass2
```

### Example 5: Per-URL Auth Headers
```csv
url,mode,scope_class,format,download_images,auth_enabled,auth_type,auth_headers
https://api1.com,content,main-content,txt,false,true,headers,"{\"Authorization\": \"Bearer token123\"}"
https://api2.com,content,main-content,txt,false,true,headers,"{\"X-API-Key\": \"key456\"}"
```

### Example 6: Mixed (Some with auth, some without)
```csv
url,mode,scope_class,format,download_images,auth_enabled,auth_type,cookies
https://protected.com,content,main-content,txt,false,true,cookies,"session=abc"
https://public.com,content,main-content,txt,false,false,,
https://another-protected.com,content,main-content,txt,false,true,cookies,"token=xyz"
```

## User Workflows

### Workflow 1: Crawl Multiple Pages on Same Site
```
1. Prepare CSV with just URLs
2. Upload CSV file
3. Check "Apply authentication to all URLs in CSV"
4. Select authentication method (e.g., Cookies)
5. Paste cookies from browser DevTools
6. Click "Start Crawling"
7. ✅ All URLs crawled with same credentials
```

### Workflow 2: Crawl Multiple Different Sites
```
1. Prepare CSV with auth columns:
   - auth_enabled, auth_type, cookies (or other auth fields)
2. Fill in different credentials for each site
3. Upload CSV file
4. Leave global authentication unchecked
5. Click "Start Crawling"
6. ✅ Each URL uses its own credentials
```

### Workflow 3: Mix of Public and Protected Pages
```
1. Prepare CSV with auth columns
2. Set auth_enabled=true for protected URLs
3. Set auth_enabled=false for public URLs
4. Upload CSV
5. Don't enable global authentication
6. Click "Start Crawling"
7. ✅ Protected URLs use credentials, public URLs don't
```

## Authentication Priority

The system follows this priority order:

1. **Per-URL Authentication** (CSV columns)
   - If `auth_enabled=true` in CSV row
   - Uses credentials from that specific row
   - Highest priority

2. **Global Authentication** (UI checkbox)
   - If global auth enabled AND row has no per-URL auth
   - Uses global credentials for that row
   - Medium priority

3. **No Authentication**
   - If neither global nor per-URL auth specified
   - Default behavior

## Benefits

✅ **Flexible**: Support both global and per-URL authentication

✅ **Powerful**: Can crawl protected sites in bulk

✅ **User-Friendly**: Simple checkbox for global auth, examples for per-URL

✅ **Comprehensive**: Supports all three auth types (cookies, headers, basic)

✅ **Smart Priority**: Per-URL auth overrides global auth

✅ **Well-Documented**: Clear examples in UI and documentation

✅ **Backward Compatible**: Works with existing CSV files (no auth required)

## Testing

### Test Case 1: Global Authentication
```
1. Create CSV with 3 URLs from same site
2. Upload CSV
3. Check "Apply authentication to all URLs"
4. Enter cookies
5. Start crawl
6. ✅ All 3 pages should be crawled with authentication
```

### Test Case 2: Per-URL Authentication
```
1. Create CSV with auth columns
2. Include different credentials for different URLs
3. Upload CSV
4. Don't check global authentication
5. Start crawl
6. ✅ Each URL should use its own credentials
```

### Test Case 3: Mixed (Global + Per-URL)
```
1. Create CSV where some rows have auth_enabled=true
2. Upload CSV
3. Check "Apply authentication to all URLs"
4. Enter global credentials
5. Start crawl
6. ✅ Rows with auth_enabled use their own credentials
7. ✅ Rows without use global credentials
```

### Test Case 4: No Authentication
```
1. Create CSV with just URLs
2. Upload CSV
3. Don't check global authentication
4. Start crawl
5. ✅ All URLs crawled without authentication (public access)
```

## Files Modified

### Backend
- ✅ `backend/utils/csv_processor.py` - Added auth column parsing
- ✅ `backend/api/routes.py` - Added global auth parameter handling
- ✅ `backend/api/tasks.py` - Added auth priority logic and cookie parsing

### Frontend
- ✅ `frontend/src/components/CSVUpload.jsx` - Added CSV format examples
- ✅ `frontend/src/components/CrawlForm.jsx` - Added global auth UI section
- ✅ `frontend/src/services/api.js` - Updated API call to include auth data
- ✅ `frontend/src/pages/Crawler.jsx` - Pass auth data to API

## Future Enhancements

Potential improvements:
- CSV template download button with auth columns
- Auth credential validation before crawl
- Save auth templates for reuse
- Support for OAuth flows
- Auth credentials encryption in CSV

## Date
December 25, 2025

## Status
✅ Complete and Ready for Testing

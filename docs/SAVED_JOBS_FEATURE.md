# Saved Jobs Feature

## Overview
The Saved Jobs feature allows users to save their crawling configurations for quick reuse. This is particularly useful for recurring tasks like daily news extraction or monitoring specific web pages.

## Features

### 1. Save Job Configuration
- Save any crawling setup with a custom name and description
- Includes all settings:
  - Input method (single URL or bulk CSV)
  - Mode (content or link extraction)
  - URL or CSV filename
  - Output formats
  - Scope class/ID
  - Download images setting
  - Link type filter
  - Authentication settings (cookies, headers, basic auth)

### 2. Saved Jobs List
- View all saved jobs in a clean card-based interface
- See key details at a glance:
  - Job name and description
  - Mode and URL
  - Scope settings
  - Authentication type
  - Last updated date

### 3. Load Saved Job
- Click "Load Job" to restore all settings
- Automatically fills in all form fields
- Includes authentication credentials
- Ready to run immediately

### 4. Delete Saved Jobs
- Remove outdated configurations
- Confirmation prompt prevents accidental deletion

## Usage

### Saving a Job

1. **Fill in the crawl form** with your desired settings:
   - Enter URL or upload CSV
   - Select mode and formats
   - Configure scope and authentication

2. **Click "Save Job Configuration"** button (below the main action buttons)

3. **Enter job details**:
   - **Name**: Required (e.g., "Daily News Crawler")
   - **Description**: Optional (e.g., "Extract news from intranet")

4. **Click "Save Job"** - Your configuration is now saved!

### Loading a Saved Job

1. **Navigate to "Saved Jobs"** from the main menu

2. **Browse your saved jobs** - View cards showing:
   - Job name and description
   - URL and settings
   - Last updated date

3. **Click "Load Job"** - You'll be redirected to the Crawler page with all settings pre-filled

4. **Run immediately** or modify settings before crawling

### Managing Saved Jobs

- **Update**: Load a job, modify settings, and save again with the same name
- **Delete**: Click the trash icon, confirm deletion

## Technical Details

### Backend API

**Endpoints:**
- `POST /api/jobs/saved` - Create new saved job
- `GET /api/jobs/saved` - List all saved jobs
- `GET /api/jobs/saved/<id>` - Get specific saved job
- `PUT /api/jobs/saved/<id>` - Update saved job
- `DELETE /api/jobs/saved/<id>` - Delete saved job

**Storage:**
- Saved jobs are stored in `saved_jobs.json` file
- Persists across container restarts
- Located in backend working directory

**Data Model:**
```python
SavedJob:
  - saved_job_id: Unique identifier
  - name: Job name
  - description: Optional description
  - created_at: Creation timestamp
  - updated_at: Last update timestamp
  - input_method: 'single' or 'bulk'
  - mode: 'content' or 'link'
  - url: Target URL (for single mode)
  - csv_filename: CSV file reference (for bulk mode)
  - formats: List of output formats
  - scope_class: Optional scope class
  - scope_id: Optional scope ID
  - download_images: Boolean
  - link_type: 'all', 'internal', or 'external'
  - auth_method: 'cookies', 'headers', 'basic', or null
  - cookies: Cookie string
  - auth_headers: Headers JSON string
  - basic_auth_username: Username
  - basic_auth_password: Password
```

### Frontend Components

**New Components:**
- `SavedJobs.jsx` - Saved jobs list page
- `SaveJobModal.jsx` - Modal for saving job configuration

**Updated Components:**
- `CrawlForm.jsx` - Added save button and load saved job support
- `Crawler.jsx` - Added save job handler and saved job prop
- `App.jsx` - Added Saved Jobs route and navigation

**Navigation:**
- New "Saved Jobs" menu item with bookmark icon
- Located between "Crawler" and "History"

## Use Cases

### 1. Daily News Extraction
Save configuration for daily news crawling from an intranet:
- Name: "Daily Company News"
- URL: `https://intranet.company.com/news`
- Scope: `class="content-section"`
- Auth: Cookies from Chrome DevTools
- Formats: TXT, MD

### 2. Multiple Site Monitoring
Save bulk configurations for monitoring multiple websites:
- Name: "Competitor Price Monitor"
- Input: CSV with 20 competitor URLs
- Scope: Product price containers
- Run weekly to track changes

### 3. Authenticated Content
Save credentials for protected content:
- Name: "Internal Knowledge Base"
- Authentication method and credentials saved
- No need to re-enter credentials each time

## Security Considerations

- **Credentials Storage**: Authentication credentials (cookies, passwords) are saved in plain text in `saved_jobs.json`
- **File Permissions**: Ensure proper file permissions on `saved_jobs.json`
- **Production Use**: Consider encrypting sensitive fields or using environment variables
- **User Access**: Currently no user isolation - all saved jobs are shared

## Future Enhancements

Potential improvements:
- [ ] User authentication and job ownership
- [ ] Encrypt sensitive credentials
- [ ] Schedule saved jobs to run automatically
- [ ] Export/import saved jobs
- [ ] Job templates and sharing
- [ ] Version history for saved jobs
- [ ] Search and filter saved jobs

## Troubleshooting

**Jobs not loading after restart:**
- Check if `saved_jobs.json` exists in backend directory
- Verify file permissions
- Check backend logs for errors

**Saved job missing fields:**
- May be from older version before field was added
- Delete and re-save the job

**Authentication not working after loading:**
- Verify credentials are still valid
- Re-save job with updated credentials

## File Locations

- **Backend Code**: `backend/api/models.py` (SavedJob, SavedJobStore)
- **Backend Routes**: `backend/api/routes.py` (Saved jobs endpoints)
- **Storage File**: `saved_jobs.json` (root of backend container)
- **Frontend Page**: `frontend/src/pages/SavedJobs.jsx`
- **Frontend Modal**: `frontend/src/components/SaveJobModal.jsx`
- **API Service**: `frontend/src/services/api.js` (savedJobs methods)

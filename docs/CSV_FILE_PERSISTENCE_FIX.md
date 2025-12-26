# CSV File Persistence Fix

## Problem
When saving a bulk CSV job configuration and then loading it from the saved jobs list, the uploaded CSV file would disappear. Only the filename was being saved, but not the actual file content.

## Root Cause
The saved job feature was only storing the CSV filename (`csv_filename`) but not the actual CSV file content. When loading the saved job:
1. The filename was restored
2. But no File object was created
3. Users had to re-upload the CSV file every time

## Solution

### Backend Changes (`backend/api/models.py`)
Added a new field to the `SavedJob` dataclass to store CSV content:
```python
csv_content: Optional[str] = None  # Store CSV file content for bulk jobs
```

### Frontend Changes (`frontend/src/components/CrawlForm.jsx`)

#### 1. Saving CSV Content
Modified `handleSaveJob` to read and save the CSV file content:
```javascript
// Read CSV file content if in bulk mode
let csvContent = null;
if (inputMethod === 'bulk' && csvFile) {
  try {
    csvContent = await csvFile.text();
  } catch (error) {
    console.error('Error reading CSV file:', error);
  }
}

const jobData = {
  ...jobInfo,
  csv_filename: inputMethod === 'bulk' && csvFile ? csvFile.name : null,
  csv_content: csvContent,
  // ... other fields
};
```

#### 2. Restoring CSV File
Modified the `useEffect` hook that loads saved jobs to recreate the File object:
```javascript
// Restore CSV file from saved content
if (savedJob.input_method === 'bulk' && savedJob.csv_content && savedJob.csv_filename) {
  try {
    // Create a File object from the CSV content
    const blob = new Blob([savedJob.csv_content], { type: 'text/csv' });
    const file = new File([blob], savedJob.csv_filename, { type: 'text/csv' });
    setCsvFile(file);
  } catch (error) {
    console.error('Error restoring CSV file:', error);
  }
}
```

## How It Works Now

1. **Saving a Bulk Job**:
   - User uploads a CSV file
   - User configures other settings (mode, formats, etc.)
   - User clicks "Save Job Configuration"
   - The CSV file content is read using `file.text()`
   - Both filename and content are saved to the backend

2. **Loading a Saved Bulk Job**:
   - User clicks "Load Job" on a saved bulk job
   - The saved job data includes both `csv_filename` and `csv_content`
   - A new File object is created from the saved content
   - The file appears in the CSV upload component
   - User can start crawling immediately without re-uploading

## Benefits
- ✅ CSV files persist across save/load cycles
- ✅ No need to re-upload CSV files
- ✅ Complete job configuration is preserved
- ✅ Better user experience for recurring bulk jobs

## Testing
To verify the fix:
1. Go to the Crawler page
2. Select "Bulk CSV" input method
3. Upload a CSV file
4. Configure other settings
5. Click "Save Job Configuration"
6. Go to Saved Jobs page
7. Click "Load Job" on the saved job
8. Verify the CSV file appears in the upload area
9. You should be able to start crawling without re-uploading

## Files Modified
- `backend/api/models.py` - Added `csv_content` field to SavedJob
- `frontend/src/components/CrawlForm.jsx` - Added CSV content save/restore logic

## Date
December 25, 2025

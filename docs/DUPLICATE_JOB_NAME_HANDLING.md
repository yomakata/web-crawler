# Duplicate Job Name Handling Feature

## Overview
Enhanced the saved job feature to detect duplicate job names and prompt users to confirm before updating/replacing existing jobs. This prevents accidental overwrites and provides clear feedback about existing configurations.

## Problem Solved
Previously, when users saved a job with the same name as an existing job, the behavior was unclear:
- No warning was shown
- Users might accidentally overwrite important job configurations
- No way to intentionally update an existing job without deleting it first

## Solution

### Backend Changes

#### 1. Added `find_by_name` Method (`backend/api/models.py`)
Added a new method to the `SavedJobStore` class to find jobs by name (case-insensitive):

```python
def find_by_name(self, name: str) -> Optional[SavedJob]:
    """Find saved job by name (case-insensitive)"""
    name_lower = name.lower().strip()
    for job in self.jobs.values():
        if job.name.lower().strip() == name_lower:
            return job
    return None
```

#### 2. Updated Create Endpoint (`backend/api/routes.py`)
Modified the `/jobs/saved` POST endpoint to:
- Check for duplicate names before creating
- Return a 409 Conflict status with existing job details if duplicate found
- Support `force_update` parameter to allow intentional updates
- Update existing job instead of creating new one when `force_update=true`

**New Request Body Parameter:**
```json
{
  "name": "My Job",
  "description": "...",
  "force_update": false,  // Set to true to update existing job
  ...
}
```

**Response on Duplicate (409 Conflict):**
```json
{
  "success": false,
  "error": "duplicate_name",
  "message": "A job with name 'My Job' already exists",
  "existing_job_id": "abc-123",
  "existing_job": { /* full job details */ }
}
```

**Response on Successful Update:**
```json
{
  "success": true,
  "message": "Job updated successfully",
  "saved_job": { /* updated job details */ },
  "updated": true
}
```

### Frontend Changes

#### 1. Enhanced SaveJobModal Component (`frontend/src/components/SaveJobModal.jsx`)

**New State Variables:**
- `showConfirmUpdate`: Controls confirmation dialog visibility
- `existingJob`: Stores details of the existing job with duplicate name

**Two-Stage Dialog:**

**Stage 1 - Normal Save Dialog:**
- User enters job name and description
- Submits to save the job

**Stage 2 - Confirmation Dialog (if duplicate detected):**
- Shows warning that job name already exists
- Displays existing job details:
  - Description
  - Input method (Single/Bulk)
  - Mode
  - URL (if applicable)
  - Last updated timestamp
- Shows warning message about permanent replacement
- Provides two options:
  - **Cancel**: Go back to edit the name
  - **Update & Replace**: Confirm overwriting the existing job

**Visual Design:**
- Yellow warning icon (⚠️) in header
- Yellow background for warning message
- Gray background panel showing existing job details
- Clear action buttons with appropriate colors

#### 2. Updated Crawler Component (`frontend/src/pages/Crawler.jsx`)

Modified `handleSaveJob` to:
- Return the result from the mutation (needed for modal to detect duplicates)
- Re-throw errors so modal can handle them appropriately
- Show different success messages for new jobs vs. updates

## User Experience Flow

### Scenario 1: Saving with Unique Name
1. User clicks "Save Job Configuration"
2. Enters unique job name
3. Clicks "Save Job"
4. ✅ Success message: "Job configuration saved successfully!"
5. Modal closes

### Scenario 2: Saving with Duplicate Name
1. User clicks "Save Job Configuration"
2. Enters name that already exists (e.g., "Daily News")
3. Clicks "Save Job"
4. ⚠️ **Confirmation dialog appears** showing:
   - Warning header: "Job Name Already Exists"
   - Message: "A job with the name 'Daily News' already exists..."
   - Details of existing job
   - Warning: "This will permanently replace..."
5. User has two choices:
   - **Cancel**: Goes back to change the name
   - **Update & Replace**: Confirms the update
6. If confirmed:
   - ✅ Success message: "Job configuration updated successfully!"
   - Modal closes
   - Existing job is updated with new configuration

### Scenario 3: Case-Insensitive Matching
- "Daily News", "daily news", "DAILY NEWS" are all treated as the same name
- Prevents confusion from capitalization differences

## Benefits

✅ **Prevents Accidental Overwrites**: Users must explicitly confirm before replacing existing jobs

✅ **Better Visibility**: Users can see what they're about to overwrite

✅ **Intentional Updates**: Provides a clear way to update existing job configurations

✅ **User-Friendly**: Clear warning messages and visual feedback

✅ **Smart Matching**: Case-insensitive name matching prevents duplicates with different capitalization

## Technical Details

### API Flow
```
Frontend (SaveJobModal)
    ↓ POST /jobs/saved { name: "Daily News" }
Backend (routes.py)
    ↓ Check for duplicate using find_by_name()
    ├─ No duplicate → Create new job → Return 201 Created
    └─ Duplicate found
        ├─ force_update=false → Return 409 Conflict with existing job details
        └─ force_update=true → Update existing job → Return 200 OK
Frontend (SaveJobModal)
    ↓ Receives 409 Conflict
    └─ Show confirmation dialog
        ├─ User cancels → Stay in modal
        └─ User confirms → Retry with force_update=true
```

### Database Impact
- No schema changes required
- Uses existing `saved_jobs.json` storage
- Updates preserve the original `saved_job_id` and `created_at` timestamp
- Only `updated_at` timestamp is refreshed on updates

## Testing

### Test Case 1: New Job with Unique Name
1. Go to Crawler page
2. Configure a crawl job
3. Click "Save Job Configuration"
4. Enter name: "Test Job 1"
5. Click "Save Job"
6. ✅ Should save successfully

### Test Case 2: Duplicate Name - Cancel
1. Configure another crawl job
2. Click "Save Job Configuration"
3. Enter name: "Test Job 1" (same as before)
4. Click "Save Job"
5. ⚠️ Should show confirmation dialog
6. Click "Cancel"
7. ✅ Should stay in modal, allowing name change

### Test Case 3: Duplicate Name - Update
1. Configure another crawl job (different settings)
2. Click "Save Job Configuration"
3. Enter name: "Test Job 1"
4. Click "Save Job"
5. ⚠️ Should show confirmation dialog with existing job details
6. Click "Update & Replace"
7. ✅ Should update the existing job
8. Go to Saved Jobs page
9. ✅ Should see only one "Test Job 1" with updated configuration

### Test Case 4: Case Insensitive
1. Save job named "Daily News"
2. Try to save another as "daily news"
3. ⚠️ Should detect as duplicate
4. Try "DAILY NEWS"
5. ⚠️ Should also detect as duplicate

## Files Modified

### Backend
- `backend/api/models.py` - Added `find_by_name()` method
- `backend/api/routes.py` - Enhanced `/jobs/saved` POST endpoint with duplicate detection

### Frontend
- `frontend/src/components/SaveJobModal.jsx` - Added confirmation dialog for duplicates
- `frontend/src/pages/Crawler.jsx` - Updated save handler to return result

## Future Enhancements

Potential improvements:
- Add "Save As Copy" option to create a new job with incremented name (e.g., "Daily News (2)")
- Show list of all existing job names while typing to prevent duplicates earlier
- Add job version history to track changes over time
- Implement job templates/categories for better organization

## Date
December 25, 2025

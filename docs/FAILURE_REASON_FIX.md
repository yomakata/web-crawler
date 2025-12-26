# Failure Reason Display Fix

## Issue
When an extraction fails, the Results Modal was showing "Extraction Failed" but not displaying the specific failure reason, even though the backend was generating detailed failure information.

## Root Cause
The frontend ResultsModal component was using strict conditional checks (`result.failure_info && result.failure_info.failure_reason`) which would fail silently if:
1. `failure_info` object existed but `failure_reason` was undefined/empty
2. The error structure was slightly different than expected
3. Only the `error` field was present instead of `failure_info`

## Changes Made

### 1. Updated ResultsModal.jsx - Failure Reason Display
**Location:** `frontend/src/components/ResultsModal.jsx` (lines 82-91)

**Before:**
```jsx
{result.status === 'failed' && result.failure_info && (
  <>
    <p className="text-sm text-error-700 mt-1 font-medium">
      {result.failure_info.failure_reason}
    </p>
    <span className="inline-block mt-2 px-2 py-1 text-xs font-medium rounded-md bg-error-100 text-error-800">
      {result.failure_info.error_type.replace('_', ' ').toUpperCase()}
    </span>
  </>
)}
```

**After:**
```jsx
{result.status === 'failed' && (
  <>
    <p className="text-sm text-error-700 mt-1 font-medium">
      {result.failure_info?.failure_reason || result.error || 'An unknown error occurred'}
    </p>
    {result.failure_info?.error_type && (
      <span className="inline-block mt-2 px-2 py-1 text-xs font-medium rounded-md bg-error-100 text-error-800">
        {result.failure_info.error_type.replace('_', ' ').toUpperCase()}
      </span>
    )}
  </>
)}
```

**Key improvements:**
- Uses optional chaining (`?.`) to safely access nested properties
- Provides fallback chain: `failure_reason` → `error` → default message
- Only shows error_type badge if it exists
- Removes redundant `result.failure_info &&` check (handled by optional chaining)

### 2. Updated Failure Details Section
**Location:** `frontend/src/components/ResultsModal.jsx` (lines 95-152)

**Changes:**
- Changed condition from `result.failure_info &&` to `(result.failure_info || result.error) &&`
- Added optional chaining for all `failure_info` property access
- Set retry button to show if `retry_possible` is true OR if `failure_info` is missing (safer default)
- Added fallbacks for `error_code` ('N/A') and `error_type` ('Unknown')
- Made all `failure_info` properties safe with optional chaining

### 3. Added Debug Logging
**Location:** `frontend/src/components/ResultsModal.jsx` (after line 32)

Added console logging to help debug what data is actually being received:
```jsx
console.log('ResultsModal - Full results:', results);
console.log('ResultsModal - First result:', result);
console.log('ResultsModal - Result status:', result?.status);
console.log('ResultsModal - Failure info:', result?.failure_info);
console.log('ResultsModal - Error:', result?.error);
```

## Expected Behavior After Fix

### When Extraction Fails:
1. **Always shows a failure message** - Falls back through multiple sources
2. **Displays specific failure reason** from `failure_info.failure_reason`
3. **Shows error type badge** if available
4. **Lists actionable suggestions** if provided by backend
5. **Shows retry button** if error is retryable
6. **Displays troubleshooting section** with error details

### Fallback Chain:
1. First tries `result.failure_info.failure_reason` (most specific)
2. Falls back to `result.error` (generic error message)
3. Finally shows "An unknown error occurred" (last resort)

## Testing Recommendations

To verify the fix works, test these failure scenarios:

1. **Network timeout**
   - URL: Use a very slow server or break internet connection
   - Expected: "Connection timeout - Server took too long to respond"

2. **404 Not Found**
   - URL: https://example.com/nonexistent-page-12345
   - Expected: "404 Not Found" with suggestions

3. **Invalid URL**
   - URL: Enter "not-a-url" or "ht tp://broken.com"
   - Expected: "Invalid URL format - Please check the URL syntax"

4. **Element not found (Content mode with scope)**
   - URL: Any valid URL
   - Scope Class: "nonexistent-class-name-xyz"
   - Expected: "Target element not found - The specified class or ID does not exist on the page"

5. **403 Forbidden**
   - URL: Try a URL that blocks automated access
   - Expected: "403 Forbidden" with suggestions

## Backend Error Flow (Reference)

The backend already implements comprehensive error handling:

1. **Exception occurs** in `tasks.py` `crawl_single_url()`
2. **Error handler processes** via `handle_extraction_failure()` in `error_handler.py`
3. **Creates `failure_info` dict** with:
   - `failure_reason`: Human-readable message
   - `error_type`: Category (network_error, http_error, etc.)
   - `error_code`: HTTP status or error identifier
   - `retry_possible`: Boolean flag
   - `suggestions`: List of actionable tips
4. **Formatted for API** via `format_failure_for_api()`
5. **Added to result** and stored in job
6. **Returned to frontend** via `/job/{job_id}/results` endpoint

## Debug Console Output

After loading a failed extraction, check the browser console for:
```
ResultsModal - Full results: {results: Array(1), ...}
ResultsModal - First result: {status: 'failed', url: '...', failure_info: {...}}
ResultsModal - Result status: failed
ResultsModal - Failure info: {failure_reason: '...', error_type: '...', ...}
ResultsModal - Error: Connection timeout...
```

If `failure_info` is `undefined`, this indicates the backend is not properly setting it in the result.

## Related Files

- **Frontend:** `frontend/src/components/ResultsModal.jsx`
- **Backend:** `backend/api/tasks.py` (crawl_single_url function)
- **Backend:** `backend/utils/error_handler.py` (error handling logic)
- **Spec:** `dev-spec.md` (section 6: Extraction Metadata & Results Display)

## Status
✅ Fixed - Failure reasons should now display correctly in all scenarios

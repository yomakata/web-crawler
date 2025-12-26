# Preview Formatting Fix

## Date: December 25, 2025

## Problem

The preview modal was not showing newlines in the scoped element content preview, even though the text formatting improvements were implemented in the parser.

**Symptom:**
```
BackMQDCทำพลาด! MQDC 'โปร ปีด ปี' สุดพิเศษสงท่าน!| Don't Miss! MQDC Special Year-End OfferPost on Wed 03 December 2025...
```
All text ran together without line breaks.

---

## Root Cause

In the preview endpoint (`backend/api/routes.py`), the code was using BeautifulSoup's basic `get_text(strip=True)` method which strips ALL whitespace including newlines:

```python
# OLD CODE (WRONG)
scope_text = scope_element.get_text(strip=True)
```

This bypassed the ContentParser's `extract_text()` method which has the improved formatting logic.

---

## Solution

Modified the preview endpoint to use ContentParser's `extract_text()` method instead:

```python
# NEW CODE (CORRECT)
from crawler.parser import ContentParser
parser = ContentParser(html, url)
scope_text = parser.extract_text(scope_element)
```

Now the preview uses the same formatting logic as the actual extraction!

---

## Changes Made

### File: `backend/api/routes.py` (lines 433-462)

**Before:**
```python
if scope_class:
    scope_element = soup.find(class_=scope_class)
    if scope_element:
        has_scope_element = True
        scope_text = scope_element.get_text(strip=True)  # ❌ No formatting
        scope_element_preview = scope_text[:500] + ('...' if len(scope_text) > 500 else '')
```

**After:**
```python
if scope_class:
    scope_element = soup.find(class_=scope_class)
    if scope_element:
        has_scope_element = True
        # Use ContentParser to get properly formatted text
        from crawler.parser import ContentParser
        parser = ContentParser(html, url)
        scope_text = parser.extract_text(scope_element)  # ✅ With formatting
        scope_element_preview = scope_text[:500] + ('...' if len(scope_text) > 500 else '')
```

Same fix applied for `scope_id` case.

---

## Result

### Before Fix
```
BackMQDCทำพลาด! MQDC 'โปร ปีด ปี' สุดพิเศษสงท่าน!| Don't Miss! MQDC Special Year-End OfferPost on Wed 03 December 2025 | MQDCMQDCจัด'โปร ปีด ปี'สุดพิเศษสงท่าน...
```

### After Fix
```
BackMQDCทำพลาด! MQDC 'โปร ปีด ปี' สุดพิเศษสงท่าน! | Don't Miss! MQDC Special Year-End Offer

Post on Wed 03 December 2025 | MQDC

MQDCจัด'โปร ปีด ปี'สุดพิเศษสงท่าน...
```

Now has proper line breaks! ✅

---

## What Gets Formatted

The preview now applies the same formatting rules as extraction:

1. ✅ **Headings (h1-h6)** - Each on new line
2. ✅ **Paragraphs (p)** - Each on new line
3. ✅ **Block spans** - Spans outside `<p>` get newlines
4. ✅ **Block elements** - div, section, article, etc. get newlines
5. ✅ **Inline spans** - Spans inside `<p>` stay inline

---

## Preview Modal Display

The preview modal already had the correct CSS for displaying newlines:

```jsx
<div className="... whitespace-pre-wrap">
  {preview.scope_element_preview}
</div>
```

- `whitespace-pre-wrap` preserves newlines and spaces
- Now that backend sends formatted text, it displays correctly

---

## Impact

### ✅ Preview Modal
- Content preview now shows proper formatting
- Easier to verify content structure before extraction
- Matches what you'll get in output files

### ✅ Consistency
- Preview formatting = Extraction formatting
- What you see is what you get (WYSIWYG)
- No surprises when downloading extracted content

### ✅ User Experience
- Better readability in preview
- Can verify formatting before proceeding
- More confidence in extraction quality

---

## Example Preview

### HTML Input
```html
<div class="content-section">
  <h1>Main Headline</h1>
  <p>First paragraph of content.</p>
  <h2>Subheading</h2>
  <p>Second paragraph here.</p>
  <div>
    <span class="label">Category:</span>
    <span class="value">News</span>
  </div>
</div>
```

### Preview Display (Now Correct)
```
Main Headline

First paragraph of content.

Subheading

Second paragraph here.

Category:

News
```

---

## Technical Flow

### Preview Endpoint Flow

1. **Receive request** with URL and scope parameters
2. **Fetch page** with authentication
3. **Parse HTML** with BeautifulSoup
4. **Find scoped element** by class or ID
5. **Create ContentParser** instance ⭐ NEW
6. **Extract formatted text** using `parser.extract_text()` ⭐ NEW
7. **Take first 500 chars** for preview
8. **Return JSON** with formatted text
9. **Frontend displays** with `whitespace-pre-wrap`

---

## Testing

### Test Case 1: Preview with Authentication
```
1. Enter intranet URL
2. Paste cookies
3. Set scope_class="content-section"
4. Click "Preview Page"
5. ✅ Check: Content preview shows line breaks
6. ✅ Verify: Headings are separated
7. ✅ Verify: Paragraphs are on new lines
```

### Test Case 2: Compare Preview vs Extraction
```
1. Preview page (note the formatting)
2. Click "Continue with Extraction"
3. Download TXT file
4. ✅ Verify: Formatting matches preview exactly
```

---

## Files Modified

1. **backend/api/routes.py** (lines 433-462)
   - Added ContentParser import in preview section
   - Use `parser.extract_text()` instead of `get_text()`
   - Applied to both `scope_class` and `scope_id` cases

---

## Deployment

✅ Backend rebuilt with the fix  
✅ Backend running on port 5000  
✅ Preview now shows formatted text  
✅ Consistent with extraction output  

---

## Related Documentation

- [TEXT_FORMATTING_IMPROVEMENTS.md](./TEXT_FORMATTING_IMPROVEMENTS.md) - Original formatting implementation
- [PREVIEW_SIMPLIFIED.md](./PREVIEW_SIMPLIFIED.md) - Preview modal updates
- [PAGE_PREVIEW_GUIDE.md](./PAGE_PREVIEW_GUIDE.md) - User guide

---

## Summary

**Problem:** Preview not showing newlines  
**Cause:** Using `get_text(strip=True)` which removes formatting  
**Solution:** Use `ContentParser.extract_text()` with formatting logic  
**Result:** Preview now matches extraction output exactly! ✅

The preview modal now properly displays formatted text with line breaks, making it much easier to verify content structure before proceeding with extraction! 🎉

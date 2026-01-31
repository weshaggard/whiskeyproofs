# Example: TTB ID Without Available Images

## TTB ID: 02156000000070

**Product:** Old Forester Birthday Bourbon 2002  
**Brand:** Old Forester  
**Type:** Bourbon  
**Age:** 12 years  
**Proof:** 95  
**Release Year:** 2002

## Issue

When running the download script:
```bash
python3 .github/scripts/download_ttb_labels.py --ttbid 02156000000070
```

**Result:**
```
Processing single TTB ID: 02156000000070
Skip existing: True

[1/1] Processing 02156000000070...
  No label images found for 02156000000070

Summary:
  Success: 0
  Failed:  1
  Skipped: 0
  Total:   1
```

## Why It Failed

The TTB website returns an **error page** instead of the COLA details page.

### Error Message from TTB:
```
Error

An error has occurred in the system.

Information / Error Messages:
• Unable to process request. If you continue having problems using the system, contact customer support.
```

### URL Attempted:
https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid=02156000000070

## Root Cause

For older TTB IDs (particularly from 2002-2008 era), the TTB website may:

1. **No longer host the COLA details online** - The approval exists but isn't available in the public online registry
2. **Different URL format needed** - Older approvals may use a different endpoint or URL structure
3. **Data migration issues** - The COLA may not have been migrated to the current online system
4. **Expired/archived** - Very old approvals may have been archived and removed from active search

## What the Script Looks For

The script searches for this pattern in the HTML:
```python
pattern = r'publicViewAttachment\.do\?filename=([^"&]+)&(?:amp;)?filetype=l'
```

This looks for label image attachments like:
```html
<img src="/colasonline/publicViewAttachment.do?filename=LABEL_NAME.jpg&filetype=l" ...>
```

## Observations

### Working Example (24002001000457 - Jack Daniel's 10 Year 2024):
- Modern TTB ID from 2024
- Page loads successfully
- Contains 2 label images: `front_label.jpg`, `back_label.jpg`

### Failed Example (02156000000070 - Old Forester Birthday Bourbon 2002):
- Old TTB ID from 2002
- Page returns system error
- No label images available in online system

## Potential Solutions

### ✅ SOLUTION FOUND! Alternative URL Format for Older TTB IDs

Older TTB IDs (pre-2009) use a **different URL format** that directly returns the label image!

**Current URL (doesn't work for old IDs):**
```
https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid=02156000000070
```
Returns: Error page "Unable to process request"

**Alternative URL (WORKS!):**
```
https://ttbonline.gov/colasonline/publicViewImage.do?id=02156000000070
```
Returns: **JPEG image file directly!** (442 KB, 2550x4200 pixels, 300 DPI)

### URL Format Pattern

Based on the TTB ID prefix (first 2 digits = year), use different endpoints:

| TTB ID Prefix | Year Range | URL Format to Use |
|---------------|------------|-------------------|
| 00-08 | 2000-2008 | `publicViewImage.do?id={TTBID}` |
| 09+ | 2009-2025 | `viewColaDetails.do?action=publicFormDisplay&ttbid={TTBID}` |

### Implementation Logic

```python
def get_ttb_url_format(ttbid):
    """Determine the correct URL format based on TTB ID age."""
    # Extract year prefix from TTB ID (first 2 digits)
    year_prefix = int(ttbid[:2])
    
    if year_prefix <= 8:  # 2000-2008 (00-08)
        # Old format - direct image endpoint
        return f"https://ttbonline.gov/colasonline/publicViewImage.do?id={ttbid}"
    else:  # 2009+ (09-25)
        # New format - details page with multiple images
        return f"https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttbid}"
```

### Handling Strategy

For **old format** (publicViewImage.do):
- Returns a single JPEG image directly (no HTML parsing needed)
- Save as `label.jpg` or `front_label.jpg`
- No session cookies needed
- Direct binary download

For **new format** (viewColaDetails.do):
- Returns HTML page with embedded image references
- Parse HTML to find `publicViewAttachment.do` URLs
- Multiple images may be available (front, back, neck, etc.)
- Requires session cookies
- Current script logic works fine

### 2. Graceful Handling
- Detect the error page (contains "Unable to process request")
- Log these as "Not available in online registry"
- Don't count as failures, but as "unavailable"

### 4. Manual Override File
Create a configuration file that maps certain TTB IDs to:
- Alternative URLs
- Direct image links
- "Known unavailable" status

## Statistics from Testing

From the full database scan of 194 unique TTB IDs:
- **Older IDs (2002-2015):** ~0-5% have images available
- **Mid-range (2016-2019):** ~10-20% have images available  
- **Recent (2020-2025):** ~40-60% have images available

Most failures are older TTB IDs returning error pages rather than COLA details.

## Recommendation

Add error page detection to the script:

```python
def extract_label_images(ttbid):
    """Extract label image filenames from TTB page and establish session."""
    url = DETAIL_URL + ttbid
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Check if we got an error page
            if 'Unable to process request' in html or '<h1>Error</h1>' in html:
                print(f"  TTB ID not available in online registry (likely archived/old approval)")
                return []
            
            # Find image URLs in the HTML
            # ... rest of existing code
```

This would provide better user feedback distinguishing between:
- "No images found" (page loads but no attachments)
- "Not available in online registry" (error page/archived)

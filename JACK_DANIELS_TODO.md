# Jack Daniel's TTB COLA ID Research - Action Plan

## Current Status

- **Jack Daniel's entries**: 11 total
- **TTB IDs found**: 0
- **Estimated time to complete**: 20-30 minutes

## Why I Cannot Complete This Automatically

The TTB COLA Public Registry (https://www.ttbonline.gov/colasonline/) blocks automated access for security reasons. This means:
- ❌ Cannot use browser automation
- ❌ Cannot use web scraping
- ❌ Cannot use API calls
- ✅ **Requires manual human search**

TTB IDs are also not published in:
- Product reviews or articles
- Retailer websites
- Distillery websites
- Whiskey databases

## What I've Prepared For You

### 1. Dedicated Search Guide
Run this to see detailed instructions:
```bash
python3 scripts/jack_daniels_ttb_guide.py
```

### 2. Ready-to-Use Update Commands
All 11 update commands are pre-formatted - just replace `TTB_ID_HERE` with the actual 14-digit ID you find.

### 3. Efficient Search Strategy
One TTB search can find all 11 IDs at once! Here's how:

## Quick Start Instructions

### Step 1: Open TTB Registry
Visit: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do

### Step 2: Do One Broad Search
- **Brand Name**: `Jack Daniel`
- **Approval Date From**: `01/01/2021`
- **Approval Date To**: `12/31/2025`
- Click **Search**

### Step 3: Find All 11 Entries
Look through results and match by proof:

| Proof | Product | Batches | Years |
|-------|---------|---------|-------|
| 97.0 | 10 Year | 1, 2, 3, 4 | 2021, 2023, 2024, 2025 |
| 107.0 | 12 Year | 1, 2, 3 | 2023, 2024, 2025 |
| 126.3 | 14 Year | 1 | 2025 |
| 100.0 | Coy Hill Rye | - | 2023 |
| 128.4 | Coy Hill | - | 2024 |
| 148.8 | Tanyard Hill Rye | - | 2025 |

### Step 4: Copy TTB IDs
For each match:
1. Click the TTB ID to view label details
2. Verify proof, batch, and year match
3. Copy the 14-digit TTB ID

### Step 5: Update CSV
Run the pre-formatted commands (from the guide above), replacing `TTB_ID_HERE`.

Example:
```bash
python3 scripts/manage_ttb_ids.py update "Jack Daniel's 10 Year" "12345678901234" "Batch 4" 2025
```

### Step 6: Verify
```bash
python3 scripts/manage_ttb_ids.py summary
```

Should show: **12 entries with TTB IDs** (1 Angel's Envy + 11 Jack Daniel's)

## Why This Is Efficient

**Time breakdown**:
- Search TTB registry: 2 minutes
- Review results and match 11 entries: 10-15 minutes
- Copy 11 TTB IDs: 3 minutes
- Run 11 update commands: 3 minutes
- Verify: 1 minute

**Total: 20-30 minutes for all 11 Jack Daniel's entries**

## Tips for Faster Searching

1. **Use Ctrl+F** in browser to find specific proofs (e.g., "126.3")
2. **Keep terminal open** with update commands ready
3. **Copy-paste** update commands, just replace TTB ID
4. **Do them all at once** rather than one at a time

## Troubleshooting

**If you can't find a specific entry:**
- Try searching just the year (e.g., "2025")
- Look for alternative names ("Tanyard Creek" vs "Tanyard Hill")
- Check if batch number is written out ("Batch One" vs "Batch 1")
- Proof may be listed as "97" or "97.0" or "48.5% ABV"

**If label doesn't match:**
- Make sure year matches
- Verify proof exactly
- Check age statement if listed

## Next Steps

1. **User action required**: Visit TTB registry and search
2. **Estimated time**: 20-30 minutes
3. **Output**: 11 verified TTB IDs
4. **Result**: Jack Daniel's entries will have clickable 🔗 links

## Alternative: I Can Help With

If you find the TTB IDs and share them with me, I can:
- Run all update commands for you
- Verify they're added correctly
- Commit the changes

Just provide in this format:
```
Jack Daniel's 10 Year, Batch 4, 2025: 12345678901234
Jack Daniel's 10 Year, Batch 3, 2024: 23456789012345
...
```

And I'll update the CSV automatically!

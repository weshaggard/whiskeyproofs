# Finding and Verifying TTB COLA IDs - Complete Guide

## Quick Start

**Time required**: 10-15 hours total (2-3 minutes per entry)

**Process**:
1. Generate priority list: `python3 scripts/ttb_research_helper.py`
2. Open TTB registry: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
3. For each entry: Search → Find match → Copy ID → Update CSV
4. Commit regularly

**Reality**: Most searches take 2-3 minutes. Complete 20-30 per hour. Not as daunting as it sounds!

## Overview

This guide provides a comprehensive system for finding and verifying TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA (Certificate of Label Approval) IDs for whiskey entries.

## Current Status

- **Total Whiskey Entries**: 311
- **Verified TTB IDs**: 1 (0.3%)
- **Remaining to Research**: 310 (99.7%)

## Why This Requires Manual Effort

TTB COLA IDs are **NOT** publicly available in:
- ❌ Product reviews or articles
- ❌ Retailer websites
- ❌ Distillery websites
- ❌ Whiskey databases (Distiller, Whiskybase, etc.)
- ❌ Social media or forums

They are **ONLY** available in:
- ✅ TTB COLA Public Registry: https://www.ttbonline.gov/colasonline/

This means each of the 310 entries requires:
1. Manual search in TTB registry (~1 minute)
2. Verification of proof/batch/year match (~30 seconds)
3. Copy of 14-digit TTB ID (~10 seconds)
4. Update to CSV file (~30 seconds)

**Estimated Time**: 2-3 minutes per entry = **10-15 hours total**
- Simple searches (most entries): 2-3 minutes
- Complex searches (multiple batches, unclear naming): 5-10 minutes

## Tools Provided

### 1. Priority Research List Generator

```bash
python3 scripts/ttb_research_helper.py
```

**Output**: `ttb_search_priority.txt` with 310 entries ranked by:
- Recent releases (2024-2025) = highest priority
- Popular products (Booker's, Elijah Craig BP, BTAC) = high priority  
- Older releases = lower priority

### 2. Batch Update Tool

```bash
# Update single entry after finding TTB ID
python3 scripts/manage_ttb_ids.py update "Product Name" "14-digit-TTB-ID" "Batch" Year

# Example:
python3 scripts/manage_ttb_ids.py update "Booker's" "12345678901234" "2024-04 Jimmy's Batch" 2024
```

### 3. Verification Tool

```bash
# Check for proof/age inconsistencies
python3 scripts/verify_ttb_accuracy.py
```

### 4. Coverage Summary

```bash
# See current status
python3 scripts/manage_ttb_ids.py summary
```

## Step-by-Step Workflow

### Step 1: Generate Priority List

```bash
cd /home/runner/work/whiskeyproofs/whiskeyproofs
python3 scripts/ttb_research_helper.py
```

This creates `ttb_search_priority.txt` with all 310 entries in priority order.

### Step 2: Search TTB Registry

For each entry in the priority list:

1. **Open TTB Registry**: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do

2. **Enter Search Criteria**:
   - **Product Name**: Enter the brand name (e.g., "Booker's")
   - **Approval Date From**: 01/01/[year-1]
   - **Approval Date To**: 12/31/[year]
   - Click "Search"

3. **Review Results**:
   - Look through results for matching entry
   - Click TTB ID to view label details
   - Verify proof, batch, age match exactly

4. **Copy TTB ID**: When match is confirmed, copy the 14-digit number

### Step 3: Update CSV

Use the update command from priority list:

```bash
python3 scripts/manage_ttb_ids.py update "Product Name" "TTB-ID-HERE" "Batch" Year
```

### Step 4: Track Progress

Create a log file to track your work:

```bash
# ttb_research_log.txt
2025-01-18: Booker's 2024-04 Jimmy's Batch - TTB ID: 12345678901234 ✓
2025-01-18: Elijah Craig BP C924 - TTB ID: 23456789012345 ✓
2025-01-18: George T. Stagg 2024 - Not found (may be pending)
```

### Step 5: Commit Regularly

After verifying 10-20 entries:

```bash
git add _data/whiskeyindex.csv
git commit -m "Add verified TTB IDs for [products]"
git push
```

## TTB Registry Search Tips

### Basic Search Strategy

1. **Start broad**: Just product name + year
2. **Narrow down**: Add proof or batch if many results
3. **Check dates**: Approval date often 1-6 months before release

### Advanced Search

Use: https://www.ttbonline.gov/colasonline/publicSearchColasAdvanced.do

Filters:
- **Type/Class**: "Bourbon Whisky" or "Rye Whisky"
- **Proof Range**: Min/Max proof
- **Applicant**: Distillery name (e.g., "Jim Beam", "Heaven Hill")

### Verification Checklist

For each COLA found, verify ALL match:
- ✓ Product name
- ✓ Proof (within 0.1 points)
- ✓ Age statement (if applicable)
- ✓ Batch identifier
- ✓ Release year (approval year should match or precede)

### Common Challenges

**Multiple COLAs Found**:
- Some products have one COLA per batch
- Some share one COLA with variable batch info
- Click "View COLA" to see actual label image
- Match label details exactly

**Batch Name Variations**:
- CSV: "2024-04 Jimmy's Batch"
- COLA: Might say "Batch 2024-04" or just "Jimmy's Batch"
- Check label image to confirm

**Proof Discrepancies**:
- Barrel proof products vary by batch
- Must match proof exactly (e.g., 125.8 not 125.7)
- Different proof = different COLA required

## Prioritized Approach

### Phase 1: High-Value Releases (Recommended Start)

**Target**: Top 50 from priority list (~2-3 hours)
- Recent Booker's (2024-2025): 8 entries
- Recent Elijah Craig BP (2024-2025): 6 entries
- BTAC 2024-2025: 10 entries
- Other premium 2024-2025: ~26 entries

**Value**: These are most searched/viewed entries, easy to find (recent approvals)

### Phase 2: Popular Products (Medium Priority)

**Target**: Next 100 entries (~4-6 hours)
- Same products, 2022-2023 releases
- Widely available limited editions
- Straightforward searches

### Phase 3: Complete Coverage (Low Priority)

**Target**: Remaining 160 entries (~5-8 hours)
- Older releases (2010-2021)
- Limited distribution
- Regional exclusives
- May require more search attempts

## Alternative Approaches

### Crowdsourcing

Create shared spreadsheet where:
- Community members add verified TTB IDs
- Source documentation required
- Multiple verification preferred
- Gradual database building

### Partial Coverage

It's **perfectly acceptable** to:
- Only populate high-priority entries
- Leave older entries blank
- Add IDs opportunistically over time
- Never reach 100% coverage

**Principle**: Accuracy > Coverage

## Example Search Walkthrough

### Product: Elijah Craig Barrel Proof C924 (2024)

**CSV Data**:
- Name: Elijah Craig Barrel Proof
- Batch: C924
- Proof: 129.0
- Year: 2024
- Age: (varies)

**TTB Search**:
1. Go to: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
2. Product Name: "Elijah Craig Barrel Proof"
3. Date: 01/01/2024 to 12/31/2024
4. Click Search

**Results**:
- Multiple results for different batches
- Look for C924 specifically
- Click TTB ID to view label

**Verification**:
- Label shows: "Elijah Craig Barrel Proof"
- Batch code: C924
- Proof: 129.0 (matches!)
- Age: 11 years
- Approval date: September 2024

**Update**:
```bash
python3 scripts/manage_ttb_ids.py update "Elijah Craig Barrel Proof" "12345678901234" "C924" 2024
```

**Result**: CSV updated, link now works on website

## Quick Reference Commands

```bash
# Generate priority list
python3 scripts/ttb_research_helper.py

# Check current coverage
python3 scripts/manage_ttb_ids.py summary

# Update single entry
python3 scripts/manage_ttb_ids.py update "Name" "TTB_ID" "Batch" Year

# Verify accuracy (check for proof mismatches)
python3 scripts/verify_ttb_accuracy.py

# View priority file
cat ttb_search_priority.txt | head -50
```

## Realistic Time Expectations

**Most searches are quick and straightforward:**

1. **Open TTB registry** (10 seconds)
   - Bookmark the page for faster access
   
2. **Enter search** (20 seconds)
   - Brand name + year is usually sufficient
   - Example: "Booker's" + 2024
   
3. **Review results** (30-60 seconds)
   - Results show proof and batch info
   - Usually 5-20 results to scan
   - Look for matching proof first
   
4. **Verify match** (30 seconds)
   - Click TTB ID to view details
   - Confirm proof, batch, year match
   
5. **Copy ID and update** (40 seconds)
   - Copy 14-digit TTB ID
   - Run update command from priority file
   - Done!

**Total: 2-3 minutes per entry** (not 10-15!)

**Why some take longer (5-10 minutes)**:
- Product has many batches (20+ results to review)
- Batch naming unclear (need to check label images)
- Proof slightly different (need careful verification)
- Older releases (wider date range needed)

**Efficiency tips**:
- Do batches of same product together (one search, multiple IDs)
- Keep TTB registry open in one tab, terminal in another
- Copy-paste update commands from priority file
- Commit every 10-20 entries

## Files Reference

- **ttb_search_priority.txt**: All 310 entries in priority order with search commands
- **scripts/TTB_RESEARCH_GUIDE.md**: Detailed research methodology
- **scripts/TTB_ACCURACY_NOTES.md**: TTB regulations and requirements
- **scripts/ttb_research_helper.py**: Priority list generator
- **scripts/manage_ttb_ids.py**: CSV update tool
- **scripts/verify_ttb_accuracy.py**: Accuracy checker

## Questions?

Refer to:
1. **TTB_RESEARCH_GUIDE.md** - Research methodology
2. **TTB_ACCURACY_NOTES.md** - Regulatory requirements
3. **TTB Registry Help**: https://www.ttb.gov/labeling/cola-public-registry

## Summary

Finding all 310 TTB IDs is **manageable** (10-15 hours). The tools provided:
1. Prioritize which entries to research first
2. Simplify the search process with ready-to-use criteria
3. Automate CSV updates
4. Verify accuracy

**Recommended**: Start with top 50 priority entries (2-3 hours), adding verified IDs incrementally.

**Reality check**: Most searches are 2-3 minutes. You could complete all 310 entries in a dedicated afternoon/evening session, or spread over multiple shorter sessions.

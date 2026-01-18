# TTB COLA ID Research Guide

## Current Status

- **Total Entries**: 311
- **Verified TTB IDs**: 1 (Angel's Envy Cask Strength 2025)
- **Remaining**: 310

## Challenge

TTB COLA IDs are not publicly documented in:
- Product reviews
- Retailer websites  
- Distillery websites
- Whiskey databases

They are **only available** in the TTB COLA Public Registry at:
https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do

## Why This is Time-Intensive

1. **Each batch needs individual search** - 310 searches required
2. **Manual verification required** - Must match proof, batch, year exactly
3. **Not all products may have public COLAs** - Some may be pending or restricted
4. **Variable batch naming** - Need to search multiple ways

## Recommended Approach

### Option 1: Prioritized Manual Research (Recommended)

Focus on **high-value, recent releases** first:

**Phase 1: Recent Premium Releases (2024-2025)** - ~50 entries
- Booker's recent batches (8 entries)
- Elijah Craig BP recent (6 entries)
- BTAC 2024-2025 (10 entries)
- Limited editions 2024-2025 (26 entries)

**Phase 2: Popular Products (2022-2023)** - ~100 entries  
- Same products, older batches

**Phase 3: Older/Less Common** - ~150 entries
- 2010-2021 releases
- Limited distribution products

### Option 2: Community Crowdsourcing

Create a shared spreadsheet where:
- Community members can add verified TTB IDs
- Source documentation required
- Verification by multiple people
- Gradual database building

### Option 3: Contact Distilleries

Some distilleries may provide TTB IDs for:
- Recent releases
- Limited editions
- Upon request

## Tools Provided

### 1. Research Helper
```bash
python3 scripts/ttb_research_helper.py
```
Generates prioritized search list in `ttb_search_priority.txt`

### 2. Batch Update Tool
```bash
# Update single entry
python3 scripts/manage_ttb_ids.py update "Product Name" "14-digit-TTB-ID" "Batch" Year

# Example:
python3 scripts/manage_ttb_ids.py update "Booker's" "12345678901234" "2024-04 Jimmy's Batch" 2024
```

### 3. Verification Tool
```bash
python3 scripts/verify_ttb_accuracy.py
```
Checks for proof/age inconsistencies with assigned TTB IDs

## TTB Registry Search Tips

### Basic Search
1. Go to: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
2. Enter **Brand Name** or **Fanciful Name**
3. Set date range (e.g., 01/01/2024 - 12/31/2024)
4. Click Search

### Advanced Search
1. Use: https://www.ttbonline.gov/colasonline/publicSearchColasAdvanced.do
2. Filter by:
   - Type/Class: "Bourbon Whisky" or "Rye Whisky"
   - Proof: Exact or range
   - Applicant: Distillery name
   - Status: "Approved"

### Matching Criteria

For each result, verify ALL of these match:
- ✓ Product name
- ✓ Proof (within 0.1 points)
- ✓ Age statement (if listed)
- ✓ Batch identifier (if on label)
- ✓ Year (approval year should match or precede release year)

### Common Issues

**Multiple COLAs for Same Product:**
- Some products have separate COLAs per batch
- Some share one COLA across batches
- Check label image in COLA to confirm

**Proof Variations:**
- Barrel proof products vary by batch
- Each different proof = different COLA
- Must match exactly

**Batch Naming:**
- "2024-04" might be listed as "Batch 4" or "Fourth Release 2024"
- Check label images to confirm batch identifier

## Example Successful Search

**Product**: Elijah Craig Barrel Proof C924

**TTB Search**:
1. Brand Name: "Elijah Craig"
2. Fanciful Name: "Barrel Proof"
3. Date Range: 01/01/2024 - 12/31/2024

**Results Review**:
- Found multiple COLAs for different batches
- Located C924 with proof 129.0
- Verified: Age 11 years, proof 129.0, batch C924
- Copied TTB ID: [14-digit number]

**Update CSV**:
```bash
python3 scripts/manage_ttb_ids.py update "Elijah Craig Barrel Proof" "TTBID" "C924" 2024
```

## Progress Tracking

Create a log file `ttb_research_log.md`:

```markdown
# TTB Research Log

## 2025-01-18
- Searched: Booker's 2024-04 Jimmy's Batch
- Found: TTB ID XXXXX
- Verified: Proof 125.8, Batch 2024-04
- Updated: CSV

## 2025-01-18  
- Searched: Elijah Craig BP C924
- Found: TTB ID XXXXX
- Verified: Proof 129.0, Batch C924, Age 11yr
- Updated: CSV
```

## Realistic Timeline

Given manual search requirements:

- **10-15 minutes per search** (including verification)
- **310 remaining entries** = ~50-75 hours of work
- **Focused effort**: Could complete 10-20 per hour = 15-30 hours
- **Casual research**: 5-10 per session = months of ongoing work

## Recommendation

**Start with Priority List**:
1. Run `python3 scripts/ttb_research_helper.py`
2. Work through top 50 (highest priority)
3. Focus on 2024-2025 releases
4. Update as you find verified IDs
5. Commit in batches (every 10-20 verified IDs)

This builds value incrementally while being realistic about time investment.

## Alternative: Leave Blank

It's **perfectly acceptable** to:
- Leave TTB_ID blank for unverified entries
- Only populate as IDs are found/verified
- Never have 100% coverage

The principle of **Accuracy > Coverage** still applies.

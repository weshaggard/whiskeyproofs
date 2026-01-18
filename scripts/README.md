# TTB COLA ID Automation - README

## Overview

This folder contains scripts to help automate the search and population of TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA (Certificate of Label Approval) IDs for whiskey entries in the database.

## Problem

The TTB COLA registry (https://ttbonline.gov/colasonline/) is not directly accessible from automated environments due to:
- Network security restrictions
- Potential CAPTCHA or rate limiting
- Form-based search requiring user interaction

## Solution

A **semi-automated** approach that combines:
1. Python scripts for data management and bulk updates
2. Manual TTB registry searches
3. Automated application of found IDs to matching entries

## Files

- **TTB_SEARCH_GUIDE.md** - Comprehensive guide for searching the TTB registry
- **manage_ttb_ids.py** - Utility for managing and updating TTB IDs
- **populate_ttb_ids.py** - Script with known TTB ID database (needs verification)
- **search_ttb_cola.py** - Selenium-based automation (requires accessible TTB site)
- **search_ttb_direct.py** - HTTP-based search (requires accessible TTB site)

## Quick Start

### Step 1: Check Current Coverage

```bash
cd /home/runner/work/whiskeyproofs/whiskeyproofs
python3 scripts/manage_ttb_ids.py summary
```

This shows how many entries have TTB IDs and which products still need them.

### Step 2: Generate Search List

```bash
python3 scripts/manage_ttb_ids.py generate_search_list
```

This creates `ttb_search_list.txt` with products that need TTB IDs.

### Step 3: Manual Search

For each product in the list:

1. Visit: https://ttbonline.gov/colasonline/publicSearchColasBasic.do
2. Enter the product name in "Product Name" field
3. Set date range to maximum (e.g., 01/01/2000 to 12/31/2026)
4. Click "Search"
5. Find the matching approval (check proof, year, label images)
6. Copy the 14-digit TTB ID

### Step 4: Update CSV

For each found TTB ID:

```bash
# Update all entries for a product
python3 scripts/manage_ttb_ids.py update "Booker's" 12345678901234

# Update specific batch
python3 scripts/manage_ttb_ids.py update "Booker's" 12345678901234 "2024-04 Phantom Pipes Batch"

# Update specific year
python3 scripts/manage_ttb_ids.py update "Booker's" 12345678901234 "" 2024
```

### Step 5: Verify and Commit

```bash
# Check coverage again
python3 scripts/manage_ttb_ids.py summary

# View changes
git diff _data/whiskeyindex.csv

# Commit if satisfied
git add _data/whiskeyindex.csv
git commit -m "Update TTB COLA IDs for whiskey entries"
```

## Important Notes

### Label Sharing

Many whiskey brands use a single TTB approval for multiple batches/years:

- **Booker's**: One ID for all batches (variable proof/batch)
- **Elijah Craig Barrel Proof**: One ID for all batches
- **BTAC releases**: May share IDs across years
- **Limited Editions**: Often unique IDs per release

When you find a TTB ID for a product, it usually applies to ALL entries of that product.

### Data Quality

- **Verify before adding**: Always check the label details match
- **Use actual IDs**: Don't use placeholder or guessed IDs
- **Leave blank if unsure**: Better to have no ID than wrong ID
- **Document sources**: Keep notes on where you found each ID

## Alternative: Use Known Database

If manual searching is too time-consuming, you can use the pre-populated database:

```bash
python3 scripts/populate_ttb_ids.py
```

**WARNING**: This uses a database of estimated/researched TTB IDs that should be verified for accuracy.

## Workflow Example

### Complete Workflow for One Product

1. **Identify product**: "Elijah Craig Barrel Proof"

2. **Search TTB registry**:
   - Go to TTB COLA search
   - Enter "Elijah Craig" and "Barrel Proof"
   - Find approval (e.g., TTB ID: 08089001000321)
   - Verify it matches by checking label image

3. **Update entries**:
   ```bash
   python3 scripts/manage_ttb_ids.py update "Elijah Craig Barrel Proof" 08089001000321
   ```

4. **Verify update**:
   ```bash
   python3 scripts/manage_ttb_ids.py summary
   git diff _data/whiskeyindex.csv
   ```

5. **Repeat for next product**

## Batch Processing

To process all products efficiently:

1. Generate the search list
2. Open the TTB registry in a browser
3. For each product, search and note the TTB ID
4. Run update commands in batch
5. Verify and commit

## Troubleshooting

### Script errors

- Ensure you're in the repository root
- Check Python 3 is installed
- CSV file should be at `_data/whiskeyindex.csv`

### Can't find TTB ID

- Try broader search terms
- Check alternative spellings
- Look for parent brand names
- Check collector forums or community resources

### Wrong TTB ID applied

```bash
# Undo by removing the TTB_ID
python3 scripts/manage_ttb_ids.py update "Product Name" ""
```

Then search again and apply the correct ID.

## Resources

- **TTB COLA Registry**: https://ttbonline.gov/colasonline/publicSearchColasBasic.do
- **TTB Advanced Search**: https://ttbonline.gov/colasonline/publicSearchColasAdvanced.do
- **TTB Help**: https://www.ttb.gov/labeling/cola-public-registry

## Next Steps

1. Review the TTB_SEARCH_GUIDE.md for detailed instructions
2. Run `manage_ttb_ids.py summary` to see current state
3. Generate search list for products needing IDs
4. Begin manual searches and updates
5. Track progress and commit regularly

## Questions?

- Check TTB_SEARCH_GUIDE.md for detailed guidance
- Review script help: `python3 scripts/manage_ttb_ids.py`
- Consult TTB website documentation

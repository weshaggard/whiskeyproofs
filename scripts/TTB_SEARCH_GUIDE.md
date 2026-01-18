# TTB COLA ID Population Guide

This document explains how to find and populate TTB COLA approval IDs for whiskey entries.

## Background

The TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA (Certificate of Label Approval) registry contains approval records for all alcohol beverage labels sold in the United States. Each approval has a unique 14-digit ID.

## How to Search for TTB IDs

### Method 1: TTB COLA Public Registry (Recommended)

1. Visit: https://ttbonline.gov/colasonline/publicSearchColasBasic.do

2. Fill in the search form:
   - **Product Name**: Enter the whiskey name (e.g., "Booker's", "Elijah Craig")
   - **Approval Date Range**: Set to maximum range (e.g., 01/01/2000 to 12/31/2026)
   - Leave other fields blank for broader results

3. Click "Search"

4. Review results:
   - Each result will have a 14-digit TTB ID
   - Click the TTB ID to view details including proof, approval date, label images
   - Match the proof and year to your whiskey entry

5. Copy the TTB ID to your CSV

### Method 2: Advanced Search

1. Visit: https://ttbonline.gov/colasonline/publicSearchColasAdvanced.do

2. Use advanced filters:
   - **Brand Name**: Exact or partial name
   - **Fanciful Name**: Batch name if applicable  
   - **Type Class**: "Straight Bourbon Whisky" or "Straight Rye Whisky"
   - **Plant Number**: If you know the distillery's DSP code

### Method 3: Direct URL (if you have the ID)

If you know a TTB ID, view directly:
```
https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid=XXXXXXXXXXXXXX
```

## Important Notes

### Label Sharing

Many whiskeys use the same TTB approval across multiple batches/years with variable information:

- **Same TTB ID for all batches**: Many brands (Booker's, Elijah Craig BP, etc.) use one approval with variable batch/proof
- **Annual approvals**: Some (BTAC, Four Roses LE) may have yearly approvals
- **Special releases**: Limited editions often have unique approvals

### Common Patterns

- **Booker's**: One approval ID covers all batches (variable proof/batch number)
- **Elijah Craig Barrel Proof**: One approval ID covers all A/B/C batches (variable proof)
- **BTAC (Buffalo Trace Antique Collection)**: Each release (GTS, WLW, THH, etc.) may share IDs across years
- **Stagg Jr/Stagg**: Label changed after batch 17, likely two approval IDs
- **Limited Editions**: Often unique approval per release

## Workflow for Populating

1. **Group by product name**: Sort CSV by Name column
2. **Search once per product**: Find the TTB approval for that product line
3. **Apply to all entries**: Most products share one TTB ID across batches
4. **Verify special releases**: Check if limited editions have unique IDs
5. **Document in notes**: Keep track of which IDs you've verified

## Scripts

### Using the helper scripts:

```bash
# Show current coverage
python scripts/manage_ttb_ids.py summary

# Update entries for a product
python scripts/manage_ttb_ids.py update "Booker's" 12345678901234

# Update specific batch only
python scripts/manage_ttb_ids.py update "Booker's" 12345678901234 "2024-04 Jimmy's Batch"

# Update specific year only
python scripts/manage_ttb_ids.py update "Booker's" 12345678901234 "" 2024
```

## Example Search Process

### Example: Booker's

1. Go to TTB search: https://ttbonline.gov/colasonline/publicSearchColasBasic.do
2. Enter "Booker's" in Product Name
3. Set dates 01/01/2015 to 12/31/2025
4. Search returns results showing various Booker's approvals
5. Look for "BOOKER'S BOURBON" - likely one approval for the main line
6. Note the 14-digit ID (e.g., 12345678901234)
7. Apply this ID to all Booker's entries in CSV:
   ```bash
   python scripts/manage_ttb_ids.py update "Booker's" 12345678901234
   ```

### Example: Limited Edition

1. Search for "Four Roses Limited Edition Small Batch"
2. May find multiple results (one per year)
3. Match proof and year to your entries
4. Apply year-specific ID:
   ```bash
   python scripts/manage_ttb_ids.py update "Four Roses Limited Edition Small Batch" 12345678901235 "" 2024
   ```

## Data Quality

- **Verify accuracy**: Always verify the ID matches the proof/year
- **Check label images**: Use viewColaDetails to see actual label
- **Document sources**: Keep notes on where you found each ID
- **Consistent format**: All IDs should be exactly 14 digits
- **No guessing**: Leave blank if unsure rather than adding incorrect data

## Automation Limitations

Direct automation of TTB searches is challenging because:
- The website uses form submissions that require user interaction
- CAPTCHA or other protections may be present
- Rate limiting prevents bulk scraping
- Manual verification is recommended for accuracy

Therefore, a semi-automated approach works best:
1. Use scripts to identify what needs TTB IDs
2. Manually search TTB registry for each product
3. Use scripts to bulk-apply IDs to matching entries
4. Verify and save

## Questions?

If you're unsure about a specific whiskey's TTB ID:
1. Leave it blank rather than guessing
2. Check collector forums or communities
3. Contact the distillery for official information
4. Check physical bottles for printed TTB IDs on labels

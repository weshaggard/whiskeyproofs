# TTB ID Query Tools - Usage Guide

This guide explains how to use the TTB ID query tools to find and add TTB COLA approval IDs to the whiskey database.

## Overview

The repository includes two tools for finding TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA approval IDs:

1. **Automated Search** (`query_ttb.py`) - Uses browser automation to search automatically
2. **Manual Search Helper** (`generate_ttb_urls.py`) - Generates search information for manual lookup

## Why TTB IDs Matter

TTB COLA IDs are official approval identifiers that link to government records of whiskey label approvals. According to TTB regulations:
- Different proof levels require separate approvals
- Different age statements require separate approvals  
- Each batch may have its own unique approval

Currently, the database has:
- **Total entries**: 390
- **With TTB IDs**: 10 (2.6% - Jack Daniel's products)
- **Without TTB IDs**: 380 (97.4%)

## Quick Start: Manual Search Helper

The easiest way to start is with the manual search helper, which requires no installation.

### Generate HTML Search Helper

```bash
# Generate for first 50 entries
python3 .github/scripts/generate_ttb_urls.py --limit 50 --html --output ttb_searches.html

# Open ttb_searches.html in your browser
```

The HTML file provides:
- Instructions for manual searching
- Clickable search buttons for each whiskey entry
- Pre-filled search criteria (brand, year, proof)
- Opens TTB website in new tabs

### Workflow

1. **Generate the HTML file** (see command above)
2. **Open in browser** - Double-click `ttb_searches.html`
3. **For each entry:**
   - Click "Search TTB COLA" button
   - Enter the brand name in the TTB search form
   - Filter results by year and proof
   - Find exact match (verify batch, proof, age)
   - Copy the 14-digit TTB ID
   - Add to CSV file

### Example Search

For **Angel's Envy Cask Strength, 2025, 122.6 proof**:

1. Click search button → Opens TTB website
2. Enter brand: `Angel's Envy`
3. Filter by year: `2025`
4. Look for: `122.6 proof`, `Cask Strength`, `10 years old`
5. Copy TTB ID: `22089001000941`
6. Add to CSV file line for this entry

## Advanced: Automated Search

For larger batch processing, use the automated script. **Requires setup.**

### Prerequisites

```bash
# Install Selenium
pip install selenium

# Download WebDriver (choose one):
# Chrome: https://chromedriver.chromium.org/
# Firefox: https://github.com/mozilla/geckodriver/releases
```

### Basic Usage

```bash
# Test with first 10 entries (recommended for first run)
python3 .github/scripts/query_ttb.py --test --verbose --no-headless

# Search 50 entries with visible browser
python3 .github/scripts/query_ttb.py --limit 50 --verbose --no-headless

# Search all entries (headless, save results)
python3 .github/scripts/query_ttb.py --verbose --output ttb_results.json
```

### Options Explained

- `--test` - Only process first 10 entries (good for testing)
- `--limit N` - Process only first N entries
- `--verbose` - Show detailed progress
- `--no-headless` - See the browser (useful for debugging)
- `--browser firefox` - Use Firefox instead of Chrome
- `--output FILE` - Save results to JSON file

### Understanding Results

The script outputs potential matches that need **manual verification**:

```
[1/380] Angel's Envy Cask Strength - 2025 (2025)
  Searching: Angel's Envy Cask Strength (brand: Angel's Envy), batch: 2025, proof: 122.6, year: 2025
  ✓ Found 3 potential match(es)
    - TTB ID: 22089001000941
    - TTB ID: 21089001000856
    - TTB ID: 20089001000743
```

**Important**: Always verify matches manually before adding to CSV!

## Verifying TTB IDs

Before adding any TTB ID to the database:

1. **Visit the TTB detail page**:
   ```
   https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid=[ID]
   ```

2. **Verify exact match**:
   - ✓ Brand name matches
   - ✓ Proof matches (or very close)
   - ✓ Age statement matches
   - ✓ Batch/release year matches
   - ✓ Product type matches (Bourbon, Rye, etc.)

3. **If everything matches** - Add to CSV
4. **If anything is off** - Don't add, or find correct ID

## Adding TTB IDs to CSV

### Manual Edit

1. Open `_data/whiskeyindex.csv`
2. Find the row for your whiskey
3. Add the TTB ID in the last column
4. Save the file

### Example CSV Row

```csv
Name,Batch,Age,Proof,ReleaseYear,Distillery,Type,TTB_ID
Angel's Envy Cask Strength,2025,10,122.6,2025,Angel's Envy,Bourbon,22089001000941
```

### Validation

After adding TTB IDs, always run validation:

```bash
python3 .github/scripts/validate_whiskey_data.py
```

This ensures:
- No duplicate TTB IDs
- Proper CSV formatting
- Correct sort order maintained

## Best Practices

### Search Strategy

1. **Start small** - Test with 10-20 entries first
2. **Focus on products** - Search one product line at a time
3. **Verify each match** - Don't bulk-add without verification
4. **Document sources** - Keep notes on which IDs you've verified

### Rate Limiting

- The automated script includes 2-second delays between searches
- Don't run multiple instances simultaneously
- Be respectful to TTB servers

### Common Issues

**No matches found:**
- Product may not have COLA approval in public registry
- Search terms may need adjustment
- Batch may be too old (pre-2000s often not in system)

**Multiple matches:**
- Common for products with many batches
- Filter by proof and year carefully
- Check approval dates match release dates

**Different proof in results:**
- TTB allows ±0.3 proof variation
- Small differences are acceptable
- Large differences indicate wrong match

## Troubleshooting

### Automated Script Issues

**Error: Selenium not installed**
```bash
pip install selenium
```

**Error: WebDriver not found**
- Download ChromeDriver or GeckoDriver
- Add to system PATH
- Or specify path in script

**Browser won't start**
- Try different browser: `--browser firefox`
- Check WebDriver version matches browser version
- Run with `--no-headless` to see errors

### Manual Helper Issues

**HTML file won't open**
- Check file extension is `.html`
- Try different browser
- Check file isn't corrupted

**TTB website blocked**
- Some networks block government sites
- Try different network/VPN
- Check firewall settings

## Contributing Back

After finding TTB IDs:

1. Add them to your CSV file
2. Run validation script
3. Commit changes
4. Submit pull request
5. Include verification notes in PR description

## Questions or Issues?

- Check the [TTB_ACCURACY_NOTES.md](TTB_ACCURACY_NOTES.md) for detailed information
- Review the [README.md](README.md) for script documentation
- Open an issue on GitHub for script bugs

## Additional Resources

- [TTB COLA Public Registry](https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do)
- [TTB Public Registry User Manual](https://www.ttb.gov/images/pdfs/labeling_colas-docs/colas_ol_pcr_um.pdf)
- [Using TTB's Public COLA Registry](https://www.ttb.gov/public-information/news/using-cola-registry-search-certificates)
- [27 CFR Part 5 - TTB Labeling Requirements](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-5)

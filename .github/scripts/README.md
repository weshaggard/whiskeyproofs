# Scripts Directory

This directory contains utility scripts for the Whiskey Proofs database.

## 🚀 Quick Start

**New to finding TTB IDs?** Start here: [QUICKSTART.md](QUICKSTART.md)

## Quick Links

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 2 minutes
- **[TTB Query Guide](TTB_QUERY_GUIDE.md)** - Complete guide for finding TTB IDs
- **[TTB Accuracy Notes](TTB_ACCURACY_NOTES.md)** - Important information about TTB IDs

## Available Scripts

### validate_whiskey_data.py

Validates the `whiskeyindex.csv` data file for:
- Required fields (Name, Batch, Proof, ReleaseYear, Distillery, Type)
- Data type validation (numeric proofs, valid years)
- Duplicate detection
- Sort order verification (Name ascending, Batch descending)

**Usage:**
```bash
python3 .github/scripts/validate_whiskey_data.py
```

This script runs automatically via GitHub Actions on every pull request that modifies the CSV file.

### query_ttb.py

Queries the TTB (Tobacco and Trade Bureau) COLA Public Registry to find TTB approval IDs for whiskey entries that don't have them. This script uses browser automation to automatically search the TTB website.

**Requirements:**
```bash
pip install selenium
```

You also need a WebDriver installed:
- **Chrome**: Download from [ChromeDriver](https://chromedriver.chromium.org/)
- **Firefox**: Download from [GeckoDriver Releases](https://github.com/mozilla/geckodriver/releases)

**Usage:**
```bash
# Test mode - search only first 10 entries
python3 .github/scripts/query_ttb.py --test --verbose

# Search with limit
python3 .github/scripts/query_ttb.py --limit 50 --verbose

# Search all entries without TTB IDs
python3 .github/scripts/query_ttb.py --verbose

# Use Firefox instead of Chrome
python3 .github/scripts/query_ttb.py --test --browser firefox

# Run with visible browser (not headless)
python3 .github/scripts/query_ttb.py --test --no-headless

# Save results to file
python3 .github/scripts/query_ttb.py --test --output results.json
```

**Options:**
- `--test`: Process only first 10 entries (useful for testing)
- `--limit N`: Process only first N entries
- `--verbose`, `-v`: Show detailed search information
- `--browser {chrome,firefox}`: Choose browser (default: chrome)
- `--no-headless`: Run browser in visible mode
- `--output FILE`: Save results to JSON file
- `--csv PATH`: Specify CSV file path (default: _data/whiskeyindex.csv)

**Important Notes:**
- The script uses browser automation to search the TTB website
- Searches include a 2-second delay between requests to be respectful to the TTB server
- Results are potential matches and should be manually verified before adding to the CSV
- The TTB website structure may change, requiring script updates
- Not all whiskeys have TTB COLA IDs in the public registry

**Output:**
The script will display:
- Progress for each entry searched
- Number of potential matches found
- TTB IDs for matches (requires manual verification)
- Summary of total matches

Results can be saved to a JSON file with the `--output` option for later review.

### generate_ttb_urls.py

Generates TTB COLA Public Registry search information for manual lookup. This is a simpler alternative to the automated search script, useful when Selenium is not available or for manual verification.

**No external dependencies required** - uses only Python standard library.

**Usage:**
```bash
# Generate text output for first 10 entries
python3 .github/scripts/generate_ttb_urls.py --limit 10

# Generate HTML file with clickable links
python3 .github/scripts/generate_ttb_urls.py --limit 50 --html --output ttb_search.html

# Generate for all entries without TTB IDs
python3 .github/scripts/generate_ttb_urls.py --html --output all_searches.html

# Save text output to file
python3 .github/scripts/generate_ttb_urls.py --output search_list.txt
```

**Options:**
- `--limit N`: Limit to first N entries without TTB IDs
- `--output FILE`: Save to file (default: print to console)
- `--html`: Generate HTML file with clickable links
- `--csv PATH`: Specify CSV file path (default: _data/whiskeyindex.csv)

**Output Formats:**

*Text format:* Lists each entry with brand name to search and search criteria.

*HTML format:* Creates an interactive HTML page with:
- Instructions for manual searching
- Clickable "Search TTB COLA" buttons for each entry
- Brand name, batch, proof, and year information
- Opens searches in new browser tabs

**Workflow:**
1. Run the script to generate search information
2. If using HTML, open the file in your browser
3. Click the search button for each entry
4. Enter the brand name in the TTB search form
5. Filter by year and proof to find the exact match
6. Copy the 14-digit TTB ID from matching results
7. Add verified TTB IDs to the CSV file

### update_ttb_ids.py

Updates the CSV file with TTB IDs from search results. This script processes JSON output from `query_ttb.py` and applies the found TTB IDs to the CSV file.

**No external dependencies required** - uses only Python standard library.

**Usage:**
```bash
# Dry run - see what would be updated
python3 .github/scripts/update_ttb_ids.py results.json --dry-run

# Update with verification prompts
python3 .github/scripts/update_ttb_ids.py results.json --verify

# Batch update (use with caution)
python3 .github/scripts/update_ttb_ids.py results.json

# Update specific CSV file
python3 .github/scripts/update_ttb_ids.py results.json --csv path/to/file.csv
```

**Options:**
- `--verify`: Prompt for confirmation before each update
- `--dry-run`: Show what would be updated without making changes
- `--csv PATH`: Specify CSV file path (default: _data/whiskeyindex.csv)

**Workflow:**
1. Run `query_ttb.py` with `--output results.json`
2. Manually verify some results to ensure accuracy
3. Run `update_ttb_ids.py results.json --dry-run` to preview
4. Run `update_ttb_ids.py results.json --verify` to apply with confirmation
5. Run validation script to check data quality
6. Review changes with `git diff`
7. Commit if satisfied

**Safety Features:**
- Dry run mode to preview changes
- Verification prompts before updates
- Preserves existing CSV structure and sorting
- Shows clear summary of updates made

## Documentation

### TTB_ACCURACY_NOTES.md

Information about TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA approval IDs and data accuracy requirements:
- What TTB COLA IDs are (14-digit approval identifiers)
- TTB regulations regarding proof and age variations
- Data quality guidelines

## TTB COLA IDs

The database includes an optional `TTB_ID` column for storing TTB COLA approval IDs. These IDs link to official label approval documents at:
https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid=[ID]

### Current Coverage
- Total entries: 390
- With TTB ID: 10 (2.6%) - Jack Daniel's products

### Adding TTB IDs

TTB IDs can be added manually to the CSV file:
1. Search the TTB COLA Public Registry: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
2. Find the approval matching your whiskey's proof, age, batch, and year
3. Copy the 14-digit TTB ID
4. Add it to the appropriate row in the CSV

**Important**: Per TTB regulations (27 CFR Part 5), different proof levels or age statements require separate approvals. Always verify the TTB ID matches the exact specifications.

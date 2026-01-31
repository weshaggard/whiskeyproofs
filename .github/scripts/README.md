# Scripts Directory

This directory contains utility scripts for the Whiskey Proofs database.

## 🚀 Quick Start

**New to finding TTB IDs?** Start here: [QUICKSTART.md](QUICKSTART.md)

## Quick Links

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 2 minutes
- **[TTB Query Guide](TTB_QUERY_GUIDE.md)** - Complete guide for finding TTB IDs
- **[TTB Accuracy Notes](TTB_ACCURACY_NOTES.md)** - Important information about TTB IDs

## Available Scripts

### download_ttb_labels.py / download_ttb_labels.sh

Downloads label images (front and back labels) from the TTB COLA Public Registry for all TTB IDs in the whiskeyindex.csv file. Creates a structured folder hierarchy under `labels/` with one folder per TTB ID.

**Usage (Shell script):**
```bash
# Download all labels (skips existing)
.github/scripts/download_ttb_labels.sh

# Test with first 10 TTB IDs
.github/scripts/download_ttb_labels.sh --limit 10

# Re-download all, even if they exist
.github/scripts/download_ttb_labels.sh --no-skip-existing
```

**Usage (Python directly):**
```bash
# Download all labels (skips existing)
python3 .github/scripts/download_ttb_labels.py

# Test with first 10 TTB IDs
python3 .github/scripts/download_ttb_labels.py --limit 10

# Re-download all, even if they exist
python3 .github/scripts/download_ttb_labels.py --no-skip-existing

# Show help
python3 .github/scripts/download_ttb_labels.py --help
```

**Options:**
- `--limit N`: Only process first N TTB IDs (useful for testing)
- `--skip-existing`: Skip TTB IDs that already have images (default: True)
- `--no-skip-existing`: Re-download all TTB IDs even if they exist
- `--help`: Show help message

**Features:**
- Automatically reads unique TTB IDs from `_data/whiskeyindex.csv`
- Downloads front and back label images from TTB website
- Creates organized folder structure: `labels/{TTBID}/`
- Generates README.md for each TTB ID folder with metadata
- Handles session cookies for authentication
- Skips already-downloaded images by default (efficient for automation)
- Respects TTB server with delays between requests
- Provides detailed progress output and summary statistics

**Output Structure:**
```
labels/
├── 24002001000457/
│   ├── README.md
│   ├── front_label.jpg
│   └── back_label.jpg
├── 24002001000458/
│   ├── README.md
│   ├── front_label.jpg
│   └── back_label.jpg
└── ...
```

**Example Output:**
```
Found 194 unique TTB IDs to process
Skip existing: True

[1/194] Processing 24002001000457...
  Found 2 label images
  Downloading front_label.jpg...
    ✓ Saved to front_label.jpg
  Downloading back_label.jpg...
    ✓ Saved to back_label.jpg

...

Summary:
  Success: 150
  Failed:  20
  Skipped: 24
  Total:   194
```

**Notes:**
- Not all TTB IDs have label images available online
- Some older TTB IDs may not have images in the public registry
- The script uses session-based authentication to access TTB images
- SSL certificate verification is disabled due to TTB certificate issues

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

### validate_ttb_urls.py

Validates all TTB IDs in the CSV file by checking if their generated URLs resolve correctly. This script follows the same URL generation logic used in `index.md`:
- TTB IDs with prefix < 9 (00-08, representing 2000-2008) use the old `publicViewImage.do` format
- TTB IDs with prefix >= 9 (09+, representing 2009 onward, plus 1980s-1990s) use the new `viewColaDetails.do` format

**Usage:**
```bash
# Dry run - check which TTB IDs would be removed (default)
python3 .github/scripts/validate_ttb_urls.py

# Actually remove invalid TTB IDs
python3 .github/scripts/validate_ttb_urls.py --apply

# Adjust delay between requests
python3 .github/scripts/validate_ttb_urls.py --delay 0.5
```

**Options:**
- `--apply`: Actually remove invalid TTB IDs (default is dry-run mode)
- `--delay N`: Delay between requests in seconds (default: 0.3)
- `--csv PATH`: Specify CSV file path (default: _data/whiskeyindex.csv)

**Features:**
- Validates TTB IDs by making HTTP GET requests to generated URLs and checking response content
- **Important:** Checks response body for "Unable to process request" error (TTB returns 200 even for invalid IDs)
- Caches validation results to avoid redundant checks for duplicate TTB IDs
- Provides detailed progress output and summary statistics
- Dry-run mode by default to preview changes before applying
- Automatically removes invalid TTB IDs from the CSV when using `--apply`

**Example Output:**
```
Validating 354 TTB ID entries (173 unique IDs) from _data/whiskeyindex.csv...
✓ [1/354] Angel's Envy Cask Strength - 2025 (TTB: 23132001000515)
❌ [50/354] Example Product - Batch (TTB: 12345678901234)
   URL: https://ttbonline.gov/...
   Error: TTB Error: Unable to process request
...
VALIDATION SUMMARY
Total TTB ID entries: 354
Unique TTB IDs validated: 173
Valid TTB IDs: 354
Invalid TTB IDs: 0
```

**Note:** The script performs content validation, not just HTTP status checks. The TTB website returns HTTP 200 even for invalid IDs but includes an error message "Unable to process request" in the response body.

### validate_urls.py

Validates all product URLs in the CSV file by checking if they return 200 status codes. Uses caching to avoid redundant checks for duplicate URLs.

**Usage:**
```bash
python3 .github/scripts/validate_urls.py
```

**Features:**
- Validates URLs by making HTTP HEAD requests
- Caches validation results for duplicate URLs (performance optimization)
- Treats Angel's Envy 403 errors as valid (bot protection)
- Shows detailed progress with checkmarks for valid URLs
- Provides summary statistics

**Example Output:**
```
Validating 400 URL entries (150 unique URLs) from _data/whiskeyindex.csv...
✓ [1/400] Whiskey Name - Batch
...
VALIDATION SUMMARY
Total URL entries: 400
Unique URLs validated: 150
Valid URLs: 400
Invalid URLs: 0
```

### query_ttb.py

Queries the TTB (Tobacco and Trade Bureau) COLA Public Registry to find TTB approval IDs for whiskey entries that don't have them. This script uses HTTP POST requests to search the TTB website.

**Requirements:**
```bash
pip install requests beautifulsoup4
```

**Usage:**
```bash
# Test mode - search only first 10 entries
python3 .github/scripts/query_ttb.py --test --verbose

# Search with limit
python3 .github/scripts/query_ttb.py --limit 50 --verbose

# Search all entries without TTB IDs
python3 .github/scripts/query_ttb.py --verbose

# Save results to file
python3 .github/scripts/query_ttb.py --test --output results.json
```

**Options:**
- `--test`: Process only first 10 entries (useful for testing)
- `--limit N`: Process only first N entries
- `--verbose`, `-v`: Show detailed search information
- `--output FILE`: Save results to JSON file
- `--csv PATH`: Specify CSV file path (default: _data/whiskeyindex.csv)

**Important Notes:**
- The script uses HTTP POST requests to search the TTB website (no browser automation required)
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

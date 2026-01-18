# TTB COLA ID Scripts

This directory contains utilities for finding and managing TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA approval IDs for whiskey entries.

## Overview

TTB COLA IDs are unique 14-digit identifiers assigned to label approvals by the TTB. These scripts help:
1. Search the TTB COLA Public Registry
2. Match search results to whiskey entries
3. Update the CSV database with verified IDs
4. Validate data accuracy

## Current Status

As of this commit:
- **Total entries**: 390
- **With TTB ID**: 188 (48.2%)
- **Remaining**: 202 (51.8%)

Products with 100% coverage include Booker's, Jack Daniel's, Four Roses LE, Thomas H. Handy, Sazerac 18, and several Knob Creek variants.

## Available Tools

### Search & Automation

**automated_ttb_search.py** - Main TTB registry search automation
- Searches TTB COLA registry programmatically
- Handles date range splitting (TTB 15-year limit)
- Extracts TTB IDs from HTML results
- Primary tool for finding new IDs

**alternate_search.py** - Alternate search strategies
- Tests different product name variations
- Removes descriptive words (Barrel Proof, Birthday, etc.)
- Tries brand-only searches
- Useful when standard searches fail

**search_birthday_bourbon.py** - Old Forester Birthday Bourbon specific search
- Specialized search for Birthday Bourbon releases
- Handles unique naming patterns
- Example of product-specific approach

**universal_ttb_matcher.py** - General-purpose matching logic
- Matches TTB approvals to CSV entries by year
- Handles perfect and imperfect year alignments
- Core matching algorithm used by other scripts

### Management & Validation

**manage_ttb_ids.py** - CSV management utility
- Check coverage status with `summary` command
- Update individual entries
- Generate search lists
- Validate data integrity

**verify_ttb_accuracy.py** - Data quality validation
- Detects proof/age variations using same TTB ID
- Ensures TTB regulations compliance (different proofs need different IDs)
- Reports potential data issues

## Quick Start

### Check Current Status

```bash
python3 scripts/manage_ttb_ids.py summary
```

### Search for TTB IDs (Automated)

```bash
# Search for a specific product
python3 scripts/automated_ttb_search.py "Product Name" start_year end_year

# Example: Search Larceny releases
python3 scripts/automated_ttb_search.py "Larceny" 2020 2025
```

### Try Alternate Search Names

```bash
python3 scripts/alternate_search.py "Product Name" year
```

### Update Single Entry

```bash
python3 scripts/manage_ttb_ids.py update "Product Name" "TTB_ID" "Batch" Year
```

Example:
```bash
python3 scripts/manage_ttb_ids.py update "Booker's" "12345678901234" "2025-04" 2025
```

### Validate Data

```bash
python3 scripts/verify_ttb_accuracy.py
```

## Documentation

- **FINDING_TTB_IDS.md** - Complete step-by-step guide for finding TTB IDs manually
- **TTB_ACCURACY_NOTES.md** - TTB regulations and data accuracy requirements

## TTB COLA Registry

Public search: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do

Search tips:
- Use brand name without descriptive words (e.g., "Larceny" not "Larceny Barrel Proof")
- TTB limits searches to 15-year date ranges
- Match by proof and year to identify specific batches
- Verify batch details on approval documents

## Data Quality Requirements

Always verify TTB IDs match:
- ✓ Exact product name
- ✓ Exact proof (within 0.1-0.2 degrees)
- ✓ Correct release year
- ✓ Matching batch identifier (if applicable)
- ✓ Correct age statement (if applicable)

**Important**: Different proofs or ages require different TTB COLA approvals per 27 CFR Part 5 regulations.

## Notes

- TTB IDs are 14-digit numbers (e.g., `22089001000941`)
- Each unique proof/age combination requires its own approval
- Some products share approvals across batches if proof/age are identical
- Older releases (pre-2012) may not be in online database
- Firewall must allow access to ttbonline.gov for automated searches

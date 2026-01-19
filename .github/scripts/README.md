# Scripts Directory

This directory contains utility scripts for the Whiskey Proofs database.

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

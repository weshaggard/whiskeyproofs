# Find New Bourbon and Rye Releases

Research new bourbon and rye whiskey releases announced in the past week and suggest additions to the whiskey index database.

## Research Tasks

1. Search for new batch announcements and limited releases from major distilleries, including:
   - Buffalo Trace Antique Collection (George T. Stagg, William Larue Weller, Sazerac 18, Thomas H. Handy, Eagle Rare 17)
   - Booker's Bourbon quarterly batches
   - Four Roses Limited Editions and Single Barrel releases
   - Elijah Craig Barrel Proof batches
   - Wild Turkey Master's Keep and Russell's Reserve releases
   - Old Forester Birthday Bourbon and 1920 Prohibition Style batches
   - Woodford Reserve Master's Collection releases
   - Parker's Heritage Collection releases
   - Angel's Envy Cask Strength and Finished releases
   - Jefferson's Ocean and other special releases
   - Any other notable limited or allocated bourbon/rye releases

2. For each new release found:
   - Confirm the batch name/number and release year
   - Find the proof (alcohol by volume × 2)
   - Note the age statement if available
   - Find the distillery
   - Classify the type (Bourbon, Rye, etc.)
   - Look for a URL (official distillery page preferred, then breakingbourbon.com)
   - Search for a TTB COLA ID at https://www.ttbonline.gov/colasonline/

3. Compare findings against the existing `_data/whiskeyindex.csv` to identify:
   - Truly new entries not yet in the database
   - Entries that may need proof or batch updates

## Output Requirements

For each new release to add, propose a CSV row following ALL rules in `.github/copilot-instructions.md`:

- **Name**: Official product name (e.g., "George T. Stagg")
- **Batch**: Official batch identifier (e.g., "2025", "2025-04", "Batch 15")
- **Age**: Age statement in years (leave blank if NAS)
- **Proof**: Numeric proof value — use whole numbers for integer proofs (e.g., "100", "128") and include a decimal only when necessary (e.g., "128.2"; never "128.20")
- **ReleaseYear**: 4-digit year (e.g., "2025")
- **Distillery**: Distillery name (e.g., "Buffalo Trace Distillery")
- **Type**: Whiskey type (e.g., "Bourbon", "Rye")
- **URL**: Best available URL per priority guidelines
- **TTBID**: TTB COLA ID if found

## Acceptance Criteria

Before proposing any CSV changes:
1. Run `python3 .github/scripts/validate_whiskey_data.py` to confirm sort order and data quality
2. Ensure no duplicate entries (same Name + Batch + ReleaseYear already in CSV)
3. Follow all sorting rules: Name ascending, then Batch descending within each product

If valid new entries are found, create a pull request with the additions. If no new entries are found, close this issue with a comment summarizing what was checked.

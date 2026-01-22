# Copilot Instructions for Whiskey Proofs Repository

## CSV File Sorting Rules

When editing the `_data/whiskeyindex.csv` file, always maintain the following sort order:

1. **Primary Sort**: Name (ascending/alphabetical)
2. **Secondary Sort**: Batch (descending - newest/highest first within each product)

### Example Sorting
For products with the same Name:
- Sort alphabetically by product name first (A-Z)
- Within each product, sort batches in descending order (newest/latest batch first)

```
Booker's,2025-04,...
Booker's,2025-03,...
Booker's,2025-02,...
Booker's,2025-01,...
Booker's,2024-04,...
```

### Batch Sorting Details

**Numeric Batch Sorting**: When batch names contain numbers (like "Batch 15", "Batch 2"), they must be sorted **numerically**, not alphabetically:

✅ **Correct** (numeric sort):
```
E.H. Taylor Barrel Proof,Batch 15,...
E.H. Taylor Barrel Proof,Batch 14,...
E.H. Taylor Barrel Proof,Batch 3,...
E.H. Taylor Barrel Proof,Batch 2,...
E.H. Taylor Barrel Proof,Batch 1,...
```

❌ **Incorrect** (alphabetical sort):
```
E.H. Taylor Barrel Proof,Batch 4,...
E.H. Taylor Barrel Proof,Batch 3,...
E.H. Taylor Barrel Proof,Batch 2,...
E.H. Taylor Barrel Proof,Batch 15,...  # Wrong! 15 should come before 2
E.H. Taylor Barrel Proof,Batch 14,...
```

**Implementation Note**: When sorting batches:
1. Extract numeric values from batch strings (e.g., "Batch 15" → 15)
2. Sort by the numeric value in descending order (highest first)
3. For batches without numbers, fall back to alphabetical descending sort

### Implementation
After any edits to the CSV file, always re-sort the data to maintain this order. This ensures:
- Easy navigation by product name
- Latest batches appear first within each product (numerically sorted when applicable)
- Consistent data organization across all edits

## Data Quality Standards

- All required fields must be populated: Name, Batch, Age, Proof, ReleaseYear, Distillery, Type
- Proof values must be numeric
  - **Formatting**: Use whole numbers without decimal points for integer proofs (e.g., "90", "100", "107")
  - Only include decimal portions when necessary (e.g., "94.4", "92.8", "122.6")
  - For proof ranges, apply the same rule to each value (e.g., "110-125", not "110.0-125.0")
- Release years must be valid years (or year ranges for standard releases, e.g., "1999-2025")
- No duplicate entries (same Name, Batch, and ReleaseYear)
- Batch field rules:
  - Use the official batch number/identifier when available (e.g., "2025-04", "Batch 15", "Chapter 9")
  - If there is no clear batch number, use the release year as the batch identifier
  - For products with laser codes but no batch numbers (e.g., Russell's Reserve 13 Year), use numbered batches with laser codes (e.g., "6 - LA/NE (Spring 2025)")
  - **For standard releases** (core products that don't have batch variations): use "standard" as the batch identifier
  - Ensure each batch is distinguishable within a product line
- Age field rules:
  - Use a single year value (e.g., "7", "13")
  - If the age is between years, use up to 2 decimal places (e.g., "7.5", "6.25")
  - If there is no clear age statement, leave the field empty
  - Do not use age ranges (e.g., "6-8")

## Validation Script

A Python validation script (`.github/scripts/validate_whiskey_data.py`) is available to verify data quality and sort order. **Always run this script after making changes to the CSV file.**

### Running Validation

```bash
python3 .github/scripts/validate_whiskey_data.py
```

### What the Script Validates

1. **Required Fields**: Ensures all entries have Name, Batch, Proof, ReleaseYear, Distillery, and Type
2. **Data Type Validation**:
   - Proof values are numeric or valid ranges (e.g., "122.6", "120-137.5")
   - Release years are 4-digit valid years (2000-2030)
3. **Duplicate Detection**: Identifies duplicate entries (same Name, Batch, ReleaseYear)
4. **Sort Order Verification**: Checks that data follows sorting rules (Name ascending, Batch descending)

## Standard Releases

For whiskey products that are **standard releases** (core, non-limited products available year-round without batch variations):

- **Batch field**: Use "standard" as the batch identifier
- **ReleaseYear field**: Use a year range indicating when the product started being made to the present (e.g., "1999-2025", "1984-2025")
- **Examples**:
  - Buffalo Trace Bourbon: `Batch: "standard"`, `ReleaseYear: "1999-2025"`
  - Eagle Rare 10 Year: `Batch: "standard"`, `ReleaseYear: "1975-2025"`
  - Blanton's Original: `Batch: "standard"`, `ReleaseYear: "1984-2025"`

This convention allows the index to track when standard products were first released while distinguishing them from limited or batch-specific releases.

### Batch Pattern Recognition

The validation script intelligently handles various batch naming conventions:

- **Year-batch format**: `2025-04`, `2024-03` (sorted by year desc, then batch number desc)
- **Seasonal batches**: `Fall 2025`, `Spring 2024` (Fall before Spring within same year)
- **Letter-number codes**: `C925`, `B524`, `A123` (sorted by year desc, then C > B > A)
- **Numeric batches**: `Batch 15`, `18`, `17` (sorted numerically descending)
- **Chapter format**: `Chapter 9`, `Chapter 8` (sorted by chapter number desc)
- **Year-letter codes**: `25C`, `24D`, `23A` (sorted by year desc, then letter desc)
- **Hybrid formats**: `6 - LA/NE (Spring 2025)` (sorted by year desc, then number desc)
- **Pure year batches**: `2025`, `2024`, `2016` (sorted numerically descending)
- **Parenthetical variants**: `2017 (Other States)`, `2017 (FL/GA/KY)` (alphabetically within same year)

### CI/CD Integration

The validation script runs automatically on all pull requests that modify `_data/whiskeyindex.csv` via GitHub Actions (`.github/workflows/validate-whiskey-index.yml`). PRs with validation failures cannot be merged.

### Best Practices

1. **Before committing**: Run `python3 .github/scripts/validate_whiskey_data.py` locally
2. **Fix issues immediately**: Address all validation errors before pushing
3. **Review output carefully**: The script provides specific line numbers and error descriptions
4. **Test your changes**: Verify that new entries sort correctly within their product group

## URL Validation

When adding or updating URLs in the `_data/whiskeyindex.csv` file, it's critical to ensure all links are valid and working. A URL validation script is available to check all URLs in the database.

### Running URL Validation

**Always run this script after making any URL changes:**

```bash
python3 .github/scripts/validate_urls.py
```

### What the URL Validation Script Does

1. **Checks all URLs**: Makes HTTP HEAD requests to verify each URL is accessible
2. **Caches results**: Avoids redundant checks for duplicate URLs (performance optimization)
3. **Reports errors**: Identifies broken links with specific error codes (404, 403, etc.)
4. **Provides statistics**: Shows total URLs checked vs unique URLs validated

### Why URL Validation Matters

- **User experience**: Ensures readers can access product information
- **Data quality**: Maintains the integrity of the whiskey database
- **Prevents broken links**: Catches issues before they reach production
- **Saves time**: Caching makes validation fast even with 400+ entries

### URL Priority Guidelines

When selecting URLs for whiskey entries, follow this priority order (highest to lowest):

1. **Batch-specific link from official distillery site** - The most specific and authoritative source
2. **Batch-specific link from breakingbourbon.com** - Detailed reviews when distillery doesn't have batch pages
3. **Product-specific link from official distillery site** - General product information from the source
4. **Distillery-specific link from official distillery** - Homepage or brand page when no product-specific link exists
5. **Leave URL blank** - If nothing appropriate can be found

### Best Practices for URLs

1. **Run validation before committing**: Always validate URLs after changes
2. **Follow priority guidelines**: Use the URL priority order above when selecting links
3. **Verify manually**: Spot-check a few URLs in your browser to confirm they work
4. **Fix errors immediately**: Address all validation failures before pushing changes

## TTB Label Approval Research

When researching TTB (Alcohol and Tobacco Tax and Trade Bureau) IDs for whiskey products:

- **Timing**: Labels are typically approved the year before the release, though sometimes in the release year itself
- **Search Strategy**: When looking for TTB IDs for a specific batch:
  - **First**: Search by distillery (brand name) and date range to get all approvals for that distillery
  - **Then**: Look through the results for the specific product name (fanciful name) you're searching for
  - Check the year before the release year first (labels are most often approved before public release)
  - If not found, check the release year itself
  - Example: For a 2023 batch release, search "Jack Daniel's" in 2022 approvals first, then look for "10 YEARS OLD" in the results

**TTB COLA Registry**: The public TTB COLA (Certificate of Label Approval) registry at ttbonline.gov is the authoritative source for label approvals

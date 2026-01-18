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
- Release years must be valid years
- No duplicate entries (same Name, Batch, and ReleaseYear)
- Batch field rules:
  - Use the official batch number/identifier when available (e.g., "2025-04", "Batch 15", "Chapter 9")
  - If there is no clear batch number, use the release year as the batch identifier
  - For products with laser codes but no batch numbers (e.g., Russell's Reserve 13 Year), use numbered batches with laser codes (e.g., "6 - LA/NE (Spring 2025)")
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

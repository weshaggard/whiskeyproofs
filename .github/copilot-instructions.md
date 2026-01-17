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

### Implementation
After any edits to the CSV file, always re-sort the data to maintain this order. This ensures:
- Easy navigation by product name
- Latest batches appear first within each product
- Consistent data organization across all edits

## Data Quality Standards

- All required fields must be populated: Name, Batch, Age, Proof, ReleaseYear, Distillery, Type
- Proof values must be numeric
- Release years must be valid years
- No duplicate entries (same Name, Batch, and ReleaseYear)
- Use age ranges (e.g., "6-8") for products without specific age statements

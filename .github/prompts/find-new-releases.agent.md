# Weekly Bourbon and Rye Release Discovery Task

Find new **bourbon** and **rye** releases announced since the last run and update `/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv`.

## Scope

- Search official distillery pages, press release pages, and official brand news pages first.
- If no official page exists for a specific new release, use a reputable bourbon news/review source as a fallback.
- Only add releases that are bourbon or rye products.

## Required data quality rules

For each new release, ensure all required fields are complete and valid:

- `Name`
- `Batch`
- `Age` (blank only if unknown)
- `Proof` (numeric or valid numeric range format used by this repository)
- `ReleaseYear`
- `Distillery`
- `Type` (`Bourbon` or `Rye`)
- `TTB_ID` (when available)
- `url` (prefer official product/batch page)

When adding rows:

1. Follow existing conventions in `/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv`.
2. Keep sort order valid (Name ascending, Batch descending with repository sort logic).
3. Avoid duplicates (`Name`, `Batch`, `ReleaseYear`).

## Label (TTB) lookup requirements

For each candidate release:

1. Search existing `labels/` files first for matching TTB IDs or label evidence.
2. If needed, search the public TTB COLA registry.
3. Add `TTB_ID` when confident; leave blank if not verifiable.

## Existing-release update rule

If a newly discovered release matches an existing entry where product attributes are unchanged (same Name, Batch pattern, Age, Proof, Distillery, Type), do **not** add a duplicate row.  
Instead, update the existing `ReleaseYear` value to extend the range (for example `2023-2025` → `2023-2026`).

## Validation

After edits, run:

```bash
python3 .github/scripts/validate_whiskey_data.py
python3 .github/scripts/validate_urls.py
python3 .github/scripts/validate_ttb_urls.py
```

Only keep changes that pass validation.

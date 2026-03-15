# Weekly Bourbon and Rye Release Discovery Task

## Task

Find new **bourbon** and **rye** releases announced since the last run and update `_data/whiskeyindex.csv`.

## Requirements

Scope:

- Search official distillery pages, press release pages, and official brand news pages first.
- If no official page exists for a specific new release, use one of the reputable bourbon news/review sources listed below as a fallback.
- Only add releases that are bourbon or rye products.

Reputable fallback sources (in priority order):

1. [Breaking Bourbon](https://www.breakingbourbon.com) – breaking bourbon news, release announcements, and batch details
2. [Bourbon Culture](https://bourbonculture.com) – release news, batch info, and reviews
3. [The Whiskey Wash](https://thewhiskeywash.com) – industry news and release coverage
4. [Whisky Advocate](https://www.whiskyadvocate.com) – reviews and release announcements
5. [Distiller](https://distiller.com) – product database and release details
6. [Fred Minnick](https://fredminnick.com) – bourbon journalist coverage of new releases

Acceptance criteria:

1. `_data/whiskeyindex.csv` is updated only for bourbon/rye releases discovered from official sources (or the reputable fallback sources listed above when official pages are unavailable).
2. Every added or updated row has valid required fields (`Name`, `Batch`, `Proof`, `ReleaseYear`, `Distillery`, `Type`) and valid optional fields (`Age`, `TTB_ID`, `url`) when available.
3. No duplicate row is introduced for the same `Name`, `Batch`, and `ReleaseYear`.
4. Existing releases with unchanged attributes are updated by extending `ReleaseYear` range instead of adding duplicates.
5. Errors in individual entries are isolated — a single bad entry does not block valid additions. Validation scripts complete successfully on the final set of kept changes.
6. For every **new** brand or product added, research and add all earlier/historical releases of that product as well. The index should be as complete as possible — not just the current release.

## Required data quality rules

For each new release, ensure all required fields are complete and valid:

- `Name`
- `Batch`
- `Age` (leave empty if there is no clear age statement)
- `Proof` (numeric or valid numeric range format used by this repository)
- `ReleaseYear`
- `Distillery`
- `Type` (`Bourbon` or `Rye`)
- `TTB_ID` (when available)
- `url` (prefer official product/batch page)

When adding rows:

1. Follow existing conventions in `_data/whiskeyindex.csv`.
2. Keep sort order valid (Name ascending, Batch descending with repository sort logic).
3. Avoid duplicates (`Name`, `Batch`, `ReleaseYear`).
4. **Name grouping rule**: Use the brand/distillery name as `Name` to group all expressions of that brand together. Use the `Batch` field to differentiate individual expressions within a brand. Only use a more specific `Name` for sub-series that have multiple distinct annual/numbered releases under a shared sub-brand name.
   - ✅ `Chicken Cock` + `Bourbon` / `Rye` / `Small Batch` / `Inked Cask` — all core and limited expressions grouped under the brand name
   - ✅ `Chicken Cock Annual Tin` + `Red Stave` / `Mizunara` / `Chanticleer` — separate Name for the annual tin sub-series because it has multiple distinctly-named yearly releases under that sub-brand
   - ❌ `Chicken Cock Rye`, `Chicken Cock Small Batch` — avoid encoding the expression type in the Name when Batch can serve that purpose

## Label (TTB) lookup requirements

For each candidate release:

1. Search existing `labels/` files first for matching TTB IDs or label evidence.
2. If needed, search the public TTB COLA registry.
3. Add `TTB_ID` when confident; leave blank if not verifiable.

## Existing-release update rule

If a newly discovered release matches an existing entry where product attributes are unchanged (same Name, same recurring batch identifier or `standard` pattern, same Age, Proof, Distillery, and Type), do **not** add a duplicate row.  
Instead, update the existing `ReleaseYear` value to extend the range (for example `2023-2025` → `2023-2026`).

## Retry

- **Network/transient errors** (timeouts, HTTP 5xx): retry the same operation up to 3 times.
- **Logic/data errors** (failed validation, no match found): retry with small search/query adjustments up to 3 times (for example, broaden date range by 30 days, try product name variations, and check fallback bourbon sources).
- **Permanent errors** (invalid path, permissions): stop immediately and report the error.

## Git operations

**Do NOT run any git commands.** Do not `git add`, `git commit`, `git push`, or create any branches.  
Only edit files on disk. The workflow that runs this prompt handles all git and PR operations after the agent finishes.

## Validation

Process each candidate release independently. If one entry fails validation or cannot be completed, skip that entry, record it as an error in the report, and continue processing the remaining entries. Do **not** let a single bad entry block additions of valid entries.

After all entries are processed, run validation on the full set of changes:

```bash
python3 .github/scripts/validate_whiskey_data.py
python3 .github/scripts/validate_urls.py
python3 .github/scripts/validate_ttb_urls.py
```

Only keep changes that pass validation.

## Report

At the end of the run, include:

- One-sentence result summary
- Counts for processed/succeeded/failed/skipped items
- Exact entries added or updated (including release-year range updates)
- Any errors, retries performed, and remaining follow-up work

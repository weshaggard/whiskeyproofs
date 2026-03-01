# Find New Bourbon and Rye Releases — Agent Instructions

## Task

Research new bourbon and rye whiskey releases announced in the past week and update `_data/whiskeyindex.csv` with any new or updated entries.

## Requirements

Before starting, confirm the following acceptance criteria:

1. ✅ All newly announced bourbon and rye batches/releases from the past week are identified
2. ✅ New entries added to the CSV with all required fields: Name, Batch, Age, Proof, ReleaseYear, Distillery, Type (TTB_ID and url are optional but should be populated when available)
3. ✅ Existing standard release year ranges updated if a product was re-released this year
4. ✅ CSV passes validation: `python3 .github/scripts/validate_whiskey_data.py`
5. ✅ A pull request is created with all changes

---

## Step 1: Research New Releases

Search the following official distillery websites and news sources for new bourbon and rye release announcements. Focus on releases from **the past week**.

### Priority Distilleries

| Distillery | Products to track | Website |
|---|---|---|
| Buffalo Trace | Buffalo Trace, Eagle Rare, Blanton's, E.H. Taylor, Stagg, George T. Stagg, W.L. Weller, Van Winkle | https://www.buffalotracedistillery.com/news |
| Heaven Hill | Elijah Craig Barrel Proof, Evan Williams Single Barrel, Larceny Barrel Proof, Parker's Heritage | https://heavenhill.com/blog |
| Wild Turkey | Russell's Reserve Single Barrel, Wild Turkey Rare Breed, Wild Turkey Longbranch | https://wildturkeybourbon.com |
| Four Roses | Four Roses Limited Edition Small Batch, Four Roses Single Barrel Limited | https://fourrosesbourbon.com/news |
| Brown-Forman | Woodford Reserve Batch Proof, Old Forester Birthday Bourbon, Jack Daniel's Single Barrel | https://woodfordreserve.com, https://oldforester.com |
| Jim Beam | Booker's Bourbon (quarterly), Knob Creek Limited, Little Book | https://www.bookerswhiskey.com/releases |
| Maker's Mark | Wood Finishing Series, Cask Strength | https://www.makersmark.com/releases |
| Michter's | Michter's US 1 Toasted Barrel, Michter's 10, Michter's 20, Michter's 25 | https://michters.com/limited-releases |
| Wilderness Trail | Wilderness Trail Single Barrel, Wilderness Trail Bottled in Bond | https://wildernesstraildistillery.com |
| New Riff | New Riff Bottled in Bond, New Riff Single Barrel | https://newriffdistilling.com |
| WhistlePig | WhistlePig Boss Hog, WhistlePig FarmStock | https://www.whistlepigwhiskey.com/new-releases |
| Barrell Craft Spirits | Barrell Bourbon (batch numbered), Barrell Rye, Barrell Dovetail | https://www.barrellcraftspirits.com |
| Rabbit Hole | Rabbit Hole Heigold, Rabbit Hole Boxergrail | https://rabbitholedistillery.com |
| Angel's Envy | Angel's Envy Cask Strength, Angel's Envy Port Finish | https://www.angelsenvy.com |
| Breckenridge | Breckenridge Bourbon, Breckenridge Port Cask | https://breckenridgedistillery.com |

Also check:
- **BreakingBourbon.com** (https://www.breakingbourbon.com) — aggregates new release news
- **BourbonBlog.com** (https://www.bourbonblog.com) — news and reviews
- **Distillery press release feeds** — search for "[distillery name] press release [current year]"

---

## Step 2: Check Existing CSV Data

Before adding any entries, load and review `_data/whiskeyindex.csv` to:

1. **Check if the product already exists** — search for entries matching the Name and Batch
2. **Determine whether to add or update**:
   - **New product / new batch** → Add a new row
   - **Same product, new release year** (standard or annual releases) → Update the `ReleaseYear` field to extend the year range (e.g., `1999-2024` → `1999-2025`)
   - **Exact duplicate** (same Name, Batch, ReleaseYear) → Skip, already present

---

## Step 3: Find the TTB COLA ID

For each new entry, try to find its TTB COLA label approval ID:

### 3a. Check the labels directory

Look in `labels/` directory — each subdirectory is a TTB ID. If a matching label exists, use that TTB ID.

### 3b. Search the public TTB registry

If not found locally, search the public TTB COLA registry:
- URL: https://ttbonline.gov/colasonline/publicSearchColasBasic.do
- Search by **brand/product name** and **date range** (check the year before release first)
- Filter: **Origin code 22** (Kentucky) for KY distilleries; leave blank for others
- Filter: **Product class/type 100–150** (whiskey)
- The TTB ID is the 14-digit number in the search results

### 3c. Timing note

Labels are typically approved **the year before release** (e.g., a 2025 batch may have a 2024 TTB approval date). Search the prior year first.

### 3d. If not found

Leave `TTB_ID` blank — do not guess or fabricate TTB IDs.

---

## Step 4: Find the Product URL

Use the following priority order when selecting a URL:

1. **Batch-specific page on official distillery site** (e.g., `https://www.bookerswhiskey.com/releases/bookers-2025-01/`)
2. **Batch-specific review on breakingbourbon.com**
3. **Product page on official distillery site**
4. **Distillery homepage or brand page**
5. **Leave blank** if nothing appropriate exists

---

## Step 5: Build the CSV Row

Use this column format (matching the existing CSV header):

```
Name,Batch,Age,Proof,ReleaseYear,Distillery,Type,TTB_ID,url
```

### Field rules

| Field | Rule |
|---|---|
| **Name** | Official product name as commonly known (e.g., `Booker's Bourbon`, `E.H. Taylor Barrel Proof`) |
| **Batch** | Official batch ID (e.g., `2025-01`, `Batch 18`, `Chapter 9`); use `standard` for core non-limited products |
| **Age** | Single year (e.g., `7`, `12`); blank if no age statement; no ranges |
| **Proof** | Whole number if integer (e.g., `125`, `107`); decimal only if necessary (e.g., `94.4`); range for variable-proof batches (e.g., `120-137.5`) |
| **ReleaseYear** | Single 4-digit year for limited releases; year range for standard/annual releases (e.g., `1999-2025`) |
| **Distillery** | Official distillery name (e.g., `Buffalo Trace`, `Heaven Hill`, `Jim Beam`) |
| **Type** | `Bourbon` or `Rye` (capitalize) |
| **TTB_ID** | 14-digit TTB COLA ID; leave blank if not found |
| **url** | Product URL per priority rules above; leave blank if nothing appropriate |

---

## Step 6: Maintain Sort Order

The CSV **must** be sorted:
- **Primary**: `Name` ascending (A → Z)
- **Secondary**: `Batch` descending (newest/highest first within each product)

Use the sort key logic from `.github/scripts/validate_whiskey_data.py` (the `batch_sort_key` function) to determine correct batch ordering. Key rules:
- Year-batch format (`2025-04`, `2025-03`): sort by year desc, then batch number desc
- Batch N format (`Batch 15`, `Batch 3`): sort numerically descending
- Chapter N, Pact N: sort by number descending
- General named batches: alphabetically descending (Z → A), then by year descending

---

## Step 7: Validate

After editing the CSV, run the validation script:

```bash
python3 .github/scripts/validate_whiskey_data.py
```

Fix any errors reported before proceeding.

---

## Step 8: Create a Pull Request

Create a PR with:
- **Branch name**: `automated/new-releases-YYYY-MM-DD` (use today's date)
- **Title**: `New Releases: [brief summary of what was added]`
- **Body**: List each new entry or updated entry, with source links

---

## Retry Strategy

| Failure | Strategy | Max Retries |
|---|---|---|
| Distillery website unavailable | Try alternate news source (BreakingBourbon) | 2 |
| TTB search returns no results | Broaden date range by ±1 year, try alternate product name | 3 |
| Validation errors | Fix the specific error and re-run validation | 3 |
| Duplicate entry detected | Skip — entry already exists | 0 |

---

## Report

When done, produce a summary including:
- Number of new entries added
- Number of existing entries updated (year range extended)
- Number of distilleries checked
- Any entries where TTB ID or URL could not be found
- Link to the created PR

Write a report to `.agent-session/files/task-report.md` following this structure:

```markdown
# Task Report

## Task
{one-sentence restatement of the original request}

## Result
{✅ Success | ⚠️ Partial | ❌ Failed}

## Summary
- Items processed: N
- Succeeded: N
- Failed: N
- Skipped: N

## Completed
{list of items/steps that succeeded, with enough detail to avoid re-doing them}

## Errors
{for each failure: what was attempted, the exact error message or output, and which retry attempts were made}

## Remaining Work
{explicit list of items/steps that were NOT completed}

## State
{any intermediate data or working state the next session should know about}
```

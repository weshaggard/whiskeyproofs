# Fix Broken URLs in Whiskey Index

## Task

Find valid replacement URLs for broken links in `_data/whiskeyindex.csv`. Only remove a URL if no valid replacement can be found.

## Steps

### 1. Identify broken URLs

Run the URL validation script to find all entries with broken URLs:

```bash
python3 .github/scripts/validate_urls.py
```

If there are no broken URLs, stop — there is nothing to do.

### 2. For each broken URL entry, search for a replacement

For every entry reported as broken, search for a valid replacement URL using this priority order:

1. **Batch-specific page on the official distillery/brand site** — the most authoritative source
2. **Batch-specific page on [Breaking Bourbon](https://www.breakingbourbon.com)** — detailed batch reviews and announcements
3. **Product-specific page on the official distillery/brand site** — general product information
4. **Distillery homepage or brand page** — when no product-specific page exists
5. **Other reputable sources** (in order): [Bourbon Culture](https://bourbonculture.com), [The Whiskey Wash](https://thewhiskeywash.com), [Whisky Advocate](https://www.whiskyadvocate.com)
6. **Remove the URL** — only if no valid alternative can be found after exhausting the above sources

Before accepting any candidate URL, verify it is reachable (HTTP 200 or bot-protection 403). Do not replace a broken URL with another broken URL.

### 3. Update the CSV

For each broken entry:
- If a valid replacement URL was found: update the `url` field in `_data/whiskeyindex.csv` with the new URL
- If no valid replacement was found: clear the `url` field (set it to empty string)

### 4. Verify

Run the URL validation script again to confirm all remaining URLs are valid:

```bash
python3 .github/scripts/validate_urls.py
```

All URLs must pass. If any still fail, repeat step 2–3 for those entries or clear them.

## Data quality rules

- Never replace a URL with one that returns an error (4xx, 5xx, timeout, DNS failure)
- Prefer the most specific URL (batch-level > product-level > brand-level)
- Do not add a URL if none of the sources above has a valid page for this entry

## Retry

- **Network/transient errors** (timeouts, HTTP 5xx): retry the same URL up to 3 times before moving on
- **No replacement found**: try alternate search queries (product name variations, distillery name) up to 3 times before giving up and clearing the URL

## Report

At the end of the run, report:

- Total broken URLs found
- How many were replaced with valid URLs (and what the new URLs are)
- How many were cleared because no replacement was found

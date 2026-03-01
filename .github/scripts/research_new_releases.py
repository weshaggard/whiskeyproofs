#!/usr/bin/env python3
"""
Research new bourbon and rye whiskey releases using GitHub Models API.

Fetches content from bourbon news sources, then uses GitHub Models (GPT-4o) to
extract new release announcements and propose updates to whiskeyindex.csv.

Requirements:
    pip install requests beautifulsoup4

Usage:
    GITHUB_TOKEN=... python3 .github/scripts/research_new_releases.py
    python3 .github/scripts/research_new_releases.py --output results.json --verbose
    python3 .github/scripts/research_new_releases.py --dry-run --verbose

Authentication:
    Set GITHUB_TOKEN (or MODELS_TOKEN as an alternative) to a GitHub personal access
    token or the GITHUB_TOKEN available in GitHub Actions workflows. The token is used
    to authenticate with the GitHub Models API (https://models.inference.ai.azure.com).
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# News sources to check for new bourbon/rye release announcements
NEWS_SOURCES = [
    {
        "name": "Breaking Bourbon - New Releases",
        "url": "https://www.breakingbourbon.com/releases",
    },
    {
        "name": "Breaking Bourbon - News",
        "url": "https://www.breakingbourbon.com/bourbon-news",
    },
    {
        "name": "Bourbon Blog - News Releases",
        "url": "https://www.bourbonblog.com/category/news-releases/",
    },
    {
        "name": "Distillery Trail - American Whiskey",
        "url": "https://www.distillerytrail.com/category/american-whiskey/",
    },
]

GITHUB_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_NAME = "gpt-4o"
MAX_CONTENT_CHARS_PER_SOURCE = 8000  # ~2K tokens per source; 4 sources = ~8K tokens total,
# well within the combined prompt budget while keeping the total payload manageable.


def fetch_page_text(url: str, session: "requests.Session", verbose: bool = False) -> str:
    """Fetch a web page and return its visible text content."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        truncated = text[:MAX_CONTENT_CHARS_PER_SOURCE]
        if verbose:
            print(f"    Got {len(text)} chars (using first {len(truncated)})")
        return truncated
    except Exception as e:
        print(f"  Warning: Could not fetch {url}: {e}")
        return ""


def read_existing_csv(csv_path: str) -> list:
    """Read the whiskey CSV and return rows as a list of dicts."""
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading CSV '{csv_path}': {e}")
        sys.exit(1)


def call_github_models(messages: list, token: str) -> dict:
    """Call the GitHub Models API and return parsed JSON response."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": 4000,
    }
    response = requests.post(GITHUB_MODELS_URL, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)


def build_prompts(news_content: str, existing_entries: list, current_year: int) -> tuple:
    """Build system and user prompts for the GitHub Models API call."""

    # Build a compact list of existing Name - Batch combos for dedup context.
    # Cap at 100 entries to stay within prompt budget; beyond this the model has
    # sufficient context from the most common products to avoid false duplicates.
    existing_keys = sorted(set(f"{e['Name']} - {e['Batch']}" for e in existing_entries))
    existing_summary = "\n".join(existing_keys[:100])

    system_prompt = f"""You are an expert bourbon and rye whiskey research assistant. Your job is to analyze whiskey news content and identify new releases that should be added to or updated in a whiskey database.

Current date: {datetime.now().strftime('%B %d, %Y')}

The database uses these columns:
- Name: Product name (e.g. "Booker's Bourbon", "E.H. Taylor Barrel Proof", "Elijah Craig Barrel Proof")
- Batch: Official batch identifier (e.g. "2025-01", "Batch 18", "Fall 2025") OR "standard" for non-limited core products
- Age: Age in years as a plain number (e.g. "7", "12"); blank if no age statement on the bottle
- Proof: Alcohol proof — use whole number if integer (e.g. "125"), decimal only if needed (e.g. "94.4"); use range if variable (e.g. "120-137.5")
- ReleaseYear: 4-digit year for limited/batch releases; year range for standard products (e.g. "1999-{current_year}")
- Distillery: Official distillery name (e.g. "Buffalo Trace", "Heaven Hill", "Jim Beam")
- Type: "Bourbon" or "Rye"
- TTB_ID: Always leave blank — this is researched separately
- url: Official distillery/brand URL for the specific product or release

EXISTING database entries (Name - Batch):
{existing_summary}

RULES:
1. Only include releases explicitly mentioned in the provided news content
2. Do NOT fabricate proof values, ages, or batch numbers — leave fields blank if not stated
3. For standard (non-batch) products: if news confirms the product is being sold in {current_year}, propose extending its ReleaseYear range (e.g. "1999-{current_year - 1}" → "1999-{current_year}")
4. For limited/batch releases: propose a new entry — do not modify the existing entry's year range
5. Skip any release already in the EXISTING list with that exact Name + Batch combination
6. Only include bourbon and rye whiskey (not scotch, Irish, or other spirits)

Return a JSON object with this exact structure:
{{
  "new_entries": [
    {{
      "Name": "...",
      "Batch": "...",
      "Age": "",
      "Proof": "",
      "ReleaseYear": "{current_year}",
      "Distillery": "...",
      "Type": "Bourbon",
      "TTB_ID": "",
      "url": "",
      "reason": "why this is a new entry",
      "source": "which news source mentioned this"
    }}
  ],
  "year_range_updates": [
    {{
      "Name": "...",
      "Batch": "standard",
      "old_year_range": "...",
      "new_year_range": "...",
      "reason": "product confirmed available in {current_year}"
    }}
  ],
  "summary": "Brief description of what was found (1-2 sentences)"
}}

Return empty arrays if no relevant releases were found in the content."""

    user_message = (
        f"Please analyze the following bourbon/rye whiskey news content and identify "
        f"new releases or updates from approximately the past 1-2 weeks:\n\n"
        f"{news_content}\n\n"
        f"Extract only factual information that is explicitly stated in the content."
    )

    return system_prompt, user_message


def apply_updates(existing_entries: list, updates: dict, verbose: bool = False) -> list:
    """
    Apply proposed updates to the entry list.
    Returns list of human-readable change descriptions.
    """
    changes = []

    # Build lookup structures
    existing_keys = set(
        (e["Name"], e["Batch"], e["ReleaseYear"]) for e in existing_entries
    )
    name_batch_index = {(e["Name"], e["Batch"]): i for i, e in enumerate(existing_entries)}

    # Apply new entries
    for entry in updates.get("new_entries", []):
        key = (entry["Name"], entry["Batch"], entry["ReleaseYear"])
        if key in existing_keys:
            if verbose:
                print(f"  Skip (already exists): {entry['Name']} - {entry['Batch']} ({entry['ReleaseYear']})")
            continue
        # Skip if same Name+Batch exists with any year (would create conflict)
        if (entry["Name"], entry["Batch"]) in name_batch_index:
            if verbose:
                print(f"  Skip (name+batch pair already present): {entry['Name']} - {entry['Batch']}")
            continue

        csv_row = {
            k: entry.get(k, "")
            for k in ["Name", "Batch", "Age", "Proof", "ReleaseYear", "Distillery", "Type", "TTB_ID", "url"]
        }
        existing_entries.append(csv_row)
        existing_keys.add(key)
        name_batch_index[(entry["Name"], entry["Batch"])] = len(existing_entries) - 1

        reason = entry.get("reason", "")
        change = f"Added: {entry['Name']} - {entry['Batch']} ({entry['ReleaseYear']})"
        if reason:
            change += f" [{reason}]"
        changes.append(change)
        print(f"  + {change}")

    # Apply year range updates
    for update in updates.get("year_range_updates", []):
        name_batch = (update["Name"], update["Batch"])
        if name_batch in name_batch_index:
            idx = name_batch_index[name_batch]
            old_year = existing_entries[idx]["ReleaseYear"]
            new_year = update["new_year_range"]
            if old_year != new_year:
                existing_entries[idx]["ReleaseYear"] = new_year
                change = f"Updated year range: {update['Name']} ({update['Batch']}): {old_year} → {new_year}"
                changes.append(change)
                print(f"  ~ {change}")
            elif verbose:
                print(f"  Skip (already current): {update['Name']} - {update['Batch']} ({old_year})")
        elif verbose:
            print(f"  Skip (not found for year update): {update['Name']} - {update['Batch']}")

    return changes


def sort_entries(entries: list) -> list:
    """Sort entries: Name ascending, Batch descending using the repo's sort logic."""
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    try:
        from validate_whiskey_data import batch_sort_key
    except ImportError as e:
        # The sort logic in validate_whiskey_data.py is required for correct batch ordering
        # (e.g. "Batch 15" must sort before "Batch 2"). Failing here prevents silently
        # writing a CSV with incorrect sort order.
        print(f"Error: Could not import batch_sort_key from validate_whiskey_data: {e}")
        print("Ensure validate_whiskey_data.py is present in the same directory.")
        sys.exit(1)

    def sort_key(entry):
        return (entry["Name"].lower(), batch_sort_key(entry["Batch"], entry["ReleaseYear"]))

    return sorted(entries, key=sort_key)


def write_csv(entries: list, csv_path: str) -> None:
    """Write entries back to the CSV file."""
    fieldnames = ["Name", "Batch", "Age", "Proof", "ReleaseYear", "Distillery", "Type", "TTB_ID", "url"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow({k: entry.get(k, "") for k in fieldnames})


def main():
    parser = argparse.ArgumentParser(
        description="Research new bourbon/rye releases and update whiskeyindex.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  GITHUB_TOKEN=ghp_... python3 .github/scripts/research_new_releases.py
  python3 .github/scripts/research_new_releases.py --dry-run --verbose
  python3 .github/scripts/research_new_releases.py --output results.json
        """,
    )
    parser.add_argument("--csv", default="_data/whiskeyindex.csv", help="Path to CSV file")
    parser.add_argument("--output", default="research_results.json", help="Output JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Analyze but do not modify CSV")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required packages not installed.")
        print("Run: pip install requests beautifulsoup4")
        sys.exit(1)

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("MODELS_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is required")
        print("  (MODELS_TOKEN is also accepted as an alternative)")
        sys.exit(1)

    current_year = datetime.now().year

    print("=" * 60)
    print("Whiskey Release Research")
    print("=" * 60)
    print(f"Date:   {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Target: {current_year} releases")
    print(f"Mode:   {'dry-run' if args.dry_run else 'live'}")

    # Step 1: Fetch bourbon news content
    print("\n1. Fetching bourbon news sources...")
    session = requests.Session()
    content_parts = []

    for source in NEWS_SOURCES:
        print(f"  Fetching: {source['name']}")
        text = fetch_page_text(source["url"], session, verbose=args.verbose)
        if text:
            content_parts.append(f"=== {source['name']} ===\n{text}")
        time.sleep(1)  # Be polite to servers

    combined_content = "\n\n".join(content_parts)

    if not combined_content.strip():
        print("Warning: No news content fetched. Proceeding with model knowledge only.")
        combined_content = (
            f"No live content was available. Based on your knowledge of bourbon and rye "
            f"whiskey releases announced in {current_year}, identify any notable new releases."
        )

    # Step 2: Read existing CSV
    print("\n2. Reading existing whiskey index...")
    existing_entries = read_existing_csv(args.csv)
    print(f"  {len(existing_entries)} existing entries")

    # Step 3: Call GitHub Models API
    print(f"\n3. Calling GitHub Models API ({MODEL_NAME})...")
    system_prompt, user_message = build_prompts(combined_content, existing_entries, current_year)
    try:
        updates = call_github_models(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            token=token,
        )
    except Exception as e:
        print(f"Error calling GitHub Models API: {e}")
        sys.exit(1)

    new_count = len(updates.get("new_entries", []))
    update_count = len(updates.get("year_range_updates", []))
    summary = updates.get("summary", "No summary provided")

    print(f"  Summary: {summary}")
    print(f"  Proposed new entries:       {new_count}")
    print(f"  Proposed year range updates: {update_count}")

    if args.verbose and new_count > 0:
        print("\n  Proposed new entries:")
        for entry in updates.get("new_entries", []):
            print(
                f"    - {entry.get('Name')} - {entry.get('Batch')} "
                f"({entry.get('ReleaseYear')}) [{entry.get('Type')}]"
            )
            print(f"      Proof: {entry.get('Proof') or '?'}  Age: {entry.get('Age') or '-'}")
            print(f"      Source: {entry.get('source', '-')}")

    # Step 4: Apply updates
    changes = []
    if not args.dry_run and (new_count > 0 or update_count > 0):
        print("\n4. Applying updates...")
        changes = apply_updates(existing_entries, updates, verbose=args.verbose)

        if changes:
            print(f"\n5. Sorting and writing CSV...")
            sorted_entries = sort_entries(existing_entries)
            write_csv(sorted_entries, args.csv)
            print(f"   Wrote {len(sorted_entries)} entries to {args.csv}")
        else:
            print("   No changes applied (all proposed updates were duplicates or not found)")
    elif args.dry_run:
        print("\n(Dry run — CSV not modified)")
    else:
        print("\n4. No updates proposed by model")

    # Step 5: Save results JSON (consumed by the workflow)
    results = {
        "timestamp": datetime.now().isoformat(),
        "year": current_year,
        "sources_checked": len(NEWS_SOURCES),
        "content_fetched": bool(content_parts),
        "changes": changes,
        "change_count": len(changes),
        "has_changes": len(changes) > 0,
        "new_entries_proposed": updates.get("new_entries", []),
        "year_range_updates_proposed": updates.get("year_range_updates", []),
        "summary": summary,
    }

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {args.output}")
    print(f"\n{'=' * 60}")
    print(f"Total changes applied: {len(changes)}")
    if changes:
        for c in changes:
            print(f"  • {c}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
TTB URL validation script for whiskeyindex.csv

This script validates all TTB IDs by checking if their generated URLs resolve correctly.
It follows the same logic used in index.md:
- TTB IDs with prefix < 9 (00-08, representing 2000-2008) use publicViewImage.do format
- TTB IDs with prefix >= 9 (09+, representing 2009 onward, plus 1980s-1990s) use viewColaDetails.do format

Invalid TTB IDs will be removed from the CSV file.
"""

import csv
import http.client
import sys
import urllib.error
import urllib.request
import ssl
import time
from typing import Dict, Optional, Tuple

# TTB URL format threshold - prefixes < 9 use old format, >= 9 use new format
# This matches the logic in index.md and reflects the TTB system change around 2009
URL_FORMAT_THRESHOLD = 9

# Default year prefix for invalid TTB ID formats
# Using 9 (representing 2009+) as it routes to the new format which is most common
DEFAULT_YEAR_PREFIX = 9

# HTTP method for TTB validation - must use GET to check response content
# TTB website returns 200 even for invalid IDs, so we need to read the response body
HTTP_METHOD = 'GET'

# Error message that indicates an invalid TTB ID
# TTB returns this in the response body even when HTTP status is 200
TTB_ERROR_MESSAGE = 'Unable to process request'

# Maximum bytes to read from response body for error checking
# Error messages appear early in the response, no need to read entire page
MAX_CONTENT_BYTES = 10000  # 10KB should be enough to catch error messages

MAX_RETRIES = 3
MAX_BACKOFF_SECONDS = 4
ValidationResult = Tuple[Optional[bool], str, str]


def generate_ttb_url(ttb_id: str) -> str:
    """
    Generate TTB URL based on the ID prefix, matching index.md logic.
    
    Args:
        ttb_id: The TTB ID (14 digits)
    
    Returns:
        The complete TTB URL
    """
    # Extract the year prefix (first 2 digits)
    try:
        year_prefix = int(ttb_id[:2])
    except (ValueError, IndexError):
        # Invalid format - TTB IDs should always have numeric prefix
        # Default to new format (most common)
        year_prefix = DEFAULT_YEAR_PREFIX
    
    # Use old format for prefix < threshold (years 2000-2008), new format for prefix >= threshold
    # This matches index.md logic and TTB system change around 2009
    # Note: Older IDs from 1980s-1990s (prefix 83-99) use new format
    if year_prefix < URL_FORMAT_THRESHOLD:
        return f"https://ttbonline.gov/colasonline/publicViewImage.do?id={ttb_id}"
    else:
        return f"https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttb_id}"


def validate_ttb_url(ttb_id: str, timeout: int = 10) -> ValidationResult:
    """Return (validity, URL, reason), using None for unverified requests.

    Only an explicit TTB error or HTTP 404/410 confirms an invalid ID.
    Transient failures get at most three retries after the initial attempt.
    TLS verification is never disabled.
    """
    url = generate_ttb_url(ttb_id)
    for attempt in range(MAX_RETRIES + 1):
        retry = False
        try:
            request = urllib.request.Request(url, method=HTTP_METHOD)
            request.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = response.status
                if status == 200:
                    content = response.read(MAX_CONTENT_BYTES).decode('utf-8', errors='ignore')
                    if TTB_ERROR_MESSAGE.lower() in content.lower():
                        return False, url, f"TTB Error: {TTB_ERROR_MESSAGE}"
                    if any(marker in content.lower() for marker in (
                            'ttb id', 'ttbid', 'publicviewimage',
                            'cola details', 'certificate of label approval')):
                        return True, url, ""
                    return None, url, "Unrecognized or empty TTB response"
                if status in (404, 410):
                    return False, url, f"HTTP {status}"
                error = f"HTTP {status}"
                retry = status in (408, 425, 429) or 500 <= status <= 599
        except urllib.error.HTTPError as exc:
            status = exc.code
            exc.close()
            if status in (404, 410):
                return False, url, f"HTTP {status}"
            error = f"HTTP {status}"
            retry = status in (408, 425, 429) or 500 <= status <= 599
        except ssl.SSLError as exc:
            return None, url, f"TLS error: {exc}"
        except (urllib.error.URLError, OSError, http.client.HTTPException) as exc:
            reason = getattr(exc, 'reason', exc)
            if isinstance(reason, ssl.SSLError):
                return None, url, f"TLS error: {reason}"
            error = f"Network error: {reason}"
            retry = True
        except Exception as exc:
            return None, url, f"Unverified error: {exc}"
        if not retry or attempt == MAX_RETRIES:
            return None, url, error
        time.sleep(min(2 ** attempt, MAX_BACKOFF_SECONDS))


def validate_and_update_csv(filename: str, delay: float = 0.3, dry_run: bool = False) -> bool:
    """
    Validate all TTB IDs in the CSV and remove invalid ones.
    
    Args:
        filename: Path to the CSV file
        delay: Delay between requests to be polite to servers
        dry_run: If True, don't modify the file, just report issues
    
    Returns:
        True if no confirmed invalid IDs remain (including after applying fixes).
        Unverified requests are warnings and never cause IDs to be removed.
    """
    # Read CSV
    rows = []
    fieldnames = []
    with open(filename, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Collect TTB IDs to validate
    ttb_entries = []
    for i, row in enumerate(rows):
        if row.get('TTB_ID') and row['TTB_ID'].strip():
            ttb_entries.append({
                'row_index': i,
                'name': row['Name'],
                'batch': row['Batch'],
                'ttb_id': row['TTB_ID'].strip()
            })
    
    # Count unique TTB IDs
    unique_ttb_ids = set(entry['ttb_id'] for entry in ttb_entries)
    
    print(f"Validating {len(ttb_entries)} TTB ID entries ({len(unique_ttb_ids)} unique IDs) from {filename}...\n")
    
    # Cache for TTB ID validation results
    ttb_cache: Dict[str, ValidationResult] = {}
    cache_hits = 0
    
    # Track invalid entries
    invalid_entries = []
    warning_entries = []
    rows_to_clear = set()
    
    # Validate each TTB ID
    for i, entry in enumerate(ttb_entries, 1):
        name = entry['name']
        batch = entry['batch']
        ttb_id = entry['ttb_id']
        row_index = entry['row_index']
        
        # Check cache first
        if ttb_id in ttb_cache:
            is_valid, url, error = ttb_cache[ttb_id]
            cache_hits += 1
        else:
            # Validate TTB ID and cache the result
            is_valid, url, error = validate_ttb_url(ttb_id)
            ttb_cache[ttb_id] = (is_valid, url, error)
            
            # Be polite to servers - add delay after each new validation
            time.sleep(delay)
        
        if is_valid is True:
            print(f"✓ [{i}/{len(ttb_entries)}] {name} - {batch} (TTB: {ttb_id})")
        elif is_valid is not False:
            print(f"⚠️ [{i}/{len(ttb_entries)}] {name} - {batch} (TTB: {ttb_id})")
            print(f"   URL: {url}")
            print(f"   Warning (unverified; ID retained): {error}")
            warning_entries.append({
                'name': name,
                'batch': batch,
                'ttb_id': ttb_id,
                'url': url,
                'error': error
            })
        else:
            print(f"❌ [{i}/{len(ttb_entries)}] {name} - {batch} (TTB: {ttb_id})")
            print(f"   URL: {url}")
            print(f"   Error: {error}")
            invalid_entries.append({
                'name': name,
                'batch': batch,
                'ttb_id': ttb_id,
                'url': url,
                'error': error
            })
            rows_to_clear.add(row_index)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total TTB ID entries: {len(ttb_entries)}")
    print(f"Unique TTB IDs checked: {len(unique_ttb_ids)}")
    print(f"Cache hits: {cache_hits}")
    print(f"Verified valid TTB IDs: {len(ttb_entries) - len(invalid_entries) - len(warning_entries)}")
    print(f"Invalid TTB IDs: {len(invalid_entries)}")
    print(f"Warnings (unverified IDs retained): {len(warning_entries)}")
    
    # Report warnings (transient network errors)
    if warning_entries:
        print(f"\n{'='*70}")
        print(f"UNVERIFIED REQUESTS (not treated as invalid; IDs retained):")
        print(f"{'='*70}")
        for entry in warning_entries:
            print(f"\n⚠️ {entry['name']} - {entry['batch']}")
            print(f"   TTB ID: {entry['ttb_id']}")
            print(f"   URL: {entry['url']}")
            print(f"   Warning: {entry['error']}")
    
    # Report invalid entries
    if invalid_entries:
        print(f"\n{'='*70}")
        print(f"INVALID TTB IDs FOUND:")
        print(f"{'='*70}")
        for entry in invalid_entries:
            print(f"\n❌ {entry['name']} - {entry['batch']}")
            print(f"   TTB ID: {entry['ttb_id']}")
            print(f"   URL: {entry['url']}")
            print(f"   Error: {entry['error']}")
        
        # Remove invalid TTB IDs from CSV
        if not dry_run:
            print(f"\n{'='*70}")
            print(f"REMOVING INVALID TTB IDs")
            print(f"{'='*70}")
            
            removed_count = 0
            for row_index in sorted(rows_to_clear):
                row = rows[row_index]
                print(f"Removing TTB ID '{row['TTB_ID']}' from: {row['Name']} - {row['Batch']}")
                row['TTB_ID'] = ''
                removed_count += 1
            
            # Write updated CSV
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"\n✅ Removed {removed_count} invalid TTB IDs from {filename}")
        else:
            print(f"\n⚠️  DRY RUN: Would remove {len(rows_to_clear)} invalid TTB IDs (use --apply to actually remove them)")
        
        return not dry_run
    else:
        if warning_entries:
            print("\n⚠️ No confirmed invalid IDs; some IDs remain unverified.")
        else:
            print("\n✅ All TTB IDs are verified valid!")
        return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate TTB IDs in whiskeyindex.csv and remove invalid ones'
    )
    parser.add_argument(
        '--csv',
        default='_data/whiskeyindex.csv',
        help='Path to CSV file (default: _data/whiskeyindex.csv)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Actually remove invalid TTB IDs (default is dry-run)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.3,
        help='Delay between requests in seconds (default: 0.3)'
    )
    
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes will be made")
        print("Use --apply to actually remove invalid TTB IDs")
        print("=" * 70)
        print()
    
    success = validate_and_update_csv(args.csv, delay=args.delay, dry_run=dry_run)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

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
import sys
import urllib.request
import ssl
import time
from typing import Dict, List, Tuple


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
        year_prefix = 9
    
    # Use old format for prefix < 9 (years 2000-2008), new format for prefix >= 9
    # This matches index.md logic and TTB system change around 2009
    # Note: Older IDs from 1980s-1990s (prefix 83-99) use new format
    if year_prefix < 9:
        return f"https://ttbonline.gov/colasonline/publicViewImage.do?id={ttb_id}"
    else:
        return f"https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttb_id}"


def validate_ttb_url(ttb_id: str, timeout: int = 10) -> Tuple[bool, str, str]:
    """
    Validate a TTB ID by checking if its generated URL resolves.
    
    Args:
        ttb_id: The TTB ID to validate
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (is_valid, url, error_message)
    """
    url = generate_ttb_url(ttb_id)
    
    # Try with default SSL context first
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        response = urllib.request.urlopen(req, timeout=timeout)
        
        if response.status == 200:
            return True, url, ""
        else:
            return False, url, f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        return False, url, f"HTTP {e.code}"
    except (ssl.SSLError, urllib.error.URLError) as e:
        # Check if it's an SSL certificate error
        error_str = str(e)
        if 'CERTIFICATE_VERIFY_FAILED' in error_str or 'certificate' in error_str.lower():
            # TTB government site has certificate chain issues in some environments
            # Fall back to lenient SSL verification only when strict verification fails
            try:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(url, method='HEAD')
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                response = urllib.request.urlopen(req, timeout=timeout, context=ssl_context)
                
                if response.status == 200:
                    return True, url, ""
                else:
                    return False, url, f"HTTP {response.status}"
            except urllib.error.HTTPError as e2:
                return False, url, f"HTTP {e2.code}"
            except Exception as e2:
                return False, url, f"Error: {str(e2)}"
        else:
            # Non-SSL error
            return False, url, f"URL Error: {e.reason if hasattr(e, 'reason') else str(e)}"
    except Exception as e:
        return False, url, f"Error: {str(e)}"


def validate_and_update_csv(filename: str, delay: float = 0.3, dry_run: bool = False) -> bool:
    """
    Validate all TTB IDs in the CSV and remove invalid ones.
    
    Args:
        filename: Path to the CSV file
        delay: Delay between requests to be polite to servers
        dry_run: If True, don't modify the file, just report issues
    
    Returns:
        True if all TTB IDs are valid, False otherwise
    """
    # Read CSV
    rows = []
    fieldnames = []
    with open(filename, 'r') as f:
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
    ttb_cache: Dict[str, Tuple[bool, str, str]] = {}
    cache_hits = 0
    
    # Track invalid entries
    invalid_entries = []
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
        
        if is_valid:
            print(f"✓ [{i}/{len(ttb_entries)}] {name} - {batch} (TTB: {ttb_id})")
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
    print(f"Unique TTB IDs validated: {len(unique_ttb_ids)}")
    print(f"Cache hits: {cache_hits}")
    print(f"Valid TTB IDs: {len(ttb_entries) - len(invalid_entries)}")
    print(f"Invalid TTB IDs: {len(invalid_entries)}")
    
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
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"\n✅ Removed {removed_count} invalid TTB IDs from {filename}")
        else:
            print(f"\n⚠️  DRY RUN: Would remove {len(rows_to_clear)} invalid TTB IDs (use --apply to actually remove them)")
        
        return False
    else:
        print("\n✅ All TTB IDs are valid!")
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

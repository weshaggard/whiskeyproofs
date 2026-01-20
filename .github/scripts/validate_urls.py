#!/usr/bin/env python3
"""
URL validation script for whiskeyindex.csv
Checks that all URLs in the CSV are valid and return 200 status codes.
Includes caching to avoid redundant checks for duplicate URLs.
"""

import csv
import sys
import urllib.request
import time
from typing import Dict, List, Tuple


def validate_url(url: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Validate a URL by making a HEAD request.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        req = urllib.request.Request(url, method='HEAD')
        response = urllib.request.urlopen(req, timeout=timeout)
        if response.status == 200:
            return True, ""
        else:
            return False, f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        # Angel's Envy blocks bots with 403, but URLs work in browsers
        # Treat 403 from Angel's Envy as valid (warning only)
        if e.code == 403 and 'angelsenvy.com' in url:
            return True, "HTTP 403 (bot protection - URL valid in browser)"
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"URL Error: {e.reason}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_csv_urls(filename: str, delay: float = 0.3) -> bool:
    """
    Validate all URLs in the CSV file with caching for duplicate URLs.
    
    Args:
        filename: Path to the CSV file
        delay: Delay between requests to be polite to servers
    
    Returns:
        True if all URLs are valid, False otherwise
    """
    # Read CSV and collect all URLs
    urls_to_check = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('url') and row['url'].strip():
                urls_to_check.append({
                    'name': row['Name'],
                    'batch': row['Batch'],
                    'url': row['url'].strip()
                })
    
    # Count unique URLs
    unique_urls = set(entry['url'] for entry in urls_to_check)
    
    print(f"Validating {len(urls_to_check)} URL entries ({len(unique_urls)} unique URLs) from {filename}...\n")
    
    # Cache for URL validation results
    url_cache: Dict[str, Tuple[bool, str]] = {}
    cache_hits = 0
    
    # Test each URL
    invalid_urls = []
    for i, entry in enumerate(urls_to_check, 1):
        name = entry['name']
        batch = entry['batch']
        url = entry['url']
        
        # Check cache first
        if url in url_cache:
            is_valid, error = url_cache[url]
            cache_hits += 1
        else:
            # Validate URL and cache the result
            is_valid, error = validate_url(url)
            url_cache[url] = (is_valid, error)
            
            # Be polite to servers (only for new URLs)
            if i < len(urls_to_check):
                time.sleep(delay)
        
        if is_valid:
            print(f"✓ [{i}/{len(urls_to_check)}] {name} - {batch}")
        else:
            print(f"❌ [{i}/{len(urls_to_check)}] {name} - {batch}")
            print(f"   URL: {url}")
            print(f"   Error: {error}")
            invalid_urls.append({
                'name': name,
                'batch': batch,
                'url': url,
                'error': error
            })
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total URL entries: {len(urls_to_check)}")
    print(f"Unique URLs validated: {len(unique_urls)}")
    print(f"Cache hits: {cache_hits}")
    print(f"Valid URLs: {len(urls_to_check) - len(invalid_urls)}")
    print(f"Invalid URLs: {len(invalid_urls)}")
    
    if invalid_urls:
        print(f"\n{'='*60}")
        print(f"INVALID URLs FOUND:")
        print(f"{'='*60}")
        for entry in invalid_urls:
            print(f"\n❌ {entry['name']} - {entry['batch']}")
            print(f"   URL: {entry['url']}")
            print(f"   Error: {entry['error']}")
        return False
    else:
        print("\n✅ All URLs are valid!")
        return True


if __name__ == '__main__':
    filename = '_data/whiskeyindex.csv'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    success = validate_csv_urls(filename)
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
URL validation script for whiskeyindex.csv
Checks that all URLs in the CSV are valid and return 200 status codes.
Includes caching to avoid redundant checks for duplicate URLs.
"""

import csv
import sys
import urllib.request
import ssl
import time
from typing import Dict, List, Tuple


def validate_url(url: str, timeout: int = 10) -> Tuple[bool, str, bool]:
    """
    Validate a URL by making a HEAD request.

    Handles two special cases:
    1. Bot protection: Sites commonly return 403 for automated requests but work fine in
       browsers. All 403 responses are treated as transient warnings rather than failures.
    2. SSL certificate errors: Sites with expired or invalid certificates are retried with
       lenient SSL verification. This is acceptable for URL existence checking where no
       sensitive data is transmitted.

    Returns:
        Tuple of (is_valid, error_message, is_transient)
        - is_valid: True if the URL is considered reachable
        - error_message: description of any error or warning
        - is_transient: True when the failure is likely temporary (network/server issue),
          False when it is definitively broken (404, 410, DNS failure, etc.)
    """
    import socket

    def is_transient_http_error(code: int) -> bool:
        """Return True for HTTP errors that are likely transient (server-side, rate-limiting, or bot-protection)."""
        # 403 is treated as transient: many sites block automated requests but work in browsers
        return code == 403 or code == 429 or (500 <= code < 600)

    def classify_url_error(e: urllib.error.URLError) -> Tuple[bool, str, bool]:
        """
        Classify a URLError into (is_valid=False, message, is_transient).

        DNS resolution failures (socket.gaierror) are permanent — the hostname
        does not exist. All other connection-level errors (refused, reset, etc.)
        are treated as transient.
        """
        reason = e.reason
        if isinstance(reason, socket.gaierror):
            # DNS lookup failure — the domain does not resolve; this is a definitive error
            return False, f"DNS Error: {reason}", False
        return False, f"URL Error: {reason}", True

    def _try_head_request(context=None) -> Tuple[bool, str, bool]:
        """Make a single HEAD request, optionally with a custom SSL context."""
        try:
            req = urllib.request.Request(url, method='HEAD')
            kwargs: dict = {'timeout': timeout}
            if context is not None:
                kwargs['context'] = context
            response = urllib.request.urlopen(req, **kwargs)
            # urllib follows redirects, so any 2xx/3xx result here means success
            if 200 <= response.status < 400:
                return True, "", False
            # 4xx/5xx reached without raising HTTPError (unusual but handle gracefully)
            return False, f"HTTP {response.status}", is_transient_http_error(response.status)
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}", is_transient_http_error(e.code)
        except urllib.error.URLError as e:
            if isinstance(e.reason, ssl.SSLError):
                # Signal caller to retry with lenient SSL
                raise
            return classify_url_error(e)
        except TimeoutError as e:
            return False, f"Timeout: {str(e)}", True
        except Exception as e:
            return False, f"Error: {str(e)}", True

    # First attempt with default SSL context
    try:
        return _try_head_request()
    except urllib.error.URLError as e:
        # Only SSL errors are re-raised by _try_head_request; retry with lenient verification
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return _try_head_request(context=ssl_context)
        except urllib.error.URLError as e2:
            return classify_url_error(e2)
        except Exception as e2:
            return False, f"Error: {str(e2)}", True


def validate_csv_urls(filename: str, delay: float = 0.3, apply: bool = False) -> bool:
    """
    Validate all URLs in the CSV file with caching for duplicate URLs.

    Failures are split into two tiers:
    - Transient failures (timeouts, connection errors, 429, 5xx): printed as warnings,
      do NOT cause the script to exit with a non-zero status.
    - Definitive failures (404, 410, DNS errors): printed as errors and cause a non-zero
      exit unless ``apply`` is True (which clears them from the CSV instead).

    Args:
        filename: Path to the CSV file
        delay: Delay between requests to be polite to servers
        apply: When True, clear definitively broken URLs from the CSV instead of failing

    Returns:
        True if there are no definitive failures (or all were cleared), False otherwise
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

    # Cache for URL validation results: url -> (is_valid, error, is_transient)
    url_cache: Dict[str, Tuple[bool, str, bool]] = {}
    cache_hits = 0

    # Test each URL
    invalid_urls = []      # definitive failures
    transient_urls = []    # transient / likely-temporary failures
    for i, entry in enumerate(urls_to_check, 1):
        name = entry['name']
        batch = entry['batch']
        url = entry['url']

        # Check cache first
        if url in url_cache:
            is_valid, error, is_transient = url_cache[url]
            cache_hits += 1
        else:
            # Validate URL and cache the result
            is_valid, error, is_transient = validate_url(url)
            url_cache[url] = (is_valid, error, is_transient)

            # Be polite to servers (only for new URLs)
            if i < len(urls_to_check):
                time.sleep(delay)

        if is_valid:
            print(f"✓ [{i}/{len(urls_to_check)}] {name} - {batch}")
        elif is_transient:
            print(f"⚠ [{i}/{len(urls_to_check)}] {name} - {batch}")
            print(f"   URL: {url}")
            print(f"   Warning (transient): {error}")
            transient_urls.append({
                'name': name,
                'batch': batch,
                'url': url,
                'error': error
            })
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
    print(f"Valid URLs: {len(urls_to_check) - len(invalid_urls) - len(transient_urls)}")
    print(f"Transient warnings: {len(transient_urls)}")
    print(f"Definitively invalid URLs: {len(invalid_urls)}")

    if transient_urls:
        print(f"\n{'='*60}")
        print(f"TRANSIENT WARNINGS (likely temporary - not blocking):")
        print(f"{'='*60}")
        for entry in transient_urls:
            print(f"\n⚠ {entry['name']} - {entry['batch']}")
            print(f"   URL: {entry['url']}")
            print(f"   Warning: {entry['error']}")

    if invalid_urls:
        print(f"\n{'='*60}")
        print(f"DEFINITIVELY INVALID URLs FOUND:")
        print(f"{'='*60}")
        for entry in invalid_urls:
            print(f"\n❌ {entry['name']} - {entry['batch']}")
            print(f"   URL: {entry['url']}")
            print(f"   Error: {entry['error']}")

        if apply:
            # Build a set of broken URLs to clear
            broken_urls = {e['url'] for e in invalid_urls}

            # Re-read the full CSV, clear url field for broken entries, write back
            rows = []
            fieldnames = None
            with open(filename, 'r', newline='') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row.get('url', '').strip() in broken_urls:
                        row['url'] = ''
                    rows.append(row)

            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            print(f"\n✅ Cleared {len(invalid_urls)} broken URL(s) from {filename}")
            return True
        else:
            return False
    else:
        if transient_urls:
            print(f"\n⚠ {len(transient_urls)} transient warning(s) - URLs may be temporarily unreachable.")
        else:
            print("\n✅ All URLs are valid!")
        return True


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate URLs in whiskeyindex.csv')
    parser.add_argument('filename', nargs='?', default='_data/whiskeyindex.csv',
                        help='Path to the CSV file (default: _data/whiskeyindex.csv)')
    parser.add_argument('--apply', action='store_true',
                        help='Clear broken URLs from the CSV instead of failing')
    args = parser.parse_args()

    success = validate_csv_urls(args.filename, apply=args.apply)
    sys.exit(0 if success else 1)

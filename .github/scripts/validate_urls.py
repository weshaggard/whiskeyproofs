#!/usr/bin/env python3
"""
URL validation script for whiskeyindex.csv
Checks URLs in the CSV, distinguishing definitive failures from unknown reachability.
Includes caching to avoid redundant checks for duplicate URLs.
"""

import csv
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import urllib.error
import urllib.request
import ssl
import time
from typing import Dict, Tuple


def validate_url(url: str, timeout: int = 10) -> Tuple[bool, str, bool]:
    """
    Validate a URL by making a HEAD request.

    Fall back to GET when HEAD is unsupported (405/501). Retry transient failures
    at most twice (three attempts total), always retaining certificate verification.
    TLS failures are unknown/transient warnings, never successful validations.

    Returns:
        Tuple of (is_valid, error_message, is_transient)
        - is_valid: True if the URL is considered reachable
        - error_message: description of any error or warning
        - is_transient: True when the failure is likely temporary (network/server issue),
          False when it is definitively broken (404, 410, nonexistent hostname, etc.)
    """
    def is_transient_http_error(code: int) -> bool:
        """Return True for HTTP errors that are likely transient (server-side, rate-limiting, or bot-protection)."""
        # 403 is treated as transient: many sites block automated requests but work in browsers
        return code == 403 or code == 429 or (500 <= code < 600)

    def classify_url_error(e: urllib.error.URLError) -> Tuple[bool, str, bool]:
        """
        Classify a URLError into (is_valid=False, message, is_transient).

        Only EAI_NONAME definitively identifies an unresolvable hostname.
        EAI_AGAIN and unknown resolver failures remain transient.
        """
        reason = e.reason
        if isinstance(reason, socket.gaierror):
            return False, f"DNS Error: {reason}", reason.errno != socket.EAI_NONAME
        if isinstance(reason, ssl.SSLError):
            return False, f"TLS Error (unknown reachability): {reason}", True
        return False, f"URL Error: {reason}", True

    def request(method: str) -> Tuple[bool, str, bool]:
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                status = response.status
            if method == 'HEAD' and status in (405, 501):
                return request('GET')
            if 200 <= status < 400:
                return True, "", False
            return False, f"HTTP {status}", is_transient_http_error(status)
        except urllib.error.HTTPError as e:
            code = e.code
            e.close()
            if method == 'HEAD' and code in (405, 501):
                return request('GET')
            return False, f"HTTP {code}", is_transient_http_error(code)
        except urllib.error.URLError as e:
            return classify_url_error(e)
        except socket.gaierror as e:
            return classify_url_error(urllib.error.URLError(e))
        except ssl.SSLError as e:
            return False, f"TLS Error (unknown reachability): {e}", True
        except TimeoutError as e:
            return False, f"Timeout: {str(e)}", True
        except ValueError as e:
            return False, f"Invalid URL: {e}", False
        except Exception as e:
            return False, f"Error: {str(e)}", True

    for attempt in range(3):
        result = request('HEAD')
        if result[0] or not result[2]:
            return result
        if attempt < 2:
            time.sleep(0.3 * (attempt + 1))
    return result


def read_entries(source):
    reader = csv.DictReader(source)
    if not reader.fieldnames or not {'Name', 'Batch', 'url'} <= set(reader.fieldnames):
        raise ValueError("CSV must contain Name, Batch, and url columns")
    return [
        {'name': row['Name'], 'batch': row['Batch'], 'url': row['url'].strip()}
        for row in reader if row.get('url') and row['url'].strip()
    ]


def base_urls(filename: str, base_ref: str):
    if not base_ref.strip():
        raise ValueError("Base ref must not be empty")
    root = Path(__file__).resolve().parents[2]
    csv_path = Path(filename).resolve().relative_to(root).as_posix()
    try:
        result = subprocess.run(
            ['git', 'show', '--end-of-options', f'{base_ref}:{csv_path}'],
            cwd=root, capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as error:
        raise ValueError(f"Cannot read base CSV at {base_ref}:{csv_path}: "
                         f"{(error.stderr or str(error)).strip()}") from error
    return {entry['url'] for entry in read_entries(io.StringIO(result.stdout))}


def write_reports(result, report=None, summary=None):
    if report:
        with open(report, 'w', encoding='utf-8') as output:
            json.dump(result, output, indent=2)
            output.write('\n')
    if summary:
        counts = result['counts']
        with open(summary, 'a', encoding='utf-8') as output:
            output.write(
                f"\n## URL validation: {result['status']}\n\n"
                f"Checked **{counts['unique_urls']}** unique URLs "
                f"({counts['checked_entries']} entries); "
                f"valid: **{counts['valid']}**, transient/unknown: **{counts['transient']}**, "
                f"invalid: **{counts['invalid']}**; skipped entries: "
                f"**{counts['skipped_entries']}**.\n"
            )
            for error in result['errors']:
                output.write(f"\nError: {error.replace(chr(10), ' ')}\n")


def validate_csv_urls(filename: str, delay: float = 0.3, apply: bool = False,
                      base_ref=None, report=None, summary=None) -> bool:
    """
    Validate all URLs in the CSV file with caching for duplicate URLs.

    Failures are split into two tiers:
    - Transient failures (timeouts, connection errors, 429, 5xx): printed as warnings,
      do NOT cause the script to exit with a non-zero status.
    - Definitive failures (404, 410, nonexistent hostname): printed as errors and cause a non-zero
      exit unless ``apply`` is True (which clears them from the CSV instead).

    Args:
        filename: Path to the CSV file
        delay: Delay between requests to be polite to servers
        apply: When True, clear definitively broken URLs from the CSV instead of failing
        base_ref: When supplied, check URL values absent from the CSV at this git ref
        report: Optional JSON output path; result counts classify unique checked URLs
        summary: Optional Markdown output path (appended, suitable for GITHUB_STEP_SUMMARY)

    Returns:
        True if there are no definitive failures (or all were cleared), False otherwise
    """
    result = {
        'filename': str(filename), 'base_ref': base_ref, 'apply': apply,
        'status': 'ok', 'counts': {
            'total_entries': 0, 'checked_entries': 0, 'unique_urls': 0,
            'valid': 0, 'transient': 0, 'invalid': 0, 'skipped_entries': 0,
            'cache_hits': 0, 'cleared_entries': 0,
        }, 'checks': [], 'errors': [],
    }
    counts = result['counts']
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as f:
            urls_to_check = read_entries(f)
        counts['total_entries'] = len(urls_to_check)
        if base_ref is not None:
            previous_urls = base_urls(filename, base_ref)
            urls_to_check = [entry for entry in urls_to_check if entry['url'] not in previous_urls]
    except (OSError, ValueError, csv.Error, subprocess.SubprocessError) as error:
        result['status'] = 'error'
        result['errors'].append(str(error))
        print(f"URL validation failed: {error}", file=sys.stderr)
        write_reports(result, report, summary)
        return False

    # Count unique URLs
    unique_urls = set(entry['url'] for entry in urls_to_check)
    counts['checked_entries'] = len(urls_to_check)
    counts['unique_urls'] = len(unique_urls)
    counts['skipped_entries'] = counts['total_entries'] - len(urls_to_check)

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
            status = 'valid' if is_valid else 'transient' if is_transient else 'invalid'
            counts[status] += 1
            result['checks'].append({
                'url': url, 'status': status, 'error': error,
                'entries': [{'name': item['name'], 'batch': item['batch']}
                            for item in urls_to_check if item['url'] == url],
            })

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
    counts['cache_hits'] = cache_hits
    result['status'] = 'invalid' if invalid_urls else 'warning' if transient_urls else 'ok'
    success = not invalid_urls

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
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row.get('url', '').strip() in broken_urls:
                        row['url'] = ''
                    rows.append(row)

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n')
                writer.writeheader()
                writer.writerows(rows)

            print(f"\n✅ Cleared {len(invalid_urls)} broken URL(s) from {filename}")
            counts['cleared_entries'] = len(invalid_urls)
            result['status'] = 'applied'
            success = True
        else:
            success = False
    else:
        if transient_urls:
            print(f"\n⚠ {len(transient_urls)} transient warning(s) - URLs may be temporarily unreachable.")
        else:
            print("\n✅ All URLs are valid!")
    write_reports(result, report, summary)
    return success


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate URLs in whiskeyindex.csv')
    parser.add_argument('filename', nargs='?', default='_data/whiskeyindex.csv',
                        help='Path to the CSV file (default: _data/whiskeyindex.csv)')
    parser.add_argument('--apply', action='store_true',
                        help='Clear broken URLs from the CSV instead of failing')
    parser.add_argument('--base-ref',
                        help='Check only URL values absent from this git ref CSV')
    parser.add_argument('--report', help='Write structured JSON results to this path')
    parser.add_argument('--summary', help='Append Markdown results to this path (e.g. GITHUB_STEP_SUMMARY)')
    args = parser.parse_args()

    try:
        success = validate_csv_urls(args.filename, apply=args.apply, base_ref=args.base_ref,
                                    report=args.report, summary=args.summary)
    except (OSError, ValueError, csv.Error) as error:
        print(f"URL validation failed: {error}", file=sys.stderr)
        success = False
    sys.exit(0 if success else 1)

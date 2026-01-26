#!/usr/bin/env python3
"""
TTB ID validation script for whiskeyindex.csv
Checks that all TTB IDs in the CSV resolve to valid TTB COLA pages
and attempts to verify they match the expected product details.
"""

import csv
import sys
import urllib.request
import urllib.error
import time
from typing import Dict, List, Tuple, Optional
import re
import ssl


def validate_ttb_id(ttb_id: str, timeout: int = 15) -> Tuple[bool, str, Optional[Dict]]:
    """
    Validate a TTB ID by checking if it resolves to a valid COLA page.
    
    Args:
        ttb_id: 14-digit TTB ID
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (is_valid, error_message, details_dict)
        where details_dict contains extracted information from the COLA page
    """
    if not ttb_id or not ttb_id.strip():
        return True, "", None  # Empty is OK, just no validation
    
    ttb_id = ttb_id.strip()
    
    # Validate format (should be 14 digits)
    if not re.match(r'^\d{14}$', ttb_id):
        return False, f"Invalid TTB ID format (expected 14 digits, got '{ttb_id}')", None
    
    # Construct TTB COLA detail page URL
    url = f"https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttb_id}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; TTB-Validator/1.0)')
        
        # Create SSL context that doesn't verify certificates (TTB has cert issues)
        # NOTE: This is a known security trade-off. The TTB website has SSL certificate
        # verification issues that prevent normal validation. Since we're only reading
        # public COLA data (not submitting sensitive information), this is acceptable.
        # TODO: Monitor TTB website for SSL cert fixes and remove this workaround when possible.
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        response = urllib.request.urlopen(req, timeout=timeout, context=ssl_context)
        
        if response.status != 200:
            return False, f"HTTP {response.status}", None
        
        # Read and decode the response
        content = response.read().decode('utf-8', errors='ignore')
        
        # Check for error messages in the page
        if 'No COLA found' in content or 'does not exist' in content.lower():
            return False, "TTB ID not found in COLA registry", None
        
        # Check for actual error page (not just the word "Error" in labels)
        if 'Page Not Found' in content or 'Invalid Request' in content:
            return False, "Error accessing COLA details", None
        
        # Try to extract basic information
        details = extract_cola_details(content)
        
        return True, "", details
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "TTB ID not found (HTTP 404)", None
        elif e.code == 500:
            return False, "TTB server error (HTTP 500)", None
        else:
            return False, f"HTTP {e.code}", None
    except urllib.error.URLError as e:
        return False, f"URL Error: {e.reason}", None
    except Exception as e:
        return False, f"Error: {str(e)}", None


def extract_cola_details(html_content: str) -> Dict[str, str]:
    """
    Extract product details from TTB COLA HTML page.
    
    NOTE: This is basic extraction using regex patterns. The TTB pages use
    complex table layouts that may require more sophisticated parsing.
    This function provides basic information extraction but may not capture
    all details or may capture incorrect data from malformed HTML.
    
    Returns:
        Dictionary with extracted details (brand_name, fanciful_name, alcohol_content, etc.)
    """
    details = {}
    
    # These are basic regex patterns - TTB pages use tables with specific labels
    # This is a simple extraction and may need refinement
    # TODO: Consider using BeautifulSoup for more robust HTML parsing
    
    patterns = {
        'brand_name': r'Brand Name.*?<td[^>]*>(.*?)</td>',
        'fanciful_name': r'Fanciful Name.*?<td[^>]*>(.*?)</td>',
        'alcohol_content': r'Alcohol Content.*?<td[^>]*>(.*?)</td>',
        'formula': r'Formula.*?<td[^>]*>(.*?)</td>',
        'type': r'Type.*?<td[^>]*>(.*?)</td>',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            # Clean HTML tags (basic approach, may fail with complex HTML)
            # TODO: Use html.parser or BeautifulSoup for robust HTML stripping
            value = re.sub(r'<[^>]+>', '', value)
            value = re.sub(r'\s+', ' ', value).strip()
            details[key] = value
    
    return details


def validate_csv_ttb_ids(filename: str, delay: float = 1.0, verbose: bool = True) -> bool:
    """
    Validate all TTB IDs in the CSV file.
    
    Args:
        filename: Path to the CSV file
        delay: Delay between requests to be polite to TTB servers
        verbose: Print detailed information during validation
    
    Returns:
        True if all TTB IDs are valid, False otherwise
    """
    # Read CSV and collect all TTB IDs
    entries_to_check = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # Line 2 is first data row
            if row.get('TTB_ID') and row['TTB_ID'].strip():
                entries_to_check.append({
                    'line': i,
                    'name': row['Name'],
                    'batch': row['Batch'],
                    'proof': row['Proof'],
                    'age': row.get('Age', ''),
                    'year': row['ReleaseYear'],
                    'ttb_id': row['TTB_ID'].strip()
                })
    
    # Count unique TTB IDs
    unique_ttb_ids = set(entry['ttb_id'] for entry in entries_to_check)
    
    print(f"Validating {len(entries_to_check)} TTB ID entries ({len(unique_ttb_ids)} unique IDs) from {filename}...\n")
    
    # Cache for TTB ID validation results
    ttb_cache: Dict[str, Tuple[bool, str, Optional[Dict]]] = {}
    cache_hits = 0
    
    # Track results
    invalid_ttb_ids = []
    duplicate_usage = {}  # Track which TTB IDs are used multiple times
    
    # Test each TTB ID
    for i, entry in enumerate(entries_to_check, 1):
        ttb_id = entry['ttb_id']
        
        # Track duplicate usage
        if ttb_id not in duplicate_usage:
            duplicate_usage[ttb_id] = []
        duplicate_usage[ttb_id].append(entry)
        
        # Check cache first
        if ttb_id in ttb_cache:
            is_valid, error, details = ttb_cache[ttb_id]
            cache_hits += 1
        else:
            # Validate TTB ID and cache the result
            is_valid, error, details = validate_ttb_id(ttb_id)
            ttb_cache[ttb_id] = (is_valid, error, details)
            
            # Be polite to TTB servers (only for new IDs)
            if i < len(entries_to_check):
                time.sleep(delay)
        
        if verbose:
            if is_valid:
                print(f"✓ [{i}/{len(entries_to_check)}] {entry['name']} - {entry['batch']} (TTB: {ttb_id})")
                if details:
                    # Show extracted details if available
                    if 'brand_name' in details:
                        print(f"   Brand: {details['brand_name']}")
                    if 'alcohol_content' in details:
                        print(f"   Alcohol: {details['alcohol_content']}")
            else:
                print(f"❌ [{i}/{len(entries_to_check)}] {entry['name']} - {entry['batch']} (TTB: {ttb_id})")
                print(f"   Error: {error}")
        
        if not is_valid:
            invalid_ttb_ids.append({
                'line': entry['line'],
                'name': entry['name'],
                'batch': entry['batch'],
                'proof': entry['proof'],
                'year': entry['year'],
                'ttb_id': ttb_id,
                'error': error
            })
    
    # Check for duplicate TTB ID usage (potential issues)
    duplicates_with_diff_proof = []
    for ttb_id, usages in duplicate_usage.items():
        if len(usages) > 1:
            # Check if they have significantly different proofs
            proofs = []
            for usage in usages:
                try:
                    # Handle proof ranges (supports '-' delimiter)
                    # TODO: Support other delimiters like '~', '±' if they appear in data
                    proof_str = usage['proof']
                    if '-' in proof_str:
                        # Take the first value in a range
                        proof_str = proof_str.split('-')[0]
                    proof = float(proof_str)
                    proofs.append(proof)
                except (ValueError, AttributeError):
                    pass
            
            if proofs:
                min_proof = min(proofs)
                max_proof = max(proofs)
                proof_diff = max_proof - min_proof
                
                # If proof difference is > 2, this might be incorrect
                if proof_diff > 2.0:
                    duplicates_with_diff_proof.append({
                        'ttb_id': ttb_id,
                        'count': len(usages),
                        'usages': usages,
                        'proof_range': f"{min_proof} - {max_proof}",
                        'proof_diff': proof_diff
                    })
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total TTB ID entries: {len(entries_to_check)}")
    print(f"Unique TTB IDs validated: {len(unique_ttb_ids)}")
    print(f"Cache hits: {cache_hits}")
    print(f"Valid TTB IDs: {len(entries_to_check) - len(invalid_ttb_ids)}")
    print(f"Invalid TTB IDs: {len(invalid_ttb_ids)}")
    print(f"Duplicate TTB IDs with proof variations: {len(duplicates_with_diff_proof)}")
    
    all_valid = True
    
    if invalid_ttb_ids:
        all_valid = False
        print(f"\n{'='*70}")
        print(f"INVALID TTB IDs FOUND:")
        print(f"{'='*70}")
        for entry in invalid_ttb_ids:
            print(f"\n❌ Line {entry['line']}: {entry['name']} - {entry['batch']} ({entry['year']})")
            print(f"   TTB ID: {entry['ttb_id']}")
            print(f"   Proof: {entry['proof']}")
            print(f"   Error: {entry['error']}")
    
    if duplicates_with_diff_proof:
        print(f"\n{'='*70}")
        print(f"WARNING: DUPLICATE TTB IDs WITH SIGNIFICANT PROOF VARIATIONS")
        print(f"{'='*70}")
        print("According to TTB regulations, different proof levels require separate COLA approvals.")
        print("The following TTB IDs are used across batches with >2 proof point differences:\n")
        
        for dup in duplicates_with_diff_proof:
            print(f"\n⚠️  TTB ID: {dup['ttb_id']} (used {dup['count']} times)")
            print(f"   Proof range: {dup['proof_range']} (Δ {dup['proof_diff']:.1f} points)")
            print(f"   Entries:")
            for usage in dup['usages']:
                print(f"     - Line {usage['line']}: {usage['name']} - {usage['batch']} ({usage['year']}) - {usage['proof']} proof")
    
    if all_valid and not duplicates_with_diff_proof:
        print("\n✅ All TTB IDs are valid with no suspicious duplicates!")
    elif all_valid:
        print("\n⚠️  All TTB IDs resolve correctly, but there are suspicious duplicate usages.")
        print("    Review the warnings above and verify each TTB ID matches its specific batch/proof.")
    
    return all_valid


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate TTB IDs in whiskeyindex.csv'
    )
    parser.add_argument(
        '--csv',
        default='_data/whiskeyindex.csv',
        help='Path to CSV file (default: _data/whiskeyindex.csv)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between TTB requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    
    success = validate_csv_ttb_ids(args.csv, delay=args.delay, verbose=not args.quiet)
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Query TTB COLA Public Registry for whiskey approval IDs.

This script searches the TTB (Alcohol and Tobacco Tax and Trade Bureau) 
COLA Public Registry to find TTB approval IDs for whiskey entries in the database.

The script uses HTTP POST requests to query the TTB website.

Requirements:
    pip install requests beautifulsoup4
    
Usage:
    python3 .github/scripts/query_ttb.py [--test] [--verbose]
    
Options:
    --test       Run in test mode with a small sample of entries
    --verbose    Enable verbose output
    --limit N    Limit to N entries (default: all without TTB_ID)
    --output FILE Save results to JSON file
"""

import csv
import re
import sys
import time
import argparse
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class TTBQuerier:
    """Query the TTB COLA Public Registry for whiskey approval IDs"""
    
    SEARCH_URL = "https://ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search"
    DETAIL_URL = "https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid="
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Disable SSL verification warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
    def _extract_brand_name(self, name):
        """Extract brand name from product name"""
        # Split on common product type terms
        split_terms = [
            'Cask Strength',
            'Barrel Proof',
            'Single Barrel',
            'Small Batch',
            'Limited Edition',
            'Special Release',
            'Straight',
            'BTAC',
        ]
        
        brand = name
        for term in split_terms:
            if term in name:
                brand = name.split(term)[0].strip()
                break
                
        # Remove common suffixes
        brand = brand.replace('(WLW)', '').replace('(GTS)', '').replace('(THH)', '').strip()
        
        return brand
    
    def search_whiskey(self, name, batch, proof, release_year):
        """
        Search TTB COLA registry for a whiskey entry using HTTP POST.
        
        Args:
            name: Product name (e.g., "Booker's", "Angel's Envy Cask Strength")
            batch: Batch identifier
            proof: Proof value
            release_year: Release year
            
        Returns:
            List of matching TTB IDs with their details, or empty list if none found
        """
        # Extract brand name for search
        brand = self._extract_brand_name(name)
        
        if self.verbose:
            print(f"  Searching: {name} (brand: {brand}), batch: {batch}, proof: {proof}, year: {release_year}")
        
        # Set date range around the release year
        date_from = f"01/01/{release_year}"
        date_to = f"12/31/{release_year}"
        
        # Prepare form data for POST request
        form_data = {
            'searchCriteria.dateCompletedFrom': date_from,
            'searchCriteria.dateCompletedTo': date_to,
            'searchCriteria.productOrFancifulName': brand,
            'searchCriteria.productNameSearchType': 'C',  # C = Contains, E = Exact
            'searchCriteria.classTypeFrom': '',
            'searchCriteria.classTypeTo': '',
            'searchCriteria.originCode': ''
        }
        
        try:
            # Make POST request
            response = self.session.post(self.SEARCH_URL, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            # Parse results
            results = self._parse_search_results(response.text, proof, release_year, name)
            
            if self.verbose:
                print(f"    Found {len(results)} potential match(es)")
            
            return results
            
        except Exception as e:
            if self.verbose:
                print(f"    Error during search: {e}")
            return []
    
    def _parse_search_results(self, html_content, target_proof, target_year, product_name):
        """
        Parse the search results HTML to extract TTB IDs.
        
        Filters results by proof and year to find the best matches.
        """
        results = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for result table rows
            # The TTB results are typically in a table with class 'resultTable' or similar
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    # Look for links containing ttbid
                    links = row.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href', '')
                        
                        if 'ttbid=' in href:
                            # Extract TTB ID from URL
                            match = re.search(r'ttbid=(\d+)', href)
                            if match:
                                ttb_id = match.group(1)
                                
                                # Get row text for context
                                row_text = row.get_text(strip=True, separator=' ')
                                
                                # Try to extract proof from text
                                proof_match = re.search(r'(\d+\.?\d*)\s*(?:proof|%)', row_text, re.IGNORECASE)
                                found_proof = float(proof_match.group(1)) if proof_match else None
                                
                                # Check if proof matches (within reasonable range)
                                proof_matches = False
                                if found_proof:
                                    # Allow ±1 proof variation
                                    try:
                                        target_proof_val = float(target_proof)
                                        proof_matches = abs(found_proof - target_proof_val) <= 1.0
                                    except (ValueError, TypeError):
                                        proof_matches = False
                                
                                # Store result with metadata
                                results.append({
                                    'ttb_id': ttb_id,
                                    'text': row_text[:200],  # First 200 chars
                                    'url': href if href.startswith('http') else f"https://ttbonline.gov{href}",
                                    'proof': found_proof,
                                    'proof_matches': proof_matches
                                })
        
        except Exception as e:
            if self.verbose:
                print(f"    Error parsing results: {e}")
        
        return results
    
    def query_csv_entries(self, csv_file, test_mode=False, limit=None):
        """
        Query TTB for all entries in CSV that don't have TTB IDs.
        
        Args:
            csv_file: Path to whiskeyindex.csv
            test_mode: If True, only process first 10 entries
            limit: Maximum number of entries to process
            
        Returns:
            Dictionary mapping row indices to found TTB IDs
        """
        results = {}
        
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return results
        
        # Filter to entries without TTB IDs
        entries_to_search = [
            (i, row) for i, row in enumerate(rows, start=2)
            if not row.get('TTB_ID', '').strip()
        ]
        
        print(f"Found {len(entries_to_search)} entries without TTB IDs")
        
        if test_mode:
            entries_to_search = entries_to_search[:10]
            print(f"Test mode: Processing only first {len(entries_to_search)} entries")
        elif limit:
            entries_to_search = entries_to_search[:limit]
            print(f"Limit set: Processing only first {len(entries_to_search)} entries")
        
        for idx, (i, row) in enumerate(entries_to_search, start=1):
            name = row['Name']
            batch = row['Batch']
            proof = row['Proof']
            year = row['ReleaseYear']
            
            print(f"\n[{idx}/{len(entries_to_search)}] {name} - {batch} ({year})")
            
            ttb_results = self.search_whiskey(name, batch, proof, year)
            
            if ttb_results:
                results[i] = ttb_results
                print(f"  ✓ Found {len(ttb_results)} potential match(es)")
                for result in ttb_results:
                    proof_indicator = " ✓" if result.get('proof_matches') else ""
                    print(f"    - TTB ID: {result['ttb_id']} (proof: {result.get('proof', 'N/A')}){proof_indicator}")
            else:
                print(f"  ✗ No matches found")
            
            # Rate limiting - be respectful to the TTB server
            time.sleep(2)
        
        return results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Query TTB COLA Public Registry for whiskey approval IDs'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode with only first 10 entries'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--csv',
        default='_data/whiskeyindex.csv',
        help='Path to CSV file (default: _data/whiskeyindex.csv)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of entries to process'
    )
    parser.add_argument(
        '--output',
        help='Output file to save results (JSON format)'
    )
    
    args = parser.parse_args()
    
    # Check if dependencies are available
    if not DEPENDENCIES_AVAILABLE:
        print("=" * 60)
        print("ERROR: Required dependencies not installed")
        print("=" * 60)
        print()
        print("This script requires requests and beautifulsoup4.")
        print()
        print("To install:")
        print("  pip install requests beautifulsoup4")
        print()
        sys.exit(1)
    
    print("=" * 60)
    print("TTB COLA Registry Query Tool")
    print("=" * 60)
    print()
    print("Querying TTB website using HTTP POST...")
    print()
    
    querier = TTBQuerier(verbose=args.verbose)
    
    try:
        results = querier.query_csv_entries(
            args.csv,
            test_mode=args.test,
            limit=args.limit
        )
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Results Summary")
    print("=" * 60)
    print(f"Total entries searched: {len(results) if results else 0}")
    print(f"Entries with matches found: {len(results)}")
    
    if results:
        print("\nMatched entries:")
        for line_num, ttb_results in results.items():
            print(f"  Line {line_num}: {len(ttb_results)} potential match(es)")
            for result in ttb_results:
                proof_indicator = " (proof match)" if result.get('proof_matches') else ""
                print(f"    - {result['ttb_id']}{proof_indicator}")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")
    else:
        print("\nNo matches found.")


if __name__ == '__main__':
    main()

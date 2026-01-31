#!/usr/bin/env python3
"""
Find new TTB COLA labels in the registry that are not yet in the labels directory.

This script searches the TTB COLA Public Registry for new label approvals with:
- Origin code 22 (Kentucky)
- Product class/type 100-150 (whiskey)
- Within a specified date range

It then compares the results against existing labels in the labels/ directory
and outputs only the new TTB IDs that haven't been downloaded yet.

Requirements:
    pip install requests beautifulsoup4
    
Usage:
    # Search for labels from the past 7 days
    python3 .github/scripts/find_new_ttb_labels.py

    # Search for labels in a specific date range
    python3 .github/scripts/find_new_ttb_labels.py --from 2024-01-01 --to 2024-12-31
    
    # Search with verbose output
    python3 .github/scripts/find_new_ttb_labels.py --verbose
    
    # Save results to JSON file
    python3 .github/scripts/find_new_ttb_labels.py --output new_labels.json
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

try:
    import requests
    from bs4 import BeautifulSoup
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False


class TTBLabelFinder:
    """Find new TTB COLA labels in the registry"""
    
    SEARCH_URL = "https://ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search"
    DETAIL_URL = "https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid="
    NEXT_PAGE_URL = "https://ttbonline.gov/colasonline/publicPageBasicCola.do?action=page&pgfcn=nextset"
    MAX_PAGES = 100  # Safety limit to prevent infinite loops
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Disable SSL verification warnings
        # Note: SSL verification is disabled (verify=False) due to known certificate issues
        # with the TTB website. This is consistent with other TTB scripts in this repository.
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def search_ttb_registry(self, date_from, date_to, origin_code='22', class_type_from='100', class_type_to='150'):
        """
        Search TTB COLA registry for labels within date range and filters.
        Automatically handles pagination to retrieve all results.
        
        Args:
            date_from: Start date in MM/DD/YYYY format
            date_to: End date in MM/DD/YYYY format
            origin_code: TTB origin code (default: 22 for Kentucky)
            class_type_from: Start of product class/type range (default: 100)
            class_type_to: End of product class/type range (default: 150)
            
        Returns:
            List of TTB IDs found in the search
        """
        if self.verbose:
            print(f"Searching TTB registry:")
            print(f"  Date range: {date_from} to {date_to}")
            print(f"  Origin code: {origin_code} (Kentucky)")
            print(f"  Product class/type: {class_type_from}-{class_type_to} (whiskey)")
        
        all_ttb_ids = []
        
        # Prepare form data for POST request
        form_data = {
            'searchCriteria.dateCompletedFrom': date_from,
            'searchCriteria.dateCompletedTo': date_to,
            'searchCriteria.productOrFancifulName': '',
            'searchCriteria.productNameSearchType': 'E',
            'searchCriteria.classTypeFrom': class_type_from,
            'searchCriteria.classTypeTo': class_type_to,
            'searchCriteria.originCode': origin_code
        }
        
        try:
            # Make initial POST request
            # Note: verify=False due to known certificate issues with TTB website
            response = self.session.post(self.SEARCH_URL, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            
            # Parse first page results
            ttb_ids, has_next = self._parse_search_results(response.text)
            all_ttb_ids.extend(ttb_ids)
            
            if self.verbose:
                print(f"  Page 1: Found {len(ttb_ids)} TTB IDs")
            
            # Fetch additional pages if they exist
            page_num = 2
            while has_next and page_num <= self.MAX_PAGES:
                if self.verbose:
                    print(f"  Fetching page {page_num}...")
                
                page_ttb_ids, has_next = self._fetch_next_page()
                all_ttb_ids.extend(page_ttb_ids)
                
                if self.verbose:
                    print(f"  Page {page_num}: Found {len(page_ttb_ids)} TTB IDs")
                
                page_num += 1
                
                # Add a small delay between page requests to be respectful
                if has_next:
                    time.sleep(0.5)
            
            # Warn if we hit the limit and there are still more pages
            if has_next and page_num > self.MAX_PAGES:
                print(f"  WARNING: Reached maximum page limit ({self.MAX_PAGES}). There may be more results.")
            
            if self.verbose or page_num > 2:
                print(f"  Total: Found {len(all_ttb_ids)} TTB IDs across {page_num - 1} page(s)")
            
            return all_ttb_ids
            
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def _fetch_next_page(self):
        """
        Fetch the next page of search results.
        Uses the session to maintain state from the initial search.
        
        Returns:
            Tuple of (list of TTB IDs from this page, has_next_page boolean)
        """
        try:
            response = self.session.get(self.NEXT_PAGE_URL, timeout=30, verify=False)
            response.raise_for_status()
            return self._parse_search_results(response.text)
        except Exception as e:
            print(f"Error fetching next page: {e}")
            return [], False
    
    def _parse_search_results(self, html_content):
        """
        Parse the search results HTML to extract TTB IDs.
        Returns tuple of (list of unique TTB IDs, has_next_page boolean).
        """
        ttb_ids = []
        seen_ids = set()
        has_next = False
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Check for "Next >" link to determine if there are more pages
            next_links = soup.find_all('a', string=re.compile(r'Next\s*>'))
            has_next = len(next_links) > 0
            
            # Look for result tables
            tables = soup.find_all('table')
            
            for table in tables:
                # Get all rows
                all_rows = table.find_all('tr', recursive=False)
                if len(all_rows) < 2:  # Need at least header + 1 data row
                    continue
                
                for row in all_rows[1:]:  # Skip header row
                    # Look for links containing ttbid
                    links = row.find_all('a', href=True)
                    for link in links:
                        link_href = link.get('href', '')
                        if 'ttbid=' in link_href:
                            # Extract TTB ID from URL
                            match = re.search(r'ttbid=(\d+)', link_href)
                            if match:
                                ttb_id = match.group(1)
                                if ttb_id not in seen_ids:
                                    seen_ids.add(ttb_id)
                                    ttb_ids.append(ttb_id)
                                    if self.verbose:
                                        print(f"    Found: {ttb_id}")
        
        except Exception as e:
            print(f"Error parsing results: {e}")
        
        return ttb_ids, has_next
    
    def get_existing_ttb_ids(self, labels_dir):
        """
        Get list of TTB IDs that already exist in the labels directory.
        
        Args:
            labels_dir: Path to labels directory
            
        Returns:
            Set of existing TTB IDs
        """
        labels_path = Path(labels_dir)
        existing_ids = set()
        
        if labels_path.exists():
            # Each subdirectory name is a TTB ID
            for item in labels_path.iterdir():
                if item.is_dir() and item.name.isdigit():
                    existing_ids.add(item.name)
        
        if self.verbose:
            print(f"\nFound {len(existing_ids)} existing TTB IDs in {labels_dir}")
        
        return existing_ids
    
    def find_new_labels(self, date_from, date_to, labels_dir, origin_code='22', 
                        class_type_from='100', class_type_to='150'):
        """
        Find TTB IDs in registry that are not yet in the labels directory.
        
        Args:
            date_from: Start date in MM/DD/YYYY format
            date_to: End date in MM/DD/YYYY format
            labels_dir: Path to labels directory
            origin_code: TTB origin code (default: 22 for Kentucky)
            class_type_from: Start of product class/type range (default: 100)
            class_type_to: End of product class/type range (default: 150)
            
        Returns:
            Tuple of (list of new TTB IDs, total count from registry)
        """
        # Search registry
        registry_ids = self.search_ttb_registry(
            date_from, date_to, origin_code, class_type_from, class_type_to
        )
        
        # Get existing IDs
        existing_ids = self.get_existing_ttb_ids(labels_dir)
        
        # Find new IDs
        new_ids = [ttb_id for ttb_id in registry_ids if ttb_id not in existing_ids]
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Results:")
            print(f"  TTB IDs in registry: {len(registry_ids)}")
            print(f"  Already in labels/: {len(registry_ids) - len(new_ids)}")
            print(f"  New TTB IDs: {len(new_ids)}")
            print(f"{'='*60}")
        
        return new_ids, len(registry_ids)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Find new TTB COLA labels not yet in the labels directory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for labels from the past 7 days
  python3 .github/scripts/find_new_ttb_labels.py

  # Search for labels in a specific date range
  python3 .github/scripts/find_new_ttb_labels.py --from 2024-01-01 --to 2024-12-31
  
  # Search with verbose output
  python3 .github/scripts/find_new_ttb_labels.py --verbose
  
  # Save results to JSON file
  python3 .github/scripts/find_new_ttb_labels.py --output new_labels.json
        """
    )
    parser.add_argument(
        '--from',
        dest='date_from',
        help='Start date in YYYY-MM-DD format (default: 7 days ago)'
    )
    parser.add_argument(
        '--to',
        dest='date_to',
        help='End date in YYYY-MM-DD format (default: today)'
    )
    parser.add_argument(
        '--origin',
        default='22',
        help='TTB origin code (default: 22 for Kentucky)'
    )
    parser.add_argument(
        '--class-from',
        dest='class_from',
        default='100',
        help='Start of product class/type range (default: 100)'
    )
    parser.add_argument(
        '--class-to',
        dest='class_to',
        default='150',
        help='End of product class/type range (default: 150)'
    )
    parser.add_argument(
        '--labels-dir',
        default='labels',
        help='Path to labels directory (default: labels)'
    )
    parser.add_argument(
        '--output',
        help='Output file to save results (JSON format)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
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
    
    # Parse dates
    if args.date_to:
        try:
            end_date = datetime.strptime(args.date_to, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid end date format '{args.date_to}'. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        end_date = datetime.now()
    
    if args.date_from:
        try:
            start_date = datetime.strptime(args.date_from, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid start date format '{args.date_from}'. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        # Default to 7 days ago
        start_date = end_date - timedelta(days=7)
    
    # Convert to MM/DD/YYYY format for TTB API
    date_from = start_date.strftime('%m/%d/%Y')
    date_to = end_date.strftime('%m/%d/%Y')
    
    print("=" * 60)
    print("TTB COLA Registry - New Label Finder")
    print("=" * 60)
    print()
    
    # Find new labels
    finder = TTBLabelFinder(verbose=args.verbose)
    
    try:
        new_ids, total_registry_results = finder.find_new_labels(
            date_from=date_from,
            date_to=date_to,
            labels_dir=args.labels_dir,
            origin_code=args.origin,
            class_type_from=args.class_from,
            class_type_to=args.class_to
        )
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Display results
    print()
    if new_ids:
        print(f"Found {len(new_ids)} new TTB ID(s):")
        for ttb_id in new_ids:
            url = f"https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttb_id}"
            print(f"  - {ttb_id}: {url}")
        
        # Save to file if requested
        if args.output:
            output_data = {
                'search_date': datetime.now().isoformat(),
                'date_range': {
                    'from': args.date_from or start_date.strftime('%Y-%m-%d'),
                    'to': args.date_to or end_date.strftime('%Y-%m-%d')
                },
                'filters': {
                    'origin_code': args.origin,
                    'class_type_from': args.class_from,
                    'class_type_to': args.class_to
                },
                'new_ttb_ids': new_ids,
                'count': len(new_ids),
                'total_registry_results': total_registry_results
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\nResults saved to: {args.output}")
    else:
        print("No new TTB IDs found.")
        
        # Save to file even if no new labels (for workflow to read)
        if args.output:
            output_data = {
                'search_date': datetime.now().isoformat(),
                'date_range': {
                    'from': args.date_from or start_date.strftime('%Y-%m-%d'),
                    'to': args.date_to or end_date.strftime('%Y-%m-%d')
                },
                'filters': {
                    'origin_code': args.origin,
                    'class_type_from': args.class_from,
                    'class_type_to': args.class_to
                },
                'new_ttb_ids': [],
                'count': 0,
                'total_registry_results': total_registry_results
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
    
    print()


if __name__ == '__main__':
    main()

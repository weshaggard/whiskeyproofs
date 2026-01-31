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
    NEXT_PAGE_URL = "https://ttbonline.gov/colasonline/publicPageBasicCola.do?action=page&pgfcn=nextset"
    MAX_PAGES = 100  # Safety limit to prevent infinite loops
    
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
    
    def search_whiskey(self, name, year_from, year_to):
        """
        Search TTB COLA registry for a whiskey entry using HTTP POST.
        Automatically handles pagination to retrieve all results.
        
        Args:
            name: Product name (e.g., "Booker's", "Angel's Envy Cask Strength")
            year_from: Start year for search range
            year_to: End year for search range
            
        Returns:
            List of matching TTB IDs with their details, or empty list if none found
        """
        # Extract brand name for search
        brand = self._extract_brand_name(name)
        
        if self.verbose:
            print(f"  Searching: {name} (brand: {brand}), years: {year_from}-{year_to}")
        
        # Set date range
        date_from = f"01/01/{year_from}"
        date_to = f"12/31/{year_to}"
        
        # Prepare form data for POST request
        form_data = {
            'searchCriteria.dateCompletedFrom': date_from,
            'searchCriteria.dateCompletedTo': date_to,
            'searchCriteria.productOrFancifulName': brand,
            'searchCriteria.productNameSearchType': 'E',  # F = Fanciful Name, B = Brand Name, E = Either
            'searchCriteria.classTypeFrom': '',
            'searchCriteria.classTypeTo': '',
            'searchCriteria.originCode': ''
        }
        
        all_results = []
        
        try:
            # Make initial POST request
            response = self.session.post(self.SEARCH_URL, data=form_data, timeout=30, verify=False)
            response.raise_for_status()
            print(f"    date_from: {date_from}, date_to: {date_to}, brand: {brand}")
            
            # Parse first page results
            results, has_next = self._parse_search_results(response.text)
            all_results.extend(results)
            
            if self.verbose:
                print(f"    Page 1: Found {len(results)} potential match(es)")
            
            # Fetch additional pages if they exist
            page_num = 2
            while has_next and page_num <= self.MAX_PAGES:
                if self.verbose:
                    print(f"    Fetching page {page_num}...")
                
                page_results, has_next = self._fetch_next_page()
                all_results.extend(page_results)
                
                if self.verbose:
                    print(f"    Page {page_num}: Found {len(page_results)} potential match(es)")
                
                page_num += 1
                
                # Add a small delay between page requests to be respectful
                if has_next:
                    time.sleep(0.5)
            
            # Warn if we hit the limit and there are still more pages
            if has_next and page_num > self.MAX_PAGES:
                print(f"    WARNING: Reached maximum page limit ({self.MAX_PAGES}). There may be more results.")
            
            if self.verbose or page_num > 2:
                print(f"    Total: Found {len(all_results)} potential match(es) across {page_num - 1} page(s)")
            
            return all_results
            
        except Exception as e:
            if self.verbose:
                print(f"    Error during search: {e}")
            return []
    
    def _fetch_next_page(self):
        """
        Fetch the next page of search results.
        Uses the session to maintain state from the initial search.
        
        Returns:
            Tuple of (list of result dicts from this page, has_next_page boolean)
        """
        try:
            response = self.session.get(self.NEXT_PAGE_URL, timeout=30, verify=False)
            response.raise_for_status()
            return self._parse_search_results(response.text)
        except Exception as e:
            if self.verbose:
                print(f"    Error fetching next page: {e}")
            return [], False
    
    def _parse_search_results(self, html_content):
        """
        Parse the search results HTML to extract TTB IDs and metadata.
        Only returns unique TTB IDs (one per result row).
        Parses all table columns and maps them to header names.
        
        Returns:
            Tuple of (list of result dicts, has_next_page boolean)
        """
        results = []
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
                # Get all rows first to identify header and data rows
                all_rows = table.find_all('tr', recursive=False)
                if len(all_rows) < 2:  # Need at least header + 1 data row
                    continue
                
                # Try to find the header row (first row with th or first row)
                headers = []
                data_rows = []
                
                for idx, row in enumerate(all_rows):
                    cells = row.find_all(['th', 'td'], recursive=False)
                    if not cells:
                        continue
                    
                    # Check if this looks like a header row
                    has_th = row.find('th', recursive=False) is not None
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    
                    # If we haven't found headers yet and this looks like a header row
                    if not headers and (has_th or any(text in ['TTB ID', 'Permit No.', 'Serial Number', 'Completed Date', 
                                                                'Fanciful Name', 'Brand Name', 'Origin', 'Class/Type'] 
                                                       for text in cell_texts)):
                        headers = cell_texts
                    elif headers:
                        # This is a data row
                        data_rows.append(row)
                
                # Skip if no valid headers found
                if not headers or len(headers) == 0:
                    continue
                
                for row in data_rows:
                    # Look for the first link containing ttbid in this row
                    ttb_id = None
                    href = None
                    
                    links = row.find_all('a', href=True, recursive=False)
                    for link in links:
                        link_href = link.get('href', '')
                        if 'ttbid=' in link_href:
                            # Extract TTB ID from URL
                            match = re.search(r'ttbid=(\d+)', link_href)
                            if match:
                                ttb_id = match.group(1)
                                href = link_href
                                break  # Only use the first ttbid link per row
                    
                    # Also check nested links
                    if not ttb_id:
                        links = row.find_all('a', href=True)
                        for link in links:
                            link_href = link.get('href', '')
                            if 'ttbid=' in link_href:
                                match = re.search(r'ttbid=(\d+)', link_href)
                                if match:
                                    ttb_id = match.group(1)
                                    href = link_href
                                    break
                    
                    # If we found a TTB ID in this row and haven't seen it before
                    if ttb_id and ttb_id not in seen_ids:
                        seen_ids.add(ttb_id)
                        
                        # Parse all cells in the row (only direct children)
                        cells = row.find_all(['td', 'th'], recursive=False)
                        row_data = {}
                        
                        # Map cells to headers
                        for idx, cell in enumerate(cells):
                            if idx < len(headers):
                                header_name = headers[idx]
                                # Get only direct text from this cell, not nested elements
                                cell_value = cell.get_text(strip=True)
                                if cell_value:  # Only add non-empty values
                                    row_data[header_name] = cell_value
                        
                        # Get row text for context
                        row_text = row.get_text(strip=True, separator=' ')
                        
                        # Try to extract proof from row data or text
                        found_proof = None
                        proof_match = re.search(r'(\d+\.?\d*)\s*(?:proof|%)', row_text, re.IGNORECASE)
                        if proof_match:
                            found_proof = float(proof_match.group(1))
                        
                        # Try to extract year from row data or text
                        found_year = None
                        year_match = re.search(r'\b(20\d{2})\b', row_text)
                        if year_match:
                            found_year = int(year_match.group(1))
                        
                        if self.verbose:
                            print(f"      Found unique: TTB {ttb_id}, Proof: {found_proof}, Year: {found_year}")
                            print(f"        Data: {row_data}")
                        
                        # Create result with flattened fields
                        result = {
                            'ttb_id': ttb_id,
                            'text': row_text[:200],  # First 200 chars
                            'url': f"https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttb_id}",
                            'proof': found_proof,
                            'year': found_year
                        }
                        
                        # Flatten fields into result, avoiding duplicates
                        for field_name, field_value in row_data.items():
                            # Skip if this field value is already captured
                            if field_name == 'TTB ID' and field_value == ttb_id:
                                continue  # Already have ttb_id
                            # Add field with original name
                            result[field_name] = field_value
                        
                        results.append(result)
        
        except Exception as e:
            if self.verbose:
                print(f"    Error parsing results: {e}")
        
        return results, has_next
    
    def search_whiskey_with_chunking(self, name, year_from, year_to):
        """
        Search TTB with automatic 15-year chunking if needed.
        
        Args:
            name: Product name
            year_from: Start year
            year_to: End year
            
        Returns:
            List of all matching TTB IDs across all chunks
        """
        all_results = []
        year_span = year_to - year_from
        
        if year_span <= 15:
            # Single query
            ttb_results = self.search_whiskey(name, year_from, year_to)
            all_results.extend(ttb_results)
        else:
            # Multiple queries in 15-year chunks
            chunks = []
            current_start = year_from
            while current_start <= year_to:
                current_end = min(current_start + 15, year_to)
                chunks.append((current_start, current_end))
                current_start = current_end + 1
            
            if self.verbose:
                print(f"  Splitting into {len(chunks)} queries (15-year max):")
            
            for chunk_idx, (chunk_start, chunk_end) in enumerate(chunks, start=1):
                if self.verbose:
                    print(f"    Query {chunk_idx}/{len(chunks)}: {chunk_start}-{chunk_end}")
                ttb_results = self.search_whiskey(name, chunk_start, chunk_end)
                all_results.extend(ttb_results)
                
                # Rate limit between chunks (except last one)
                if chunk_idx < len(chunks):
                    time.sleep(2)
        
        return all_results
    
    def query_csv_entries(self, csv_file, test_mode=False, limit=None, filter_text=None):
        """
        Query TTB for all entries in CSV that don't have TTB IDs.
        Optimized to query once per unique name across all years.
        
        Args:
            csv_file: Path to whiskeyindex.csv
            test_mode: If True, only process first 10 entries
            limit: Maximum number of entries to process
            filter_text: Optional text to filter entries by Name (case-insensitive)
            
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
        
        # Apply text filter if provided
        if filter_text:
            filter_text_lower = filter_text.lower()
            entries_to_search = [
                (i, row) for i, row in entries_to_search
                if filter_text_lower in row['Name'].lower()
            ]
            print(f"Found {len(entries_to_search)} entries without TTB IDs matching '{filter_text}'")
        else:
            print(f"Found {len(entries_to_search)} entries without TTB IDs")
        
        if test_mode:
            entries_to_search = entries_to_search[:10]
            print(f"Test mode: Processing only first {len(entries_to_search)} entries")
        elif limit:
            entries_to_search = entries_to_search[:limit]
            print(f"Limit set: Processing only first {len(entries_to_search)} entries")
        
        # Group entries by Name and determine date ranges
        name_groups = {}
        for i, row in entries_to_search:
            name = row['Name']
            if name not in name_groups:
                name_groups[name] = {
                    'entries': [],
                    'min_year': float('inf'),
                    'max_year': 0
                }
            
            name_groups[name]['entries'].append((i, row))
            try:
                year = int(row['ReleaseYear'])
                name_groups[name]['min_year'] = min(name_groups[name]['min_year'], year)
                name_groups[name]['max_year'] = max(name_groups[name]['max_year'], year)
            except (ValueError, KeyError):
                pass
        
        print(f"\nGrouped into {len(name_groups)} unique product names")
        print(f"This will require {len(name_groups)} queries instead of {len(entries_to_search)}\n")
        
        # Query once per unique name (split into 15-year chunks if needed)
        ttb_cache = {}
        for idx, (name, group_info) in enumerate(name_groups.items(), start=1):
            year_from = group_info['min_year'] - 1  # One year before earliest
            year_to = group_info['max_year']
            entry_count = len(group_info['entries'])
            
            print(f"\n[{idx}/{len(name_groups)}] {name}")
            print(f"  Entries: {entry_count}, Year range: {year_from}-{year_to}")
            
            # Use chunking method
            year_span = year_to - year_from
            if year_span > 15:
                print(f"  Splitting into multiple queries (15-year max)")
            
            all_results = self.search_whiskey_with_chunking(name, year_from, year_to)
            ttb_cache[name] = all_results
            
            if all_results:
                print(f"  ✓ Found {len(all_results)} total TTB entries")
            else:
                print(f"  ✗ No matches found")
            
            # Rate limiting - be respectful to the TTB server
            time.sleep(2)
        
        print("\n" + "=" * 60)
        print("Matching TTB results to entries...")
        print("=" * 60)
        
        # Match results to individual entries
        for name, group_info in name_groups.items():
            ttb_results = ttb_cache.get(name, [])
            
            if not ttb_results:
                continue
            
            for i, row in group_info['entries']:
                try:
                    target_proof = float(row['Proof'])
                    target_year = int(row['ReleaseYear'])
                except (ValueError, KeyError):
                    continue
                
                # Find matching TTB entries (by proof and year)
                matches = []
                for ttb_result in ttb_results:
                    proof_match = False
                    year_match = False
                    
                    # Check proof (within ±1.0)
                    if ttb_result.get('proof'):
                        proof_match = abs(ttb_result['proof'] - target_proof) <= 1.0
                    
                    # Check year (allow exact match or one year before release)
                    if ttb_result.get('year'):
                        year_match = ttb_result['year'] == target_year or ttb_result['year'] == target_year - 1
                    
                    # Add if either proof or year matches (prefer both)
                    if proof_match or year_match:
                        match_quality = (2 if proof_match and year_match 
                                       else 1.5 if proof_match 
                                       else 1)
                        matches.append({
                            **ttb_result,
                            'match_quality': match_quality,
                            'proof_matches': proof_match,
                            'year_matches': year_match
                        })
                
                if matches:
                    # Sort by match quality (best matches first)
                    matches.sort(key=lambda x: x['match_quality'], reverse=True)
                    results[i] = matches
        
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
    parser.add_argument(
        '--filter',
        help='Filter entries by name (case-insensitive substring match)'
    )
    parser.add_argument(
        '--name',
        help='Product name to search (standalone mode, does not use CSV)'
    )
    parser.add_argument(
        '--year-from',
        type=int,
        help='Start year for search (use with --name)'
    )
    parser.add_argument(
        '--year-to',
        type=int,
        help='End year for search (use with --name)'
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
    
    querier = TTBQuerier(verbose=args.verbose)
    
    # Check if standalone mode (--name specified)
    if args.name:
        if not args.year_from or not args.year_to:
            print("ERROR: --year-from and --year-to are required when using --name")
            sys.exit(1)
        
        print("Standalone Query Mode")
        print(f"Product: {args.name}")
        print(f"Year Range: {args.year_from}-{args.year_to}")
        print()
        print("Querying TTB website using HTTP POST...")
        print()
        
        try:
            year_span = args.year_to - args.year_from
            if year_span > 15:
                print(f"Splitting into multiple queries (15-year max)\n")
            
            all_results = querier.search_whiskey_with_chunking(args.name, args.year_from, args.year_to)
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
        print("Results")
        print("=" * 60)
        print(f"Found {len(all_results)} TTB entries")
        print()
        
        if all_results:
            for idx, result in enumerate(all_results, start=1):
                print(f"{idx}. TTB Entry:")
                for field_name, field_value in result.items():
                    if field_value is not None and field_value != '':  # Only show non-empty values
                        print(f"   {field_name}: {field_value}")
                print()
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(all_results, f, indent=2)
                print(f"Results saved to: {args.output}")
        else:
            print("No results found.")
        
        return
    
    # CSV mode
    print("Querying TTB website using HTTP POST...")
    print()
    
    try:
        results = querier.query_csv_entries(
            args.csv,
            test_mode=args.test,
            limit=args.limit,
            filter_text=args.filter
        )
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Read CSV data for displaying matched entries
    try:
        with open(args.csv, 'r') as f:
            reader = csv.DictReader(f)
            csv_rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV for display: {e}")
        csv_rows = []
    
    print()
    print("=" * 60)
    print("Results Summary")
    print("=" * 60)
    print(f"Total entries searched: {len(results) if results else 0}")
    print(f"Entries with matches found: {len(results)}")
    
    if results:
        print("\nMatched entries:")
        for line_num, ttb_results in results.items():
            # Get the CSV row data (line_num is 2-indexed, so subtract 2 for 0-indexed list)
            row_index = line_num - 2
            if 0 <= row_index < len(csv_rows):
                csv_entry = csv_rows[row_index]
                print(f"\n  Line {line_num}: {csv_entry['Name']} - {csv_entry['Batch']} ({csv_entry['ReleaseYear']}) - {csv_entry['Proof']} proof")
                print(f"  Found {len(ttb_results)} potential match(es):")
            else:
                print(f"\n  Line {line_num}: {len(ttb_results)} potential match(es)")
            
            for result in ttb_results:
                print(f"    TTB Match:")
                for field_name, field_value in result.items():
                    if field_value is not None and field_value != '':  # Only show non-empty values
                        print(f"      {field_name}: {field_value}")
                print()
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")
    else:
        print("\nNo matches found.")


if __name__ == '__main__':
    main()

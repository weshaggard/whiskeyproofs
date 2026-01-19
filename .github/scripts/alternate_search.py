#!/usr/bin/env python3
"""
Search TTB COLA registry using alternate product names.
"""

import csv
import re
import time
import requests
from urllib.parse import urlencode
import urllib3
from bs4 import BeautifulSoup

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Alternate search names for products
ALTERNATE_NAMES = {
    'Larceny Barrel Proof': 'Larceny',
    'Thomas H. Handy': 'Thomas Handy',
    'Sazerac 18 Year': 'Sazerac',
    'Wild Turkey Master\'s Keep': 'Wild Turkey Master\'s Keep',
    'Old Forester Birthday Bourbon': 'Old Forester Birthday',
    'Parker\'s Heritage Collection': 'Parker\'s Heritage',
    'E.H. Taylor Barrel Proof': 'E.H. Taylor',
    'Old Fitzgerald BiB': 'Old Fitzgerald',
    'Michter\'s 20 Year': 'Michter\'s',
    'Michter\'s 25 Year': 'Michter\'s',
    'Michter\'s Celebration': 'Michter\'s',
}

def search_ttb(product_name, year_from=2015, year_to=2025):
    """Search TTB COLA registry for a product.
    
    Note: TTB limits date ranges to 15 years max.
    """
    base_url = 'https://www.ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search'
    
    # Ensure date range is within 15 years
    if year_to - year_from > 15:
        year_from = year_to - 15
    
    params = {
        'searchCriteria.productOrFancifulName': product_name,
        'searchCriteria.productNameSearchType': 'B',  # B=Begins with
        'searchCriteria.dateCompletedFrom': f'01/01/{year_from}',
        'searchCriteria.dateCompletedTo': f'12/31/{year_to}',
        'searchCriteria.classTypeFrom': '',
        'searchCriteria.classTypeTo': '',
        'searchCriteria.originCode': ''
    }
    
    try:
        response = requests.post(base_url, data=params, verify=False, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error searching for {product_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_ttb_ids(html_content):
    """Extract TTB IDs and approval dates from search results."""
    
    results = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all tables and look for TTB IDs in links
    tables = soup.find_all('table')
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Look for TTB ID in first cell link
                link = cells[0].find('a')
                if link and 'ttbid=' in str(link.get('href', '')):
                    ttb_id_match = re.search(r'ttbid=(\d+)', link.get('href'))
                    if ttb_id_match:
                        ttb_id = ttb_id_match.group(1)
                        row_text = row.get_text(strip=True)
                        
                        # Filter out navigation rows - actual results have DSP codes
                        if 'DSP-' in row_text or 'BR-' in row_text:
                            # Extract details from row
                            details = {
                                'ttb_id': ttb_id,
                                'row_text': row_text[:200]
                            }
                            
                            # Try to extract year from TTB ID (first 2 digits)
                            year_prefix = ttb_id[:2]
                            details['year'] = f"20{year_prefix}"
                            
                            # Check if it's barrel proof
                            details['is_barrel_proof'] = 'BARREL PROOF' in row_text.upper()
                            
                            results.append(details)
    
    # Remove duplicates
    seen = set()
    unique_results = []
    for r in results:
        if r['ttb_id'] not in seen:
            seen.add(r['ttb_id'])
            unique_results.append(r)
    
    return unique_results

def load_csv():
    """Load the whiskey index CSV."""
    csv_path = '/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv'
    entries = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    
    return entries

def save_csv(entries):
    """Save the whiskey index CSV."""
    csv_path = '/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv'
    
    if not entries:
        return
    
    fieldnames = entries[0].keys()
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)

def main():
    print("Loading CSV...")
    entries = load_csv()
    
    # Group entries by product name
    by_product = {}
    for entry in entries:
        name = entry['Name']
        if name not in by_product:
            by_product[name] = []
        by_product[name].append(entry)
    
    # Process products with alternate names
    total_found = 0
    
    for product_name, alt_name in ALTERNATE_NAMES.items():
        if product_name not in by_product:
            print(f"Product not found: {product_name}")
            continue
        
        product_entries = by_product[product_name]
        
        # Count how many already have TTB IDs
        existing = sum(1 for e in product_entries if e.get('TTB_ID', '').strip())
        print(f"\n{product_name}: {len(product_entries)} entries, {existing} already have TTB IDs")
        
        if existing == len(product_entries):
            print(f"  Skipping - all entries already have TTB IDs")
            continue
        
        # Search TTB registry
        print(f"  Searching TTB with: '{alt_name}'...")
        html = search_ttb(alt_name, year_from=2015, year_to=2025)
        
        if not html:
            print(f"  No results - search_ttb returned None/empty")
            continue
        
        print(f"  HTML length: {len(html)} bytes")
        
        # Extract TTB IDs
        results = extract_ttb_ids(html)
        print(f"  Found {len(results)} TTB approvals")
        
        if not results:
            continue
        
        # Match results to entries by year and batch details
        # Group entries by year
        by_year = {}
        for entry in product_entries:
            year = entry['ReleaseYear']
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(entry)
        
        # Match by year and barrel proof designation
        for result in results:
            ttb_id = result['ttb_id']
            result_year = result.get('year', '')
            is_bp = result.get('is_barrel_proof', False)
            
            # Find matching entries for this year
            year_entries = by_year.get(result_year, [])
            
            # Filter by barrel proof designation if applicable
            if product_name == 'Larceny Barrel Proof' and is_bp:
                # Match to Larceny Barrel Proof entries
                for entry in year_entries:
                    if not entry.get('TTB_ID', '').strip():
                        entry['TTB_ID'] = ttb_id
                        total_found += 1
                        print(f"    Assigned {ttb_id} to {entry['Name']} {entry['Batch']} ({entry['ReleaseYear']})")
                        break
            else:
                # Generic matching - assign to first entry without TTB ID
                for entry in product_entries:
                    if not entry.get('TTB_ID', '').strip():
                        entry['TTB_ID'] = ttb_id
                        total_found += 1
                        print(f"    Assigned {ttb_id} to {entry['Name']} {entry['Batch']} ({entry['ReleaseYear']})")
                        break
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\n\nTotal new TTB IDs found: {total_found}")
    
    if total_found > 0:
        print("Saving CSV...")
        save_csv(entries)
        print("Done!")
    else:
        print("No new IDs found - CSV not modified")

if __name__ == '__main__':
    main()

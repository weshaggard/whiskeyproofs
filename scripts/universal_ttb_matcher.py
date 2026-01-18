#!/usr/bin/env python3
"""
Universal TTB ID matcher - works for any product
Matches based on year and chronological order
"""

import csv
import sys
import requests
import urllib3
from bs4 import BeautifulSoup
import re
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SEARCH_URL = "https://www.ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search"

def search_and_match_product(product_name, search_name=None):
    """Match product entries based on year and approval date."""
    
    if search_name is None:
        search_name = product_name
    
    print("\n" + "="*70)
    print(f"{product_name.upper()} TTB ID MATCHING")
    print("="*70)
    
    # Load CSV
    csv.field_size_limit(sys.maxsize)
    with open('_data/whiskeyindex.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        fieldnames = reader.fieldnames
        
    entries = [r for r in all_rows if r['Name'] == product_name and not r.get('TTB_ID', '').strip()]
    
    if not entries:
        print(f"✓ All {product_name} entries already have TTB IDs")
        return 0
    
    print(f"📊 Found {len(entries)} {product_name} entries needing TTB IDs")
    
    # Group by year
    by_year = {}
    for entry in entries:
        year = int(entry['ReleaseYear'])
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(entry)
    
    print(f"📅 Years: {sorted(by_year.keys())}")
    
    # Search TTB for each year
    matches = {}
    
    for year in sorted(by_year.keys()):
        year_entries = by_year[year]
        print(f"\n🔍 Searching for {year} ({len(year_entries)} releases)...")
        
        params = {
            'searchCriteria.productOrFancifulName': search_name,
            'searchCriteria.productNameSearchType': 'B',
            'searchCriteria.dateCompletedFrom': f'01/01/{year}',
            'searchCriteria.dateCompletedTo': f'12/31/{year}',
        }
        
        response = requests.post(SEARCH_URL, data=params, verify=False, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract TTB IDs and dates
        ttb_results = []
        for table in soup.find_all('table'):
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    link = cells[0].find('a')
                    if link and 'ttbid=' in str(link.get('href', '')):
                        ttb_id_match = re.search(r'ttbid=(\d+)', link.get('href'))
                        if ttb_id_match:
                            ttb_id = ttb_id_match.group(1)
                            date_str = cells[3].get_text(strip=True)
                            
                            # Only add unique TTB IDs
                            if ttb_id not in [r['ttb_id'] for r in ttb_results]:
                                try:
                                    ttb_results.append({
                                        'ttb_id': ttb_id,
                                        'date': date_str,
                                        'date_obj': datetime.strptime(date_str, '%m/%d/%Y')
                                    })
                                except:
                                    pass
        
        print(f"  Found {len(ttb_results)} TTB approvals")
        
        # Sort entries by batch
        year_entries_sorted = sorted(year_entries, key=lambda e: e['Batch'])
        
        # Sort TTB results by date
        ttb_sorted = sorted(ttb_results, key=lambda r: r['date_obj'])
        
        # Match based on count and order
        if len(year_entries_sorted) == len(ttb_sorted):
            print(f"  ✓ Perfect match: {len(year_entries_sorted)} releases = {len(ttb_sorted)} approvals")
            for entry, ttb in zip(year_entries_sorted, ttb_sorted):
                key = (entry['Name'], entry['Batch'], entry['ReleaseYear'])
                matches[key] = ttb['ttb_id']
                print(f"    {entry['Batch']} → TTB ID {ttb['ttb_id']} ({ttb['date']})")
        elif len(ttb_sorted) > 0:
            print(f"  ⚠ Mismatch: {len(year_entries_sorted)} releases but {len(ttb_sorted)} approvals")
            
            if len(ttb_sorted) == 1:
                # Single approval for all releases
                ttb_id = ttb_sorted[0]['ttb_id']
                for entry in year_entries_sorted:
                    key = (entry['Name'], entry['Batch'], entry['ReleaseYear'])
                    matches[key] = ttb_id
                    print(f"    {entry['Batch']} → TTB ID {ttb_id} (shared)")
            else:
                # Distribute approvals
                for i, entry in enumerate(year_entries_sorted):
                    ttb_idx = min(i, len(ttb_sorted) - 1)
                    ttb = ttb_sorted[ttb_idx]
                    key = (entry['Name'], entry['Batch'], entry['ReleaseYear'])
                    matches[key] = ttb['ttb_id']
                    print(f"    {entry['Batch']} → TTB ID {ttb['ttb_id']} ({ttb['date']})")
        else:
            print(f"  ✗ No approvals found for {year}")
    
    print(f"\n📊 Total matched: {len(matches)}/{len(entries)}")
    
    # Update CSV
    if matches:
        print(f"\n💾 Updating CSV...")
        updated_count = 0
        for row in all_rows:
            key = (row['Name'], row['Batch'], row['ReleaseYear'])
            if key in matches:
                row['TTB_ID'] = matches[key]
                updated_count += 1
        
        with open('_data/whiskeyindex.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        
        print(f"✅ Updated {updated_count} {product_name} entries!")
        return updated_count
    
    return 0

def main():
    """Process multiple products."""
    products = [
        ("Elijah Craig Barrel Proof (ECBP)", "Elijah Craig"),
        ("George T. Stagg (GTS)", "George T. Stagg"),
        ("William Larue Weller (WLW)", "William Larue Weller"),
        ("Thomas H. Handy", "Thomas H. Handy"),
        ("Stagg Jr", "Stagg Jr"),
        ("Stagg", "Stagg"),
    ]
    
    total_updated = 0
    
    for product_name, search_name in products:
        try:
            updated = search_and_match_product(product_name, search_name)
            total_updated += updated
            
            if updated > 0:
                import time
                time.sleep(2)  # Be nice to the server
        except Exception as e:
            print(f"❌ Error processing {product_name}: {e}")
            continue
    
    print(f"\n" + "="*70)
    print(f"✅ TOTAL ENTRIES UPDATED: {total_updated}")
    print(f"="*70)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Single product mode
        product_name = sys.argv[1]
        search_name = sys.argv[2] if len(sys.argv) > 2 else None
        search_and_match_product(product_name, search_name)
    else:
        # Batch mode
        main()

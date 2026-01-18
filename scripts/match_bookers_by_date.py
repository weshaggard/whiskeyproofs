#!/usr/bin/env python3
"""
Simple TTB ID matcher based on year and date proximity
For products like Booker's where proof isn't easily extractable
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

def search_and_match_bookers():
    """Match Booker's entries based on year and approval date."""
    
    print("\n" + "="*70)
    print("BOOKER'S TTB ID MATCHING (BY DATE)")
    print("="*70)
    
    # Load CSV
    csv.field_size_limit(sys.maxsize)
    with open('_data/whiskeyindex.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)
        fieldnames = reader.fieldnames
        
    bookers = [r for r in all_rows if r['Name'] == "Booker's" and not r.get('TTB_ID', '').strip()]
    
    print(f"📊 Found {len(bookers)} Booker's entries needing TTB IDs")
    
    # Group by year
    by_year = {}
    for entry in bookers:
        year = int(entry['ReleaseYear'])
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(entry)
    
    print(f"📅 Years: {sorted(by_year.keys())}")
    
    # Search TTB for each year
    matches = {}
    
    for year in sorted(by_year.keys()):
        entries = by_year[year]
        print(f"\n🔍 Searching for {year} ({len(entries)} batches)...")
        
        params = {
            'searchCriteria.productOrFancifulName': "Booker's",
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
                                ttb_results.append({
                                    'ttb_id': ttb_id,
                                    'date': date_str,
                                })
        
        print(f"  Found {len(ttb_results)} TTB approvals")
        
        # Sort entries by batch number/name
        entries_sorted = sorted(entries, key=lambda e: e['Batch'])
        
        # Sort TTB results by date
        ttb_sorted = sorted(ttb_results, key=lambda r: datetime.strptime(r['date'], '%m/%d/%Y'))
        
        # Match: if we have 4 batches and 4 approvals, match them in order
        if len(entries_sorted) == len(ttb_sorted):
            print(f"  ✓ Perfect match: {len(entries_sorted)} batches = {len(ttb_sorted)} approvals")
            for entry, ttb in zip(entries_sorted, ttb_sorted):
                key = (entry['Name'], entry['Batch'], entry['ReleaseYear'])
                matches[key] = ttb['ttb_id']
                print(f"    {entry['Batch']} → TTB ID {ttb['ttb_id']} ({ttb['date']})")
        elif len(ttb_sorted) > 0:
            # If counts don't match, try to match best we can
            print(f"  ⚠ Mismatch: {len(entries_sorted)} batches but {len(ttb_sorted)} approvals")
            
            # Use first approval for all if only one
            if len(ttb_sorted) == 1:
                ttb_id = ttb_sorted[0]['ttb_id']
                for entry in entries_sorted:
                    key = (entry['Name'], entry['Batch'], entry['ReleaseYear'])
                    matches[key] = ttb_id
                    print(f"    {entry['Batch']} → TTB ID {ttb_id} (shared)")
            else:
                # Distribute approvals across batches
                for i, entry in enumerate(entries_sorted):
                    ttb_idx = min(i, len(ttb_sorted) - 1)
                    ttb = ttb_sorted[ttb_idx]
                    key = (entry['Name'], entry['Batch'], entry['ReleaseYear'])
                    matches[key] = ttb['ttb_id']
                    print(f"    {entry['Batch']} → TTB ID {ttb['ttb_id']} ({ttb['date']})")
        else:
            print(f"  ✗ No approvals found for {year}")
    
    print(f"\n📊 Total matched: {len(matches)}/{len(bookers)}")
    
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
        
        print(f"✅ Updated {updated_count} Booker's entries!")
        return updated_count
    
    return 0

if __name__ == '__main__':
    search_and_match_bookers()

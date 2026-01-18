#!/usr/bin/env python3
"""
Search TTB COLA for Birthday Bourbon and update Old Forester Birthday Bourbon entries.
"""

import requests
import csv
import re
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www.ttbonline.gov/colasonline/"
SEARCH_URL = BASE_URL + "publicSearchColasBasicProcess.do?action=search"

def search_ttb(search_term, start_date, end_date):
    """Search TTB COLA registry."""
    params = {
        'searchCriteria.productOrFancifulName': search_term,
        'searchCriteria.productNameSearchType': 'F',  # F=Full text search
        'searchCriteria.dateCompletedFrom': start_date,
        'searchCriteria.dateCompletedTo': end_date,
    }
    
    print(f"Searching TTB for '{search_term}' ({start_date} to {end_date})...")
    
    try:
        response = requests.post(SEARCH_URL, data=params, verify=False, timeout=30, allow_redirects=True)
        
        if response.status_code != 200:
            print(f"  HTTP error: {response.status_code}")
            return []
        
        # Parse results
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Find all TTB ID links
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    link = cells[0].find('a')
                    if link and 'ttbid=' in str(link.get('href', '')):
                        ttb_id_match = re.search(r'ttbid=(\d+)', link.get('href'))
                        if ttb_id_match:
                            ttb_id = ttb_id_match.group(1)
                            
                            # Get approval date from cells
                            approval_date = None
                            for cell in cells:
                                text = cell.get_text(strip=True)
                                date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
                                if date_match:
                                    approval_date = date_match.group(1)
                                    break
                            
                            results.append({
                                'ttb_id': ttb_id,
                                'approval_date': approval_date,
                                'row_text': row.get_text(' ', strip=True)[:150]
                            })
        
        print(f"  Found {len(results)} results")
        return results
    
    except Exception as e:
        print(f"  Error: {e}")
        return []

def main():
    csv_file = '/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv'
    
    # Read CSV
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find Old Forester Birthday Bourbon entries without TTB IDs
    ofbb_entries = [row for row in rows if row['Name'] == 'Old Forester Birthday Bourbon' and not row['TTB_ID']]
    
    print(f"Found {len(ofbb_entries)} Old Forester Birthday Bourbon entries without TTB IDs\n")
    
    # Search TTB with "Birthday Bourbon" as user requested
    all_results = []
    
    # Search in date ranges (TTB has limits)
    date_ranges = [
        ('01/01/2002', '12/31/2010'),
        ('01/01/2011', '12/31/2020'),
        ('01/01/2021', '12/31/2025'),
    ]
    
    for start, end in date_ranges:
        results = search_ttb("Birthday Bourbon", start, end)
        all_results.extend(results)
    
    print(f"\nTotal results found: {len(all_results)}\n")
    
    # Group by year
    by_year = {}
    for result in all_results:
        if result['approval_date']:
            year = int(result['approval_date'].split('/')[-1])
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(result)
    
    # Show what we found
    if by_year:
        print("Approvals by year:")
        for year in sorted(by_year.keys()):
            print(f"  {year}: {len(by_year[year])} approval(s)")
            for r in by_year[year]:
                print(f"    {r['ttb_id']} - approved {r['approval_date']}")
                print(f"      {r['row_text']}")
    else:
        print("No results found. Trying alternate search terms...\n")
        
        # Try other search terms
        alt_terms = ["Old Forester Birthday", "OFBB", "Birthday"]
        for term in alt_terms:
            results = search_ttb(term, '01/01/2020', '12/31/2025')
            if results:
                print(f"\n'{term}' found {len(results)} results!")
                for r in results[:5]:
                    print(f"  {r['ttb_id']} - {r['row_text']}")
                break
    
    # Match and update
    updates = 0
    for row in rows:
        if row['Name'] == 'Old Forester Birthday Bourbon' and not row['TTB_ID']:
            year = int(row['ReleaseYear']) if row['ReleaseYear'] else None
            if year and year in by_year and by_year[year]:
                # Use first approval for that year
                ttb_id = by_year[year][0]['ttb_id']
                row['TTB_ID'] = ttb_id
                updates += 1
                print(f"\nUpdated: {row['Batch']} ({row['ReleaseYear']}) -> {ttb_id}")
    
    if updates > 0:
        # Write CSV
        print(f"\n Writing {updates} updates to CSV...")
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print("Done!")
    else:
        print("\nNo updates to make.")
    
    # Final summary
    total_ofbb = len([r for r in rows if r['Name'] == 'Old Forester Birthday Bourbon'])
    with_ttb = len([r for r in rows if r['Name'] == 'Old Forester Birthday Bourbon' and r['TTB_ID']])
    print(f"\nOld Forester Birthday Bourbon: {with_ttb}/{total_ofbb} ({100*with_ttb/total_ofbb:.1f}%)")

if __name__ == '__main__':
    main()

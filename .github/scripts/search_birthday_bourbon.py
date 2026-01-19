#!/usr/bin/env python3
"""Search TTB COLA registry for Birthday Bourbon and update Old Forester Birthday Bourbon entries."""

import csv
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

# Disable SSL warnings for the proxy
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search_ttb(brand_name, start_year, end_year):
    """Search TTB COLA registry for a brand within a date range."""
    url = "https://www.ttbonline.gov/colasonline/publicSearchColasBasicProcess.do"
    
    # Convert years to dates
    start_date = f"01/01/{start_year}"
    end_date = f"12/31/{end_year}"
    
    data = {
        'action': 'search',
        'brand': brand_name,
        'approvalDateFrom': start_date,
        'approvalDateTo': end_date,
        'ttbid': '',
        'serialNum': '',
        'issued': '',
        'fancifulName': '',
        'type': '',
        'class': '',
        'origin': ''
    }
    
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error searching TTB: {e}")
        return None

def parse_ttb_results(html):
    """Parse TTB search results to extract TTB IDs and approval dates."""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # Find all result rows
    rows = soup.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:
            # Extract TTB ID (usually in a link)
            ttb_link = row.find('a', href=re.compile(r'ttbid='))
            if ttb_link:
                href = ttb_link.get('href', '')
                match = re.search(r'ttbid=(\d+)', href)
                if match:
                    ttb_id = match.group(1)
                    
                    # Try to extract approval date from cells
                    approval_date = None
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        # Look for date pattern MM/DD/YYYY
                        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
                        if date_match:
                            approval_date = date_match.group(1)
                            break
                    
                    results.append({
                        'ttb_id': ttb_id,
                        'approval_date': approval_date
                    })
    
    return results

def get_year_from_date(date_str):
    """Extract year from MM/DD/YYYY date string."""
    if not date_str:
        return None
    try:
        return int(date_str.split('/')[-1])
    except:
        return None

def main():
    csv_file = '/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv'
    
    # Read CSV
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Find Old Forester Birthday Bourbon entries
    ofbb_entries = [row for row in rows if row['Name'] == 'Old Forester Birthday Bourbon']
    
    print(f"Found {len(ofbb_entries)} Old Forester Birthday Bourbon entries")
    print(f"Release years: {sorted(set(row['ReleaseYear'] for row in ofbb_entries))}")
    
    # Search TTB registry for "Birthday Bourbon"
    print("\nSearching TTB registry for 'Birthday Bourbon'...")
    
    # Search in chunks (TTB has a 15-year limit)
    all_results = []
    year_ranges = [
        (2002, 2010),
        (2011, 2020),
        (2021, 2025)
    ]
    
    for start_year, end_year in year_ranges:
        print(f"Searching {start_year}-{end_year}...")
        html = search_ttb("Birthday Bourbon", start_year, end_year)
        if html:
            results = parse_ttb_results(html)
            print(f"  Found {len(results)} approvals")
            all_results.extend(results)
    
    print(f"\nTotal TTB approvals found: {len(all_results)}")
    
    # Group results by year
    results_by_year = {}
    for result in all_results:
        year = get_year_from_date(result['approval_date'])
        if year:
            if year not in results_by_year:
                results_by_year[year] = []
            results_by_year[year].append(result)
    
    print("\nApprovals by year:")
    for year in sorted(results_by_year.keys()):
        print(f"  {year}: {len(results_by_year[year])} approval(s)")
        for result in results_by_year[year]:
            print(f"    TTB ID: {result['ttb_id']} (approved {result['approval_date']})")
    
    # Match to entries
    updates = 0
    for row in rows:
        if row['Name'] == 'Old Forester Birthday Bourbon' and not row['TTB_ID']:
            year = int(row['ReleaseYear']) if row['ReleaseYear'] else None
            if year and year in results_by_year:
                # Use the first approval for that year
                # (for years with multiple batches, we'll use chronological order)
                if results_by_year[year]:
                    ttb_id = results_by_year[year][0]['ttb_id']
                    row['TTB_ID'] = ttb_id
                    updates += 1
                    print(f"\nUpdated: {row['Name']} {row['Batch']} ({row['ReleaseYear']})")
                    print(f"  TTB ID: {ttb_id}")
    
    if updates > 0:
        # Write updated CSV
        print(f"\nWriting {updates} updates to CSV...")
        fieldnames = rows[0].keys()
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print("CSV updated successfully!")
    else:
        print("\nNo updates to make.")
    
    # Summary
    ofbb_with_ttb = sum(1 for row in rows if row['Name'] == 'Old Forester Birthday Bourbon' and row['TTB_ID'])
    ofbb_total = len([row for row in rows if row['Name'] == 'Old Forester Birthday Bourbon'])
    print(f"\nOld Forester Birthday Bourbon coverage: {ofbb_with_ttb}/{ofbb_total} ({100*ofbb_with_ttb/ofbb_total:.1f}%)")

if __name__ == '__main__':
    main()

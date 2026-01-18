#!/usr/bin/env python3
"""
Automated TTB COLA Registry Search

Searches the TTB COLA public registry and extracts TTB IDs for whiskey entries.
Now working with firewall disabled!
"""

import requests
import csv
import re
import sys
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from datetime import datetime

# Disable SSL warnings since we're using verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://www.ttbonline.gov/colasonline/"
SEARCH_URL = BASE_URL + "publicSearchColasBasicProcess.do?action=search"

def search_ttb_cola(brand_name, start_date="01/01/2020", end_date=None):
    """
    Search TTB COLA registry for a brand
    
    Args:
        brand_name: Brand name to search for (e.g., "Jack Daniel's")
        start_date: Start date in MM/DD/YYYY format
        end_date: End date in MM/DD/YYYY format (defaults to today)
    
    Returns:
        List of dicts with TTB ID, proof, brand, etc.
    """
    if end_date is None:
        end_date = datetime.now().strftime("%m/%d/%Y")
    
    # Prepare search parameters (matching the actual form fields)
    params = {
        'searchCriteria.productOrFancifulName': brand_name,
        'searchCriteria.productNameSearchType': 'B',  # B=Begins with, F=Full text, E=Exact
        'searchCriteria.dateCompletedFrom': start_date,
        'searchCriteria.dateCompletedTo': end_date,
        'searchCriteria.classTypeFrom': '',
        'searchCriteria.classTypeTo': '',
        'searchCriteria.originCode': ''
    }
    
    print(f"Searching TTB for: {brand_name} ({start_date} to {end_date})")
    
    try:
        # Submit search
        response = requests.post(
            SEARCH_URL,
            data=params,
            verify=False,  # Skip SSL verification
            timeout=30,
            allow_redirects=True
        )
        
        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return []
        
        # Parse HTML results
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find results table
        results = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 5:
                    # Extract TTB ID from link
                    link = cells[0].find('a')
                    if link and 'ttbid=' in str(link.get('href', '')):
                        ttb_id_match = re.search(r'ttbid=(\d+)', link.get('href'))
                        if ttb_id_match:
                            ttb_id = ttb_id_match.group(1)
                            
                            # Extract other fields
                            brand = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                            serial = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                            
                            # Look for proof in the row
                            row_text = row.get_text()
                            proof_match = re.search(r'(\d+\.?\d*)\s*(?:proof|%)', row_text, re.IGNORECASE)
                            proof = proof_match.group(1) if proof_match else ''
                            
                            results.append({
                                'ttb_id': ttb_id,
                                'brand': brand,
                                'serial': serial,
                                'proof': proof,
                                'row_text': row_text[:200]  # First 200 chars for debugging
                            })
        
        print(f"Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"Error searching TTB: {e}")
        import traceback
        traceback.print_exc()
        return []

def load_csv_entries(csv_path):
    """Load whiskey entries from CSV"""
    entries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    return entries

def find_jack_daniels_entries(csv_path):
    """Find all Jack Daniel's entries needing TTB IDs"""
    entries = load_csv_entries(csv_path)
    jd_entries = []
    
    for entry in entries:
        if "Jack Daniel" in entry.get('Name', ''):
            if not entry.get('TTB_ID', '').strip():
                jd_entries.append(entry)
    
    return jd_entries

def main():
    csv_path = '/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv'
    
    print("=" * 80)
    print("TTB COLA Automated Search - Jack Daniel's")
    print("=" * 80)
    print()
    
    # Find Jack Daniel's entries
    jd_entries = find_jack_daniels_entries(csv_path)
    print(f"Found {len(jd_entries)} Jack Daniel's entries without TTB IDs:")
    print()
    
    for i, entry in enumerate(jd_entries, 1):
        print(f"{i}. {entry['Name']} - {entry['Batch']} ({entry['ReleaseYear']}) - {entry['Proof']} proof")
    
    print()
    print("Searching TTB COLA registry...")
    print()
    
    # Search for Jack Daniel's (broader search)
    results = search_ttb_cola("Jack Daniel", start_date="01/01/2020")
    
    if results:
        print(f"\nFound {len(results)} TTB COLA entries:")
        for result in results[:20]:  # Show first 20
            print(f"  TTB ID: {result['ttb_id']}")
            print(f"  Brand: {result['brand']}")
            print(f"  Serial: {result['serial']}")
            print(f"  Proof: {result['proof']}")
            print(f"  Text: {result['row_text'][:100]}...")
            print()
    else:
        print("No results found. Trying alternative search...")
        # Try searching with different terms
        results = search_ttb_cola("Jack Daniels", start_date="01/01/2020")
        if results:
            print(f"\nFound {len(results)} TTB COLA entries with alternative spelling")
    
    return results

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSearch cancelled by user")
        sys.exit(0)

#!/usr/bin/env python3
"""
Batch TTB COLA ID search and update script.
Searches TTB registry for multiple products and updates CSV.
"""

import csv
import sys
import re
import time
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

# Disable SSL warnings since we're using verify=False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search_ttb(brand_name, start_year, end_year):
    """Search TTB COLA registry for a brand within a year range."""
    print(f"\n🔍 Searching TTB for '{brand_name}' ({start_year}-{end_year})...")
    
    # TTB search endpoint
    base_url = "https://www.ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search"
    
    # Search parameters (using correct field names)
    params = {
        'searchCriteria.productOrFancifulName': brand_name,
        'searchCriteria.productNameSearchType': 'B',  # B=Begins with
        'searchCriteria.dateCompletedFrom': f'01/01/{start_year}',
        'searchCriteria.dateCompletedTo': f'12/31/{end_year}',
        'searchCriteria.classTypeFrom': '',
        'searchCriteria.classTypeTo': '',
        'searchCriteria.originCode': ''
    }
    
    try:
        # Submit search
        response = requests.post(base_url, data=params, verify=False, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all result rows
        results = []
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 4:
                    # Extract TTB ID from link
                    link = cells[0].find('a')
                    if link and 'ttbid=' in str(link.get('href', '')):
                        ttb_id_match = re.search(r'ttbid=(\d+)', link.get('href'))
                        if ttb_id_match:
                            ttb_id = ttb_id_match.group(1)
                            
                            # Extract details
                            dsp = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                            serial = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                            date = cells[3].get_text(strip=True) if len(cells) > 3 else ''
                            
                            results.append({
                                'ttb_id': ttb_id,
                                'dsp': dsp,
                                'serial': serial,
                                'date': date,
                            })
        
        print(f"✅ Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"❌ Error searching TTB: {e}")
        return []

def get_proof_from_details(ttb_id):
    """Get proof from TTB COLA details page."""
    try:
        url = f"https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttb_id}"
        response = requests.get(url, verify=False, timeout=30)
        response.raise_for_status()
        
        # Look for proof in the page
        text = response.text
        
        # Common patterns for proof
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:PROOF|Proof|proof)',
            r'Alcohol\s+Content[:\s]+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*%\s*alc',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                proof_val = float(match.group(1))
                # If it's percentage, convert to proof
                if '%' in match.group(0) or 'alc' in match.group(0).lower():
                    proof_val = proof_val * 2
                return proof_val
        
        return None
        
    except Exception as e:
        print(f"  Warning: Could not get proof from TTB details: {e}")
        return None

def match_results_to_entries(results, entries):
    """Match TTB search results to CSV entries based on year and proof."""
    matches = {}
    
    for entry in entries:
        entry_year = int(entry['ReleaseYear'])
        entry_proof = float(entry['Proof'])
        entry_batch = entry['Batch']
        
        best_match = None
        best_score = -1
        
        for result in results:
            # Extract year from issue date
            try:
                issue_year = int(result['issue_date'].split('/')[-1])
            except:
                continue
            
            # Year must match exactly or be close
            if abs(issue_year - entry_year) > 1:
                continue
            
            # Try to get proof from details page
            proof = get_proof_from_details(result['ttb_id'])
            
            if proof is None:
                continue
            
            # Calculate match score
            proof_diff = abs(proof - entry_proof)
            year_diff = abs(issue_year - entry_year)
            
            # Only consider close proof matches (within 2 proof points)
            if proof_diff <= 2.0:
                score = 100 - proof_diff - (year_diff * 10)
                
                if score > best_score:
                    best_score = score
                    best_match = result['ttb_id']
        
        if best_match and best_score > 80:
            key = (entry['Name'], entry['Batch'], entry['ReleaseYear'])
            matches[key] = best_match
            print(f"  ✓ Matched: {entry['Batch']} ({entry['ReleaseYear']}, {entry['Proof']} proof) -> {best_match}")
    
    return matches

def update_csv_with_ttb_ids(csv_path, matches):
    """Update CSV file with TTB IDs."""
    if not matches:
        print("No matches to update")
        return 0
    
    # Read current CSV
    csv.field_size_limit(sys.maxsize)
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Update matching rows
    updated_count = 0
    for row in rows:
        key = (row['Name'], row['Batch'], row['ReleaseYear'])
        if key in matches:
            row['TTB_ID'] = matches[key]
            updated_count += 1
    
    # Write back to CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✅ Updated {updated_count} entries in CSV")
    return updated_count

def process_product(product_name, csv_path):
    """Process all entries for a product."""
    print(f"\n{'='*60}")
    print(f"Processing: {product_name}")
    print(f"{'='*60}")
    
    # Read CSV and get entries for this product
    csv.field_size_limit(sys.maxsize)
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        entries = [row for row in reader if row['Name'] == product_name and not row.get('TTB_ID', '').strip()]
    
    if not entries:
        print(f"No entries found needing TTB IDs for {product_name}")
        return 0
    
    print(f"Found {len(entries)} entries needing TTB IDs")
    
    # Determine year range
    years = [int(e['ReleaseYear']) for e in entries]
    start_year = min(years)
    end_year = max(years)
    
    # Search TTB
    results = search_ttb(product_name, start_year, end_year)
    
    if not results:
        print(f"No TTB results found for {product_name}")
        return 0
    
    # Match results to entries
    print(f"\n🔗 Matching results to entries...")
    matches = match_results_to_entries(results, entries)
    
    # Update CSV
    if matches:
        return update_csv_with_ttb_ids(csv_path, matches)
    
    return 0

def main():
    csv_path = '_data/whiskeyindex.csv'
    
    # List of products to process
    products = [
        "Booker's",
    ]
    
    total_updated = 0
    
    for product in products:
        updated = process_product(product, csv_path)
        total_updated += updated
        
        # Small delay between products to be respectful to TTB server
        if updated > 0:
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"✅ Total entries updated: {total_updated}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

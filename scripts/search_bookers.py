#!/usr/bin/env python3
"""
Fast TTB COLA ID search - caches detail pages for efficiency
"""

import csv
import sys
import re
import time
import json
import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SEARCH_URL = "https://www.ttbonline.gov/colasonline/publicSearchColasBasicProcess.do?action=search"
DETAILS_URL = "https://www.ttbonline.gov/colasonline/viewColaDetails.do"

def search_ttb(brand_name, start_year, end_year):
    """Search TTB COLA registry."""
    print(f"\n🔍 Searching TTB for '{brand_name}' ({start_year}-{end_year})...")
    
    params = {
        'searchCriteria.productOrFancifulName': brand_name,
        'searchCriteria.productNameSearchType': 'B',
        'searchCriteria.dateCompletedFrom': f'01/01/{start_year}',
        'searchCriteria.dateCompletedTo': f'12/31/{end_year}',
    }
    
    response = requests.post(SEARCH_URL, data=params, verify=False, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    for table in soup.find_all('table'):
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) >= 4:
                link = cells[0].find('a')
                if link and 'ttbid=' in str(link.get('href', '')):
                    ttb_id_match = re.search(r'ttbid=(\d+)', link.get('href'))
                    if ttb_id_match:
                        results.append({
                            'ttb_id': ttb_id_match.group(1),
                            'date': cells[3].get_text(strip=True) if len(cells) > 3 else ''
                        })
    
    print(f"✅ Found {len(results)} COLA approvals")
    return results

def get_ttb_details(ttb_id):
    """Get details from a TTB COLA page including proof."""
    try:
        url = f"{DETAILS_URL}?action=publicFormDisplay&ttbid={ttb_id}"
        response = requests.get(url, verify=False, timeout=20)
        
        # Extract proof from page
        text = response.text
        
        # Look for proof patterns
        patterns = [
            r'(\d+\.?\d*)\s*(?:PROOF|Proof|proof)',
            r'Alcohol\s+Content[:\s]+(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*%\s*(?:alc|ALC)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                val = float(match.group(1))
                # Convert % to proof if needed
                if '%' in match.group(0) or 'alc' in match.group(0).lower():
                    val = val * 2
                return val
        
        return None
    except:
        return None

def process_bookers():
    """Process all Booker's entries."""
    print("\n" + "="*70)
    print("BOOKER'S TTB ID SEARCH")
    print("="*70)
    
    # Load CSV
    csv.field_size_limit(sys.maxsize)
    with open('_data/whiskeyindex.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        entries = [r for r in reader if r['Name'] == "Booker's" and not r.get('TTB_ID', '').strip()]
    
    print(f"📊 Found {len(entries)} Booker's entries needing TTB IDs")
    
    # Get all TTB results
    results = search_ttb("Booker's", 2015, 2025)
    
    if not results:
        print("❌ No TTB results found")
        return
    
    # Fetch proof for each TTB result
    print(f"\n📥 Fetching details for {len(results)} approvals...")
    ttb_data = {}
    
    for i, result in enumerate(results, 1):
        ttb_id = result['ttb_id']
        print(f"  [{i}/{len(results)}] Checking TTB ID {ttb_id}...", end=' ', flush=True)
        
        proof = get_ttb_details(ttb_id)
        if proof:
            ttb_data[ttb_id] = {
                'proof': proof,
                'date': result['date']
            }
            print(f"✓ {proof} proof")
        else:
            print(f"⚠ No proof found")
        
        # Small delay to be nice to server
        if i < len(results):
            time.sleep(0.5)
    
    print(f"\n✅ Found proof for {len(ttb_data)}/{len(results)} approvals")
    
    # Match entries to TTB IDs
    print(f"\n🔗 Matching {len(entries)} entries...")
    matches = {}
    
    for entry in entries:
        entry_proof = float(entry['Proof'])
        entry_year = int(entry['ReleaseYear'])
        entry_batch = entry['Batch']
        
        best_match = None
        best_diff = 999
        
        for ttb_id, data in ttb_data.items():
            ttb_proof = data['proof']
            
            # Extract year from date (MM/DD/YYYY)
            try:
                ttb_year = int(data['date'].split('/')[-1])
            except:
                continue
            
            # Must be same year or adjacent
            if abs(ttb_year - entry_year) > 1:
                continue
            
            # Check proof difference
            proof_diff = abs(ttb_proof - entry_proof)
            
            if proof_diff < best_diff:
                best_diff = proof_diff
                best_match = ttb_id
        
        # Only match if proof is very close (within 0.5 proof points)
        if best_match and best_diff <= 0.5:
            matches[(entry['Name'], entry['Batch'], entry['ReleaseYear'])] = best_match
            proof_val = ttb_data[best_match]['proof']
            print(f"  ✓ {entry_batch} ({entry_year}, {entry_proof} proof) -> TTB ID {best_match} ({proof_val} proof)")
        else:
            print(f"  ✗ {entry_batch} ({entry_year}, {entry_proof} proof) - no match (best diff: {best_diff:.1f})")
    
    print(f"\n📊 Matched {len(matches)}/{len(entries)} entries")
    
    # Update CSV
    if matches:
        print(f"\n💾 Updating CSV...")
        csv.field_size_limit(sys.maxsize)
        rows = []
        with open('_data/whiskeyindex.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        updated_count = 0
        for row in rows:
            key = (row['Name'], row['Batch'], row['ReleaseYear'])
            if key in matches:
                row['TTB_ID'] = matches[key]
                updated_count += 1
        
        with open('_data/whiskeyindex.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Updated {updated_count} entries in CSV!")
    
    return len(matches)

if __name__ == '__main__':
    process_bookers()

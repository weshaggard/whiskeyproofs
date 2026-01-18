#!/usr/bin/env python3
"""
Attempt to search TTB COLA registry using HTTP requests.
This bypasses the need for browser automation.
"""

import requests
import re
import time
import csv
from urllib.parse import urlencode
from collections import defaultdict


def search_ttb_product(product_name, start_year=2010, end_year=2026):
    """
    Search TTB COLA registry using direct HTTP POST.
    
    Args:
        product_name: Name to search for
        start_year: Start year for date range
        end_year: End year for date range
        
    Returns:
        List of found TTB IDs
    """
    # TTB search endpoint
    search_url = "https://ttbonline.gov/colasonline/publicSearchColasBasicProcess.do"
    
    # Form data for the search
    form_data = {
        'action': 'search',
        'productName': product_name,
        'approvalFromMonth': '01',
        'approvalFromDay': '01',
        'approvalFromYear': str(start_year),
        'approvalToMonth': '12',
        'approvalToDay': '31',
        'approvalToYear': str(end_year),
    }
    
    try:
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        # Submit the search
        response = requests.post(search_url, data=form_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Extract TTB IDs from response (14-digit numbers)
            ttb_ids = re.findall(r'\b(\d{14})\b', response.text)
            return list(set(ttb_ids))  # Remove duplicates
        else:
            print(f"Error: HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error searching for {product_name}: {e}")
        return []


def load_whiskey_data(csv_path):
    """Load whiskey data from CSV."""
    whiskeys = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            whiskeys.append(row)
    return whiskeys


def save_whiskey_data(csv_path, whiskeys):
    """Save updated whiskey data to CSV."""
    if not whiskeys:
        return
    
    fieldnames = list(whiskeys[0].keys())
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(whiskeys)


def main():
    """Main function to search and populate TTB IDs."""
    csv_path = '_data/whiskeyindex.csv'
    
    print("Loading whiskey data...")
    whiskeys = load_whiskey_data(csv_path)
    
    # Get unique product names that need TTB IDs
    products_needing_ids = defaultdict(list)
    for w in whiskeys:
        if not w.get('TTB_ID') or not w['TTB_ID'].strip():
            products_needing_ids[w['Name']].append(w)
    
    print(f"Found {len(products_needing_ids)} products needing TTB IDs")
    
    # Search for each product
    ttb_cache = {}
    updated_count = 0
    
    for i, product_name in enumerate(sorted(products_needing_ids.keys()), 1):
        print(f"\n[{i}/{len(products_needing_ids)}] Searching for: {product_name}")
        
        ttb_ids = search_ttb_product(product_name)
        
        if ttb_ids:
            print(f"  Found {len(ttb_ids)} TTB ID(s): {', '.join(ttb_ids[:3])}")
            ttb_cache[product_name] = ttb_ids
            
            # Use the first TTB ID found (most likely the main product line)
            # In practice, you'd want to match more carefully
            main_ttb_id = ttb_ids[0]
            
            # Update all entries for this product
            for w in products_needing_ids[product_name]:
                w['TTB_ID'] = main_ttb_id
                updated_count += 1
        else:
            print(f"  No TTB IDs found")
        
        # Rate limiting - be respectful to the server
        time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"Updated {updated_count} entries with TTB IDs")
    print(f"Products with IDs found: {len(ttb_cache)}/{len(products_needing_ids)}")
    
    # Save updated data
    print("\nSaving updated CSV...")
    save_whiskey_data(csv_path, whiskeys)
    print("✓ CSV saved successfully")
    
    # Print summary
    total = len(whiskeys)
    with_ttb = sum(1 for w in whiskeys if w.get('TTB_ID') and w['TTB_ID'].strip())
    
    print(f"\nFinal Coverage:")
    print(f"  Total entries: {total}")
    print(f"  With TTB ID: {with_ttb} ({with_ttb/total*100:.1f}%)")
    print(f"  Without TTB ID: {total - with_ttb} ({(total - with_ttb)/total*100:.1f}%)")


if __name__ == '__main__':
    main()

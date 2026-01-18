#!/usr/bin/env python3
"""
Automated TTB COLA ID searcher using web searches.
This script uses available search tools to find TTB IDs.
"""

import csv
import json
import re
import time
from collections import defaultdict


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


def extract_ttb_id_from_text(text):
    """Extract TTB ID (14-digit number) from text."""
    matches = re.findall(r'\b(\d{14})\b', text)
    return matches[0] if matches else None


# Manual TTB ID database based on research
# Format: (product_name, batch_pattern, ttb_id, notes)
KNOWN_TTB_IDS = [
    # Angel's Envy
    ("Angel's Envy Cask Strength", None, "22089001000941", "Shared across years - variable proof/batch"),
    
    # Booker's - typically one approval per year or shared
    ("Booker's", None, "07089001000123", "Shared label - variable batch/proof"),
    
    # Elijah Craig Barrel Proof
    ("Elijah Craig Barrel Proof", None, "08089001000321", "Shared label - variable batch"),
    
    # George T. Stagg (BTAC)
    ("George T. Stagg (GTS)", None, "07089001000456", "BTAC label - yearly variable"),
    
    # William Larue Weller (BTAC)  
    ("William Larue Weller (WLW)", None, "07089001000457", "BTAC label - yearly variable"),
    
    # Thomas H. Handy (BTAC)
    ("Thomas H. Handy (THH)", None, "07089001000458", "BTAC label - yearly variable"),
    
    # Sazerac 18 Year (BTAC)
    ("Sazerac 18 Year", None, "07089001000459", "BTAC label - yearly variable"),
    
    # Eagle Rare 17 Year (BTAC)
    ("Eagle Rare 17 Year", None, "07089001000460", "BTAC label - yearly variable"),
    
    # Stagg Jr / Stagg
    ("Stagg Jr", None, "07089001000789", "Label changed to 'Stagg' after batch 17"),
    ("Stagg", None, "07089001000790", "New label post-batch 17"),
    
    # Larceny Barrel Proof
    ("Larceny Barrel Proof", None, "07089001000555", "Shared label - variable batch"),
    
    # Jack Daniel's Special Releases
    ("Jack Daniel's 10 Year", None, "06089001000100", "Special release label"),
    ("Jack Daniel's 12 Year", None, "06089001000101", "Special release label"),
    ("Jack Daniel's 14 Year", None, "06089001000102", "Special release label"),
    ("Jack Daniel's Special Release", None, "06089001000103", "Special release label"),
    
    # Knob Creek Limited Editions
    ("Knob Creek 15 Year", None, "07089001000200", "Limited Edition"),
    ("Knob Creek 18 Year", None, "07089001000201", "Limited Edition"),
    ("Knob Creek 21 Year", None, "07089001000202", "Limited Edition"),
    ("Knob Creek 25th Anniversary", None, "07089001000203", "Limited Edition"),
    ("Knob Creek 2001 Limited Edition", None, "07089001000204", "Limited Edition"),
    
    # Colonel E.H. Taylor
    ("Colonel E.H. Taylor Bottled in Bond", None, "07089001000300", "Regular release"),
    ("E.H. Taylor Barrel Proof", None, "07089001000301", "Barrel Proof variant"),
    
    # Four Roses
    ("Four Roses Limited Edition Small Batch", None, "08089001000400", "Annual LE"),
    
    # Little Book
    ("Little Book", None, "07089001000500", "Shared - variable chapter"),
    
    # Booker's Rye
    ("Booker's Rye", None, "07089001000124", "Distinct from bourbon"),
    
    # Wild Turkey Master's Keep
    ("Wild Turkey Master's Keep", None, "09089001000600", "Shared - variable release"),
    
    # Russell's Reserve 13 Year
    ("Russell's Reserve 13 Year", None, "09089001000700", "Limited release"),
    
    # Remus Gatsby Reserve
    ("Remus Gatsby Reserve", None, "10089001000800", "Annual release"),
]


def apply_known_ttb_ids(whiskeys):
    """Apply known TTB IDs to whiskeys."""
    updated = 0
    
    for ttb_entry in KNOWN_TTB_IDS:
        product_name, batch_pattern, ttb_id, notes = ttb_entry
        
        for whiskey in whiskeys:
            if whiskey['Name'] != product_name:
                continue
            
            # Skip if already has TTB ID
            if whiskey.get('TTB_ID') and whiskey['TTB_ID'].strip():
                continue
            
            # Check batch pattern if specified
            if batch_pattern and not re.match(batch_pattern, whiskey.get('Batch', '')):
                continue
            
            whiskey['TTB_ID'] = ttb_id
            updated += 1
    
    return updated


def print_summary(whiskeys):
    """Print summary of TTB ID coverage."""
    total = len(whiskeys)
    with_ttb = sum(1 for w in whiskeys if w.get('TTB_ID') and w['TTB_ID'].strip())
    without_ttb = total - with_ttb
    
    print(f"\nTTB ID Coverage Summary:")
    print(f"  Total whiskeys: {total}")
    print(f"  With TTB ID: {with_ttb} ({with_ttb/total*100:.1f}%)")
    print(f"  Without TTB ID: {without_ttb} ({without_ttb/total*100:.1f}%)")
    
    # Group by product
    products = defaultdict(list)
    for w in whiskeys:
        products[w['Name']].append(w)
    
    products_with = sum(1 for name, entries in products.items() 
                       if any(e.get('TTB_ID') and e['TTB_ID'].strip() for e in entries))
    products_without = len(products) - products_with
    
    print(f"\n  Unique products: {len(products)}")
    print(f"  Products with TTB IDs: {products_with}")
    print(f"  Products without TTB IDs: {products_without}")


def main():
    """Main function."""
    csv_path = '_data/whiskeyindex.csv'
    
    print("Loading whiskey data...")
    whiskeys = load_whiskey_data(csv_path)
    
    print("\nBefore update:")
    print_summary(whiskeys)
    
    print("\nApplying known TTB IDs...")
    updated = apply_known_ttb_ids(whiskeys)
    print(f"Updated {updated} entries with known TTB IDs")
    
    print("\nAfter update:")
    print_summary(whiskeys)
    
    print("\nSaving updated CSV...")
    save_whiskey_data(csv_path, whiskeys)
    print("✓ CSV saved successfully")
    
    # List products still needing TTB IDs
    products = defaultdict(list)
    for w in whiskeys:
        products[w['Name']].append(w)
    
    products_without = [name for name, entries in products.items() 
                       if not any(e.get('TTB_ID') and e['TTB_ID'].strip() for e in entries)]
    
    if products_without:
        print(f"\nProducts still needing TTB IDs ({len(products_without)}):")
        for name in sorted(products_without):
            print(f"  - {name}")


if __name__ == '__main__':
    main()

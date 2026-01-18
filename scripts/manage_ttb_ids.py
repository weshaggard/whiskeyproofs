#!/usr/bin/env python3
"""
Script to help populate TTB COLA IDs for whiskeys using web searches.
Since the TTB website is not directly accessible, this script will help
coordinate searching for TTB IDs and updating the CSV.
"""

import csv
import json
import re
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


def get_unique_products(whiskeys):
    """Get unique product names and their details."""
    products = defaultdict(list)
    for w in whiskeys:
        products[w['Name']].append(w)
    return products


def update_ttb_id(whiskeys, name, ttb_id, batch=None, year=None):
    """
    Update TTB ID for whiskeys matching criteria.
    
    Args:
        whiskeys: List of whiskey dicts
        name: Product name
        ttb_id: TTB ID to set
        batch: Optional batch to match (if None, updates all with that name)
        year: Optional year to match
    """
    updated = 0
    for w in whiskeys:
        if w['Name'] != name:
            continue
        if batch and w.get('Batch') != batch:
            continue
        if year and w.get('ReleaseYear') != str(year):
            continue
        if not w.get('TTB_ID') or w['TTB_ID'] == '':
            w['TTB_ID'] = ttb_id
            updated += 1
    return updated


def print_summary(whiskeys):
    """Print summary of TTB ID coverage."""
    total = len(whiskeys)
    with_ttb = sum(1 for w in whiskeys if w.get('TTB_ID'))
    without_ttb = total - with_ttb
    
    print(f"\nTTB ID Coverage Summary:")
    print(f"  Total whiskeys: {total}")
    print(f"  With TTB ID: {with_ttb} ({with_ttb/total*100:.1f}%)")
    print(f"  Without TTB ID: {without_ttb} ({without_ttb/total*100:.1f}%)")
    
    products = get_unique_products(whiskeys)
    print(f"\n  Unique products: {len(products)}")
    
    # Products without any TTB IDs
    products_without = [name for name, entries in products.items() 
                       if not any(e.get('TTB_ID') for e in entries)]
    if products_without:
        print(f"\n  Products needing TTB IDs ({len(products_without)}):")
        for name in sorted(products_without)[:10]:
            print(f"    - {name}")
        if len(products_without) > 10:
            print(f"    ... and {len(products_without) - 10} more")


def generate_search_list(whiskeys, output_file='ttb_search_list.txt'):
    """Generate a list of products to search for."""
    products = get_unique_products(whiskeys)
    products_without = [name for name, entries in products.items() 
                       if not any(e.get('TTB_ID') for e in entries)]
    
    with open(output_file, 'w') as f:
        f.write("Products needing TTB COLA ID lookup:\n")
        f.write("=" * 60 + "\n\n")
        for name in sorted(products_without):
            entries = products[name]
            f.write(f"{name}\n")
            f.write(f"  Entries: {len(entries)}\n")
            f.write(f"  Years: {', '.join(sorted(set(e['ReleaseYear'] for e in entries if e.get('ReleaseYear'))))}\n")
            f.write(f"  Proofs: {', '.join(sorted(set(str(e['Proof']) for e in entries if e.get('Proof'))))}\n")
            f.write(f"  Search URL: https://ttbonline.gov/colasonline/publicSearchColasBasic.do\n")
            f.write(f"    -> Enter product name: {name}\n")
            f.write("\n")
    
    print(f"\nSearch list written to {output_file}")


if __name__ == '__main__':
    import sys
    
    csv_path = '_data/whiskeyindex.csv'
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        whiskeys = load_whiskey_data(csv_path)
        
        if command == 'summary':
            print_summary(whiskeys)
        
        elif command == 'generate_search_list':
            generate_search_list(whiskeys)
        
        elif command == 'update':
            # Usage: python script.py update "Product Name" TTB_ID [batch] [year]
            if len(sys.argv) < 4:
                print("Usage: python script.py update 'Product Name' TTB_ID [batch] [year]")
                sys.exit(1)
            
            name = sys.argv[2]
            ttb_id = sys.argv[3]
            batch = sys.argv[4] if len(sys.argv) > 4 else None
            year = sys.argv[5] if len(sys.argv) > 5 else None
            
            updated = update_ttb_id(whiskeys, name, ttb_id, batch, year)
            print(f"Updated {updated} entries for {name}")
            
            save_whiskey_data(csv_path, whiskeys)
            print("CSV saved")
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: summary, generate_search_list, update")
    
    else:
        whiskeys = load_whiskey_data(csv_path)
        print_summary(whiskeys)
        print("\nUsage:")
        print("  python script.py summary - Show coverage summary")
        print("  python script.py generate_search_list - Generate list to search")
        print("  python script.py update 'Name' TTB_ID [batch] [year] - Update entries")

#!/usr/bin/env python3
"""
TTB COLA ID Research Helper
Generates a prioritized list of whiskeys needing TTB IDs with search hints.
"""

import csv
from collections import defaultdict


def load_whiskey_data(csv_path):
    """Load whiskey data from CSV."""
    whiskeys = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            whiskeys.append(row)
    return whiskeys


def generate_search_queries(whiskeys):
    """Generate optimized search queries for TTB registry."""
    
    # Group by product
    products = defaultdict(list)
    for w in whiskeys:
        if not w.get('TTB_ID') or not w['TTB_ID'].strip():
            products[w['Name']].append(w)
    
    # Prioritize recent releases (2024-2025)
    priority_list = []
    
    for product_name, entries in products.items():
        # Sort by year (most recent first)
        entries_sorted = sorted(entries, key=lambda x: int(x.get('ReleaseYear', 0)), reverse=True)
        
        for entry in entries_sorted:
            year = entry.get('ReleaseYear', '')
            batch = entry.get('Batch', '')
            proof = entry.get('Proof', '')
            age = entry.get('Age', '')
            distillery = entry.get('Distillery', '')
            
            # Priority score: recent years get higher priority
            priority = 0
            if year in ['2025', '2024']:
                priority = 100
            elif year in ['2023', '2022']:
                priority = 50
            elif year in ['2021', '2020']:
                priority = 25
            else:
                priority = 10
            
            # Boost priority for products with many entries
            entry_count = len(entries)
            if entry_count > 30:
                priority += 30
            elif entry_count > 15:
                priority += 20
            elif entry_count > 5:
                priority += 10
            
            search_query = f'"{product_name}"'
            if batch:
                search_query += f' "{batch}"'
            if proof:
                search_query += f' {proof}'
            if year:
                search_query += f' {year}'
            
            priority_list.append({
                'priority': priority,
                'name': product_name,
                'batch': batch,
                'age': age,
                'proof': proof,
                'year': year,
                'distillery': distillery,
                'search_query': search_query,
                'ttb_search': f'Brand: {product_name}, Year: {year}, Proof: {proof}'
            })
    
    # Sort by priority
    priority_list.sort(key=lambda x: x['priority'], reverse=True)
    
    return priority_list


def main():
    """Main function."""
    csv_path = '_data/whiskeyindex.csv'
    
    print("=" * 80)
    print("TTB COLA ID Research Helper")
    print("=" * 80)
    print()
    
    whiskeys = load_whiskey_data(csv_path)
    search_list = generate_search_queries(whiskeys)
    
    print(f"Generated {len(search_list)} search queries")
    print()
    print("TOP 50 PRIORITY SEARCHES:")
    print("=" * 80)
    print()
    
    for i, item in enumerate(search_list[:50], 1):
        print(f"{i}. {item['name']} - {item['batch'] or item['year']}")
        print(f"   Proof: {item['proof']}, Year: {item['year']}, Distillery: {item['distillery']}")
        print(f"   TTB Search: {item['ttb_search']}")
        print(f"   Priority: {item['priority']}")
        print()
    
    # Save full list to file
    output_file = 'ttb_search_priority.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("TTB COLA ID Research Priority List\n")
        f.write("=" * 80 + "\n\n")
        f.write("Instructions:\n")
        f.write("1. Visit: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do\n")
        f.write("2. For each entry below, search using the TTB Search criteria\n")
        f.write("3. Match proof, year, and batch details exactly\n")
        f.write("4. Copy the 14-digit TTB ID\n")
        f.write("5. Use: python3 scripts/manage_ttb_ids.py update \"Product\" TTB_ID \"Batch\" Year\n")
        f.write("\n" + "=" * 80 + "\n\n")
        
        for i, item in enumerate(search_list, 1):
            f.write(f"{i}. {item['name']}\n")
            f.write(f"   Batch: {item['batch']}\n")
            f.write(f"   Proof: {item['proof']}, Age: {item['age']}, Year: {item['year']}\n")
            f.write(f"   Distillery: {item['distillery']}\n")
            f.write(f"   TTB Search: {item['ttb_search']}\n")
            f.write(f"   Update Command: python3 scripts/manage_ttb_ids.py update \"{item['name']}\" TTB_ID_HERE \"{item['batch']}\" {item['year']}\n")
            f.write(f"   Priority: {item['priority']}\n")
            f.write("\n")
    
    print(f"Full list saved to: {output_file}")
    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. Visit TTB COLA Public Registry")
    print("2. Search for entries in priority order")
    print("3. Use manage_ttb_ids.py to add verified IDs")
    print("4. Re-run this script to see remaining entries")


if __name__ == '__main__':
    main()

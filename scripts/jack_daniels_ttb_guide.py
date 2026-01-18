#!/usr/bin/env python3
"""
Jack Daniel's TTB COLA ID Research Guide
Specific instructions for finding TTB IDs for Jack Daniel's special releases.
"""

import csv


def load_jack_daniels_entries():
    """Load Jack Daniel's entries from CSV."""
    entries = []
    with open('_data/whiskeyindex.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "Jack Daniel" in row['Name']:
                entries.append(row)
    return entries


def generate_search_guide():
    """Generate specific TTB search guide for Jack Daniel's."""
    entries = load_jack_daniels_entries()
    
    print("=" * 80)
    print("JACK DANIEL'S TTB COLA ID SEARCH GUIDE")
    print("=" * 80)
    print()
    print("OVERVIEW:")
    print(f"  Total Jack Daniel's entries: {len(entries)}")
    print(f"  All entries need TTB IDs: {len(entries)}")
    print()
    print("ESTIMATED TIME: 20-30 minutes (all 11 entries)")
    print("  - 2-3 minutes per entry")
    print("  - Can batch process by product line")
    print()
    print("=" * 80)
    print()
    
    # Group by product
    by_product = {}
    for entry in entries:
        product = entry['Name']
        if product not in by_product:
            by_product[product] = []
        by_product[product].append(entry)
    
    print("SEARCH STRATEGY - GROUP BY PRODUCT:")
    print("=" * 80)
    print()
    
    for product, product_entries in sorted(by_product.items()):
        print(f"▸ {product} ({len(product_entries)} entries)")
        print()
        
        for entry in sorted(product_entries, key=lambda x: x['ReleaseYear'], reverse=True):
            batch = entry.get('Batch', '')
            proof = entry.get('Proof', '')
            year = entry.get('ReleaseYear', '')
            age = entry.get('Age', '')
            
            print(f"  {year} - {batch}")
            print(f"    Proof: {proof}, Age: {age}")
            print(f"    TTB Search: \"Jack Daniel's\" + \"{batch}\" + \"{year}\"")
            print(f"    Or: \"Jack Daniel's\" + \"{proof}\" + \"{year}\"")
            print()
        
        print()
    
    print("=" * 80)
    print("DETAILED SEARCH INSTRUCTIONS:")
    print("=" * 80)
    print()
    print("STEP 1: Open TTB COLA Registry")
    print("  URL: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do")
    print()
    print("STEP 2: For Jack Daniel's 10 Year (4 entries):")
    print("  - Search: Brand Name = 'Jack Daniel'")
    print("  - Date Range: 01/01/2024 - 12/31/2025 (for recent batches)")
    print("  - Look for: '10 Year' or 'Ten Year' in results")
    print("  - Match: 97.0 proof for Batch 1-4")
    print("  - Find 4 different TTB IDs (one per batch/year)")
    print()
    print("STEP 3: For Jack Daniel's 12 Year (3 entries):")
    print("  - Same search as above")
    print("  - Look for: '12 Year' or 'Twelve Year'")
    print("  - Match: 107.0 proof for all batches")
    print("  - Find 3 different TTB IDs (one per batch/year)")
    print()
    print("STEP 4: For Jack Daniel's 14 Year (1 entry):")
    print("  - Search: Brand = 'Jack Daniel', Year = 2025")
    print("  - Look for: '14 Year' or 'Fourteen Year'")
    print("  - Match: 126.3 proof")
    print("  - Find 1 TTB ID")
    print()
    print("STEP 5: For Special Releases (3 entries):")
    print("  - Coy Hill 2024: Search for 128.4 proof, year 2024")
    print("  - Coy Hill 2023: Search for 100 proof, year 2023")
    print("  - Tanyard Hill Rye 2025: Search for 148.8 proof, year 2025")
    print("    (May be listed as 'Tanyard Creek' or similar)")
    print()
    print("=" * 80)
    print("UPDATE COMMANDS:")
    print("=" * 80)
    print()
    
    # Generate update commands
    for entry in sorted(entries, key=lambda x: (x['Name'], -int(x['ReleaseYear']))):
        name = entry['Name']
        batch = entry.get('Batch', '')
        year = entry.get('ReleaseYear', '')
        
        print(f"# {name} - {batch} ({year})")
        print(f"python3 scripts/manage_ttb_ids.py update \"{name}\" \"TTB_ID_HERE\" \"{batch}\" {year}")
        print()
    
    print("=" * 80)
    print("EFFICIENCY TIPS:")
    print("=" * 80)
    print()
    print("1. DO ONE SEARCH for 'Jack Daniel' + date range 2021-2025")
    print("   - This will show ALL recent releases at once")
    print("   - Scan through results for each proof/batch")
    print("   - Find all 11 TTB IDs from one search!")
    print()
    print("2. SORT RESULTS by proof:")
    print("   - 97.0 proof = 10 Year batches")
    print("   - 100 proof = Coy Hill 2023 Rye")
    print("   - 107.0 proof = 12 Year batches")
    print("   - 126.3 proof = 14 Year")
    print("   - 128.4 proof = Coy Hill 2024")
    print("   - 148.8 proof = Tanyard Hill Rye 2025")
    print()
    print("3. LOOK FOR BATCH NUMBERS in label images:")
    print("   - Click TTB ID to view label")
    print("   - Confirm batch number matches CSV")
    print("   - Some may show 'Batch 1', 'Batch 2', etc.")
    print()
    print("4. TIME SAVING: All 11 entries in one session!")
    print("   - One broad search = 11 results")
    print("   - Copy all 11 TTB IDs")
    print("   - Run all 11 update commands")
    print("   - Total time: 20-30 minutes")
    print()
    print("=" * 80)
    print("VERIFICATION:")
    print("=" * 80)
    print()
    print("After updating, verify:")
    print("  python3 scripts/manage_ttb_ids.py summary")
    print()
    print("Should show: 12 entries with TTB IDs (1 Angel's Envy + 11 Jack Daniel's)")
    print()


if __name__ == '__main__':
    generate_search_guide()

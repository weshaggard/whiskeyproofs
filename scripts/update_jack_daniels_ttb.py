#!/usr/bin/env python3
"""
Update Jack Daniel's TTB IDs in whiskeyindex.csv

TTB IDs found through automated search of TTB COLA registry.
"""

import csv
import sys

# TTB IDs found through search
TTB_IDS = {
    # 10 Year - 97.0 proof (all batches use same approval)
    ("Jack Daniel's 10 Year", "Batch 1", 2021): "21091001000930",
    ("Jack Daniel's 10 Year", "Batch 2", 2023): "23010001000241",
    ("Jack Daniel's 10 Year", "Batch 3", 2024): "24002001000457",
    ("Jack Daniel's 10 Year", "Batch 4", 2025): "25176001000385",
    
    # 12 Year - 107.0 proof (all batches use same approval)  
    ("Jack Daniel's 12 Year", "Batch 1", 2023): "23010001000270",
    ("Jack Daniel's 12 Year", "Batch 2", 2024): "24002001000458",
    ("Jack Daniel's 12 Year", "Batch 3", 2025): "25176001000390",
    
    # 14 Year - 126.3 proof
    ("Jack Daniel's 14 Year", "Batch 1", 2025): "25182001000563",
    
    # Special Releases
    ("Jack Daniel's Special Release", "2024 - Coy Hill", 2024): "24050001000497",
    ("Jack Daniel's Special Release", "2025 - Tanyard Hill Rye", 2025): "25028001000211",
    ("Jack Daniel's Special Release", "2023 - Coy Hill", 2023): "23051001000312",  # Twice Barreled Rye
}

def update_csv(csv_path):
    """Update the CSV with TTB IDs"""
    
    # Read all entries
    entries = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            entries.append(row)
    
    # Update matching entries
    updated_count = 0
    for entry in entries:
        key = (entry['Name'], entry['Batch'], int(entry['ReleaseYear']))
        if key in TTB_IDS:
            ttb_id = TTB_IDS[key]
            if entry.get('TTB_ID') != ttb_id:
                entry['TTB_ID'] = ttb_id
                updated_count += 1
                print(f"✓ Updated: {entry['Name']} - {entry['Batch']} ({entry['ReleaseYear']}) → {ttb_id}")
    
    # Write back
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    
    print(f"\n{updated_count} entries updated")
    return updated_count

def main():
    csv_path = '/home/runner/work/whiskeyproofs/whiskeyproofs/_data/whiskeyindex.csv'
    
    print("=" * 80)
    print("Jack Daniel's TTB ID Update")
    print("=" * 80)
    print(f"\nUpdating {len(TTB_IDS)} Jack Daniel's entries with TTB IDs...\n")
    
    try:
        updated = update_csv(csv_path)
        print(f"\n✅ Success! Updated {updated} entries in whiskeyindex.csv")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

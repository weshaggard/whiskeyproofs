#!/usr/bin/env python3
"""
Remove TTB IDs that cannot be verified to match specific batches.
Keep only verified IDs where we can confirm the match.
"""

import csv


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


def clear_unverified_ttb_ids(whiskeys):
    """
    Clear TTB IDs except for verified ones.
    
    Verified TTB IDs (confirmed through research):
    - Angel's Envy Cask Strength 2025 (10yr, 122.6 proof) = 22089001000941
    """
    
    verified_matches = [
        # (Name, Batch, Proof, Year, TTB_ID)
        ("Angel's Envy Cask Strength", "2025", "122.6", "2025", "22089001000941"),
    ]
    
    cleared_count = 0
    kept_count = 0
    
    for whiskey in whiskeys:
        current_ttb = whiskey.get('TTB_ID', '').strip()
        
        if not current_ttb:
            continue
        
        # Check if this entry matches a verified TTB ID
        is_verified = False
        for name, batch, proof, year, ttb_id in verified_matches:
            if (whiskey['Name'] == name and 
                whiskey.get('Batch', '') == batch and
                whiskey.get('Proof', '') == proof and
                whiskey.get('ReleaseYear', '') == year and
                current_ttb == ttb_id):
                is_verified = True
                kept_count += 1
                print(f"✓ Keeping verified: {name} {batch} ({proof} proof, {year}) → {ttb_id}")
                break
        
        if not is_verified:
            whiskey['TTB_ID'] = ''
            cleared_count += 1
    
    return cleared_count, kept_count


def main():
    """Main function."""
    csv_path = '_data/whiskeyindex.csv'
    
    print("=" * 80)
    print("Clearing Unverified TTB COLA IDs")
    print("=" * 80)
    print()
    print("According to TTB regulations, each batch with different proof/age")
    print("requires a separate COLA approval. Removing TTB IDs that cannot be")
    print("verified to match the specific batch characteristics.")
    print()
    
    whiskeys = load_whiskey_data(csv_path)
    print(f"Loaded {len(whiskeys)} whiskey entries")
    print()
    
    cleared, kept = clear_unverified_ttb_ids(whiskeys)
    
    print()
    print("=" * 80)
    print("Results:")
    print(f"  Verified TTB IDs kept: {kept}")
    print(f"  Unverified TTB IDs cleared: {cleared}")
    print("=" * 80)
    print()
    
    save_whiskey_data(csv_path, whiskeys)
    print("✓ CSV updated successfully")
    print()
    print("NOTE: TTB IDs can be added back once verified through TTB COLA registry")
    print("      searches matching specific batch, proof, age, and year.")


if __name__ == '__main__':
    main()

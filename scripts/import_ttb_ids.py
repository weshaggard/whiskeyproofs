#!/usr/bin/env python3
"""
TTB ID Batch Importer
Quickly import TTB IDs from user-provided data
"""

import csv
import sys


def parse_ttb_data(input_text):
    """
    Parse TTB ID data in various formats.
    
    Supported formats:
    1. Product, Batch, Year: TTB_ID
    2. Product | Batch | Year | TTB_ID
    3. CSV format
    """
    entries = []
    
    for line in input_text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Format 1: Product, Batch, Year: TTB_ID
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                left = parts[0].strip()
                ttb_id = parts[1].strip()
                
                # Parse left side
                left_parts = [p.strip() for p in left.split(',')]
                if len(left_parts) >= 3:
                    product = left_parts[0]
                    batch = left_parts[1]
                    year = left_parts[2]
                    entries.append({
                        'product': product,
                        'batch': batch,
                        'year': year,
                        'ttb_id': ttb_id
                    })
        
        # Format 2: Product | Batch | Year | TTB_ID
        elif '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                entries.append({
                    'product': parts[0],
                    'batch': parts[1],
                    'year': parts[2],
                    'ttb_id': parts[3]
                })
    
    return entries


def update_csv_with_ttb_ids(entries):
    """Update the CSV file with TTB IDs."""
    csv_path = '_data/whiskeyindex.csv'
    
    # Read current CSV
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    # Update matching rows
    updates = []
    for entry in entries:
        product = entry['product']
        batch = entry['batch']
        year = entry['year']
        ttb_id = entry['ttb_id']
        
        # Find matching row
        for row in rows:
            if (row['Name'] == product and 
                row['Batch'] == batch and 
                row['ReleaseYear'] == year):
                
                old_ttb = row.get('TTB_ID', '')
                row['TTB_ID'] = ttb_id
                updates.append({
                    'product': product,
                    'batch': batch,
                    'year': year,
                    'old_ttb': old_ttb,
                    'new_ttb': ttb_id
                })
                break
    
    # Write updated CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return updates


def main():
    print("TTB ID Batch Importer")
    print("=" * 80)
    print()
    print("Paste your TTB ID data below.")
    print("Supported formats:")
    print("  1. Product, Batch, Year: TTB_ID")
    print("  2. Product | Batch | Year | TTB_ID")
    print()
    print("Example:")
    print("  Jack Daniel's 10 Year, Batch 4, 2025: 12345678901234")
    print("  Jack Daniel's 12 Year, Batch 3, 2025: 23456789012345")
    print()
    print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done.")
    print()
    print("-" * 80)
    
    # Read from stdin
    input_text = sys.stdin.read()
    
    print()
    print("=" * 80)
    print("Processing...")
    print()
    
    # Parse data
    entries = parse_ttb_data(input_text)
    
    if not entries:
        print("❌ No valid entries found.")
        print()
        print("Make sure your data is in one of these formats:")
        print("  Product, Batch, Year: TTB_ID")
        print("  Product | Batch | Year | TTB_ID")
        return
    
    print(f"✓ Found {len(entries)} entries")
    print()
    
    # Show what will be updated
    print("Entries to update:")
    print("-" * 80)
    for i, entry in enumerate(entries, 1):
        print(f"{i}. {entry['product']} - {entry['batch']} ({entry['year']})")
        print(f"   TTB ID: {entry['ttb_id']}")
    print()
    
    # Confirm
    response = input("Update CSV with these TTB IDs? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    # Update CSV
    updates = update_csv_with_ttb_ids(entries)
    
    print()
    print("=" * 80)
    print("✅ CSV Updated!")
    print()
    print(f"Updated {len(updates)} entries:")
    for update in updates:
        print(f"  • {update['product']} - {update['batch']} ({update['year']})")
        if update['old_ttb']:
            print(f"    Changed: {update['old_ttb']} → {update['new_ttb']}")
        else:
            print(f"    Added: {update['new_ttb']}")
    print()
    print("Run 'python3 scripts/manage_ttb_ids.py summary' to verify.")
    print()


if __name__ == '__main__':
    main()

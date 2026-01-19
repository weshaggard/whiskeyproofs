#!/usr/bin/env python3
"""
Update CSV file with TTB IDs from a results file.

This script takes a JSON file of TTB search results and updates
the CSV file with verified TTB IDs.

Usage:
    python3 .github/scripts/update_ttb_ids.py results.json [--verify] [--dry-run]
    
Options:
    --verify    Prompt for verification before each update
    --dry-run   Show what would be updated without making changes
    --csv FILE  Specify CSV file path (default: _data/whiskeyindex.csv)
"""

import csv
import json
import sys
import argparse


def load_results(results_file):
    """Load TTB search results from JSON file"""
    try:
        with open(results_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Results file not found: {results_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in results file: {e}")
        sys.exit(1)


def update_csv(csv_file, results, verify=False, dry_run=False):
    """Update CSV file with TTB IDs from results"""
    
    # Read the CSV
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False
    
    updates_made = 0
    skipped = 0
    
    # Process each result
    for line_num_str, ttb_results in results.items():
        line_num = int(line_num_str)
        row_index = line_num - 2  # CSV line to list index (header is line 1, data starts line 2)
        
        if row_index < 0 or row_index >= len(rows):
            print(f"Warning: Invalid line number {line_num}, skipping")
            skipped += 1
            continue
        
        row = rows[row_index]
        
        # Validate row has required columns
        required_cols = ['Name', 'Batch', 'ReleaseYear', 'TTB_ID']
        missing_cols = [col for col in required_cols if col not in row]
        if missing_cols:
            print(f"Warning: Row at line {line_num} missing columns {missing_cols}, skipping")
            skipped += 1
            continue
        
        # Get TTB ID from results (take first match if multiple)
        if isinstance(ttb_results, list) and len(ttb_results) > 0:
            ttb_id = ttb_results[0].get('ttb_id', '')
        elif isinstance(ttb_results, dict):
            ttb_id = ttb_results.get('ttb_id', '')
        else:
            ttb_id = str(ttb_results)
        
        if not ttb_id:
            print(f"Warning: No TTB ID found for line {line_num}, skipping")
            skipped += 1
            continue
        
        # Show what we're updating
        print(f"\nLine {line_num}: {row['Name']} - {row['Batch']} ({row['ReleaseYear']})")
        print(f"  Current TTB ID: {row.get('TTB_ID', '(empty)')}")
        print(f"  New TTB ID: {ttb_id}")
        
        # Ask for verification if requested
        if verify:
            response = input("  Update this entry? [y/N]: ").strip().lower()
            if response != 'y':
                print("  Skipped")
                skipped += 1
                continue
        
        if dry_run:
            print("  [DRY RUN] Would update")
        else:
            row['TTB_ID'] = ttb_id
            updates_made += 1
            print("  ✓ Updated")
    
    # Write updated CSV
    if not dry_run and updates_made > 0:
        try:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"\n✓ CSV file updated successfully")
        except Exception as e:
            print(f"\nError writing CSV: {e}")
            return False
    
    print(f"\nSummary:")
    print(f"  Updates made: {updates_made}")
    print(f"  Skipped: {skipped}")
    
    if dry_run:
        print(f"\n[DRY RUN] No changes were made to the CSV file")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Update CSV file with TTB IDs from search results'
    )
    parser.add_argument(
        'results',
        help='JSON file with TTB search results'
    )
    parser.add_argument(
        '--csv',
        default='_data/whiskeyindex.csv',
        help='Path to CSV file (default: _data/whiskeyindex.csv)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Prompt for verification before each update'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be updated without making changes'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("TTB ID Update Tool")
    print("=" * 60)
    print()
    
    if args.dry_run:
        print("Running in DRY RUN mode - no changes will be made")
        print()
    
    # Load results
    print(f"Loading results from: {args.results}")
    results = load_results(args.results)
    print(f"Found {len(results)} entries with TTB IDs")
    print()
    
    # Update CSV
    success = update_csv(args.csv, results, verify=args.verify, dry_run=args.dry_run)
    
    if success and not args.dry_run:
        print()
        print("=" * 60)
        print("Next steps:")
        print("=" * 60)
        print("1. Run validation: python3 .github/scripts/validate_whiskey_data.py")
        print("2. Review changes: git diff _data/whiskeyindex.csv")
        print("3. Commit if satisfied: git add _data/whiskeyindex.csv && git commit")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

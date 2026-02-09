
import json
import csv
import sys
import argparse

def load_results(results_file):
    with open(results_file, 'r') as f:
        return json.load(f)

def update_csv(csv_file, results, dry_run=False, exclude=None):
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    updates = 0
    skipped = 0
    
    exclude_list = [e.lower() for e in (exclude or [])]

    for line_num_str, ttb_list in results.items():
        line_num = int(line_num_str)
        row_idx = line_num - 2
        if row_idx < 0 or row_idx >= len(rows):
            continue
        
        row = rows[row_idx]
        if row['Name'].lower() in exclude_list:
            continue
            
        current_id = row.get('TTB_ID', '')
        if current_id:
            continue # Already has ID

        if not ttb_list:
            continue

        # Filter candidates
        # 1. Filter by Class/Type if possible. CSV Type "Bourbon" -> Class 101. "Rye" -> 102.
        # This is a heuristic.
        filtered = ttb_list
        csv_type = row.get('Type', '').lower()
        if 'bourbon' in csv_type:
            filtered = [r for r in filtered if r.get('Class/Type') == '101']
        elif 'rye' in csv_type:
            filtered = [r for r in filtered if r.get('Class/Type') == '102']
        
        if not filtered:
             # If filtering removed all, fall back to all (maybe special case)
             filtered = ttb_list
        
        # Check if all candidates are "same" product (Brand + Fanciful)
        first = filtered[0]
        brand = first.get('Brand Name', '')
        fanciful = first.get('Fanciful Name', '')
        
        is_consistent = True
        for r in filtered[1:]:
            if r.get('Brand Name', '') != brand or r.get('Fanciful Name', '') != fanciful:
                is_consistent = False
                break
        
        selected_id = None
        reason = ""

        # Strategy 1: High quality match (proof verified)
        high_quality = [r for r in filtered if r.get('match_quality', 0) >= 1.5]
        if high_quality:
            selected_id = high_quality[0]['ttb_id']
            reason = f"High quality match ({high_quality[0].get('match_quality')})"
        
        # Strategy 2: Unique match (after type filtering)
        elif len(filtered) == 1:
            selected_id = filtered[0]['ttb_id']
            reason = "Unique match"
            
        # Strategy 3: Consistent duplicates (same product, likely different sizes)
        elif is_consistent and len(filtered) > 0:
            selected_id = filtered[0]['ttb_id']
            reason = f"Consistent duplicates ({len(filtered)})"
            
        if selected_id:
            print(f"Line {line_num}: {row['Name']} ({row['ReleaseYear']}) -> {selected_id} [{reason}]")
            if not dry_run:
                row['TTB_ID'] = selected_id
            updates += 1
        else:
            # print(f"Skipping Line {line_num}: {len(filtered)} matches, not consistent/unique")
            skipped += 1

    if not dry_run and updates > 0:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved {updates} updates to {csv_file}")
    else:
        print(f"Found {updates} potential updates (Dry Run)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('results')
    parser.add_argument('--csv', default='_data/whiskeyindex.csv')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--exclude', nargs='+', help='List of names to exclude')
    args = parser.parse_args()
    
    update_csv(args.csv, load_results(args.results), dry_run=args.dry_run, exclude=args.exclude)

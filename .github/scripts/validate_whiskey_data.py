#!/usr/bin/env python3
"""
Validation script for whiskeyindex.csv
Checks data quality and sort order according to repository standards.
"""

import csv
import re
import sys
from collections import defaultdict


class ReverseStr:
    """Wrapper class for reverse string comparison (descending alphabetical order)"""
    def __init__(self, s):
        self.s = s
    def __lt__(self, other):
        return self.s > other.s
    def __le__(self, other):
        return self.s >= other.s
    def __gt__(self, other):
        return self.s < other.s
    def __ge__(self, other):
        return self.s <= other.s
    def __eq__(self, other):
        return self.s == other.s
    def __repr__(self):
        return f'ReverseStr({self.s!r})'


def extract_numeric_from_batch(batch):
    """Extract numeric value from batch for numeric sorting"""
    match = re.search(r'\b(\d+)\b', batch)
    if match:
        return int(match.group(1))
    return None


def batch_sort_key(batch, release_year):
    """
    Create a sort key for batch ordering (descending - newest/latest first).
    
    Handles various batch naming conventions:
    - Year-batch format (2025-04, 2024-03)
    - Seasonal batches (Fall 2025, Spring 2024)
    - Letter-number format (C925, B524, A123)  
    - Batch N format (Batch 15, Batch 2)
    - Numeric batches (18, 17, 16)
    - Chapter format (Chapter 9, Chapter 8)
    - Year-letter codes (25C, 24D, 23A)
    - Number prefix with text (6 - LA/NE, 5 - LL/LE)
    - Year with parenthetical (2017 (Other States))
    """
    
    # Handle year-batch format like "2025-04", "2024-03"
    year_batch_match = re.match(r'^(\d{4})-(\d+)', batch)
    if year_batch_match:
        year = int(year_batch_match.group(1))
        batch_num = int(year_batch_match.group(2))
        return (0, -year, -batch_num, batch)
    
    # Handle number prefix with text (e.g., "6 - LA/NE", "5 - LL/LE")
    # MUST come before seasonal check to handle "6 - LA/NE (Spring 2025)" correctly
    number_prefix_match = re.match(r'^(\d+)\s*-\s*', batch)
    if number_prefix_match:
        number = int(number_prefix_match.group(1))
        return (7, -int(release_year), -number, batch)
    
    # Handle seasonal batches (Fall/Spring)
    if 'Fall' in batch or 'Spring' in batch:
        year_match = re.search(r'(\d{4})', batch)
        year = int(year_match.group(1)) if year_match else int(release_year)
        season = 'Fall' if 'Fall' in batch else 'Spring'
        season_order = 0 if season == 'Fall' else 1
        return (8, -year, season_order, batch)
    
    # Handle ECBP-style letter-number format (C925, B524, A123, A314, A215)
    ecbp_match = re.match(r'^([A-Z])(\d+)$', batch)
    if ecbp_match and len(ecbp_match.group(2)) in [3, 2]:
        letter = ecbp_match.group(1)
        year = int(release_year)
        # C > B > A for descending (C is 3rd/latest batch of year)
        letter_value = ord(letter) - ord('A') + 1
        return (2, -year, -letter_value, batch)
    
    # Handle "Batch N" format
    if batch.startswith('Batch '):
        batch_num_match = re.search(r'Batch (\d+)', batch)
        if batch_num_match:
            batch_num = int(batch_num_match.group(1))
            return (3, -batch_num, batch)
    
    # Handle pure year batches (e.g., "2018", "2016") - MUST come before generic numeric check
    if batch.isdigit() and len(batch) == 4:
        year = int(batch)
        return (8, -year, batch)
    
    # Handle pure numeric batches (e.g., "18", "17", "16" for Stagg Jr)
    if batch.isdigit():
        return (4, -int(batch), batch)
    
    # Handle "Chapter N" format
    if 'Chapter' in batch:
        chapter_match = re.search(r'Chapter (\d+)', batch)
        if chapter_match:
            chapter_num = int(chapter_match.group(1))
            return (5, -chapter_num, batch)
    
    # Handle Stagg batch codes like "25C", "24D", "23A"
    batch_code_match = re.match(r'^(\d{2})([A-Z])$', batch)
    if batch_code_match:
        year_suffix = int(batch_code_match.group(1))
        letter = batch_code_match.group(2)
        year = 2000 + year_suffix
        letter_value = ord(letter) - ord('A') + 1
        return (6, -year, -letter_value, batch)
    
    # Handle year with parenthetical text (e.g., "2017 (Other States)", "2017 (FL/GA/KY)")
    year_paren_match = re.match(r'^(\d{4})\s*\(', batch)
    if year_paren_match:
        year = int(year_paren_match.group(1))
        # Sort alphabetically descending by the batch string
        return (8, -year, ReverseStr(batch))
    
    # Default: use release year and alphabetical descending
    return (99, -int(release_year), batch)


def validate_csv(filename):
    """Validate the CSV file for data quality and sort order"""
    
    # Read the CSV file
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return False
    
    all_valid = True
    
    print("=== Data Quality Checks ===\n")
    
    # 1. Check for missing required fields
    print("1. Checking required fields...")
    missing_fields = []
    for i, row in enumerate(rows, start=2):
        for field in ['Name', 'Batch', 'Proof', 'ReleaseYear', 'Distillery', 'Type']:
            if not row[field].strip():
                missing_fields.append(f"Line {i}: Missing {field} for {row['Name']}")
    
    if missing_fields:
        print(f"   ❌ Found {len(missing_fields)} missing fields:")
        for issue in missing_fields[:10]:
            print(f"      {issue}")
        if len(missing_fields) > 10:
            print(f"      ... and {len(missing_fields) - 10} more")
        all_valid = False
    else:
        print("   ✓ All required fields present")
    
    # 2. Check proof values
    print("\n2. Checking proof values...")
    invalid_proofs = []
    for i, row in enumerate(rows, start=2):
        proof = row['Proof'].strip()
        # Skip empty proofs (they'll be caught by missing fields check)
        if proof and not re.match(r'^[\d\.\-]+$', proof):
            invalid_proofs.append(f"Line {i}: Invalid proof '{proof}' for {row['Name']}")
    
    if invalid_proofs:
        print(f"   ❌ Found {len(invalid_proofs)} invalid proof values:")
        for issue in invalid_proofs[:10]:
            print(f"      {issue}")
        all_valid = False
    else:
        print("   ✓ All proof values valid")
    
    # 3. Check release years
    print("\n3. Checking release years...")
    invalid_years = []
    for i, row in enumerate(rows, start=2):
        year = row['ReleaseYear'].strip()
        if not re.match(r'^\d{4}$', year):
            invalid_years.append(f"Line {i}: Invalid year '{year}' for {row['Name']}")
        elif int(year) < 2000 or int(year) > 2030:
            invalid_years.append(f"Line {i}: Unusual year '{year}' for {row['Name']}")
    
    if invalid_years:
        print(f"   ⚠ Found {len(invalid_years)} year issues:")
        for issue in invalid_years[:10]:
            print(f"      {issue}")
    else:
        print("   ✓ All release years valid")
    
    # 4. Check for duplicates
    print("\n4. Checking for duplicates...")
    seen = set()
    duplicates = []
    for i, row in enumerate(rows, start=2):
        key = (row['Name'], row['Batch'], row['ReleaseYear'])
        if key in seen:
            duplicates.append(f"Line {i}: Duplicate {row['Name']} - {row['Batch']} ({row['ReleaseYear']})")
        seen.add(key)
    
    if duplicates:
        print(f"   ❌ Found {len(duplicates)} duplicates:")
        for issue in duplicates:
            print(f"      {issue}")
        all_valid = False
    else:
        print("   ✓ No duplicates found")
    
    # 5. Check sort order
    print("\n5. Checking sort order...")
    sort_issues = []
    
    # Group by product name
    products = defaultdict(list)
    for i, row in enumerate(rows, start=2):
        products[row['Name']].append((i, row))
    
    # Check alphabetical order of products
    product_names = list(products.keys())
    sorted_names = sorted(product_names)
    
    if product_names != sorted_names:
        print("   ❌ Products not in alphabetical order")
        # Find and show which products are out of order
        product_order_issues = []
        for i, (actual, expected) in enumerate(zip(product_names, sorted_names)):
            if actual != expected:
                product_order_issues.append(
                    f"Position {i+1}: Found '{actual}', expected '{expected}'"
                )
        
        if product_order_issues:
            print("   Product ordering issues:")
            for issue in product_order_issues[:5]:
                print(f"      {issue}")
            if len(product_order_issues) > 5:
                print(f"      ... and {len(product_order_issues) - 5} more")
        all_valid = False
    else:
        # Check batch order within each product
        for product_name, product_rows in products.items():
            prev_key = None
            prev_batch = None
            for line_num, row in product_rows:
                current_key = batch_sort_key(row['Batch'], row['ReleaseYear'])
                # Keys use negated values for descending, so current < prev is an error
                # Compare all elements of the sort key to properly validate ordering
                if prev_key is not None:
                    if current_key < prev_key:
                        sort_issues.append(
                            f"Line {line_num}: {product_name} batch '{row['Batch']}' ({row['ReleaseYear']}) " 
                            f"should come before '{prev_batch}' (sort keys: {current_key} < {prev_key})"
                        )
                prev_key = current_key
                prev_batch = row['Batch']
    
    if sort_issues:
        print(f"   ❌ Found {len(sort_issues)} sort order issues:")
        for issue in sort_issues[:10]:
            print(f"      {issue}")
        if len(sort_issues) > 10:
            print(f"      ... and {len(sort_issues) - 10} more")
        all_valid = False
    else:
        print("   ✓ Sort order correct (Name: ascending, Batch: descending)")
    
    # Summary
    print("\n=== Summary ===")
    print(f"Total entries: {len(rows)}")
    print(f"Unique products: {len(products)}")
    print(f"Years covered: {min(r['ReleaseYear'] for r in rows)} - {max(r['ReleaseYear'] for r in rows)}")
    
    if all_valid:
        print("\n✅ All checks passed!")
        return True
    else:
        print("\n❌ Validation failed - please fix the issues above")
        return False


if __name__ == '__main__':
    filename = '_data/whiskeyindex.csv'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    success = validate_csv(filename)
    sys.exit(0 if success else 1)

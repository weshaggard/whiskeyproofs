#!/usr/bin/env python3
"""Validate whiskeyindex.csv data quality, schema, and sort order."""

import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal


CSV_FIELDS = ('Name', 'Batch', 'Age', 'Proof', 'ReleaseYear',
              'Distillery', 'Type', 'TTB_ID', 'url')
REQUIRED_FIELDS = ('Name', 'Batch', 'Proof', 'ReleaseYear', 'Distillery', 'Type')
NUMBER = r'[0-9]+(?:\.[0-9]+)?'


class ReverseStr:
    """Compare strings in descending alphabetical order."""

    def __init__(self, value):
        self.s = value

    def __lt__(self, other):
        return self.s > other.s

    def __eq__(self, other):
        return isinstance(other, ReverseStr) and self.s == other.s

    def __repr__(self):
        return f'ReverseStr({self.s!r})'


def extract_numeric_from_batch(batch):
    """Extract a standalone numeric batch value."""
    match = re.search(r'\b([0-9]+)\b', batch)
    return int(match.group(1)) if match else None


def batch_sort_key(batch, release_year):
    """Return uniformly typed keys, including for mixed batch conventions.

    Preserve established pattern precedence. Year, seasonal, and parenthetical
    batches share chronological ordering. Pattern-specific text tie breakers
    retain existing ordering, with parenthetical variants descending.
    General variants group by descending name before descending release year.
    Invalid release years use a sentinel here and are diagnosed by validation.
    """
    year_text = release_year.split('-')[0]
    release = int(year_text) if re.fullmatch(r'[0-9]{4}', year_text) else 0

    def key(category, first=0, second=0, descending=False):
        return (category, first, second, '' if descending else batch,
                ReverseStr(batch if descending else ''), -release)

    match = re.match(r'^([0-9]{4})-([0-9]+)', batch)
    if match:
        return key(0, -int(match[1]), -int(match[2]))
    match = re.match(r'^([0-9]+)\s*-\s*', batch)
    if match:
        return key(7, -release, -int(match[1]))
    if 'Fall' in batch or 'Spring' in batch:
        match = re.search(r'[0-9]{4}', batch)
        year = int(match[0]) if match else release
        return key(8, -year, 0 if 'Fall' in batch else 1)
    match = re.fullmatch(r'([A-Z])([0-9]{2,3})', batch)
    if match:
        return key(2, -release, -ord(match[1]))
    match = re.match(r'^Batch ([0-9]+)', batch)
    if match:
        return key(3, -int(match[1]))
    if re.fullmatch(r'[0-9]{4}', batch):
        return key(8, -int(batch))
    if re.fullmatch(r'[0-9]+', batch):
        return key(4, -int(batch))
    match = re.search(r'\bChapter ([0-9]+)\b', batch)
    if match:
        return key(5, -int(match[1]))
    match = re.match(r'^Pact ([0-9]+)', batch)
    if match:
        return key(10, -int(match[1]))
    match = re.fullmatch(r'Series ([IVX]+|[0-9]+)', batch)
    if match:
        roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                     'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
        value = int(match[1]) if match[1].isdigit() else roman_map.get(match[1])
        if value is not None:
            return key(11, -value)
    match = re.fullmatch(r'([0-9]{2})([A-Z])', batch)
    if match:
        return key(6, -(2000 + int(match[1])), -ord(match[2]))
    match = re.match(r'^([0-9]{4})\s*\(', batch)
    if match:
        return key(8, -int(match[1]), descending=True)
    return key(99, descending=True)


def valid_proof(proof):
    """Accept positive numbers or ascending ranges, without integer decimals."""
    if not re.fullmatch(rf'{NUMBER}(?:-{NUMBER})?', proof):
        return False
    parts = proof.split('-')
    values = [Decimal(part) for part in parts]
    if any(value <= 0 for value in values):
        return False
    if any('.' in part and value == value.to_integral_value()
           for part, value in zip(parts, values)):
        return False
    return len(values) == 1 or values[0] <= values[1]


def valid_year(year):
    """Allow modern release years and historical standard-release ranges."""
    if re.fullmatch(r'[0-9]{4}-[0-9]{4}', year):
        start, end = map(int, year.split('-'))
        return 1900 <= start <= end <= 2030
    return bool(re.fullmatch(r'[0-9]{4}', year)) and 2000 <= int(year) <= 2030


def validate_csv(filename):
    """Report invalid data without crashing on malformed input."""
    issues = []
    rows = []
    try:
        with open(filename, encoding='utf-8-sig', newline='') as source:
            reader = csv.reader(source, strict=True)
            header = next(reader, None)
            if header is None:
                print('❌ Empty CSV file: missing header and data')
                return False
            if len(header) != len(set(header)):
                issues.append('Header: duplicate column names')
            missing = sorted(set(CSV_FIELDS) - set(header))
            unexpected = sorted(set(header) - set(CSV_FIELDS))
            if missing:
                issues.append(f"Header: missing columns: {', '.join(missing)}")
            if unexpected:
                issues.append(f"Header: unexpected columns: {', '.join(unexpected)}")
            if issues:
                for issue in issues:
                    print(f'❌ {issue}')
                return False
            for values in reader:
                line = reader.line_num
                if len(values) != len(header):
                    issues.append(
                        f'Line {line}: Malformed row: expected {len(header)} fields, '
                        f'found {len(values)}')
                    continue
                rows.append((line, dict(zip(header, (v.strip() for v in values)))))
    except (OSError, UnicodeError, csv.Error) as error:
        line = reader.line_num if 'reader' in locals() else '?'
        print(f'❌ Error reading CSV file at line {line}: {error}')
        return False

    if not rows:
        issues.append('CSV contains no data rows')

    products = defaultdict(list)
    seen = set()
    previous_name = None
    closed_products = set()
    for line, row in rows:
        name, batch, year = row['Name'], row['Batch'], row['ReleaseYear']
        for field in REQUIRED_FIELDS:
            if not row[field]:
                issues.append(f'Line {line}: Missing {field} for {name}')
        if row['Proof'] and not valid_proof(row['Proof']):
            issues.append(f"Line {line}: Invalid proof '{row['Proof']}' for {name}")
        if not valid_year(year):
            issues.append(f"Line {line}: Invalid release year '{year}' for {name}")
        identity = (name, batch, year)
        if identity in seen:
            issues.append(f'Line {line}: Duplicate {name} - {batch} ({year})')
        seen.add(identity)
        if previous_name is not None and name != previous_name:
            closed_products.add(previous_name)
            if name in closed_products:
                issues.append(f"Line {line}: Product '{name}' is not contiguous")
            if name < previous_name:
                issues.append(f"Line {line}: Products not in alphabetical order: "
                              f"'{name}' follows '{previous_name}'")
        previous_name = name
        products[name].append((line, row))

    for name, entries in products.items():
        previous_key = None
        previous_batch = None
        for line, row in entries:
            current_key = batch_sort_key(row['Batch'], row['ReleaseYear'])
            if previous_key is not None and current_key < previous_key:
                issues.append(f"Line {line}: {name} batch '{row['Batch']}' "
                              f"should come before '{previous_batch}'")
            previous_key, previous_batch = current_key, row['Batch']

    print('=== Data Quality and Sort Checks ===')
    for issue in issues:
        print(f'❌ {issue}')
    print(f'\nTotal entries: {len(rows)}')
    print(f'Unique products: {len(products)}')
    print(f'Validation errors: {len(issues)}')
    print('\n❌ Validation failed' if issues else '\n✅ All checks passed!')
    return not issues


if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else '_data/whiskeyindex.csv'
    sys.exit(0 if validate_csv(filename) else 1)

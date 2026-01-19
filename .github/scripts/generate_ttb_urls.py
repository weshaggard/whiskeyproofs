#!/usr/bin/env python3
"""
Generate TTB COLA Public Registry search URLs for manual lookup.

This script creates search URLs for whiskey entries without TTB IDs,
allowing for manual verification in a browser.

Usage:
    python3 .github/scripts/generate_ttb_urls.py [--limit N] [--output FILE]
    
Options:
    --limit N      Limit to first N entries without TTB IDs
    --output FILE  Save URLs to file (default: print to console)
    --html         Generate HTML file with clickable links
"""

import csv
import sys
import argparse
from urllib.parse import urlencode, quote


def extract_brand_name(name):
    """Extract brand name from product name"""
    split_terms = [
        'Cask Strength',
        'Barrel Proof',
        'Single Barrel',
        'Small Batch',
        'Limited Edition',
        'Special Release',
        'Straight',
    ]
    
    brand = name
    for term in split_terms:
        if term in name:
            brand = name.split(term)[0].strip()
            break
            
    return brand


def generate_search_url(name, batch, proof, release_year):
    """Generate TTB COLA Public Registry search URL"""
    brand = extract_brand_name(name)
    
    # The TTB search form uses these parameters (may need adjustment)
    # This is a basic URL - the actual form may have different parameters
    base_url = "https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do"
    
    # Create a search URL with the brand name
    # Note: The actual search requires form submission, but this provides a starting point
    return f"{base_url}?brandName={quote(brand)}"


def main():
    parser = argparse.ArgumentParser(
        description='Generate TTB COLA search URLs for whiskey entries'
    )
    parser.add_argument(
        '--csv',
        default='_data/whiskeyindex.csv',
        help='Path to CSV file (default: _data/whiskeyindex.csv)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of entries to process'
    )
    parser.add_argument(
        '--output',
        help='Output file to save URLs'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML file with clickable links'
    )
    
    args = parser.parse_args()
    
    # Read CSV
    try:
        with open(args.csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return 1
    
    # Filter entries without TTB IDs
    entries = [
        row for row in rows
        if not row.get('TTB_ID', '').strip()
    ]
    
    print(f"Found {len(entries)} entries without TTB IDs")
    
    if args.limit:
        entries = entries[:args.limit]
        print(f"Limited to first {len(entries)} entries")
    
    # Generate output
    if args.html:
        output = generate_html(entries)
        ext = '.html'
    else:
        output = generate_text(entries)
        ext = '.txt'
    
    # Save or print
    if args.output:
        output_file = args.output
        if not output_file.endswith(ext):
            output_file += ext
        
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"\nOutput saved to: {output_file}")
    else:
        print("\n" + "=" * 70)
        print(output)
    
    return 0


def generate_text(entries):
    """Generate plain text output"""
    lines = []
    lines.append("TTB COLA Public Registry Search URLs")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Copy these URLs into your browser to search manually:")
    lines.append("")
    
    for row in entries:
        name = row['Name']
        batch = row['Batch']
        proof = row['Proof']
        year = row['ReleaseYear']
        brand = extract_brand_name(name)
        
        lines.append(f"{name} - {batch} ({year}) - {proof} proof")
        lines.append(f"  Brand: {brand}")
        lines.append(f"  Search: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do")
        lines.append(f"  Enter brand name: {brand}")
        lines.append(f"  Filter by year: {year}, proof: {proof}")
        lines.append("")
    
    return "\n".join(lines)


def generate_html(entries):
    """Generate HTML output with clickable links"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>TTB COLA Search Helper</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1000px; 
            margin: 20px auto; 
            padding: 20px;
        }
        h1 { color: #333; }
        .entry { 
            border: 1px solid #ddd; 
            margin: 10px 0; 
            padding: 15px; 
            background: #f9f9f9;
        }
        .product-name { 
            font-weight: bold; 
            font-size: 1.1em; 
            color: #0066cc;
        }
        .details { 
            color: #666; 
            margin: 5px 0;
        }
        .search-link { 
            display: inline-block;
            margin-top: 10px;
            padding: 8px 15px;
            background: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .search-link:hover {
            background: #0052a3;
        }
        .instructions {
            background: #ffffcc;
            border: 1px solid #ffcc00;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>TTB COLA Search Helper</h1>
    
    <div class="instructions">
        <strong>Instructions:</strong>
        <ol>
            <li>Click "Search TTB COLA" button for each entry</li>
            <li>Enter the brand name in the search form</li>
            <li>Filter results by year and proof to find exact match</li>
            <li>Copy the 14-digit TTB ID from the matching result</li>
            <li>Add the TTB ID to the CSV file</li>
        </ol>
    </div>
"""
    
    for row in entries:
        name = row['Name']
        batch = row['Batch']
        proof = row['Proof']
        year = row['ReleaseYear']
        brand = extract_brand_name(name)
        
        html += f"""
    <div class="entry">
        <div class="product-name">{name}</div>
        <div class="details">
            Batch: {batch} | Proof: {proof} | Year: {year}
        </div>
        <div class="details">
            <strong>Brand to search:</strong> {brand}
        </div>
        <a href="https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do" 
           target="_blank" 
           class="search-link">Search TTB COLA</a>
    </div>
"""
    
    html += """
</body>
</html>
"""
    return html


if __name__ == '__main__':
    sys.exit(main())

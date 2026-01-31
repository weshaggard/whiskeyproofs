#!/usr/bin/env python3
"""
Update existing label README files to add Origin Code and Product Class/Type.

This script goes through all label directories and updates their README.md files
to include Origin Code and Product Class/Type metadata if they're missing.

Usage:
    python3 .github/scripts/update_label_readmes.py
"""

import os
import sys
import time
import urllib.parse
import urllib.request
import http.cookiejar
import ssl
import re
from pathlib import Path

# Base URLs
TTB_BASE_URL = "https://ttbonline.gov/colasonline"
DETAIL_URL = f"{TTB_BASE_URL}/viewColaDetails.do?action=publicFormDisplay&ttbid="

# Create SSL context that doesn't verify certificates (TTB has cert issues)
ssl_context = ssl._create_unverified_context()

# Create cookie jar for session management
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookie_jar),
    urllib.request.HTTPSHandler(context=ssl_context)
)
urllib.request.install_opener(opener)

def extract_metadata_from_ttb(ttbid):
    """Extract Origin Code and Product Class/Type from TTB page."""
    url = DETAIL_URL + ttbid
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Check for captcha - if detected, we're blocked
            if 'captcha' in html.lower() or 'recaptcha' in html.lower():
                print(f"⚠️  CAPTCHA DETECTED - stopping processing")
                return 'CAPTCHA', None
            
            # Extract Origin Code (OR) and Product Class/Type (CT)
            metadata = {}
            
            # These appear as label-data pairs in the HTML
            label_sections = re.findall(r'<div class="label">([^<]+)</div>\s*<div class="data">([^<]+)</div>', html)
            for label, data in label_sections:
                import html as html_module
                label_clean = html_module.unescape(label.strip()).rstrip(':').strip()
                data_clean = html_module.unescape(data.strip())
                
                if label_clean == 'OR':
                    metadata['origin_code'] = data_clean
                elif label_clean == 'CT':
                    metadata['product_class_type'] = data_clean
            
            return 'SUCCESS', metadata
    except Exception as e:
        print(f"  Error fetching TTB page for {ttbid}: {e}")
        return 'ERROR', None

def update_readme(readme_path, ttbid):
    """Update a README file to add Origin Code and Product Class/Type if missing."""
    
    # Read current README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has Origin Code and Product Class/Type
    if 'Origin Code:' in content and 'Product Class/Type:' in content:
        print(f"  ✓ Already has both fields")
        return 'skipped'
    
    # Fetch metadata from TTB
    status, metadata = extract_metadata_from_ttb(ttbid)
    
    if status == 'CAPTCHA':
        return 'captcha'
    
    if status == 'ERROR' or not metadata:
        print(f"  ✗ Failed to fetch metadata")
        return 'error'
    
    # Check what we got
    has_origin = metadata.get('origin_code')
    has_product = metadata.get('product_class_type')
    
    if not has_origin and not has_product:
        print(f"  ⚠️  No Origin Code or Product Class/Type found on TTB page")
        return 'not_found'
    
    # Update the README content
    lines = content.split('\n')
    new_lines = []
    inserted = False
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Insert after Issue Date line and before Source line
        if not inserted and line.startswith('**Issue Date:**'):
            # Skip the next line if it's blank (to avoid double blank lines)
            if i + 1 < len(lines) and not lines[i + 1].strip():
                i += 1  # Skip the blank line, we'll add it back
            
            # Add blank line, then Origin Code if available and not already present
            new_lines.append('')
            if has_origin and 'Origin Code:' not in content:
                new_lines.append(f"**Origin Code:** {metadata['origin_code']}")
                new_lines.append('')
            
            # Add Product Class/Type if available and not already present
            if has_product and 'Product Class/Type:' not in content:
                new_lines.append(f"**Product Class/Type:** {metadata['product_class_type']}")
                new_lines.append('')
            
            inserted = True
        
        i += 1
    
    if not inserted:
        print(f"  ⚠️  Could not find Issue Date line to insert after")
        return 'error'
    
    # Write updated content
    new_content = '\n'.join(new_lines)
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    added = []
    if has_origin and 'Origin Code:' not in content:
        added.append('Origin Code')
    if has_product and 'Product Class/Type:' not in content:
        added.append('Product Class/Type')
    
    if added:
        print(f"  ✓ Added: {', '.join(added)}")
        return 'updated'
    else:
        print(f"  ✓ Already present")
        return 'skipped'

def main():
    # Get repository root
    repo_root = Path(__file__).parent.parent.parent
    labels_dir = repo_root / 'labels'
    
    if not labels_dir.exists():
        print(f"Error: Labels directory not found at {labels_dir}")
        return 1
    
    # Get all label directories
    label_dirs = sorted([d for d in labels_dir.iterdir() if d.is_dir()])
    
    print(f"Found {len(label_dirs)} label directories\n")
    
    # Process each directory
    stats = {
        'updated': 0,
        'skipped': 0,
        'error': 0,
        'not_found': 0,
        'captcha': False
    }
    
    for i, label_dir in enumerate(label_dirs, 1):
        ttbid = label_dir.name
        readme_path = label_dir / 'README.md'
        
        if not readme_path.exists():
            print(f"[{i}/{len(label_dirs)}] {ttbid}: No README.md found")
            stats['error'] += 1
            continue
        
        print(f"[{i}/{len(label_dirs)}] {ttbid}:")
        
        result = update_readme(readme_path, ttbid)
        
        if result == 'captcha':
            print(f"\n{'='*60}")
            print(f"⚠️  CAPTCHA DETECTED - Stopping processing")
            print(f"{'='*60}\n")
            stats['captcha'] = True
            break
        
        stats[result] = stats.get(result, 0) + 1
        
        # Small delay to be nice to the server
        time.sleep(0.5)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Updated: {stats['updated']}")
    print(f"  Skipped (already had fields): {stats['skipped']}")
    print(f"  Not found on TTB page: {stats['not_found']}")
    print(f"  Errors: {stats['error']}")
    if stats['captcha']:
        print(f"  ⚠️  Processing stopped due to CAPTCHA")
    print(f"{'='*60}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Download label images for all TTB IDs in whiskeyindex.csv

This script can be run manually or in automation to download TTB COLA label images.
It reads unique TTB IDs from _data/whiskeyindex.csv and downloads the front and back
label images for each one.

Usage:
    python3 .github/scripts/download_ttb_labels.py [--limit N] [--skip-existing]

Options:
    --limit N         Only process the first N TTB IDs (for testing)
    --skip-existing   Skip TTB IDs that already have a folder with images
    --help           Show this help message
"""

import csv
import os
import sys
import time
import urllib.parse
import urllib.request
import http.cookiejar
import ssl
import argparse
from pathlib import Path

# Base URLs
TTB_BASE_URL = "https://ttbonline.gov/colasonline"
DETAIL_URL = f"{TTB_BASE_URL}/viewColaDetails.do?action=publicFormDisplay&ttbid="
ATTACHMENT_URL = f"{TTB_BASE_URL}/publicViewAttachment.do"

# Create SSL context that doesn't verify certificates (TTB has cert issues)
ssl_context = ssl._create_unverified_context()

# Create cookie jar for session management
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(cookie_jar),
    urllib.request.HTTPSHandler(context=ssl_context)
)
urllib.request.install_opener(opener)

def get_unique_ttbids(csv_file):
    """Extract unique TTB IDs from the CSV file."""
    ttbids = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ttbid = row.get('TTB_ID', '').strip()
            if ttbid:
                ttbids.add(ttbid)
    return sorted(ttbids)

def download_file(url, output_path):
    """Download a file from URL to output_path using session cookies."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            
            # Check if we got HTML instead of an image
            if data.startswith(b'<html') or data.startswith(b'<!DOCTYPE'):
                return False
            
            # Check if file is too small (likely an error)
            if len(data) < 1000:
                return False
            
            with open(output_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False

def extract_label_images(ttbid):
    """Extract label image filenames from TTB page and establish session."""
    url = DETAIL_URL + ttbid
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Find image URLs in the HTML
            # Look for publicViewAttachment.do?filename=...&filetype=l
            images = []
            
            # Simple pattern matching for label images
            import re
            pattern = r'publicViewAttachment\.do\?filename=([^"&]+)&amp;filetype=l'
            matches = re.findall(pattern, html)
            
            for filename in matches:
                # Decode HTML entities and URL encoding
                decoded = urllib.parse.unquote(filename)
                images.append({
                    'filename': decoded,
                    'url_param': filename  # Keep original for URL
                })
            
            return images
    except Exception as e:
        print(f"  Error fetching TTB page for {ttbid}: {e}")
        return []

def download_ttb_labels(ttbid, labels_dir, skip_existing=True):
    """Download label images for a given TTB ID."""
    ttbid_dir = labels_dir / ttbid
    
    # Skip if directory already exists and has images
    if skip_existing and ttbid_dir.exists():
        existing_images = list(ttbid_dir.glob('*.jpg')) + list(ttbid_dir.glob('*.png'))
        if len(existing_images) >= 1:  # At least one label
            print(f"Skipping {ttbid} - already has {len(existing_images)} images")
            return 'skipped'
    
    print(f"Processing {ttbid}...")
    
    # Create directory
    ttbid_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract label image filenames (this also establishes session)
    images = extract_label_images(ttbid)
    
    if not images:
        print(f"  No label images found for {ttbid}")
        # Clean up empty directory
        try:
            ttbid_dir.rmdir()
        except:
            pass
        return 'failed'
    
    print(f"  Found {len(images)} label images")
    
    # Download each image
    success_count = 0
    for idx, img_info in enumerate(images):
        filename = img_info['filename']
        url_param = img_info['url_param']
        
        # Determine output filename based on content
        if 'FL' in filename.upper() or 'FRONT' in filename.upper() or 'FRT' in filename.upper():
            output_name = 'front_label.jpg'
        elif 'BL' in filename.upper() or 'BACK' in filename.upper():
            output_name = 'back_label.jpg'
        else:
            # Generic naming for other labels
            output_name = f'label_{idx+1}.jpg'
        
        output_path = ttbid_dir / output_name
        
        # Build download URL - use the URL parameter as-is (already encoded in HTML)
        download_url = f"{ATTACHMENT_URL}?filename={url_param}&filetype=l"
        
        print(f"  Downloading {output_name}...")
        if download_file(download_url, output_path):
            success_count += 1
            print(f"    ✓ Saved to {output_name}")
        else:
            print(f"    ✗ Failed to download {output_name}")
        
        # Small delay to be nice to the server
        time.sleep(0.5)
    
    if success_count == 0:
        # Clean up if no images were downloaded
        try:
            ttbid_dir.rmdir()
        except:
            pass
        return 'failed'
    
    # Create README
    readme_path = ttbid_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(f"# TTB COLA Label Images - TTBID {ttbid}\n\n")
        f.write(f"This folder contains the label images for TTB ID: {ttbid}\n\n")
        f.write(f"## Source\n")
        f.write(f"https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttbid}\n\n")
        f.write(f"## Label Images\n")
        for img_file in sorted(ttbid_dir.glob('*.jpg')):
            f.write(f"- `{img_file.name}`\n")
        f.write(f"\n## Download Date\n")
        from datetime import datetime
        f.write(f"{datetime.now().strftime('%B %d, %Y')}\n")
    
    return 'success'

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Download TTB COLA label images for all TTB IDs in whiskeyindex.csv'
    )
    parser.add_argument('--limit', type=int, help='Only process first N TTB IDs (for testing)')
    parser.add_argument('--skip-existing', action='store_true', default=True,
                        help='Skip TTB IDs that already have images (default: True)')
    parser.add_argument('--no-skip-existing', action='store_false', dest='skip_existing',
                        help='Re-download all TTB IDs even if they exist')
    args = parser.parse_args()
    
    # Get repository root
    repo_root = Path(__file__).parent.parent.parent
    csv_file = repo_root / '_data' / 'whiskeyindex.csv'
    labels_dir = repo_root / 'labels'
    
    # Create labels directory
    labels_dir.mkdir(exist_ok=True)
    
    # Get unique TTB IDs
    ttbids = get_unique_ttbids(csv_file)
    
    # Apply limit if specified
    if args.limit:
        ttbids = ttbids[:args.limit]
        print(f"Processing first {args.limit} TTB IDs (limited for testing)")
    
    print(f"Found {len(ttbids)} unique TTB IDs to process")
    print(f"Skip existing: {args.skip_existing}\n")
    
    # Process each TTB ID
    success = 0
    failed = 0
    skipped = 0
    
    for i, ttbid in enumerate(ttbids, 1):
        print(f"\n[{i}/{len(ttbids)}] ", end='')
        
        result = download_ttb_labels(ttbid, labels_dir, skip_existing=args.skip_existing)
        
        if result == 'success':
            success += 1
        elif result == 'skipped':
            skipped += 1
        else:
            failed += 1
        
        # Be nice to the server - delay between requests
        if i < len(ttbids):
            time.sleep(1)
    
    print(f"\n\n{'='*60}")
    print(f"Summary:")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Total:   {len(ttbids)}")
    print(f"{'='*60}")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Download label images for all TTB IDs in whiskeyindex.csv

This script can be run manually or in automation to download TTB COLA label images.
It reads unique TTB IDs from _data/whiskeyindex.csv and downloads the front and back
label images for each one.

Usage:
    # Download all TTB IDs
    python3 .github/scripts/download_ttb_labels.py
    
    # Download a specific TTB ID
    python3 .github/scripts/download_ttb_labels.py --ttbid 24002001000457
    
    # Download with options
    python3 .github/scripts/download_ttb_labels.py --limit 10 --skip-existing

Options:
    --ttbid TTBID     Download labels for a specific TTB ID only
    --limit N         Only process the first N TTB IDs (for testing)
    --skip-existing   Skip TTB IDs that already have a folder with images (default)
    --no-skip-existing Re-download all TTB IDs even if they exist
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

def extract_label_images_and_metadata(ttbid):
    """Extract label image filenames and metadata from TTB page and establish session."""
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
                print(f"\n{'='*60}")
                print(f"⚠️  CAPTCHA DETECTED - Machine is blocked!")
                print(f"{'='*60}")
                print(f"The TTB website has returned a captcha challenge.")
                print(f"Processing has been stopped to avoid further blocking.")
                print(f"Please wait before running another batch.")
                print(f"{'='*60}\n")
                # Return a special value to signal captcha
                return 'CAPTCHA_DETECTED', {}
            
            # Find image URLs in the HTML
            # Look for publicViewAttachment.do?filename=...&filetype=l
            images = []
            
            # Simple pattern matching for label images
            # Match both &amp; (HTML entity) and & (raw)
            import re
            pattern = r'publicViewAttachment\.do\?filename=([^"&]+)&(?:amp;)?filetype=l'
            matches = re.findall(pattern, html)
            
            for filename in matches:
                # Decode HTML entities and URL encoding
                decoded = urllib.parse.unquote(filename)
                images.append({
                    'filename': decoded,
                    'url_param': filename  # Keep original for URL
                })
            
            # Extract metadata from the page
            metadata = {}
            
            # Extract Brand Name (field 6)
            brand_pattern = r'6\.\s*BRAND NAME.*?<div class="data">([^<]+)</div>'
            brand_match = re.search(brand_pattern, html, re.DOTALL | re.IGNORECASE)
            if brand_match:
                import html as html_module
                metadata['brand_name'] = html_module.unescape(brand_match.group(1).strip())
            
            # Extract Fanciful Name (field 7)
            fanciful_pattern = r'7\.\s*FANCIFUL NAME.*?<div class="data">([^<]+)</div>'
            fanciful_match = re.search(fanciful_pattern, html, re.DOTALL | re.IGNORECASE)
            if fanciful_match:
                import html as html_module
                metadata['fanciful_name'] = html_module.unescape(fanciful_match.group(1).strip())
            
            # Extract Issue Date (various possible patterns)
            issue_date_patterns = [
                r'Issue Date.*?<div class="data">([^<]+)</div>',
                r'Approval Date.*?<div class="data">([^<]+)</div>',
                r'Date Issued.*?<div class="data">([^<]+)</div>'
            ]
            for pattern in issue_date_patterns:
                date_match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if date_match:
                    import html as html_module
                    metadata['issue_date'] = html_module.unescape(date_match.group(1).strip())
                    break
            
            # Extract Origin Code (OR) and Product Class/Type (CT)
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
            
            return images, metadata
    except Exception as e:
        print(f"  Error fetching TTB page for {ttbid}: {e}")
        return [], {}

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
    
    # Extract label image filenames and metadata (this also establishes session)
    result = extract_label_images_and_metadata(ttbid)
    
    # Check if we got a captcha response
    if result[0] == 'CAPTCHA_DETECTED':
        # Clean up directory and signal to stop processing
        try:
            ttbid_dir.rmdir()
        except:
            pass
        return 'captcha'
    
    images, metadata = result
    
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
    downloaded_images = []
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
        
        # Build download URL - properly encode the filename parameter
        encoded_filename = urllib.parse.quote(filename)
        download_url = f"{ATTACHMENT_URL}?filename={encoded_filename}&filetype=l"
        
        print(f"  Downloading {output_name}...")
        if download_file(download_url, output_path):
            success_count += 1
            downloaded_images.append(output_name)
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
    
    # Create README with embedded images and metadata
    readme_path = ttbid_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(f"# TTB COLA Label Images - TTBID {ttbid}\n\n")
        
        # Add metadata if available
        if metadata.get('brand_name'):
            f.write(f"**Brand Name:** {metadata['brand_name']}\n\n")
        if metadata.get('fanciful_name'):
            f.write(f"**Fanciful Name:** {metadata['fanciful_name']}\n\n")
        if metadata.get('issue_date'):
            f.write(f"**Issue Date:** {metadata['issue_date']}\n\n")
        if metadata.get('origin_code'):
            f.write(f"**Origin Code:** {metadata['origin_code']}\n\n")
        if metadata.get('product_class_type'):
            f.write(f"**Product Class/Type:** {metadata['product_class_type']}\n\n")
        
        f.write(f"**Source:** [TTB Public COLA Registry](https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={ttbid})\n\n")
        
        f.write(f"## Label Images\n\n")
        
        # Embed images with markdown syntax
        for img_file in sorted(ttbid_dir.glob('*.jpg')):
            img_name = img_file.name
            # Create a nice display name
            display_name = img_name.replace('_', ' ').replace('.jpg', '').title()
            f.write(f"### {display_name}\n\n")
            f.write(f"![{display_name}](./{img_name})\n\n")
    
    return 'success'

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Download TTB COLA label images for all TTB IDs in whiskeyindex.csv'
    )
    parser.add_argument('--ttbid', type=str, help='Download labels for a specific TTB ID only')
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
    
    # Handle single TTB ID mode
    if args.ttbid:
        ttbids = [args.ttbid]
        print(f"Processing single TTB ID: {args.ttbid}\n")
    else:
        # Get unique TTB IDs from CSV
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
    captcha_detected = False
    
    for i, ttbid in enumerate(ttbids, 1):
        print(f"\n[{i}/{len(ttbids)}] ", end='')
        
        result = download_ttb_labels(ttbid, labels_dir, skip_existing=args.skip_existing)
        
        if result == 'success':
            success += 1
        elif result == 'skipped':
            skipped += 1
        elif result == 'captcha':
            # Captcha detected - stop processing immediately
            captcha_detected = True
            print(f"\n{'='*60}")
            print(f"❌ STOPPED: Captcha detected on TTB ID {ttbid}")
            print(f"{'='*60}")
            print(f"Processed {i-1} of {len(ttbids)} TTB IDs before blocking.")
            print(f"Please wait before running another batch.")
            print(f"{'='*60}\n")
            break
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
    if captcha_detected:
        print(f"  ⚠️  Captcha: BLOCKED (stopped processing)")
    print(f"  Total:   {len(ttbids)}")
    print(f"{'='*60}")
    
    return 0 if (failed == 0 and not captcha_detected) else 1

if __name__ == '__main__':
    sys.exit(main())

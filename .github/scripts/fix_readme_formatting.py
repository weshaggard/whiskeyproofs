#!/usr/bin/env python3
"""
Fix formatting in label README files to ensure proper blank line after Issue Date.

This script goes through all label directories and fixes the formatting
to ensure there's a blank line between Issue Date and Origin Code.
"""

import os
import sys
from pathlib import Path

def fix_readme_formatting(readme_path):
    """Fix formatting in a README file."""
    
    # Read current README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has the fields we're looking for
    if 'Issue Date:' not in content or 'Origin Code:' not in content:
        return 'skipped'
    
    lines = content.split('\n')
    new_lines = []
    fixed = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Check if this is an Issue Date line followed directly by Origin Code
        if line.startswith('**Issue Date:**') and i + 1 < len(lines):
            next_line = lines[i + 1]
            
            # If the next line is Origin Code (missing blank line), add one
            if next_line.startswith('**Origin Code:**'):
                new_lines.append('')
                fixed = True
    
    if not fixed:
        return 'no_change'
    
    # Write updated content
    new_content = '\n'.join(new_lines)
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return 'fixed'

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
        'fixed': 0,
        'no_change': 0,
        'skipped': 0
    }
    
    for i, label_dir in enumerate(label_dirs, 1):
        ttbid = label_dir.name
        readme_path = label_dir / 'README.md'
        
        if not readme_path.exists():
            continue
        
        result = fix_readme_formatting(readme_path)
        stats[result] = stats.get(result, 0) + 1
        
        if result == 'fixed':
            print(f"[{i}/{len(label_dirs)}] {ttbid}: Fixed formatting")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Fixed: {stats['fixed']}")
    print(f"  No change needed: {stats['no_change']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"{'='*60}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Analyze Product Class/Type codes in TTB COLA label README files.

This script scans all label README files in the repository and generates
a summary of Product Class/Type distributions, including counts of labels
without type information and identification of any types outside the
standard whiskey range (100-150).

Usage:
    python3 .github/scripts/analyze_product_types.py [--output FILE]

Options:
    --output FILE    Write summary to specified file (default: labels/PRODUCT_TYPE_SUMMARY.md)
    --json          Output in JSON format
    --help          Show this help message
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def find_repo_root():
    """Find the repository root directory."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("Could not find repository root (no .git directory found)")

def analyze_product_types(repo_root):
    """Analyze Product Class/Type codes in all label READMEs."""
    labels_dir = repo_root / "labels"
    
    total_readmes = 0
    with_type = 0
    without_type = []
    product_types = defaultdict(list)
    outside_range = defaultdict(list)
    
    # Process all README files
    for readme_path in sorted(labels_dir.glob("*/README.md")):
        total_readmes += 1
        ttbid = readme_path.parent.name
        
        content = readme_path.read_text()
        
        # Look for Product Class/Type
        match = re.search(r'\*\*Product Class/Type:\*\* (\d+)', content)
        
        if match:
            with_type += 1
            product_type = int(match.group(1))
            
            # Count product types
            product_types[product_type].append(ttbid)
            
            # Check if outside 100-150 range
            if product_type < 100 or product_type > 150:
                outside_range[product_type].append(ttbid)
        else:
            without_type.append(ttbid)
    
    return {
        'total_readmes': total_readmes,
        'with_type': with_type,
        'without_type': without_type,
        'product_types': dict(product_types),
        'outside_range': dict(outside_range),
        'unique_types': len(product_types)
    }

def generate_markdown_summary(data):
    """Generate markdown summary document."""
    lines = []
    lines.append("# TTB Label Product Type Summary")
    lines.append("")
    lines.append(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append("This document provides a summary of Product Class/Type codes found in the TTB COLA label README files.")
    lines.append("")
    
    # Overview section
    lines.append("## Overview")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total label README files | {data['total_readmes']} |")
    lines.append(f"| READMEs with Product Class/Type field | {data['with_type']} |")
    lines.append(f"| READMEs without Product Class/Type field | {len(data['without_type'])} |")
    lines.append(f"| Unique product types found | {data['unique_types']} |")
    lines.append("")
    
    # Distribution table
    lines.append("## Product Class/Type Distribution")
    lines.append("")
    lines.append("The following table shows all Product Class/Type codes found in the label READMEs, sorted by type code:")
    lines.append("")
    lines.append("| Product Type | Count | Percentage | In Range (100-150)? |")
    lines.append("|--------------|-------|------------|---------------------|")
    
    total_with_type = data['with_type']
    for pt in sorted(data['product_types'].keys()):
        count = len(data['product_types'][pt])
        percentage = (count / total_with_type * 100) if total_with_type > 0 else 0
        in_range = "✓ Yes" if 100 <= pt <= 150 else "✗ NO"
        lines.append(f"| {pt} | {count} | {percentage:.1f}% | {in_range} |")
    
    lines.append(f"| **Total** | **{total_with_type}** | **100%** | - |")
    lines.append("")
    lines.append("*Percentages are calculated from the " + str(total_with_type) + " READMEs that have a Product Class/Type field.*")
    lines.append("")
    
    # Outside range section
    lines.append("## Product Types Outside 100-150 Range")
    lines.append("")
    
    if data['outside_range']:
        lines.append(f"**Found:** {len(data['outside_range'])} product type(s) outside the 100-150 range")
        lines.append("")
        for pt in sorted(data['outside_range'].keys()):
            lines.append(f"### Product Type {pt}")
            lines.append("")
            lines.append(f"**Count:** {len(data['outside_range'][pt])} label(s)")
            lines.append("")
            lines.append("**TTB IDs:**")
            for ttbid in sorted(data['outside_range'][pt]):
                lines.append(f"- {ttbid}")
            lines.append("")
    else:
        lines.append("**Result:** NONE")
        lines.append("")
        lines.append("All " + str(total_with_type) + " label READMEs that contain a Product Class/Type field have values within the 100-150 range. No product types were found outside this range.")
        lines.append("")
    
    # Most common types
    lines.append("## Most Common Product Types")
    lines.append("")
    
    sorted_types = sorted(data['product_types'].items(), key=lambda x: len(x[1]), reverse=True)
    for i, (pt, ttbids) in enumerate(sorted_types[:5], 1):
        count = len(ttbids)
        percentage = (count / total_with_type * 100) if total_with_type > 0 else 0
        lines.append(f"{i}. **Type {pt}** - {count} labels ({percentage:.1f}%)")
    
    lines.append("")
    top5_total = sum(len(ttbids) for pt, ttbids in sorted_types[:5])
    top5_pct = (top5_total / total_with_type * 100) if total_with_type > 0 else 0
    lines.append(f"These top 5 product types account for {top5_pct:.1f}% of all labels with a Product Class/Type field.")
    lines.append("")
    
    # Labels without type
    lines.append("## Labels Without Product Class/Type")
    lines.append("")
    lines.append(f"**Count:** {len(data['without_type'])} labels ({len(data['without_type'])/data['total_readmes']*100:.1f}% of all labels)")
    lines.append("")
    lines.append("The Product Class/Type field is missing from " + str(len(data['without_type'])) + " label READMEs. These are typically older label approvals (pre-2017) that were added before the Product Class/Type field was included in the README template.")
    lines.append("")
    
    # Notes
    lines.append("## Notes")
    lines.append("")
    lines.append("- Product Class/Type codes are TTB (Alcohol and Tobacco Tax and Trade Bureau) classifications for alcoholic beverages")
    lines.append("- The range 100-150 specifically covers whiskey and related spirits:")
    lines.append("  - 100-109: Various whiskey types")
    lines.append("  - 110-119: Bourbon whiskey")
    lines.append("  - 120-129: Rye whiskey")
    lines.append("  - 130-139: Corn whiskey")
    lines.append("  - 140-149: Blended whiskey")
    lines.append("- Labels without Product Class/Type information are primarily older approvals where this field was not captured during label download")
    lines.append("")
    
    # Data collection info
    lines.append("## Data Collection")
    lines.append("")
    lines.append("This summary is based on analysis of all README.md files in the `/labels/` directory. Each label subdirectory contains metadata about TTB COLA (Certificate of Label Approval) registrations, including Product Class/Type codes when available.")
    lines.append("")
    lines.append("To regenerate this summary, run:")
    lines.append("```bash")
    lines.append("python3 .github/scripts/analyze_product_types.py")
    lines.append("```")
    lines.append("")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Analyze Product Class/Type codes in TTB COLA label README files"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: labels/PRODUCT_TYPE_SUMMARY.md)",
        default=None
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    args = parser.parse_args()
    
    # Find repository root
    try:
        repo_root = find_repo_root()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Analyze product types
    print("Analyzing product types in label READMEs...", file=sys.stderr)
    data = analyze_product_types(repo_root)
    
    # Determine output file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = repo_root / "labels" / "PRODUCT_TYPE_SUMMARY.md"
    
    # Generate and write output
    if args.json:
        output_content = json.dumps(data, indent=2)
        print(output_content)
    else:
        output_content = generate_markdown_summary(data)
        output_path.write_text(output_content)
        print(f"Summary written to: {output_path}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Summary:", file=sys.stderr)
        print(f"  Total labels: {data['total_readmes']}", file=sys.stderr)
        print(f"  With Product Class/Type: {data['with_type']}", file=sys.stderr)
        print(f"  Without Product Class/Type: {len(data['without_type'])}", file=sys.stderr)
        print(f"  Unique product types: {data['unique_types']}", file=sys.stderr)
        if data['outside_range']:
            print(f"  Types outside 100-150: {len(data['outside_range'])}", file=sys.stderr)
        else:
            print(f"  Types outside 100-150: NONE", file=sys.stderr)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Verify TTB ID accuracy by checking for products with varying proofs using same TTB ID.
According to TTB regulations, significant proof changes require new COLA approvals.
"""

import csv
from collections import defaultdict


def load_whiskey_data(csv_path):
    """Load whiskey data from CSV."""
    whiskeys = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            whiskeys.append(row)
    return whiskeys


def analyze_ttb_accuracy(whiskeys):
    """Analyze TTB IDs for accuracy based on proof variations."""
    
    # Group by Name and TTB_ID
    product_ttb_groups = defaultdict(lambda: defaultdict(list))
    
    for w in whiskeys:
        name = w['Name']
        ttb_id = w.get('TTB_ID', '').strip()
        if ttb_id:
            product_ttb_groups[name][ttb_id].append(w)
    
    issues = []
    
    for product_name, ttb_dict in product_ttb_groups.items():
        for ttb_id, entries in ttb_dict.items():
            # Get all proofs for this TTB ID
            proofs = []
            for entry in entries:
                proof_str = entry.get('Proof', '').strip()
                if proof_str:
                    try:
                        proof = float(proof_str)
                        proofs.append(proof)
                    except ValueError:
                        pass
            
            if len(proofs) > 1:
                min_proof = min(proofs)
                max_proof = max(proofs)
                proof_range = max_proof - min_proof
                
                # TTB allows minor variations (~1-2%), but anything more likely needs new COLA
                if proof_range > 2.0:
                    issues.append({
                        'product': product_name,
                        'ttb_id': ttb_id,
                        'num_entries': len(entries),
                        'min_proof': min_proof,
                        'max_proof': max_proof,
                        'proof_range': proof_range,
                        'years': sorted(set(e['ReleaseYear'] for e in entries if e.get('ReleaseYear'))),
                        'batches': [e.get('Batch', 'N/A') for e in entries[:3]]  # Sample batches
                    })
    
    return issues


def main():
    """Main function."""
    csv_path = '_data/whiskeyindex.csv'
    
    print("=" * 80)
    print("TTB COLA ID Accuracy Verification")
    print("=" * 80)
    print()
    print("According to TTB regulations, significant proof changes require")
    print("separate COLA approvals. Checking for products with >2 proof")
    print("point variation using the same TTB ID...")
    print()
    
    whiskeys = load_whiskey_data(csv_path)
    issues = analyze_ttb_accuracy(whiskeys)
    
    if not issues:
        print("✓ No major issues found. All TTB IDs appear consistent with proof ranges.")
        return
    
    # Sort by proof range (most problematic first)
    issues.sort(key=lambda x: x['proof_range'], reverse=True)
    
    print(f"⚠️  Found {len(issues)} products with questionable TTB ID accuracy:")
    print()
    
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue['product']}")
        print(f"   TTB ID: {issue['ttb_id']}")
        print(f"   Entries: {issue['num_entries']}")
        print(f"   Proof Range: {issue['min_proof']} - {issue['max_proof']} ({issue['proof_range']:.1f} point spread)")
        print(f"   Years: {', '.join(issue['years'][:5])}" + (" ..." if len(issue['years']) > 5 else ""))
        print(f"   Sample Batches: {', '.join(issue['batches'][:3])}")
        print()
    
    print("=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print()
    print("Products with large proof variations likely need:")
    print("1. Individual TTB IDs per batch/year (requires TTB registry search)")
    print("2. OR remove TTB_ID to avoid incorrect links")
    print("3. OR add disclaimer that ID may represent product line, not specific batch")
    print()
    print("For products with verified TTB IDs (like Angel's Envy 2025 = 22089001000941),")
    print("only that specific entry should use that ID.")


if __name__ == '__main__':
    main()

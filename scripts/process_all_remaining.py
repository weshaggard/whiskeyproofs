#!/usr/bin/env python3
"""
Batch processor for remaining products
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from universal_ttb_matcher import search_and_match_product
import time

def main():
    """Process all remaining products."""
    
    # List of (CSV_Name, TTB_Search_Name) tuples
    products = [
        ("Thomas H. Handy", "Thomas H. Handy"),
        ("Eagle Rare 17 Year (ER17)", "Eagle Rare"),
        ("Sazerac 18 Year (Saz18)", "Sazerac"),
        ("Four Roses Limited Edition Small Batch", "Four Roses"),
        ("Larceny Barrel Proof (LBP)", "Larceny"),
        ("Little Book", "Little Book"),
        ("Wild Turkey Master's Keep", "Master's Keep"),
        ("Russell's Reserve 13 Year", "Russell's Reserve"),
        ("E.H. Taylor Barrel Proof (EHTBP)", "E.H. Taylor"),
        ("Colonel E.H. Taylor Bottled in Bond", "E.H. Taylor"),
        ("Knob Creek 15 Year (KC15)", "Knob Creek"),
        ("Knob Creek 18 Year (KC18)", "Knob Creek"),
        ("Knob Creek Cask Strength Rye", "Knob Creek"),
        ("Knob Creek 2001 Limited Edition", "Knob Creek"),
        ("Knob Creek 21 Year (KC21)", "Knob Creek"),
        ("Knob Creek 25th Anniversary", "Knob Creek"),
        ("Remus Gatsby Reserve", "Remus"),
        ("Booker's Rye", "Booker's Rye"),
        ("Angel's Envy Cask Strength", "Angel's Envy"),
    ]
    
    total_updated = 0
    
    for product_name, search_name in products:
        try:
            print("\n" + "="*80)
            updated = search_and_match_product(product_name, search_name)
            total_updated += updated
            
            if updated > 0:
                time.sleep(2)  # Be respectful to the server
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            break
        except Exception as e:
            print(f"❌ Error processing {product_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*80)
    print(f"✅ GRAND TOTAL UPDATED THIS RUN: {total_updated}")
    print("="*80)

if __name__ == '__main__':
    main()

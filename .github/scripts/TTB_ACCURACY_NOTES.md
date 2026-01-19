# TTB COLA ID Accuracy - Important Notes

## Issue Identified

The initial TTB COLA ID population used a single ID per product line (e.g., all Booker's batches shared one ID). However, **this is incorrect** according to TTB regulations.

## TTB COLA Requirements

According to 27 CFR Part 5, the TTB requires:

1. **Different proof levels require separate COLA approvals** - Proof variations beyond ~1-2% need new COLAs
2. **Different age statements require separate COLAs**
3. **Significant label changes require new approvals**

### Example: Angel's Envy Cask Strength

- **2025 Release**: 122.6 proof, 10 years old → TTB ID: `22089001000941` ✓ Verified
- **2024 Release**: 118.8 proof, 8 years old → Different TTB ID required
- **2023 Release**: 118.2 proof → Different TTB ID required
- **2022 Release**: 119.8 proof → Different TTB ID required

Each year has different proof and/or age, requiring separate TTB approvals.

## Products With Proof Variations

Analysis shows the following products have significant proof variations (>2 points) across batches:

1. **Jack Daniel's Special Release**: 100.0 - 148.8 proof (48.8 point spread)
2. **Wild Turkey Master's Keep**: 86.8 - 118.0 proof (31.2 point spread)
3. **George T. Stagg (GTS)**: 116.9 - 144.1 proof (27.2 point spread)
4. **Elijah Craig Barrel Proof**: 118.2 - 140.2 proof (22.0 point spread)
5. **William Larue Weller (WLW)**: 123.4 - 140.2 proof (16.8 point spread)
6. **Booker's**: 122.4 - 130.3 proof (7.9 point spread)
7. And 11 more products...

**Each of these batches requires a separate TTB COLA approval with a unique ID.**

## Current Status

- **Total entries**: 311
- **Verified TTB IDs**: 1 (Angel's Envy Cask Strength 2025)
- **Entries without TTB ID**: 310

## Why Most TTB IDs Were Removed

The previously populated TTB IDs were:
- ❌ Not verified against TTB COLA registry
- ❌ Applied to all batches regardless of proof/age differences
- ❌ Likely to link to wrong approval documents

**To maintain accuracy**, only verified TTB IDs should be included.

## How to Verify TTB IDs

To properly populate TTB IDs:

1. Visit: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
2. Search for specific product + batch + year
3. Match proof, age, and batch details exactly
4. Copy the 14-digit TTB ID from verified match
5. Add only to the specific matching entry

### Example Verified Search

**Angel's Envy Cask Strength 2025:**
- Search: "Angel's Envy Cask Strength" + 2025
- Verify: 122.6 proof, 10 years, 2025 release
- Result: TTB ID 22089001000941 ✓
- Apply: Only to 2025 entry with matching characteristics

## Industry Practice Note

While many bourbon brands use a "template" label with variable batch/proof information, TTB regulations still require separate COLA approvals for:
- Significant proof changes
- Age statement changes  
- Major label modifications

The same brand name can have dozens of different TTB IDs across years and batches.

## Recommendations

### For Users Adding TTB IDs:

1. ✓ **Verify each ID** matches the specific batch, proof, age, and year
2. ✓ **Use TTB COLA registry** as the authoritative source
3. ✓ **Add IDs individually** per verified batch
4. ✗ **Don't assume** one ID works for all batches of a product
5. ✗ **Don't guess** or use placeholder IDs

### For Future Population:

- Consider a community-driven effort to search and verify TTB IDs
- Document verification sources for each ID added
- Regular audits to ensure accuracy
- Scripts to detect proof/age mismatches with TTB IDs

## References

- **TTB COLA Registry**: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
- **27 CFR Part 5**: TTB Labeling Requirements
- **TTB Allowable Revisions**: https://www.ttb.gov/labeling/allowable-revisions

## Verification Script

Use `scripts/verify_ttb_accuracy.py` to check for products with proof variations using the same TTB ID - these likely need separate IDs per batch.

## Summary

**Accuracy > Coverage**: It's better to have 1 verified TTB ID than 311 unverified ones. Each entry should only have a TTB ID if it's been confirmed to match that specific whiskey's batch, proof, age, and year.

# TTB ID Validation Results

**Date**: January 26, 2026  
**Validator**: validate_ttb_ids.py  
**Status**: ✅ Complete - All entries now have validated TTB IDs

## Summary

- **Total entries in database**: 550
- **Entries with TTB IDs**: 550 (100%) ✅
- **Entries without TTB IDs**: 0
- **Unique TTB IDs**: 340
- **All TTB IDs validated**: ✅ Yes (all 550 resolve correctly)
- **TTB IDs with suspicious duplicate usage**: ⚠️ 37 (potential accuracy issues)
- **URLs validated**: ✅ All 550 URLs valid

## Recent Updates

### Added TTB IDs (January 26, 2026)

The following 4 Wild Turkey products were missing TTB IDs and have been added:

1. **Wild Turkey - 101**
   - TTB ID: 20358001000428
   - Proof: 101
   - Verified: ✅ Valid COLA page

2. **Wild Turkey - Rye**
   - TTB ID: 23132001000341
   - Proof: 81
   - Verified: ✅ Valid COLA page

3. **Wild Turkey - Rare Breed**
   - TTB ID: 21337001000508
   - Proof: 116.8
   - Verified: ✅ Valid COLA page

4. **Wild Turkey - Kentucky Spirit**
   - TTB ID: 20006001000186
   - Proof: 101
   - Verified: ✅ Valid COLA page

All TTB IDs were sourced from the official TTB COLA Public Registry and verified to resolve to valid approval pages.

## Validation Results

### ✅ All TTB IDs Resolve Successfully

All 550 TTB IDs in the database successfully resolve to valid TTB COLA pages. This means:
- No broken or invalid TTB IDs
- No formatting errors
- All IDs exist in the TTB COLA registry

### ⚠️ Duplicate TTB ID Usage with Proof Variations

According to TTB regulations (27 CFR Part 5), **different proof levels require separate COLA approvals**. 

The following 37 TTB IDs are used across multiple batches with significant proof variations (>2 points difference):

#### High Priority Issues (>10 point proof spread)

1. **TTB ID: 05209000000014** - William Larue Weller (WLW)
   - Used 16 times across different years
   - Proof range: 123.4 - 140.2 (Δ 16.8 points)
   - Years: 2010-2025 BTAC Fall releases

2. **TTB ID: 24135001000259** - Woodford Reserve Master's Collection
   - Used 2 times
   - Proof range: 90.4 - 119.5 (Δ 29.1 points)
   - 2024 Madeira Cask vs 2025 Batch Proof

3. **TTB ID: 04120000000244** - George T. Stagg (GTS)
   - Used 16 times
   - Proof range: 116.9 - 144.1 (Δ 27.2 points)
   - Years: 2002-2025 BTAC Fall releases

4. **TTB ID: 04160000000256** - Eagle Rare 17 Year
   - Used 15 times
   - Proof range: 90 - 101 (Δ 11.0 points)
   - Years: 2007-2025 BTAC Fall releases

5. **TTB ID: 15169001000414** - Elijah Craig Barrel Proof
   - Used 6 times
   - Proof range: 127.8 - 140 (Δ 12.2 points)
   - Batches: C921 to C924

6. **TTB ID: 16168001000409** - Elijah Craig Barrel Proof
   - Used 5 times
   - Proof range: 128.4 - 140.2 (Δ 11.8 points)
   - Batches: A115 to B516

#### Medium Priority Issues (5-10 point spread)

7. **TTB ID: 25122001000102** - Booker's
   - Used 16 times
   - Proof range: 122.4 - 130.3 (Δ 7.9 points)

8. **TTB ID: 12355001000167** - Stagg Jr
   - Used 18 times
   - Proof range: 126.4 - 134.4 (Δ 8.0 points)

9. **TTB ID: 17152001000375** - Angel's Envy Cask Strength
   - Used 11 times
   - Proof range: 119.3 - 127.9 (Δ 8.6 points)

10. **TTB ID: 06194000000025** - Thomas H. Handy (THH)
    - Used 16 times
    - Proof range: 124.9 - 132.4 (Δ 7.5 points)

11. **TTB ID: 21302001000316** - Stagg (new format)
    - Used 12 times
    - Proof range: 125.6 - 132.2 (Δ 6.6 points)

12. **TTB ID: 14055001000867** - Russell's Reserve
    - Used 2 times
    - Proof range: 104 - 110 (Δ 6.0 points)
    - Different products: Single Barrel Rye vs Single Barrel Bourbon

[Additional 25 TTB IDs with 2-5 point variations documented in full validation output]

## Entries Without TTB IDs

✅ **All entries now have TTB IDs!**

Previously missing entries (now added):
1. ✅ Wild Turkey - 101 → TTB ID: 20358001000428
2. ✅ Wild Turkey - Rye → TTB ID: 23132001000341
3. ✅ Wild Turkey - Rare Breed → TTB ID: 21337001000508
4. ✅ Wild Turkey - Kentucky Spirit → TTB ID: 20006001000186

## Recommendations

### Immediate Actions

1. **Verify duplicate usage** - For TTB IDs with >10 point proof spreads, manually verify each batch:
   - Check if the TTB COLA actually covers the proof range
   - If not, find the correct individual TTB ID for each batch
   - Priority: William Larue Weller, George T. Stagg, Woodford Reserve Master's Collection

2. **Find missing TTB IDs** - Add TTB IDs for the 4 Wild Turkey entries:
   - Search TTB COLA registry for "Wild Turkey"
   - Match by product name and proof
   - Add to database

### Long-term Improvements

1. **Individual batch verification** - For limited release products like BTAC, each year likely has its own TTB ID
2. **Documentation** - Track sources and verification for each TTB ID added
3. **Regular validation** - Run validate_ttb_ids.py periodically to catch issues
4. **Community verification** - Consider crowdsourcing verification of TTB IDs

## How to Use This Information

### To fix a suspicious duplicate:

1. Visit the TTB COLA page for the ID: `https://www.ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid=[ID]`
2. Check the "Alcohol Content" field - does it cover the full proof range?
3. If not, search for the correct TTB ID for each specific batch
4. Update the CSV with the correct individual TTB IDs

### To find missing TTB IDs:

1. Visit: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
2. Enter the brand name (e.g., "Wild Turkey")
3. Filter by year and proof
4. Find the exact match
5. Copy the 14-digit TTB ID
6. Add to the CSV

## References

- **TTB COLA Public Registry**: https://www.ttbonline.gov/colasonline/publicSearchColasBasic.do
- **27 CFR Part 5**: TTB Labeling Requirements
- **Validation Script**: `.github/scripts/validate_ttb_ids.py`
- **Full Validation Output**: Contact maintainer for complete log

## Notes

- Validation performed on 2026-01-26
- All TTB IDs successfully resolve to valid COLA pages
- No broken links or invalid IDs found
- Main issue is potential duplicate usage across batches with different proofs
- According to TTB regulations, each significant proof variation requires a separate COLA approval

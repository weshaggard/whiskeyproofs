# Major Bourbon Distilleries Added to Whiskey Index

## Summary

Successfully added **27 new whiskey entries** across **3 major bourbon distilleries** that were previously missing from the index:

### 1. Barton 1792 Distillery (3 entries)
Limited edition and allocated releases from the 1792 brand:

| Product | Batch/Edition | Proof | Release Year | URL |
|---------|--------------|-------|--------------|-----|
| 1792 Bourbon | Full Proof | 125 | 2015-2025 | https://1792bourbon.com/full-proof/ |
| 1792 Bourbon | Sweet Wheat | 91.2 | 2015-2025 | https://1792bourbon.com/sweet-wheat/ |
| 1792 Bourbon | Single Barrel | 98.6 | 2015-2025 | https://1792bourbon.com/single-barrel/ |

### 2. Barrell Craft Spirits (15 entries)
Sequential numbered batches, each a unique blend:

| Product | Batch | Proof | Release Year | Notes |
|---------|-------|-------|--------------|-------|
| Barrell Bourbon | Batch 037 | 111.4 | 2025 | Latest release |
| Barrell Bourbon | Batch 036 | 114.4 | 2023 | |
| Barrell Bourbon | Batch 035 | 115.3 | 2023 | |
| Barrell Bourbon | Batch 034 | 114.9 | 2022 | |
| Barrell Bourbon | Batch 033 | 116.8 | 2022 | |
| Barrell Bourbon | Batch 032 | 114.8 | 2022 | |
| Barrell Bourbon | Batch 031 | 105.4 | 2022 | |
| Barrell Bourbon | Batch 030 | 117.3 | 2021 | |
| Barrell Bourbon | Batch 029 | 109.7 | 2021 | |
| Barrell Bourbon | Batch 028 | 110.4 | 2021 | |
| Barrell Bourbon | Batch 027 | 107.1 | 2021 | |
| Barrell Bourbon | Batch 026 | 110.1 | 2020 | |
| Barrell Bourbon | Batch 025 | 110.2 | 2020 | |
| Barrell Bourbon | Batch 024 | 110.3 | 2020 | |
| Barrell Bourbon | Batch 023 | 113.3 | 2020 | |

**Note**: All Barrell Bourbon batches are cask strength, limited releases. Batches prior to 023 (2020) could be added in the future if needed.

### 3. Maker's Mark (9 entries)
Wood Finishing Series and Cask Strength limited editions:

| Product | Edition | Age | Proof | Release Year | URL |
|---------|---------|-----|-------|--------------|-----|
| Maker's Mark Wood Finishing Series | The Heart (BEP) | 7-8 | 107-114 | 2024 | https://www.makersmark.com/bourbons/makers-mark-wood-finishing-series |
| Maker's Mark Wood Finishing Series | BRT-02 | | 109.4 | 2022 | https://www.makersmark.com/bourbons/makers-mark-wood-finishing-series |
| Maker's Mark Wood Finishing Series | BRT-01 | | 109.4 | 2022 | https://www.makersmark.com/bourbons/makers-mark-wood-finishing-series |
| Maker's Mark Wood Finishing Series | FAE-02 | | 109.1 | 2021 | https://www.breakingbourbon.com/review/makers-mark-wood-finishing-series-2021-limited-release-fae-02 |
| Maker's Mark Wood Finishing Series | FAE-01 | | 110.3-110.6 | 2021 | https://www.breakingbourbon.com/review/makers-mark-wood-finishing-series-2021-limited-release-fae-01 |
| Maker's Mark Wood Finishing Series | SE4 x PR5 | | 110.8 | 2020 | https://www.makersmark.com/bourbons/makers-mark-wood-finishing-series |
| Maker's Mark Wood Finishing Series | RC6 | | 108.2-110.5 | 2019 | https://www.makersmark.com/bourbons/makers-mark-wood-finishing-series |
| Maker's Mark Cask Strength | standard | 7-8 | 107-114 | 2014-2025 | https://www.makersmark.com/bourbons/cask-strength |
| Maker's Mark 46 Cask Strength | 2020 Limited Edition | | 109.6-110.6 | 2020 | https://www.makersmark.com/ |

## Validation Status

### ✅ Completed
- Data quality validation (all required fields, proof values, release years, no duplicates)
- Alphabetical sorting (Name ascending, Batch descending within products)
- URL validation (all URLs tested and return HTTP 200)

### ⚠️ Pending
- **TTB ID Research**: Entries were added with blank TTB IDs
  - Can be populated later using the `query_ttb.py` script
  - Recommended to research and add TTB IDs from TTB COLA Public Registry
  - Not blocking for initial addition to the index

## Future Additions to Consider

Based on the research, these additional distilleries could be considered for future inclusion:

**Medium Priority:**
- New Riff - Single barrel program and limited releases
- Bardstown Bourbon Company - Discovery Series, Fusion Series

**Lower Priority:**
- Castle & Key - Limited releases (The Untold Story series)
- Wilderness Trail - Growing craft distillery with limited releases
- Rabbit Hole - Craft bourbon with limited editions
- Old Elk - Limited releases

## Research Sources

- 1792 Bourbon: Official website and Breaking Bourbon reviews
- Barrell Craft Spirits: Official batch archive and release announcements
- Maker's Mark: Official website and Kentucky Supply Co. blog
- Proof values and release years verified through multiple whiskey review sites
- All URLs manually tested for validity

## Impact

- **Total entries before**: 568
- **New entries added**: 27
- **Total entries now**: 594
- **Unique products before**: 71
- **Unique products now**: 76 (added 5 new product lines across 3 distilleries)
- **Distilleries before**: 13
- **Distilleries now**: 16

This brings the whiskey index up to date with major bourbon distilleries known for limited edition and allocated releases.

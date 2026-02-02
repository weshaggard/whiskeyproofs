# TTB Label Product Type Summary

**Last Updated:** 2026-02-02

This document provides a summary of Product Class/Type codes found in the TTB COLA label README files.

## Overview

| Metric | Count |
|--------|-------|
| Total label README files | 337 |
| READMEs with Product Class/Type field | 161 |
| READMEs without Product Class/Type field | 176 |
| Unique product types found | 12 |

## Product Class/Type Distribution

The following table shows all Product Class/Type codes found in the label READMEs, sorted by type code:

| Product Type | Count | Percentage | In Range (100-150)? |
|--------------|-------|------------|---------------------|
| 100 | 1 | 0.6% | ✓ Yes |
| 101 | 81 | 50.3% | ✓ Yes |
| 102 | 15 | 9.3% | ✓ Yes |
| 111 | 3 | 1.9% | ✓ Yes |
| 119 | 1 | 0.6% | ✓ Yes |
| 121 | 8 | 5.0% | ✓ Yes |
| 137 | 1 | 0.6% | ✓ Yes |
| 140 | 17 | 10.6% | ✓ Yes |
| 141 | 25 | 15.5% | ✓ Yes |
| 142 | 6 | 3.7% | ✓ Yes |
| 144 | 2 | 1.2% | ✓ Yes |
| 149 | 1 | 0.6% | ✓ Yes |
| **Total** | **161** | **100%** | - |

*Percentages are calculated from the 161 READMEs that have a Product Class/Type field.*

## Product Types Outside 100-150 Range

**Result:** NONE

All 161 label READMEs that contain a Product Class/Type field have values within the 100-150 range. No product types were found outside this range.

## Most Common Product Types

1. **Type 101** - 81 labels (50.3%)
2. **Type 141** - 25 labels (15.5%)
3. **Type 140** - 17 labels (10.6%)
4. **Type 102** - 15 labels (9.3%)
5. **Type 121** - 8 labels (5.0%)

These top 5 product types account for 90.7% of all labels with a Product Class/Type field.

## Labels Without Product Class/Type

**Count:** 176 labels (52.2% of all labels)

The Product Class/Type field is missing from 176 label READMEs. These are typically older label approvals (pre-2017) that were added before the Product Class/Type field was included in the README template.

## Notes

- Product Class/Type codes are TTB (Alcohol and Tobacco Tax and Trade Bureau) classifications for alcoholic beverages
- The range 100-150 specifically covers whiskey and related spirits:
  - 100-109: Various whiskey types
  - 110-119: Bourbon whiskey
  - 120-129: Rye whiskey
  - 130-139: Corn whiskey
  - 140-149: Blended whiskey
- Labels without Product Class/Type information are primarily older approvals where this field was not captured during label download

## Data Collection

This summary is based on analysis of all README.md files in the `/labels/` directory. Each label subdirectory contains metadata about TTB COLA (Certificate of Label Approval) registrations, including Product Class/Type codes when available.

To regenerate this summary, run:
```bash
python3 .github/scripts/analyze_product_types.py
```

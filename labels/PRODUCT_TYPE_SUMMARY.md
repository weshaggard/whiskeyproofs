# TTB Label Product Type Summary

**Last Updated:** 2026-02-03

This document provides a summary of Product Class/Type codes found in the TTB COLA label README files.

## Overview

| Metric | Count |
|--------|-------|
| Total label README files | 282 |
| READMEs with Product Class/Type field | 282 |
| READMEs without Product Class/Type field | 0 |
| Unique product types found | 16 |

## Product Class/Type Distribution

The following table shows all Product Class/Type codes found in the label READMEs, sorted by type code:

| Product Type | Count | Percentage | In Range (100-150)? |
|--------------|-------|------------|---------------------|
| 100 | 1 | 0.4% | ✓ Yes |
| 101 | 173 | 61.3% | ✓ Yes |
| 102 | 20 | 7.1% | ✓ Yes |
| 109 | 2 | 0.7% | ✓ Yes |
| 111 | 3 | 1.1% | ✓ Yes |
| 119 | 2 | 0.7% | ✓ Yes |
| 120 | 1 | 0.4% | ✓ Yes |
| 121 | 9 | 3.2% | ✓ Yes |
| 129 | 3 | 1.1% | ✓ Yes |
| 132 | 1 | 0.4% | ✓ Yes |
| 137 | 1 | 0.4% | ✓ Yes |
| 140 | 29 | 10.3% | ✓ Yes |
| 141 | 27 | 9.6% | ✓ Yes |
| 142 | 7 | 2.5% | ✓ Yes |
| 144 | 2 | 0.7% | ✓ Yes |
| 149 | 1 | 0.4% | ✓ Yes |
| **Total** | **282** | **100%** | - |

*Percentages are calculated from the 282 READMEs that have a Product Class/Type field.*

## Product Types Outside 100-150 Range

**Result:** NONE

All 282 label READMEs that contain a Product Class/Type field have values within the 100-150 range. No product types were found outside this range.

## Most Common Product Types

1. **Type 101** - 173 labels (61.3%)
2. **Type 140** - 29 labels (10.3%)
3. **Type 141** - 27 labels (9.6%)
4. **Type 102** - 20 labels (7.1%)
5. **Type 121** - 9 labels (3.2%)

These top 5 product types account for 91.5% of all labels with a Product Class/Type field.

## Labels Without Product Class/Type

**Count:** 0 labels (0.0% of all labels)

The Product Class/Type field is missing from 0 label READMEs. These are typically older label approvals (pre-2017) that were added before the Product Class/Type field was included in the README template.

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

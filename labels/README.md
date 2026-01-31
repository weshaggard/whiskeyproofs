# TTB COLA Label Images

This directory contains label images downloaded from the TTB (Alcohol and Tobacco Tax and Trade Bureau) COLA Public Registry for whiskey products in the database.

## Organization

Each TTB ID has its own subdirectory:
```
labels/
├── {TTBID}/
│   ├── README.md          # Metadata about this TTB ID
│   ├── front_label.jpg    # Front label image (when available)
│   ├── back_label.jpg     # Back label image (when available)
│   └── label_N.jpg        # Additional label images (if any)
└── ...
```

## Downloading Label Images

Use the automated download script to fetch label images:

```bash
# Download labels for a specific TTB ID
.github/scripts/download_ttb_labels.sh --ttbid 24002001000457

# Download labels for all TTB IDs in the database
.github/scripts/download_ttb_labels.sh

# Download first 10 TTB IDs (for testing)
.github/scripts/download_ttb_labels.sh --limit 10
```

See [.github/scripts/README.md](../.github/scripts/README.md) for complete documentation.

## Image Sources

All images are sourced from:
https://ttbonline.gov/colasonline/publicSearchColasBasic.do

Individual label pages:
https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={TTBID}

## Image Availability

**Important Notes:**
- Not all TTB IDs have label images available in the public online registry
- Older TTB approvals (pre-2015) rarely have images available
- Newer TTB IDs (2020+) are more likely to have images
- Some products may have multiple label images (front, back, neck, shoulder, etc.)

Based on testing with the full database:
- Total unique TTB IDs in database: 194
- TTB IDs with available images: ~10-20 (5-10%)
- Most failures are older approvals without online images

## Image Types

The download script attempts to identify and name images based on their content:
- `front_label.jpg` - Front label (brand/front)
- `back_label.jpg` - Back label
- `label_N.jpg` - Additional labels (neck, shoulder, etc.)

## Automation

The download script can be run:
- **Manually** - For specific TTB IDs or testing
- **In CI/CD** - Automated updates when CSV changes
- **Scheduled** - Periodic updates to catch new TTB image uploads

The script automatically:
- Creates session cookies for TTB authentication
- Handles URL encoding for filenames with spaces
- Skips already-downloaded images (unless --no-skip-existing is used)
- Generates README.md for each TTB ID folder
- Provides detailed progress and summary statistics

## Contributing

When adding new whiskey entries to the database:
1. Add the TTB_ID to the CSV file
2. Run the download script for that specific TTB ID:
   ```bash
   .github/scripts/download_ttb_labels.sh --ttbid {NEW_TTBID}
   ```
3. If images are available, they'll be downloaded automatically
4. Commit both the CSV update and any new label images

## License

Label images are sourced from the U.S. Government's TTB COLA Public Registry and are in the public domain.

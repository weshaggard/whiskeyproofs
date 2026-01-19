# Quick Start: Finding TTB IDs

This is a quick start guide to help you immediately start finding TTB COLA approval IDs for whiskey entries.

## Fastest Way to Start (2 minutes)

No installation required! Just run:

```bash
python3 .github/scripts/generate_ttb_urls.py --limit 20 --html --output my_searches.html
```

Then:
1. Open `my_searches.html` in your browser
2. Click "Search TTB COLA" for each whiskey
3. Enter the brand name shown
4. Find matches by proof and year
5. Copy TTB IDs and add them to the CSV

## What You'll See

The HTML file will show entries like:

```
Angel's Envy Cask Strength
Batch: 2025 | Proof: 122.6 | Year: 2025
Brand to search: Angel's Envy
[Search TTB COLA Button]
```

## Finding a Match

When you search the TTB site:
1. Enter brand: `Angel's Envy`
2. Look for results with:
   - ✓ Proof: 122.6 (or very close)
   - ✓ Year: 2025
   - ✓ Product type: Cask Strength
3. Click the matching result
4. Copy the 14-digit TTB ID from the URL

Example TTB ID: `22089001000941`

## Adding to CSV

Open `_data/whiskeyindex.csv` and find the matching row:

```csv
Angel's Envy Cask Strength,2025,10,122.6,2025,Angel's Envy,Bourbon,
```

Add the TTB ID at the end:

```csv
Angel's Envy Cask Strength,2025,10,122.6,2025,Angel's Envy,Bourbon,22089001000941
```

## Verify Your Changes

After adding TTB IDs, always run:

```bash
python3 .github/scripts/validate_whiskey_data.py
```

This ensures your CSV is still valid and properly formatted.

## Tips for Success

- **Start small**: Try 10-20 entries first
- **One product at a time**: Focus on one whiskey brand
- **Verify matches**: Make sure proof, year, and batch all match
- **Save often**: Don't lose your work!

## Need More Help?

See the complete guide:
- [TTB_QUERY_GUIDE.md](TTB_QUERY_GUIDE.md) - Full documentation
- [README.md](README.md) - All script options

## Common Questions

**Q: I can't find a match**
A: Some whiskeys don't have TTB records in the public registry, especially older batches. Skip those.

**Q: I found multiple matches**
A: Look for the one with exact proof and year. If still unsure, verify the approval date matches the release date.

**Q: The proof is slightly different**
A: TTB allows ±0.3 proof variation. Small differences (122.6 vs 122.4) are fine.

**Q: Can I automate this?**
A: Yes! See the advanced guide for the automated script, but it requires Selenium installation.

## Contributing

Found some TTB IDs? Great! Here's how to contribute:

1. Add them to your CSV file
2. Run validation: `python3 .github/scripts/validate_whiskey_data.py`
3. Commit: `git add _data/whiskeyindex.csv && git commit -m "Add TTB IDs for [Product]"`
4. Push and create a pull request

Thank you for helping improve the database! 🥃

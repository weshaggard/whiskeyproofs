---
layout: default
title: Frequently Asked Questions
description: Common questions about using the Whiskey Proof Index, finding bourbon batches, understanding proof values, and contributing to the database.
permalink: /faq/
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is whiskey proof and how is it measured?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Whiskey proof is a measure of alcohol content. In the United States, proof is exactly twice the alcohol by volume (ABV) percentage. For example, a whiskey that is 50% ABV is 100 proof. Barrel proof or cask strength whiskeys are bottled at their natural proof without dilution, typically ranging from 100 to 140+ proof."
      }
    },
    {
      "@type": "Question",
      "name": "How do I find the proof of a specific bourbon batch?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Use the search box on the main Whiskey Proof Index page. You can search by bourbon name (e.g., 'George T Stagg'), batch number (e.g., 'Fall 2023'), or any other field. The table is instantly filtered to show matching results. You can also click column headers to sort by name, batch, proof, or release year."
      }
    },
    {
      "@type": "Question",
      "name": "What does the 🏷️ label emoji mean?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The 🏷️ emoji indicates that a TTB (Alcohol and Tobacco Tax and Trade Bureau) label approval is available for that batch. Clicking the emoji opens the official government label registration document, which provides verified information about the product including proof, age statement, and other details."
      }
    },
    {
      "@type": "Question",
      "name": "How accurate is the data in the index?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We strive for high accuracy by cross-referencing multiple sources including distillery websites, TTB label approvals, and verified batch information. However, some TTB IDs may be incorrect or unverified. If you notice any errors, please submit feedback through our GitHub issues page."
      }
    },
    {
      "@type": "Question",
      "name": "How often is the index updated with new releases?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The index is updated regularly as new whiskey batches are released. We have automated systems that check for new TTB label approvals and contributors add new releases as they become available. Major releases from popular brands like Buffalo Trace Antique Collection are typically added within days of release."
      }
    },
    {
      "@type": "Question",
      "name": "Can I download or export the whiskey data?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes! The whiskey data is stored in a CSV file that can be accessed directly on our GitHub repository. You're free to use this data for personal, non-commercial purposes. The data is licensed under Creative Commons Attribution 4.0."
      }
    },
    {
      "@type": "Question",
      "name": "How can I contribute or suggest additions?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "We welcome contributions! You can submit feedback, corrections, or new whiskey additions through our GitHub issues page. If you're familiar with GitHub, you can also submit pull requests directly to update the CSV data file."
      }
    },
    {
      "@type": "Question",
      "name": "What's the difference between barrel proof and cask strength?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Barrel proof and cask strength are essentially the same thing - whiskey bottled at the proof it comes out of the barrel without adding water to dilute it. These whiskeys typically range from 100 to 140+ proof and offer the most intense flavor experience. The terms are used interchangeably, though 'barrel proof' is more common in American whiskey and 'cask strength' in Scotch."
      }
    },
    {
      "@type": "Question",
      "name": "Why do proof values vary between batches of the same whiskey?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Natural variation in barrel proof whiskeys occurs due to differences in barrel location in the warehouse, aging time, climate conditions, and evaporation rates. Each barrel loses water and alcohol at slightly different rates, resulting in proof variations between batches. This is why barrel proof releases like George T Stagg or Booker's show different proof values each year."
      }
    },
    {
      "@type": "Question",
      "name": "What distilleries and brands are covered in the index?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The index covers major American whiskey distilleries including Buffalo Trace (BTAC, Eagle Rare, Blanton's), Heaven Hill (Elijah Craig, Henry McKenna), Old Forester, Wild Turkey (Russell's Reserve, Kentucky Spirit), Four Roses, Jim Beam, and many others. We focus primarily on bourbon and American whiskey but also include some rye whiskey and other styles."
      }
    }
  ]
}
</script>

# Frequently Asked Questions

## Common Questions About Whiskey Proof Index

### What is whiskey proof and how is it measured?

Whiskey proof is a measure of alcohol content. In the United States, proof is exactly twice the alcohol by volume (ABV) percentage. For example:
- 50% ABV = 100 proof
- 62.5% ABV = 125 proof
- 70% ABV = 140 proof

Barrel proof or cask strength whiskeys are bottled at their natural proof without dilution, typically ranging from 100 to 140+ proof.

### How do I find the proof of a specific bourbon batch?

1. Go to the [main index page]({{ '/' | relative_url }})
2. Use the search box to filter by:
   - Bourbon name (e.g., "George T Stagg")
   - Batch number (e.g., "Fall 2023")
   - Proof value
   - Release year
   - Distillery name
3. Click column headers to sort results
4. Results update instantly as you type

### What does the 🏷️ label emoji mean?

The 🏷️ emoji indicates that a TTB (Alcohol and Tobacco Tax and Trade Bureau) label approval is available for that batch. The TTB is the federal agency that approves all alcohol labels in the United States.

Clicking the emoji opens the official government label registration, which provides:
- Verified proof information
- Official age statements
- Distillery details
- Label artwork and claims

### How accurate is the data in the index?

We maintain high accuracy by:
- Cross-referencing distillery websites
- Verifying against TTB label approvals
- Using community contributions
- Regular validation and updates

**Note**: Some TTB IDs may be unverified. If you spot an error, please [submit feedback](https://github.com/weshaggard/whiskeyproofs/issues/new).

### How often is the index updated with new releases?

The index is updated regularly:
- Automated TTB label monitoring checks for new approvals
- Community contributors add releases as they become available
- Major releases (BTAC, limited editions) added within days
- Ongoing validation ensures data quality

### Can I download or export the whiskey data?

**Yes!** The data is open and accessible:

- **Format**: CSV (comma-separated values)
- **Location**: [GitHub repository](https://github.com/weshaggard/whiskeyproofs)
- **License**: Creative Commons Attribution 4.0
- **Usage**: Free for personal, non-commercial purposes

You can use the data for:
- Personal reference
- Research projects
- Creating your own tools
- Analysis and visualization

### How can I contribute or suggest additions?

We welcome contributions! Several ways to help:

1. **Submit Feedback**: [Open a GitHub issue](https://github.com/weshaggard/whiskeyproofs/issues/new)
2. **Suggest Additions**: Include whiskey name, batch, proof, and release year
3. **Report Errors**: Let us know about incorrect data
4. **Submit Pull Requests**: Directly update the CSV file if you're familiar with GitHub

### What's the difference between barrel proof and cask strength?

**They're the same thing!** Both terms mean whiskey bottled at the proof it comes out of the barrel without added water.

- **Barrel proof**: More common in American whiskey
- **Cask strength**: More common in Scotch whisky
- **Typical range**: 100-140+ proof
- **Characteristics**: Most intense flavor, undiluted, naturally varies by barrel

### Why do proof values vary between batches of the same whiskey?

Natural variation occurs due to:

1. **Barrel Location**: Position in warehouse affects evaporation
2. **Aging Time**: Longer aging can increase or decrease proof
3. **Climate**: Temperature and humidity variations
4. **Evaporation**: Different rates of water vs. alcohol loss
5. **Barrel Char**: Level of barrel char affects interaction

This is why releases like George T Stagg, Booker's, or Elijah Craig Barrel Proof show different proofs each batch - it's a natural part of the aging process.

### What distilleries and brands are covered?

The index includes major American whiskey producers:

**Buffalo Trace Distillery**:
- Buffalo Trace Antique Collection (BTAC)
- Eagle Rare
- Blanton's
- E.H. Taylor
- Stagg Jr.

**Heaven Hill**:
- Elijah Craig (including Barrel Proof)
- Henry McKenna
- Old Fitzgerald

**Old Forester**:
- Birthday Bourbon
- Whiskey Row Series
- Single Barrel selections

**Wild Turkey**:
- Russell's Reserve
- Kentucky Spirit
- Rare Breed

**Others**:
- Four Roses
- Jim Beam Small Batch
- Maker's Mark
- And many more!

### Are non-bourbon whiskeys included?

Yes! While we focus primarily on bourbon, the index also includes:
- Rye whiskey
- American single malt
- Tennessee whiskey
- Other American whiskey styles

### How do I use the search function effectively?

**Tips for better searches**:

1. **Name searches**: Type part of the name ("Stagg", "Craig")
2. **Batch searches**: Enter batch numbers ("Fall 2023", "C923")
3. **Proof searches**: Type exact proof or range
4. **Year searches**: Filter by release year
5. **Multiple terms**: Search works across all fields simultaneously

**Examples**:
- "stagg 2023" - Find all Stagg releases from 2023
- "130" - Find all whiskeys around 130 proof
- "barrel proof heaven" - Find barrel proof releases from Heaven Hill

### Is there a mobile app?

Currently, no dedicated mobile app exists. However, the website is fully responsive and works great on mobile browsers. You can:
- Bookmark the site on your phone
- Add to home screen for app-like experience
- Search and filter on any device

---

## Still have questions?

**Can't find what you're looking for?**

- [Browse the full index]({{ '/' | relative_url }})
- [Learn more about this project]({{ '/about/' | relative_url }})
- [Ask a question on GitHub](https://github.com/weshaggard/whiskeyproofs/issues/new)

<p align="left">
  <a href="https://www.buymeacoffee.com/whiskeyproofs">
    <img src="{{ '/assets/buymeadrink.png' | relative_url }}" alt="Support this project - Buy me a drink" height="60">
  </a>
</p>

[← Back to Whiskey Index]({{ '/' | relative_url }})

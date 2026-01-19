---
layout: default
title: Whiskey proof index
description: "Comprehensive searchable database of bourbon and whiskey batches. Find proof values, release years, age statements, and batch numbers for Buffalo Trace, Heaven Hill, and other premium distilleries."
---

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3605565427529797"
     crossorigin="anonymous"></script>

<link rel="stylesheet" href="{{ '/assets/css/whiskey-index.css' | relative_url }}">

# Whiskey proof index

Your comprehensive reference for whiskey batch information, proofs, and release years. Whether you're a collector tracking down specific batches, an enthusiast researching proof variations, or simply curious about whiskey releases over the years, this searchable index helps you find exactly what you're looking for.

<div class="filter-container">
  <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search by name, batch, proof, etc...">
</div>

<table class="whiskey-table" id="whiskeyTable" role="table" aria-label="Whiskey and Bourbon Batch Information Database">
  <thead>
    <tr>
      <th style="width: auto; cursor: pointer;" onclick="toggleAllGroups()">
        <span id="toggle-all-icon">▶</span>
      </th>
      <th onclick="sortTable(1)" style="cursor: pointer;" scope="col">Name</th>
      <th onclick="sortTable(2)" style="cursor: pointer;" scope="col">Batch</th>
      <th onclick="sortTable(3)" style="cursor: pointer;" scope="col">Age</th>
      <th onclick="sortTable(4)" style="cursor: pointer;" scope="col">Proof</th>
      <th onclick="sortTable(5)" style="cursor: pointer;" scope="col">Release Year</th>
    </tr>
  </thead>
  <tbody>
   {% for whiskey in site.data.whiskeyindex %}
   <tr data-name="{{ whiskey.Name }}">
     <td class="expand-icon"></td>
     <td>{{ whiskey.Name }}</td>
     <td>{{ whiskey.Batch }}</td>
     <td>{{ whiskey.Age }}</td>
     <td>{{ whiskey.Proof }}</td>
     <td>{{ whiskey.ReleaseYear }}</td>
   </tr>
   {% endfor %}
  </tbody>
</table>

## About This Database

This whiskey proof database is maintained as a free resource for bourbon and whiskey enthusiasts. Our goal is to provide accurate, up-to-date information about whiskey batch releases, helping collectors and enthusiasts make informed decisions.

**Search our extensive database** of barrel proof bourbon, cask strength whiskey, and limited releases from top distilleries including Buffalo Trace Antique Collection (BTAC), Heaven Hill, Old Forester, Wild Turkey, and many more. Find specific batch numbers, compare proof variations, track age statements, and discover release year information for your favorite bottles.

### Distilleries Covered

We track batches from major bourbon and whiskey producers including:
- **Buffalo Trace Distillery**: George T. Stagg, Stagg Jr., E.H. Taylor, William Larue Weller, Thomas H. Handy, Eagle Rare 17, Sazerac 18
- **Heaven Hill**: Elijah Craig Barrel Proof, Larceny Barrel Proof, Parker's Heritage Collection, Old Fitzgerald Bottled-in-Bond
- **Jim Beam**: Booker's, Little Book
- **Old Forester**: Birthday Bourbon
- **Wild Turkey**: Russell's Reserve, Wild Turkey Master's Keep
- And many more including Four Roses, Michter's, Knob Creek, Jack Daniel's

### Popular Searches

Find information about popular releases like George T. Stagg, Elijah Craig Barrel Proof, Booker's Bourbon, Stagg Jr., E.H. Taylor Barrel Proof, and other limited release bourbons. Perfect for collectors, enthusiasts, and anyone looking to verify batch details before purchase.

### How to Use

1. Use the search bar to filter by whiskey name, batch number, proof, or any other field
2. Click column headers to sort the data
3. Click the arrow icon to expand/collapse batch groups for easier viewing

*Last updated: {{ site.time | date: "%B %Y" }}*

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-938KTTLKL3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-938KTTLKL3');
</script>

<p align="center">
  <a href="https://www.buymeacoffee.com/whiskeyproofs">
    <img src="assets/buymeadrink.png" alt="Buy me a drink" height="60">
  </a>
</p>

<script src="{{ '/assets/js/whiskey-index.js' | relative_url }}"></script>

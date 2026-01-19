---
layout: default
title: Whiskey Proof Index - Bourbon Batch Database & Barrel Proof Reference
description: "Comprehensive searchable database of bourbon and whiskey batches. Find proof values, release years, age statements, and batch numbers for Buffalo Trace, Heaven Hill, and other premium distilleries."
---

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3605565427529797"
     crossorigin="anonymous"></script>

<link rel="stylesheet" href="{{ '/assets/css/whiskey-index.css' | relative_url }}">

# Whiskey Proof Index - Bourbon Batch Database

Your comprehensive reference for whiskey batch information, proofs, and release years. Whether you're a bourbon collector tracking down specific batches, an enthusiast researching proof variations across different releases, or simply curious about whiskey and bourbon releases over the years, this searchable database helps you find exactly what you're looking for.

**Search our extensive database** of barrel proof bourbon, cask strength whiskey, and limited releases from top distilleries including Buffalo Trace Antique Collection (BTAC), Heaven Hill, Old Forester, Wild Turkey, and many more. Find specific batch numbers, compare proof variations, track age statements, and discover release year information for your favorite bottles.

## Features

- **Comprehensive Database**: Hundreds of whiskey and bourbon entries with detailed batch information
- **Searchable Interface**: Quickly find specific batches by name, distillery, proof, or release year
- **Sortable Columns**: Organize data by name, batch number, age, proof, or release year
- **Regular Updates**: Database is continuously updated with new releases and batch information

## Popular Searches

Find information about popular releases like George T. Stagg, Elijah Craig Barrel Proof, Booker's Bourbon, Stagg Jr., E.H. Taylor Barrel Proof, and other limited release bourbons. Perfect for collectors, enthusiasts, and anyone looking to verify batch details before purchase.

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

### Distilleries Covered

We track batches from major bourbon and whiskey producers including:
- **Buffalo Trace Distillery**: George T. Stagg, Stagg Jr., E.H. Taylor, Buffalo Trace Antique Collection (BTAC)
- **Heaven Hill**: Elijah Craig Barrel Proof, Henry McKenna, Larceny Barrel Proof
- **Wild Turkey**: Russell's Reserve, Rare Breed
- **Old Forester**: Birthday Bourbon, Barrel Strength
- And many more craft and premium distilleries

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

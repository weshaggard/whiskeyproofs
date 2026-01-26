---
layout: default
title: Whiskey proof index
description: "Comprehensive searchable index of bourbon and whiskey batches. Find proof values, release years, age statements, and batch numbers for Buffalo Trace, Heaven Hill, and other premium distilleries."
---

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3605565427529797" crossorigin="anonymous"></script>

<link rel="stylesheet" href="{{ '/assets/css/whiskey-index.css' | relative_url }}">

# Whiskey proof index

<div class="filter-container">
  <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search by name, batch, proof, etc...">
</div>

<table class="whiskey-table" id="whiskeyTable" role="table" aria-label="Whiskey and Bourbon Batch Information Index">
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
     <td>
       {%- if whiskey.url and whiskey.url != '' -%}
         <a href="{{ whiskey.url | escape }}" target="_blank" rel="noopener">{{ whiskey.Batch }}</a>
       {%- else -%}
         {{ whiskey.Batch }}
       {%- endif -%}
       {%- if whiskey.TTB_ID and whiskey.TTB_ID != '' -%}
         {%- comment -%}
         TTB IDs start with a 2-digit year prefix (e.g., 02=2002, 09=2009, 23=2023).
         TTB changed their online system around 2009. IDs with prefix 02-08 (years 2002-2008)
         use the older publicViewImage.do format, while IDs 09+ (2009 onward) use the newer
         viewColaDetails.do format. The cutoff at 09 reflects this system change.
         {%- endcomment -%}
         {%- assign ttb_year_prefix = whiskey.TTB_ID | slice: 0, 2 | plus: 0 -%}
         {%- if ttb_year_prefix < 9 -%}
           &nbsp;<a href="https://ttbonline.gov/colasonline/publicViewImage.do?id={{ whiskey.TTB_ID }}" target="_blank" rel="noopener noreferrer" title="View TTB Label">🏷️</a>
         {%- else -%}
           &nbsp;<a href="https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={{ whiskey.TTB_ID }}" target="_blank" rel="noopener noreferrer" title="View TTB Label">🏷️</a>
         {%- endif -%}
       {%- endif -%}
     </td>
     <td>{{ whiskey.Age }}</td>
     <td>{{ whiskey.Proof }}</td>
     <td>{{ whiskey.ReleaseYear }}</td>
   </tr>
   {% endfor %}
  </tbody>
</table>

## About this index

This whiskey proof index is maintained as a free resource for bourbon and whiskey enthusiasts. Whether you're a collector tracking down specific batches, an enthusiast researching proof variations, or simply curious about whiskey releases over the years, this searchable index provides accurate, up-to-date information about whiskey batch releases to help you find exactly what you're looking for.

**Search our extensive index** of barrel proof bourbon, cask strength whiskey, and limited releases from top distilleries including Buffalo Trace Antique Collection (BTAC), Heaven Hill, Old Forester, Wild Turkey, and many more. Find specific batch numbers, compare proof variations, track age statements, and discover release year information for your favorite bottles.

### How to use

1. Use the search bar to filter by whiskey name, batch number, proof, or any other field
2. Click column headers to sort the data
3. Click the arrow icon to expand/collapse batch groups for easier viewing

### How to help

Found incorrect data? Want to add a missing whiskey? Have suggestions? <a href="https://github.com/weshaggard/whiskeyproofs/issues/new/choose" target="_blank" rel="noopener noreferrer">Submit Feedback</a>

**Note:** The 🏷️ label emoji indicates that a TTB (Alcohol and Tobacco Tax and Trade Bureau) label is available for that batch. Click the emoji to view the official label registration. Please be aware that not all TTB IDs have been verified and may be incorrect. If you notice an incorrect label, please submit feedback using the link above.

<p align="left">
  <a href="https://www.buymeacoffee.com/whiskeyproofs">
    <img src="assets/buymeadrink.png" alt="Buy me a drink" height="60">
  </a>
</p>

*Last updated: {{ site.time | date: "%m/%d/%Y" }}*

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-938KTTLKL3"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-938KTTLKL3');
</script>

<script src="{{ '/assets/js/whiskey-index.js' | relative_url }}"></script>

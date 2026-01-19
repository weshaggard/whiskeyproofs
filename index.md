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
      <th onclick="sortTable(6)" style="cursor: pointer;" scope="col" class="ttb-column">TTB</th>
    </tr>
  </thead>
  <tbody>
   {% for whiskey in site.data.whiskeyindex %}
   <tr data-name="{{ whiskey.Name }}">
     <td class="expand-icon"></td>
     <td>{{ whiskey.Name }}</td>
     <td>
       {%- if whiskey.url and whiskey.url != '' -%}
         {%- assign url_start = whiskey.url | slice: 0, 8 | downcase -%}
         {%- if url_start == 'https://' or url_start == 'http://' -%}
           <a href="{{ whiskey.url | url_encode }}" target="_blank" rel="noopener noreferrer">{{ whiskey.Batch }}</a>
         {%- else -%}
           {{ whiskey.Batch }}
         {%- endif -%}
       {%- else -%}
         {{ whiskey.Batch }}
       {%- endif -%}
     </td>
     <td>{{ whiskey.Age }}</td>
     <td>{{ whiskey.Proof }}</td>
     <td>{{ whiskey.ReleaseYear }}</td>
     <td class="ttb-column">{% if whiskey.TTB_ID and whiskey.TTB_ID != '' %}<a href="https://ttbonline.gov/colasonline/viewColaDetails.do?action=publicFormDisplay&ttbid={{ whiskey.TTB_ID }}" target="_blank" rel="noopener noreferrer">🔗</a>{% endif %}</td>
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

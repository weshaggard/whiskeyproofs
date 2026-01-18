---
layout: default
title: Whiskey proof index
---

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3605565427529797"
     crossorigin="anonymous"></script>

<link rel="stylesheet" href="{{ '/assets/css/whiskey-index.css' | relative_url }}">

# Whiskey proof index

Welcome to the Whiskey proof index - your comprehensive reference for bourbon batch information, proofs, and release years. Whether you're a collector tracking down specific batches, an enthusiast researching proof variations, or simply curious about whiskey releases over the years, this searchable index helps you find exactly what you're looking for.

<div class="filter-container">
  <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search by name, batch, proof, etc...">
</div>

<table class="whiskey-table" id="whiskeyTable">
  <thead>
    <tr>
      <th style="width: auto;"></th>
      <th onclick="sortTable(1)" style="cursor: pointer;">Name</th>
      <th onclick="sortTable(2)" style="cursor: pointer;">Batch</th>
      <th onclick="sortTable(3)" style="cursor: pointer;">Age</th>
      <th onclick="sortTable(4)" style="cursor: pointer;">Proof</th>
      <th onclick="sortTable(5)" style="cursor: pointer;">Release Year</th>
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

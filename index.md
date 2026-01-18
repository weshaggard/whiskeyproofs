---
layout: default
title: Whiskey Proofs Index
---

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3605565427529797"
     crossorigin="anonymous"></script>

<link rel="stylesheet" href="{{ '/assets/css/whiskey-index.css' | relative_url }}">

# Whiskey Proofs Index

Welcome to the Whiskey Proofs Index - your comprehensive reference for bourbon batch information, proofs, and release years. Whether you're a collector tracking down specific batches, an enthusiast researching proof variations, or simply curious about whiskey releases over the years, this searchable index helps you find exactly what you're looking for.

<div class="filter-container">
  <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search by name, batch, proof, etc...">
</div>

<table class="whiskey-table" id="whiskeyTable">
  <thead>
    <tr>
      <th style="width: 30px;"></th>
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

<div style="margin-top: 15px; text-align: center;">
  <a href="https://www.buymeacoffee.com/whiskeyproofs" style="display:inline-flex; align-items:center; gap:8px; padding:8px 16px; border:2px solid #b8956a; border-radius:8px; background-color:#b8956a; text-decoration:none; color:#ffffff; font-family:'Cookie',cursive; font-size:1.5rem; font-weight:400; transition:all 0.2s ease;">
    Buy me a drink <img src="{{ '/assets/whiskeyglass.png' | relative_url }}" alt="Whiskey glass" height="28" style="display:inline-block;">
  </a>
</div>

<script src="{{ '/assets/js/whiskey-index.js' | relative_url }}"></script>

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
  <label for="searchInput">Search:</label>
  <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search by name, batch, proof, etc...">
</div>

<table class="whiskey-table" id="whiskeyTable">
  <thead>
    <tr>
      <th onclick="sortTable(0)" style="width: 30px;"></th>
      <th onclick="sortTable(1)">Name ▲▼</th>
      <th onclick="sortTable(2)">Batch ▲▼</th>
      <th onclick="sortTable(3)">Age ▲▼</th>
      <th onclick="sortTable(4)">Proof ▲▼</th>
      <th onclick="sortTable(5)">Release Year ▲▼</th>
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
  <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="whiskeyproofs" data-color="#FFDD00" data-emoji="🥃" data-font="Cookie" data-text="Buy me a drink" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
</div>

<script src="{{ '/assets/js/whiskey-index.js' | relative_url }}"></script>

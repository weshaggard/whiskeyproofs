---
layout: default
title: Whiskey Proofs Index
---

<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3605565427529797"
     crossorigin="anonymous"></script>

<link rel="stylesheet" href="{{ '/assets/css/whiskey-index.css' | relative_url }}">

# Whiskey Proofs Index

Welcome to the Whiskey Index - your comprehensive reference for bourbon batch information, proof values, and release years. Whether you're a collector tracking down specific batches, an enthusiast researching proof variations, or simply curious about whiskey releases over the years, this searchable index helps you find exactly what you're looking for.

Use the search and filter tools below to find specific whiskies by name, distillery, batch number, proof, age, or release year. Sort any column by clicking the header to organize the data your way.

<div class="filter-container">
  <label for="searchInput">Search:</label>
  <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search by name, distillery, batch, proof, etc...">
</div>

<table class="whiskey-table" id="whiskeyTable">
  <thead>
    <tr>
      <th onclick="sortTable(0)">Distillery ▲▼</th>
      <th onclick="sortTable(1)">Name ▲▼</th>
      <th onclick="sortTable(2)">Batch ▲▼</th>
      <th onclick="sortTable(3)">Age ▲▼</th>
      <th onclick="sortTable(4)">Proof ▲▼</th>
      <th onclick="sortTable(5)">Release Year ▲▼</th>
      <th onclick="sortTable(6)">Type ▲▼</th>
    </tr>
  </thead>
  <tbody>
    {% assign whiskies_by_distillery = site.data.whiskeyindex | group_by: "Distillery" | sort: "name" %}
    {% for distillery_group in whiskies_by_distillery %}
      {% assign whiskies_by_name = distillery_group.items | group_by: "Name" | sort: "name" %}
      {% for name_group in whiskies_by_name %}
        {% for whiskey in name_group.items %}
        <tr>
          <td>{{ whiskey.Distillery }}</td>
          <td>{{ whiskey.Name }}</td>
          <td>{{ whiskey.Batch }}</td>
          <td>{{ whiskey.Age }}</td>
          <td>{{ whiskey.Proof }}</td>
          <td>{{ whiskey.ReleaseYear }}</td>
          <td>{{ whiskey.Type }}</td>
        </tr>
        {% endfor %}
      {% endfor %}
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

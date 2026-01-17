---
layout: default
title: Whiskey Index
---

<link rel="stylesheet" href="{{ '/assets/css/whiskey-index.css' | relative_url }}">

# Whiskey Index

<div class="stats">
  <p><strong>Total Whiskies:</strong> <span id="totalCount">{{ site.data.whiskies | size }}</span></p>
</div>

<div class="filter-container">
  <label for="typeFilter">Filter by Type:</label>
  <select id="typeFilter" onchange="filterTable()">
    <option value="">All Types</option>
    <option value="Bourbon">Bourbon</option>
    <option value="Scotch">Scotch</option>
    <option value="Rye">Rye</option>
  </select>
  
  <label for="searchInput">Search:</label>
  <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Search by name, distillery, batch, proof, etc...">
</div>

<table class="whiskey-table" id="whiskeyTable">
  <thead>
    <tr>
      <th onclick="sortTable(0)">Name ▲▼</th>
      <th onclick="sortTable(1)">Distillery ▲▼</th>
      <th onclick="sortTable(2)">Batch ▲▼</th>
      <th onclick="sortTable(3)">Age ▲▼</th>
      <th onclick="sortTable(4)">Proof ▲▼</th>
      <th onclick="sortTable(5)">Type ▲▼</th>
      <th onclick="sortTable(6)">Release Year ▲▼</th>
    </tr>
  </thead>
  <tbody>
    {% assign whiskies_by_distillery = site.data.whiskies | group_by: "Distillery" | sort: "name" %}
    {% for distillery_group in whiskies_by_distillery %}
      {% assign whiskies_by_name = distillery_group.items | group_by: "Name" | sort: "name" %}
      {% for name_group in whiskies_by_name %}
        {% for whiskey in name_group.items %}
        <tr>
          <td>{{ whiskey.Name }}</td>
          <td>{{ whiskey.Distillery }}</td>
          <td>{{ whiskey.Batch }}</td>
          <td>{{ whiskey.Age }}</td>
          <td>{{ whiskey.Proof }}</td>
          <td>{{ whiskey.Type }}</td>
          <td>{{ whiskey.ReleaseYear }}</td>
        </tr>
        {% endfor %}
      {% endfor %}
    {% endfor %}
  </tbody>
</table>

<div class="page-counter" style="margin-top: 20px; text-align: center; font-size: 0.9em; color: #666;">
  <p>Page Views: <img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fweshaggard.github.io%2Fwhiskeydata&count_bg=%238B4513&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=visits&edge_flat=false" alt="visitor counter"></p>
</div>

<div style="margin-top: 15px; text-align: center;">
  <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="whiskeyproofs" data-color="#FFDD00" data-emoji="🥃" data-font="Cookie" data-text="Buy me a drink" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
</div>

<script src="{{ '/assets/js/whiskey-index.js' | relative_url }}"></script>

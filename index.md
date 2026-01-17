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
    {% for whiskey in site.data.whiskies %}
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
  </tbody>
</table>

<script src="{{ '/assets/js/whiskey-index.js' | relative_url }}"></script>

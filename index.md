---
layout: default
title: Whiskey Index
---

<style>
  .whiskey-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 0.9em;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
  }
  
  .whiskey-table thead tr {
    background-color: #8B4513;
    color: #ffffff;
    text-align: left;
  }
  
  .whiskey-table th,
  .whiskey-table td {
    padding: 12px 15px;
  }
  
  .whiskey-table tbody tr {
    border-bottom: 1px solid #dddddd;
  }
  
  .whiskey-table tbody tr:nth-of-type(even) {
    background-color: #f3f3f3;
  }
  
  .whiskey-table tbody tr:last-of-type {
    border-bottom: 2px solid #8B4513;
  }
  
  .whiskey-table tbody tr:hover {
    background-color: #f1e8dc;
  }
  
  .filter-container {
    margin: 20px 0;
    padding: 15px;
    background-color: #f8f8f8;
    border-radius: 5px;
  }
  
  .filter-container label {
    margin-right: 10px;
    font-weight: bold;
  }
  
  .filter-container input,
  .filter-container select {
    padding: 5px 10px;
    margin-right: 15px;
    border: 1px solid #ddd;
    border-radius: 3px;
  }
  
  h1 {
    color: #8B4513;
    border-bottom: 3px solid #8B4513;
    padding-bottom: 10px;
  }
  
  .stats {
    margin: 20px 0;
    padding: 15px;
    background-color: #fff8dc;
    border-left: 4px solid #8B4513;
  }
</style>

<h1>Whiskey Index</h1>

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

<script>
  // Sort table functionality
  function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("whiskeyTable");
    switching = true;
    dir = "asc";
    
    while (switching) {
      switching = false;
      rows = table.rows;
      
      for (i = 1; i < (rows.length - 1); i++) {
        shouldSwitch = false;
        x = rows[i].getElementsByTagName("TD")[n];
        y = rows[i + 1].getElementsByTagName("TD")[n];
        
        var xContent = x.innerHTML.toLowerCase();
        var yContent = y.innerHTML.toLowerCase();
        
        // Try to parse as numbers for numeric columns
        var xNum = parseFloat(xContent);
        var yNum = parseFloat(yContent);
        
        if (!isNaN(xNum) && !isNaN(yNum)) {
          if (dir == "asc") {
            if (xNum > yNum) {
              shouldSwitch = true;
              break;
            }
          } else if (dir == "desc") {
            if (xNum < yNum) {
              shouldSwitch = true;
              break;
            }
          }
        } else {
          if (dir == "asc") {
            if (xContent > yContent) {
              shouldSwitch = true;
              break;
            }
          } else if (dir == "desc") {
            if (xContent < yContent) {
              shouldSwitch = true;
              break;
            }
          }
        }
      }
      
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        switchcount++;
      } else {
        if (switchcount == 0 && dir == "asc") {
          dir = "desc";
          switching = true;
        }
      }
    }
  }
  
  // Filter table functionality
  function filterTable() {
    var typeFilter = document.getElementById("typeFilter").value.toLowerCase();
    var searchInput = document.getElementById("searchInput").value.toLowerCase();
    var table = document.getElementById("whiskeyTable");
    var rows = table.getElementsByTagName("tr");
    var visibleCount = 0;
    
    for (var i = 1; i < rows.length; i++) {
      var row = rows[i];
      var cells = row.getElementsByTagName("td");
      
      if (cells.length > 0) {
        var name = cells[0].innerHTML.toLowerCase();
        var distillery = cells[1].innerHTML.toLowerCase();
        var batch = cells[2].innerHTML.toLowerCase();
        var age = cells[3].innerHTML.toLowerCase();
        var proof = cells[4].innerHTML.toLowerCase();
        var type = cells[5].innerHTML.toLowerCase();
        var releaseYear = cells[6].innerHTML.toLowerCase();
        
        var typeMatch = typeFilter === "" || type === typeFilter;
        var searchMatch = searchInput === "" || 
                         name.includes(searchInput) || 
                         distillery.includes(searchInput) ||
                         batch.includes(searchInput) ||
                         age.includes(searchInput) ||
                         proof.includes(searchInput) ||
                         releaseYear.includes(searchInput);
        
        if (typeMatch && searchMatch) {
          row.style.display = "";
          visibleCount++;
        } else {
          row.style.display = "none";
        }
      }
    }
    
    document.getElementById("totalCount").innerHTML = visibleCount;
  }
</script>

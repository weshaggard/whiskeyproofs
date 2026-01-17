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

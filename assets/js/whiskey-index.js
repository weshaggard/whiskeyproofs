// Global state for grouped data
var groupedData = {};
var expandedGroups = {};

// Initialize table grouping on page load
document.addEventListener('DOMContentLoaded', function() {
  initializeGroupedTable();
});

// Initialize the grouped table
function initializeGroupedTable() {
  var table = document.getElementById("whiskeyTable");
  var tbody = table.getElementsByTagName("tbody")[0];
  var rows = Array.from(tbody.getElementsByTagName("tr"));
  
  // Group rows by name
  groupedData = {};
  rows.forEach(function(row) {
    var name = row.getAttribute('data-name');
    if (!groupedData[name]) {
      groupedData[name] = [];
    }
    groupedData[name].push(row);
  });
  
  // Clear tbody
  tbody.innerHTML = '';
  
  // Recreate table with grouped rows
  Object.keys(groupedData).sort().forEach(function(name) {
    var group = groupedData[name];
    
    // Create group header row
    var headerRow = group[0].cloneNode(true);
    headerRow.classList.add('group-header');
    headerRow.setAttribute('data-group-name', name);
    
    var expandCell = headerRow.querySelector('.expand-icon');
    if (group.length > 1) {
      expandCell.innerHTML = '<span class="expand-arrow">▶</span>';
      expandCell.style.cursor = 'pointer';
      expandCell.onclick = function() {
        toggleGroup(name);
      };
      // Show count badge
      var nameCell = headerRow.cells[1];
      nameCell.innerHTML = name + ' <span class="batch-count">(' + group.length + ')</span>';
    } else {
      expandCell.innerHTML = '';
    }
    
    tbody.appendChild(headerRow);
    
    // Add detail rows (collapsed by default if more than one)
    if (group.length > 1) {
      for (var i = 0; i < group.length; i++) {
        var detailRow = group[i].cloneNode(true);
        detailRow.classList.add('group-detail');
        detailRow.classList.add('collapsed');
        detailRow.setAttribute('data-group-name', name);
        
        // Clear the name cell for detail rows
        detailRow.cells[0].innerHTML = '';
        detailRow.cells[1].innerHTML = '';
        
        tbody.appendChild(detailRow);
      }
      expandedGroups[name] = false;
    } else {
      expandedGroups[name] = true;
    }
  });
}

// Toggle group expand/collapse
function toggleGroup(groupName) {
  var table = document.getElementById("whiskeyTable");
  var rows = table.getElementsByTagName("tr");
  var isExpanded = expandedGroups[groupName];
  
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    if (row.getAttribute('data-group-name') === groupName) {
      if (row.classList.contains('group-header')) {
        var arrow = row.querySelector('.expand-arrow');
        if (arrow) {
          arrow.textContent = isExpanded ? '▶' : '▼';
        }
      } else if (row.classList.contains('group-detail')) {
        if (isExpanded) {
          row.classList.add('collapsed');
        } else {
          row.classList.remove('collapsed');
        }
      }
    }
  }
  
  expandedGroups[groupName] = !isExpanded;
}

// Expand all groups
function expandAllGroups() {
  var table = document.getElementById("whiskeyTable");
  var rows = table.getElementsByTagName("tr");
  
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    if (row.classList.contains('group-header')) {
      var arrow = row.querySelector('.expand-arrow');
      if (arrow) {
        arrow.textContent = '▼';
      }
    } else if (row.classList.contains('group-detail')) {
      row.classList.remove('collapsed');
    }
  }
  
  // Update all expanded states
  Object.keys(expandedGroups).forEach(function(key) {
    expandedGroups[key] = true;
  });
}

// Sort table functionality (updated for grouped table)
function sortTable(n) {
  // Sorting disabled for grouped table to maintain grouping
  // Could be enhanced to sort within groups or sort groups
  return;
}

// Filter table functionality (updated for grouped table)
function filterTable() {
  var searchInput = document.getElementById("searchInput").value.toLowerCase();
  var table = document.getElementById("whiskeyTable");
  var rows = table.getElementsByTagName("tr");
  
  // If searching, expand all groups
  if (searchInput !== "") {
    expandAllGroups();
  }
  
  for (var i = 1; i < rows.length; i++) {
    var row = rows[i];
    var cells = row.getElementsByTagName("td");
    
    if (cells.length > 0) {
      // Get cell content, accounting for the expand icon column
      var name = cells[1] ? cells[1].textContent.toLowerCase() : '';
      var batch = cells[2] ? cells[2].textContent.toLowerCase() : '';
      var age = cells[3] ? cells[3].textContent.toLowerCase() : '';
      var proof = cells[4] ? cells[4].textContent.toLowerCase() : '';
      var releaseYear = cells[5] ? cells[5].textContent.toLowerCase() : '';
      
      var searchMatch = searchInput === "" || 
                       name.includes(searchInput) || 
                       batch.includes(searchInput) ||
                       age.includes(searchInput) ||
                       proof.includes(searchInput) ||
                       releaseYear.includes(searchInput);
      
      if (searchMatch) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    }
  }
}

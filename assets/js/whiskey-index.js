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
    // Store the raw data from each row
    var cells = row.getElementsByTagName("td");
    groupedData[name].push({
      name: name,
      batch: cells[2] ? cells[2].textContent : '',
      age: cells[3] ? cells[3].textContent : '',
      proof: cells[4] ? cells[4].textContent : '',
      releaseYear: cells[5] ? cells[5].textContent : ''
    });
  });
  
  // Clear tbody
  tbody.innerHTML = '';
  
  // Recreate table with grouped rows
  Object.keys(groupedData).sort().forEach(function(name) {
    var group = groupedData[name];
    
    // Create group header row from first item
    var headerRow = document.createElement('tr');
    headerRow.classList.add('group-header');
    headerRow.setAttribute('data-group-name', name);
    
    var expandCell = document.createElement('td');
    expandCell.classList.add('expand-icon');
    if (group.length > 1) {
      expandCell.innerHTML = '<span class="expand-arrow">▶</span>';
      expandCell.style.cursor = 'pointer';
      expandCell.onclick = function() {
        toggleGroup(name);
      };
    }
    headerRow.appendChild(expandCell);
    
    var nameCell = document.createElement('td');
    if (group.length > 1) {
      nameCell.innerHTML = name + ' <span class="batch-count">(' + group.length + ')</span>';
    } else {
      nameCell.textContent = name;
    }
    headerRow.appendChild(nameCell);
    
    // Add data from first item
    var batchCell = document.createElement('td');
    batchCell.textContent = group[0].batch;
    headerRow.appendChild(batchCell);
    
    var ageCell = document.createElement('td');
    ageCell.textContent = group[0].age;
    headerRow.appendChild(ageCell);
    
    var proofCell = document.createElement('td');
    proofCell.textContent = group[0].proof;
    headerRow.appendChild(proofCell);
    
    var yearCell = document.createElement('td');
    yearCell.textContent = group[0].releaseYear;
    headerRow.appendChild(yearCell);
    
    tbody.appendChild(headerRow);
    
    // Add detail rows (collapsed by default if more than one)
    if (group.length > 1) {
      for (var i = 0; i < group.length; i++) {
        var detailRow = document.createElement('tr');
        detailRow.classList.add('group-detail');
        detailRow.classList.add('collapsed');
        detailRow.setAttribute('data-group-name', name);
        
        // Empty expand icon cell
        detailRow.appendChild(document.createElement('td'));
        
        // Add name cell for expanded rows
        var detailNameCell = document.createElement('td');
        detailNameCell.textContent = name;
        detailRow.appendChild(detailNameCell);
        
        // Add batch data
        var detailBatch = document.createElement('td');
        detailBatch.textContent = group[i].batch;
        detailRow.appendChild(detailBatch);
        
        var detailAge = document.createElement('td');
        detailAge.textContent = group[i].age;
        detailRow.appendChild(detailAge);
        
        var detailProof = document.createElement('td');
        detailProof.textContent = group[i].proof;
        detailRow.appendChild(detailProof);
        
        var detailYear = document.createElement('td');
        detailYear.textContent = group[i].releaseYear;
        detailRow.appendChild(detailYear);
        
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

// Sort table functionality - disabled for grouped table
// Sorting is disabled to maintain grouping by name
function sortTable(n) {
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

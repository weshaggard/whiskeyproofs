// Global state for grouped data
var groupedData = {};
var expandedGroups = {};
var currentSortColumn = -1;
var currentSortDirection = 1; // 1 for ascending, -1 for descending
var allExpanded = false; // Track whether all groups are expanded
var showTTBColumn = false; // Track whether TTB column should be shown

// Initialize table grouping on page load
document.addEventListener('DOMContentLoaded', function() {
  // Check for showTTB query parameter
  var urlParams = new URLSearchParams(window.location.search);
  showTTBColumn = urlParams.get('showTTB') === 'true';
  
  // Hide TTB column if not requested
  if (!showTTBColumn) {
    var ttbElements = document.querySelectorAll('.ttb-column');
    ttbElements.forEach(function(el) {
      el.style.display = 'none';
    });
  }
  
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
    // Column indices: 0=expand icon, 1=name, 2=batch, 3=age, 4=proof, 5=release year, 6=TTB
    var cells = row.getElementsByTagName("td");
    groupedData[name].push({
      name: name,
      batch: cells[2] ? cells[2].textContent : '',
      // batchHTML contains pre-rendered, server-side sanitized HTML from Jekyll
      // URLs are validated and escaped on the server before being inserted into links
      batchHTML: cells[2] ? cells[2].innerHTML : '',
      age: cells[3] ? cells[3].textContent : '',
      proof: cells[4] ? cells[4].textContent : '',
      releaseYear: cells[5] ? cells[5].textContent : '',
      // ttb contains pre-rendered TTB link HTML from server
      ttb: cells[6] ? cells[6].innerHTML : ''
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
    batchCell.innerHTML = group[0].batchHTML;
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
    
    var ttbCell = document.createElement('td');
    ttbCell.classList.add('ttb-column');
    ttbCell.innerHTML = group[0].ttb;
    if (!showTTBColumn) {
      ttbCell.style.display = 'none';
    }
    headerRow.appendChild(ttbCell);
    
    tbody.appendChild(headerRow);
    
    // Add detail rows (collapsed by default if more than one)
    // Start from index 1 to skip the first item (already shown in header row)
    if (group.length > 1) {
      for (var i = 1; i < group.length; i++) {
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
        detailBatch.innerHTML = group[i].batchHTML;
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
        
        var detailTTB = document.createElement('td');
        detailTTB.classList.add('ttb-column');
        detailTTB.innerHTML = group[i].ttb;
        if (!showTTBColumn) {
          detailTTB.style.display = 'none';
        }
        detailRow.appendChild(detailTTB);
        
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
  allExpanded = true;
  updateToggleAllIcon();
}

// Collapse all groups
function collapseAllGroups() {
  var table = document.getElementById("whiskeyTable");
  var rows = table.getElementsByTagName("tr");
  
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    if (row.classList.contains('group-header')) {
      var arrow = row.querySelector('.expand-arrow');
      if (arrow) {
        arrow.textContent = '▶';
      }
    } else if (row.classList.contains('group-detail')) {
      row.classList.add('collapsed');
    }
  }
  
  // Update all expanded states
  Object.keys(expandedGroups).forEach(function(key) {
    if (groupedData[key] && groupedData[key].length > 1) {
      expandedGroups[key] = false;
    }
  });
  allExpanded = false;
  updateToggleAllIcon();
}

// Toggle all groups between expanded and collapsed
function toggleAllGroups() {
  if (allExpanded) {
    collapseAllGroups();
  } else {
    expandAllGroups();
  }
}

// Update the toggle all icon in the header
function updateToggleAllIcon() {
  var toggleIcon = document.getElementById('toggle-all-icon');
  if (toggleIcon) {
    toggleIcon.textContent = allExpanded ? '▼' : '▶';
  }
}

// Sort table functionality - sorts groups by selected column
function sortTable(columnIndex) {
  // Column mapping: 0=expand icon (no sort), 1=name, 2=batch, 3=age, 4=proof, 5=release year, 6=TTB
  if (columnIndex === 0) return; // Don't sort by expand icon
  
  // Toggle sort direction if clicking the same column
  if (currentSortColumn === columnIndex) {
    currentSortDirection *= -1;
  } else {
    currentSortColumn = columnIndex;
    currentSortDirection = 1; // Default to ascending
  }
  
  // Save current expanded state
  var savedExpandedState = Object.assign({}, expandedGroups);
  
  // Get column name for sorting
  var columnMap = {
    1: 'name',
    2: 'batch',
    3: 'age',
    4: 'proof',
    5: 'releaseYear',
    6: 'ttb'
  };
  var sortKey = columnMap[columnIndex];
  
  // Helper function to compare values based on sort key
  var compareValues = function(valA, valB) {
    // Handle TTB column (sort by presence of link)
    if (sortKey === 'ttb') {
      // Extract text from HTML (just check if link exists)
      var hasLinkA = valA && valA.includes('<a');
      var hasLinkB = valB && valB.includes('<a');
      if (hasLinkA && !hasLinkB) return -1 * currentSortDirection;
      if (!hasLinkA && hasLinkB) return 1 * currentSortDirection;
      return 0;
    }
    
    // Handle numeric columns (age, proof, releaseYear)
    if (sortKey === 'age' || sortKey === 'proof' || sortKey === 'releaseYear') {
      valA = parseFloat(valA) || 0;
      valB = parseFloat(valB) || 0;
      return (valA - valB) * currentSortDirection;
    }
    
    // String comparison for name and batch
    if (valA < valB) return -1 * currentSortDirection;
    if (valA > valB) return 1 * currentSortDirection;
    return 0;
  };
  
  // Sort items within each group
  Object.keys(groupedData).forEach(function(groupName) {
    groupedData[groupName].sort(function(a, b) {
      return compareValues(a[sortKey], b[sortKey]);
    });
  });
  
  // Sort the groups based on the first item in each group
  var sortedGroupNames = Object.keys(groupedData).sort(function(a, b) {
    var valA = groupedData[a][0][sortKey];
    var valB = groupedData[b][0][sortKey];
    return compareValues(valA, valB);
  });
  
  // Rebuild the table with sorted groups
  var table = document.getElementById("whiskeyTable");
  var tbody = table.getElementsByTagName("tbody")[0];
  tbody.innerHTML = '';
  
  sortedGroupNames.forEach(function(name) {
    var group = groupedData[name];
    
    // Create group header row from first item
    var headerRow = document.createElement('tr');
    headerRow.classList.add('group-header');
    headerRow.setAttribute('data-group-name', name);
    
    var expandCell = document.createElement('td');
    expandCell.classList.add('expand-icon');
    if (group.length > 1) {
      expandCell.innerHTML = '<span class="expand-arrow">' + 
        (savedExpandedState[name] ? '▼' : '▶') + '</span>';
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
    batchCell.innerHTML = group[0].batchHTML;
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
    
    var ttbCell = document.createElement('td');
    ttbCell.classList.add('ttb-column');
    ttbCell.innerHTML = group[0].ttb;
    if (!showTTBColumn) {
      ttbCell.style.display = 'none';
    }
    headerRow.appendChild(ttbCell);
    
    tbody.appendChild(headerRow);
    
    // Add detail rows (collapsed or expanded based on saved state)
    if (group.length > 1) {
      for (var i = 1; i < group.length; i++) {
        var detailRow = document.createElement('tr');
        detailRow.classList.add('group-detail');
        if (!savedExpandedState[name]) {
          detailRow.classList.add('collapsed');
        }
        detailRow.setAttribute('data-group-name', name);
        
        // Empty expand icon cell
        detailRow.appendChild(document.createElement('td'));
        
        // Add name cell for expanded rows
        var detailNameCell = document.createElement('td');
        detailNameCell.textContent = name;
        detailRow.appendChild(detailNameCell);
        
        // Add batch data
        var detailBatch = document.createElement('td');
        detailBatch.innerHTML = group[i].batchHTML;
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
        
        var detailTTB = document.createElement('td');
        detailTTB.classList.add('ttb-column');
        detailTTB.innerHTML = group[i].ttb;
        if (!showTTBColumn) {
          detailTTB.style.display = 'none';
        }
        detailRow.appendChild(detailTTB);
        
        tbody.appendChild(detailRow);
      }
    }
  });
  
  // Restore expanded state
  expandedGroups = savedExpandedState;
  
  // Reapply search filter after sorting
  filterTable();
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
      // Column indices: 0=expand icon, 1=name, 2=batch, 3=age, 4=proof, 5=release year
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

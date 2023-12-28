let table = document.getElementById('tbl');
let tableRows = table.getElementsByTagName('tr');
const rowsPerPage = 10;
let page = 1;

function displayRows(pageNumber) {
  for (let i = 1; i < tableRows.length; i++) {
    if (i > rowsPerPage * (pageNumber - 1) && i <= rowsPerPage * pageNumber) {
      tableRows[i].style.display = '';
    } else {
      tableRows[i].style.display = 'none';
    }
  }
}

function setupPagination() {
  const pageNumber = Math.ceil((tableRows.length - 1) / rowsPerPage);
  let pagination = document.getElementById('pagination');
  
  pagination.innerHTML = "";
  for (let i = 1; i <= pageNumber; i++) {
    let pageLink = document.createElement('a');
    pageLink.href = '#';
    pageLink.textContent = i;
    pageLink.addEventListener('click', function() {
      page = i;
      displayRows(page);
    });
    pagination.appendChild(pageLink);
  }
}


function displayRowsbyMatches(matches, pageNumber) {
  let rows = table.getElementsByTagName('tr');
  for (let i = 1; i < rows.length; i++) {
    if (matches.includes(i)) {
      if (matches.indexOf(i) >= rowsPerPage * (pageNumber - 1) && matches.indexOf(i) < rowsPerPage * pageNumber) {
        rows[i].style.display = '';
      } else {
        rows[i].style.display = 'none';
      }
    } else {
      rows[i].style.display = 'none';
    }
  }
}

function updateTable() {
  let searchText = document.getElementById('searchInput').value.toLowerCase();
  let rows = table.getElementsByTagName('tr');
  let matches = [];
  for (let i = 1; i < rows.length; i++) {
      let cells = rows[i].getElementsByTagName('td');
      let found = false;
      for (let j = 0; j < cells.length; j++) {
          let cellText = cells[j].textContent.toLowerCase();
          if (cellText.includes(searchText)) {
              found = true;
              break;
          }
      }
      if (found) {
          matches.push(i);
      }
  }

  document.getElementById('pagination').innerHTML = "";
  let pageNum = Math.ceil(matches.length / rowsPerPage);
  for (let i = 1; i <= pageNum; i++) {
      let pageLink = document.createElement('a');
      pageLink.href = '#';
      pageLink.textContent = i;
      pageLink.addEventListener('click', function() {
          page = i;
          displayRowsbyMatches(matches, page);
      });
      document.getElementById('pagination').appendChild(pageLink);
  }
  displayRowsbyMatches(matches, 1);
}

setupPagination();
displayRows(page);
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
  cnt = 0
  for (let i = 0; i < tableRows.length; i++) {
    if(tableRows[i].style.display == ''){
        cnt++;
    }
  }
  const pageNumber = Math.ceil((cnt) / rowsPerPage);
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

function updateTable() {
  let filter = document.getElementById('searchInput').value.toLowerCase();
  for (let i = 1; i < tableRows.length; i++) {
    let cells = tableRows[i].getElementsByTagName('td');
    let found = false;
    for (let j = 0; j < cells.length; j++) {
      let cellText = cells[j].innerText.toLowerCase();
      if (cellText.includes(filter)) {
        found = true;
        break;
      }
    }
    if (found) {
      tableRows[i].style.display = '';
    } else {
      tableRows[i].style.display = 'none';
    }
  }
  page = 1;
  setupPagination(); 
}

setupPagination();
displayRows(page);
document.querySelectorAll('.c2').forEach(function(cell) {
    cell.addEventListener('click', function() {
      if (cell.classList.contains('expanded')) {
        cell.classList.remove('expanded');
      } else {
        cell.classList.add('expanded');
      }
    });
  });
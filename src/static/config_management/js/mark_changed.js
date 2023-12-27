let inputs = document.querySelectorAll('input[name]');

inputs.forEach(input => {
  let initialValue = input.value;
  input.addEventListener('input', function() {
    if (this.value !== initialValue) {
      this.style.border = '2px solid orange';
    } else {
      this.style.border = '2px solid black';
    }
  });
});
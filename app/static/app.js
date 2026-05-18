function handlePhaseChange(select) {
  var customInput = document.getElementById('phase_custom');
  if (!customInput) return;
  if (select.value === '__custom__') {
    customInput.classList.remove('hidden');
    customInput.focus();
  } else {
    customInput.classList.add('hidden');
    customInput.value = '';
  }
}

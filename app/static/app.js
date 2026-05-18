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

(function() {
  var startInput = document.getElementById('start_date');
  var goalInput = document.getElementById('goal_date');
  if (!startInput || !goalInput) return;

  var hint = document.getElementById('week-calc-hint');
  var error = document.getElementById('date-error');
  var form = startInput.closest('form');

  function calcWeeks() {
    var s = startInput.value;
    var g = goalInput.value;
    if (!s || !g) {
      hint.style.display = 'none';
      error.style.display = 'none';
      return;
    }
    var start = new Date(s);
    var goal = new Date(g);
    var diff = (goal - start) / (1000 * 60 * 60 * 24);
    if (diff <= 0) {
      error.textContent = 'Goal date must be after start date';
      error.style.display = 'block';
      hint.style.display = 'none';
      return;
    }
    error.style.display = 'none';
    var weeks = Math.ceil(diff / 7);
    hint.textContent = 'This will create ' + weeks + ' week' + (weeks > 1 ? 's' : '') + ' of entries';
    hint.style.display = 'block';
  }

  startInput.addEventListener('change', calcWeeks);
  goalInput.addEventListener('change', calcWeeks);

  form.addEventListener('submit', function(e) {
    var s = startInput.value;
    var g = goalInput.value;
    if (s && g) {
      var diff = (new Date(g) - new Date(s)) / (1000 * 60 * 60 * 24);
      if (diff <= 0) {
        e.preventDefault();
        error.textContent = 'Goal date must be after start date';
        error.style.display = 'block';
      }
    }
  });

  calcWeeks();
})();

const nameInput = document.querySelector('#name-input');
const nameOutput = document.querySelector('#name-output');

function onNameInput(e) {
  const name = e.target.value.trim();
  nameOutput.textContent = name || 'Anonymous';
}

nameInput.addEventListener('input', onNameInput);

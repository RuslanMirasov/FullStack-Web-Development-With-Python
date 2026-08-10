const loginForm = document.querySelector('.login-form');

function onLoginFormSubmit(e) {
  e.preventDefault();

  const { email, password } = e.target.elements;
  const emailValue = email.value.trim();
  const passwordValue = password.value.trim();

  if (!emailValue || !passwordValue) {
    alert('All form fields must be filled in');
    return;
  }

  const formData = {
    email: emailValue,
    password: passwordValue,
  };

  console.log(formData);
  e.target.reset();
}

loginForm.addEventListener('submit', onLoginFormSubmit);

// Function to show the profile form
function showProfileForm(){
  document.getElementById("profile-form").style.display = "block";
}

// Function to hide the profile form
function hideProfileForm(){
  document.getElementById("profile-form").style.display = "none";
}

// Function to compare the new password and repeat password fields
// and display an error message if they do not match
// and disable the submit button
document.addEventListener('DOMContentLoaded', function() {
  const newPasswordField = document.querySelector('[name="new_password"]');
  const repeatPasswordField = document.querySelector('[name="repeat_new_password"]');
  const submitButton = document.querySelector('button[name="update_password"]');

  // Create an element to display the error message.
  const errorMessage = document.createElement('div');
  errorMessage.style.color = 'red';
  repeatPasswordField.parentNode.insertBefore(errorMessage, repeatPasswordField.nextSibling);

  function checkPasswords() {
    if (repeatPasswordField.value !== newPasswordField.value) {
      errorMessage.textContent = "Passwords do not match!";
      submitButton.disabled = true;
    } else {
      errorMessage.textContent = "";
      submitButton.disabled = false;
    }
  }

  // Check on input changes.
  newPasswordField.addEventListener('input', checkPasswords);
  repeatPasswordField.addEventListener('input', checkPasswords);

  // Optionally, you can also prevent form submission.
  const form = submitButton.closest('form');
  form.addEventListener('submit', function(e) {
    if (repeatPasswordField.value !== newPasswordField.value) {
      e.preventDefault();
      errorMessage.textContent = "Passwords do not match!";
    }
  });
});


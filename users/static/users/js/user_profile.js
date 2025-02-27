// // Get the profile form
// document.getElementById("profileForm").addEventListener("submit", function(e){
//   e.preventDefault();
//   const data = {
//     first_name: document.getElementById("first_name").value,
//     last_name: document.getElementById("last_name").value,
//     bio: document.getElementById("bio").value,
//   }

//   console.log(data);

//   fetch("")

// });

// Function to show the profile form
function showProfileForm(){
  document.getElementById("profile-form").style.display = "block";
}

// Function to hide the profile form
function hideProfileForm(){
  document.getElementById("profile-form").style.display = "none";
}

// Wait for the entire DOM to be fully loaded before running the script
document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll('.btn-toggle-suspend').forEach(function(button) {
    button.addEventListener('click', function() {
      let userId = button.getAttribute('data-user-id');
      let url = `/toggle_suspend_user/${userId}/`; 
      
      // Make the AJAX request to the server
      fetch(url, {
        method: 'POST',
        headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        },
      })
      // Parse the JSON response
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      // Handle the JSON data
      .then(data => {
        // Update the button text and suspended status display based on the new state
        if (data.is_suspended) {
          button.textContent = 'Unsuspend';
          document.querySelector(`#user-${userId} .suspended-status`).textContent = 'Yes';
        } else {
          button.textContent = 'Suspend';
          document.querySelector(`#user-${userId} .suspended-status`).textContent = 'No';
        }
        alert(data.message);
      })
      .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the user status.');
      });
    });
  });


  // TODO:
  // Add the pagination functionality down here
  // Add event listeners to the pagination buttons
  // Initialize currentPage and totalPages based on rendered data (DOMcontentLoaded)
  let currentPage = parseInt(document.querySelector('#current-page').innerText.match(/\d+/)[0]);
  let totalPages = parseInt(document.getElementById('current-page').getAttribute('data-total-pages'));

  let searchQuery = "";

  function fetchPage(page) {
    let url = `/paginated_manage_users/?page=${page}`;
    if (searchQuery) {
      url += `&q=${encodeURIComponent(searchQuery)}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => {
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = "";

        // Append new users to the list
        data.users.forEach(user => {
          // Create the user item div
          const userListDiv = document.createElement('div');
          userListDiv.classList.add('user-item');

          // Create the user details div
          const userDetailsDiv = document.createElement('div');
          userDetailsDiv.classList.add('user-details');
          userDetailsDiv.innerHTML = `
            <strong>Username: ${user.username}</strong><br>
            <strong>Email: ${user.email}</strong><br>
            <strong>Date Joined: ${user.date_joined}</strong><br>
            <strong>User Type: ${user.user_type}</strong><br>
            <strong>Bio: ${user.bio}</strong><br>
            <strong>Alerts Created: ${user.alerts_created}</strong><br>
            <strong>Alerts Verified: ${user.alerts_verified}</strong><br>
            <strong>Email Verified: ${user.is_verified}</strong><br>
            <strong>Account Suspended: ${user.is_suspended}</strong><br>
          `;


          // Append the user details div to the user list div
          userListDiv.appendChild(userDetailsDiv);

          // 
          const userActionsDiv = document.createElement('div');
          userActionsDiv.classList.add('user-actions');
          
          // I need to check if the user is admin or ambassador
          // Then I will add the appropriate permissions to suspend users
          // Admins can suspend ambassadors and ambassadors can suspend users
          // Admins can suspend ambassadors and users
          const unsuspendButton = document.createElement('a');
          const suspendButton = document.createElement('a');
          if (data.user_type === 3){ // 3 === admin
            if (user.is_suspended) {
              // const unsuspendButton = document.createElement('a');
              unsuspendButton.textContent = 'Unsuspend'
              unsuspendButton.href = '/unsuspend_user/' + user.id + '/';
              unsuspendButton.classList.add('btn', 'btn-unsuspend');
              userActionsDiv.appendChild(unsuspendButton);
            }
            else{
              // const suspendButton = document.createElement('a');
              suspendButton.textContent = 'Suspend'
              suspendButton.href = '/suspend_user/' + user.id + '/';
              suspendButton.classList.add('btn', 'btn-suspend');
              userActionsDiv.appendChild(suspendButton);
            }
          }
          if (data.user_type === 2){ // 2 === ambassador
            if (user.user_type === 'normal user'){
              if (user.is_suspended) {
                // const unsuspendButton = document.createElement('a');
                unsuspendButton.href = '/unsuspend_user/' + user.id + '/';
                unsuspendButton.classList.add('btn btn-unsuspend');
                userActionsDiv.appendChild(unsuspendButton);
              }
              else{
                // const suspendButton = document.createElement('a');
                suspendButton.href = '/suspend_user/' + user.id + '/';
                suspendButton.classList.add('btn btn-suspend');
                userActionsDiv.appendChild(suspendButton);
              }
            }
            else {
              const notAllowd = document.createElement('span');
              notAllowd.classList.add('btn btn-disabled');
              notAllowd.textContent = 'Not Allowed';
              userActionsDiv.appendChild(notAllowd);
            }
          }

          // Append the user actions div to the user list div
          userListDiv.appendChild(userActionsDiv);


          usersList.appendChild(userListDiv);
        });

        // Update the current page number
        currentPage = data.page;
        totalPages = data.num_pages;
        updatePaginationControls(data.page, data.num_pages);

      })
    .catch(error => console.error("Error fetching users", error));
  }

  // Update pagination button states and display text
  function updatePaginationControls(page, numPages) {
    const currentPageSpan = document.getElementById("current-page");
    currentPageSpan.innerText = `Page ${page} of ${numPages}`;
    document.getElementById("first-page").disabled = (page === 1);
    document.getElementById("prev-page").disabled = (page === 1);
    document.getElementById("next-page").disabled = (page === numPages);
    document.getElementById("last-page").disabled = (page === numPages);
  }

  // Event listeners for pagination buttons
  document.getElementById("first-page").addEventListener("click", function() {
    if (currentPage > 1) {
      fetchPage(1);
    }
  });

  document.getElementById("prev-page").addEventListener("click", function() {
    if (currentPage > 1) {
      fetchPage(currentPage - 1);
    }
  });

  document.getElementById("next-page").addEventListener("click", function() {
    if (currentPage < totalPages) {
      fetchPage(currentPage + 1);
    }
  });

  // Search functionality: Listen for inputs event the search field
  let debounceTimeout;
  document.getElementById("search-input").addEventListener("input", function(e) {
    clearTimeout(debounceTimeout);

    // Update the global searchQuery variable with the current input value
    searchQuery = this.value;

    // Debounce the search input to avoid making too many requests
    debounceTimeout = setTimeout(() => {
      // Fetch the first page of results for the new search query
      fetchPage(1);
    }, 500);

    fetchPage(1);
});


});






// Helper function to get CSRF token from cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
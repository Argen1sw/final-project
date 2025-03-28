// Wait for the entire DOM to be fully loaded before running the script
document.addEventListener("DOMContentLoaded", function() {

  let currentPage = parseInt(document.querySelector('#current-page').innerText.match(/\d+/)[0]);
  let totalPages = parseInt(document.getElementById('current-page').getAttribute('data-total-pages'));

  let searchQuery = "";

  // Function to fetch a page of users from the server and optional search term
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
        // Create the user item container
        const userItem = document.createElement('div');
        userItem.classList.add(
          "p-4",
          "bg-gray-700",
          "rounded",
          "flex",
          "flex-col",
          "md:flex-row",
          "justify-between",
          "items-start",
          "md:items-center"
        );
  
        // Create the user details div
        const userDetailsDiv = document.createElement('div');
        userDetailsDiv.classList.add("mb-2", "md:mb-0");
        userDetailsDiv.innerHTML = `
          <p class="text-gray-100"><strong>Username:</strong> ${user.username}</p>
          <p class="text-gray-100"><strong>Email:</strong> ${user.email}</p>
          <p class="text-gray-100"><strong>Date Joined:</strong> ${user.date_joined}</p>
          <p class="text-gray-100"><strong>User Type:</strong> ${user.user_type_display || user.user_type}</p>
          <p class="text-gray-100"><strong>Bio:</strong> ${user.bio || "No bio"}</p>
          <p class="text-gray-100"><strong>Alerts Created:</strong> ${user.alerts_created}</p>
          <p class="text-gray-100"><strong>Alerts Verified:</strong> ${user.alerts_verified}</p>
          <p class="text-gray-100"><strong>Email Verified:</strong> ${user.is_verified ? "Yes" : "No"}</p>
          <p class="text-gray-100"><strong>Account Suspended:</strong> ${user.is_suspended ? "Yes" : "No"}</p>
        `;
        userItem.appendChild(userDetailsDiv);
  
        // Create the user actions div
        const userActionsDiv = document.createElement('div');
        userActionsDiv.classList.add("flex", "space-x-2");
  
        // Check permissions based on the logged-in user type (data.user_type)
        if (data.user_type === 3) { // 3 === admin
          if (user.is_suspended) {
            const unsuspendLink = document.createElement('a');
            unsuspendLink.href = '/suspend_unsuspend_user/' + user.id + '/';
            unsuspendLink.textContent = 'Unsuspend';
            unsuspendLink.classList.add("px-4", "py-2", "bg-indigo-600", "text-white", "rounded", "hover:bg-indigo-700", "focus:outline-none");
            userActionsDiv.appendChild(unsuspendLink);
          } else {
            const suspendLink = document.createElement('a');
            suspendLink.href = '/suspend_unsuspend_user/' + user.id + '/';
            suspendLink.textContent = 'Suspend';
            suspendLink.classList.add("px-4", "py-2", "bg-indigo-600", "text-white", "rounded", "hover:bg-indigo-700", "focus:outline-none");
            userActionsDiv.appendChild(suspendLink);
          }
        } else if (data.user_type === 2) { // 2 === ambassador
          if (user.user_type === 1) { // 1 === normal user
            if (user.is_suspended) {
              const unsuspendLink = document.createElement('a');
              unsuspendLink.href = '/suspend_unsuspend_user/' + user.id + '/';
              unsuspendLink.textContent = 'Unsuspend';
              unsuspendLink.classList.add("px-4", "py-2", "bg-indigo-600", "text-white", "rounded", "hover:bg-indigo-700", "focus:outline-none");
              userActionsDiv.appendChild(unsuspendLink);
            } else {
              const suspendLink = document.createElement('a');
              suspendLink.href = '/suspend_unsuspend_user/' + user.id + '/';
              suspendLink.textContent = 'Suspend';
              suspendLink.classList.add("px-4", "py-2", "bg-indigo-600", "text-white", "rounded", "hover:bg-indigo-700", "focus:outline-none");
              userActionsDiv.appendChild(suspendLink);
            }
          } else {
            const notAllowedSpan = document.createElement('span');
            notAllowedSpan.textContent = 'Not Allowed';
            notAllowedSpan.classList.add("px-4", "py-2", "bg-gray-600", "text-white", "rounded");
            userActionsDiv.appendChild(notAllowedSpan);
          }
        }
  
        // Append the actions div to the user item container
        userItem.appendChild(userActionsDiv);
  
        // Append the user item to the users list container
        usersList.appendChild(userItem);
      });
  
      // Update the current page number and total pages, then update pagination controls accordingly.
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

  document.getElementById("last-page").addEventListener("click", function() {
    if (currentPage < totalPages) {
      fetchPage(totalPages);
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
  
  // Initialize button states on page load
  updatePaginationControls(currentPage, totalPages);


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




// -------------------------------------------------------------------------
// Could be use in the future to toggle suspend users without a page refresh
// aka AJAX request fully dynamic
// -------------------------------------------------------------------------

// document.querySelectorAll('.btn-toggle-suspend').forEach(function(button) {
  //   button.addEventListener('click', function() {
  //     let userId = button.getAttribute('data-user-id');
  //     let url = `/toggle_suspend_user/${userId}/`; 
      
  //     // Make the AJAX request to the server
  //     fetch(url, {
  //       method: 'POST',
  //       headers: {
  //       'X-CSRFToken': getCookie('csrftoken'),
  //       'Accept': 'application/json',
  //       'Content-Type': 'application/json'
  //       },
  //     })
  //     // Parse the JSON response
  //     .then(response => {
  //       if (!response.ok) {
  //         throw new Error('Network response was not ok');
  //       }
  //       return response.json();
  //     })
  //     // Handle the JSON data
  //     .then(data => {
  //       // Update the button text and suspended status display based on the new state
  //       if (data.is_suspended) {
  //         button.textContent = 'Unsuspend';
  //         document.querySelector(`#user-${userId} .suspended-status`).textContent = 'Yes';
  //       } else {
  //         button.textContent = 'Suspend';
  //         document.querySelector(`#user-${userId} .suspended-status`).textContent = 'No';
  //       }
  //       alert(data.message);
  //     })
  //     .catch(error => {
  //       console.error('Error:', error);
  //       alert('An error occurred while updating the user status.');
  //     });
  //   });
  // });
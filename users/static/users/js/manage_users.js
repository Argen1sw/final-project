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

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.btn-toggle-suspend').forEach(function(button) {
        button.addEventListener('click', function() {
            let userId = button.getAttribute('data-user-id');
            let url = `/toggle_suspend_user/${userId}/`;  // Make sure this matches your URL pattern
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update the button text and suspended status display based on the new state
                if (data.is_suspended) {
                    button.textContent = 'Unsuspend';
                    document.querySelector(`#user-${userId} .suspended-status`).textContent = 'Yes';
                } else {
                    button.textContent = 'Suspend';
                    document.querySelector(`#user-${userId} .suspended-status`).textContent = 'No';
                }
                // Optionally, display the returned message
                alert(data.message);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating the user status.');
            });
        });
    });
});
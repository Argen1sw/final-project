// Alerts.js

// ---------------------- Expand on this by adding my own icons -------------------------------------
// Define custom icons for different hazard types
const hazardIcons = {
  // Default icon (can use Leaflet's default)
  default: L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41]
  }),
  fire: L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41]
  }),
  flood: L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41]
  }),
  earthquake: L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41]
  }),
  // Add more hazard types as needed
};

// Initialize the map
var map = L.map("map").setView([51.505, -0.09], 6);

L.tileLayer(
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
  {}
).addTo(map);

// Alerts default radius of effect 
const DEFAULT_RADIUS = {
  earthquake: 50000,    // meters
  flood: 10000,
  tornado: 5000,
  fire: 5000,
  storm: 50000
};

let currentCircle = null; // Store reference to temporary circle

const markerLayer = L.layerGroup().addTo(map);
const circleLayer = L.layerGroup();


// Fetch and display all existing alerts in the map using the geojson endpoint
fetch("/geojson/")
  .then((response) => response.json())
  .then((data) => {
    
    const alertsList = document.getElementById("alertsList");

    data.features.forEach((feature) => {
      const coords = feature.geometry.coordinates;
      const {
        description,
        hazard_type,
        effect_radius,
        country,
        city,
        county,
        created_at,
        reported_by,
        source_url,
      } = feature.properties;

      // Format creation date
      const creationDate = new Date(created_at).toLocaleString();

      // Get appropriate icon based on hazard type
      const icon = hazardIcons[hazard_type?.toLowerCase()] || hazardIcons.default

      // Add marker layer to the map
      const marker = L.marker([coords[1], coords[0]], { icon }) // Leaflet expects [lat, lng]
      .bindPopup(`
        <b>${hazard_type})</b><br>
        ${description}<br>
        Reported by: ${reported_by || "Unknown"}<br>
        <a href="${source_url}" target="_blank">More Info</a>
      `);
      markerLayer.addLayer(marker);
      
      const circle = L.circle([coords[1], coords[0]], {
        radius: effect_radius,
        color: '#ff0000',
        fillColor: '#f03',
        fillOpacity: 0.2
      });
      circleLayer.addLayer(circle);
    });
    
    let overlayMaps = {
      "markers": markerLayer,
      "radius": circleLayer
    };
 
    L.control.layers(null, overlayMaps).addTo(map);

  })
.catch((error) => console.error("Error fetching alerts:", error));


// Show form on map click event listener
map.on("click", function (e) {

  // Remove previous temporary circle
  if (currentCircle) {
    map.removeLayer(currentCircle);
  }

  // Create new circle with default radius
  const hazardType = document.getElementById('hazardType').value;

  // add the circle to the map
  currentCircle = L.circle(e.latlng, {
    radius: DEFAULT_RADIUS[hazardType] || 10000,
    color: '#ff0000',
    fillColor: '#f03',
    fillOpacity: 0.2,
    interactive: false
  }).addTo(map);
  
  document.getElementById("alertLat").value = e.latlng.lat;
  document.getElementById("alertLng").value = e.latlng.lng;
  document.getElementById('effectRadius').value = currentCircle.getRadius();

  showForm();
});


// Add instantaneous radius editing functionality
document.getElementById('effectRadius').addEventListener('input', function(e) {
  if (!currentCircle) return;
  const newRadius = parseInt(e.target.value);
  currentCircle.setRadius(newRadius);
});

// Handle alert form submission
document.getElementById("alertForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const data = {
    description: document.getElementById("alertDescription").value,
    lat: document.getElementById("alertLat").value,
    lng: document.getElementById("alertLng").value,
    effect_radius: currentCircle.getRadius(),
    hazard_type: document.getElementById("hazardType").value,
    source_url: document.getElementById("sourceUrl").value,
  };

  fetch("/create_alerts/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((err) => {
          throw new Error(JSON.stringify(err.errors));
        });
      }
      return response.json();
    })
    .then((alert) => {
  
      const icon = hazardIcons[alert.hazard_type?.toLowerCase()] || hazardIcons.default;

      // Add marker to the map
      const marker = L.marker(
        [alert.location.coordinates[1], alert.location.coordinates[0]], 
        { icon })
      .bindPopup(`
        <b>${alert.hazard_type})</b><br>
        ${alert.description}<br>
        Reported by: ${alert.reported_by || "Unknown"}<br>
        <a href="${alert.source_url || '#'}" target="_blank">More Info</a>
      `);
      
      markerLayer.addLayer(marker);

      // Add permanent circle
      const permanentCircle = L.circle(
        [alert.location.coordinates[1], alert.location.coordinates[0]], 
        {
          radius: alert.effect_radius,
          color: '#ff0000',
          fillColor: '#f03',
          fillOpacity: 0.2
        }
      ).bindPopup(`
        <b>${alert.hazard_type})</b><br>
        ${alert.description}<br>
        Reported by: ${alert.reported_by || "Unknown"}<br>
        <a href="${alert.source_url || '#'}" target="_blank">More Info</a>
      `);

      circleLayer.addLayer(permanentCircle);

      // Cleanup
      map.removeLayer(currentCircle);
      currentCircle = null;
      
      // Dynamically add the alert to the list
      const alertsList = document.getElementById("alertsList");
      const alertDiv = document.createElement("div");
      alertDiv.classList.add("alert-item");
      alertDiv.innerHTML = `
        <strong>${alert.hazard_type})</strong>
        <p>${alert.description}</p>
        <p>Location: Unknown</p>
        <p>Reported by: ${alert.reported_by || "Anonymous"}</p>
        <p><a href="${alert.source_url || '#'}" target="_blank">More Info</a></p>
        <p><em>Created on: ${new Date(alert.created_at).toLocaleString()}</em></p>
      `;
      alertsList.appendChild(alertDiv);

      hideForm();
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to submit the alert. Check console for details.");
    });
});


// ------------------ All this event listener could be in a separate JS file --------------
// Pagination and Search functionality for alerts list
document.addEventListener("DOMContentLoaded", function() {
  // Initialize currentPage and totalPages based on rendered data (DOMcontentLoaded)
  let currentPage = parseInt(document.querySelector('#current-page').innerText.match(/\d+/)[0]);
  let totalPages = parseInt(document.getElementById('current-page').getAttribute('data-total-pages'));

  // Global variable to hold the current search term
  let searchQuery = "";

  // Function to fetch alerts for a given page and optional search term
  function fetchPage(page) {

    // Build the URL including the search term if any
    let url = `/paginated_alerts/?page=${page}`;
    if (searchQuery) {
      url += `&q=${encodeURIComponent(searchQuery)}`;
    }
    fetch(url)
      .then(response => response.json())
      .then(data => {
        const alertsList = document.getElementById("alertsList");
        alertsList.innerHTML = "";

        // Append new alerts received from the server / API
        data.alerts.forEach(alert => {
          const alertDiv = document.createElement("div");
          alertDiv.classList.add("alert-item");
          alertDiv.innerHTML = `
            <strong>${alert.hazard_type}</strong>
            <p>${alert.description}</p>
            <p>Location: ${alert.city || alert.county || alert.country || "Unknown"}</p>
            <p>Reported by: ${alert.reported_by || "Unknown"}</p>
            <p><a href="${alert.source_url}" target="_blank">More Info</a></p>
            <p><em>Created on: ${new Date(alert.created_at).toLocaleString()}</em></p>
          `;
          alertDiv.addEventListener("click", function() {
            // Retrieve the latitude and longitude from the data attributes
            const lng = parseFloat(alert.location.coordinates[0]);
            const lat = parseFloat(alert.location.coordinates[1]);

            // Center the Leaflet map at the alert's location
            if (typeof map !== 'undefined') {
              map.setView([lat, lng], 13);
            }

            // Scroll the map element into view smoothly
            const mapElement = document.getElementById('map');
            if (mapElement) {
              mapElement.scrollIntoView({ behavior: 'smooth' });
            }
          });

          alertsList.appendChild(alertDiv);
        });

        // Update current page and pagination display
        currentPage = data.page;
        totalPages = data.num_pages;
        updatePaginationControls(data.page, data.num_pages);
      })
    .catch(error => console.error("Error fetching alerts:", error));

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


// Add a click event listener to each alert item to center the map at the alert's location
document.addEventListener("DOMContentLoaded", function() {
  // Select all alert items
  const alertElements = document.querySelectorAll('.alert-item');

  // Loop through each element and attach a click event listener
  alertElements.forEach(el => {
    el.addEventListener("click", function(e) {
      // Retrieve the latitude and longitude from the data attributes
      const lat = parseFloat(el.getAttribute('data-lat'));
      const lng = parseFloat(el.getAttribute('data-lng'));

      // Center the Leaflet map at the alert's location
      if (typeof map !== 'undefined') {
        map.setView([lat, lng], 13);
      }

      // Scroll the map element into view smoothly
      const mapElement = document.getElementById('map');
      if (mapElement) {
        mapElement.scrollIntoView({ behavior: 'smooth' });
      }

    });
  });
});


// Add hazard type change event listener
document.getElementById('hazardType').addEventListener('change', function(e) {
  if (!currentCircle) return;
  const newRadius = DEFAULT_RADIUS[e.target.value];
  currentCircle.setRadius(newRadius);
  document.getElementById('effectRadius').value = newRadius;
});


// Geolocate the user if possible, this will add a circle to the map in the user's location
// and display the alert form with the location pre-filled
document.addEventListener("DOMContentLoaded", function() {
  const locationBtn = document.getElementById("current-location-btn");

  locationBtn.addEventListener("click", function() {
    // Check if geolocation is supported by the browser
    if ("geolocation" in navigator) {
      // Optionally, display a loading indicator here

      navigator.geolocation.getCurrentPosition(
        function(position) {
          // On success, get the coordinates
          const latitude = position.coords.latitude;
          const longitude = position.coords.longitude;
          
          // Remove previous temporary circle
          if (currentCircle) {
            map.removeLayer(currentCircle);
          }

          // Create new circle with default radius
          const hazardType = document.getElementById('hazardType').value;

          // Update the hidden form fields so they can be submitted
          document.getElementById("alertLat").value = latitude;
          document.getElementById("alertLng").value = longitude;
          var latLng_ = L.latLng(latitude, longitude);
          
          // Center the Leaflet map at the user's location
          if (typeof map !== 'undefined') {
            map.setView([latitude, longitude], 13);

            // Add circle to map
            currentCircle = L.circle(latLng_, {
              radius: DEFAULT_RADIUS[hazardType] || 10000,
              color: '#ff0000',
              fillColor: '#f03',
              fillOpacity: 0.2,
              interactive: false
            }).addTo(map);
          }
          
          document.getElementById('effectRadius').value = currentCircle.getRadius();

          showForm();
        },
        function(error) {
          // Handle errors (e.g., user denied permission, timeout, etc.)
          console.error("Error retrieving location: ", error);
          alert("Unable to retrieve your location. Please try again.");
        }
      );
    } else {
      // Browser does not support geolocation
      alert("Geolocation is not supported by your browser.");
    }
  });
});


// Show form helper function
function showForm() {
  document.getElementById("alert-form").style.display = "block";
  document.getElementById("effectRadius").value = 
    DEFAULT_RADIUS[document.getElementById('hazardType').value];
}

// Hide form helper function
function hideForm() {

  // Remove previous temporary circle
  if (currentCircle) {
    map.removeLayer(currentCircle);
  }
  document.getElementById("alert-form").style.display = "none";

}

// Function to get the CSRF token from cookies
function getCSRFToken() {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith("csrftoken=")) {
        cookieValue = cookie.substring("csrftoken=".length);
        break;
      }
    }
  }
  return cookieValue;
}

// helper function that change the class name of the layer elements
function toggleActiveButton (activeId) {
  document.querySelectorAll('.layer-controls button').forEach(btn =>{
    btn.classList.toggle('active', btn.id === activeId);
  });
}

// Draggable feature from Jquery for the alert creation form
$(function() {
  // Make the alert form draggable.
  $( "#alert-form" ).draggable({
    // Optional: prevent dragging when interacting with form elements
    cancel: "textarea, input, button, select, option"
  });
});
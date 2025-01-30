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
var map = L.map("map").setView([51.505, -0.09], 13);
L.tileLayer(
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
  {}
).addTo(map);

// Fetch and display all existing alerts using the geojson endpoint
fetch("/geojson/")
  .then((response) => response.json())
  .then((data) => {
    const alertsList = document.getElementById("alertsList");
    data.features.forEach((feature) => {
      const coords = feature.geometry.coordinates;
      const {
        description,
        hazard_type,
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

      // Add marker to the map
      L.marker([coords[1], coords[0]], { icon }) // Leaflet expects [lat, lng]
        .addTo(map).
        bindPopup(`
          <b>${hazard_type})</b><br>
          ${description}<br>
          Reported by: ${reported_by || "Unknown"}<br>
          <a href="${source_url}" target="_blank">More Info</a>
        `);

      // Add alert to the list dynamically
      const alertDiv = document.createElement("div");
      alertDiv.classList.add("alert-item");
      alertDiv.innerHTML = `
        <strong>${hazard_type})</strong>
        <p>${description}</p>
        <p>Location: ${city || county || country || "Unknown"}</p>
        <p>Reported by: ${reported_by || "Unknown"}</p>
        <p>
          <a href="${source_url}" target="_blank">More Info</a>
        </p>
        <p><em>Created on: ${creationDate}</em></p>
      `;
      alertsList.appendChild(alertDiv);
    });
  })
  .catch((error) => console.error("Error fetching alerts:", error));

// Show form on map click event listener
map.on("click", function (e) {
  document.getElementById("alertLat").value = e.latlng.lat;
  document.getElementById("alertLng").value = e.latlng.lng;
  showForm();
});

// Show form helper function
function showForm() {
  document.getElementById("alert-form").style.display = "block";
}

// Hide form helper function
function hideForm() {
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

// Handle alert form submission
document.getElementById("alertForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const data = {
    description: document.getElementById("alertDescription").value,
    lat: document.getElementById("alertLat").value,
    lng: document.getElementById("alertLng").value,
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
      L.marker([
        alert.location.coordinates[1],
        alert.location.coordinates[0],
      ], { icon })
        .addTo(map)
        .bindPopup(`
          <b>${alert.hazard_type})</b><br>
          ${alert.description}<br>
          Reported by: ${alert.reported_by || "Unknown"}<br>
          <a href="${alert.source_url || '#'}" target="_blank">More Info</a>
        `);

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
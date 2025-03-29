// imports:
// import { fetchAlerts } from "./map_util.js";

// Define custom icons for different hazard types
const hazardIcons = {
  // Default icon (can use Leaflet's default)
  default: L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  }),
  fire: L.icon({
    iconUrl: ICONS.fire_icon,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  }),
  flood: L.icon({
    iconUrl: ICONS.flood_icon,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  }),
  earthquake: L.icon({
    iconUrl: ICONS.earthquake_icon,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  }),
  tornado: L.icon({
    iconUrl: ICONS.tornado_icon,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
  }),
};


// // Initialize the map
var map = L.map("map").setView([51.505, -0.09], 6);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  maxZoom: 19
}).addTo(map);


// layer group for markers types of alerts -- Adjust this whenever a new hazard type is added
// create an dict of layer groups for each hazard type
layerGroups = {
  earthquake: L.layerGroup().addTo(map),
  flood: L.layerGroup().addTo(map),
  tornado: L.layerGroup().addTo(map),
  fire: L.layerGroup().addTo(map)
  // default: L.layerGroup().addTo(map)
};

const circleLayer = L.layerGroup();


fetch("/geojson/")
  .then(response => response.json())
  .then(data => {

    // Loop through each feature in the GeoJSON data
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
        <b>${hazard_type}</b><br>
        ${description}<br>
        Reported by: ${reported_by || "Unknown"}<br>
        <a href="/alert/${feature.id}" target="_blank">More Details</a>
      `);
      
      // Add the marker to the appropriate layer group
      for (let key in layerGroups) {
        if (layerGroups.hasOwnProperty(key)) {
          const layerGroup = layerGroups[key];
          if (key === hazard_type) {
            layerGroup.addLayer(marker);
          }
        }
      }
      
      // Add the marker to the map
      const circle = L.circle([coords[1], coords[0]], {
        radius: effect_radius,
        color: '#ff0000',
        fillColor: '#f03',
        fillOpacity: 0.2
      });
      circleLayer.addLayer(circle);

      // Combine the marker and circle into a feature group
      const alertGroup = L.featureGroup([marker, circle]);

      if (layerGroups[hazard_type]) {
        layerGroups[hazard_type].addLayer(alertGroup);
      } else {
        console.warn(`No layer group for hazard type: ${hazard_type}`);
      }
    });
    
    // Create an object to hold the layer groups for the control
    let overlayMaps = {}

    // Add the layer groups to the map
    for (let key in layerGroups) {
      if (layerGroups.hasOwnProperty(key)) {
        const layerGroup = layerGroups[key];
        overlayMaps[key] = layerGroup;
      }
    }

    overlayMaps["Show Radius"] = circleLayer;
 
    L.control.layers(null, overlayMaps).addTo(map);
  })
.catch(error => console.error("Error loading alerts:", error));


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

        data.alerts.forEach(alert => {
          // Create the <details> container and add Tailwind classes
          const details = document.createElement("details");
          details.classList.add("alert-item", "border", "border-gray-700", "rounded-lg");
          details.setAttribute("data-lat", alert.location.coordinates[1]);
          details.setAttribute("data-lng", alert.location.coordinates[0]);
        
          // Create the <summary> element with Tailwind classes
          const summary = document.createElement("summary");
          summary.classList.add("p-2", "cursor-pointer", "bg-gray-800", "hover:bg-gray-700", "flex", "justify-between", "items-center", "text-gray-100");
          summary.innerHTML = `
            <span class="font-bold">${alert.hazard_type}</span>
            <span class="text-sm text-gray-300">
              Location: ${alert.city || alert.county || alert.country || "Unknown"}
            </span>
          `;
        
          // Create the content div that holds the alert details
          const contentDiv = document.createElement("div");
          contentDiv.classList.add("p-2", "bg-gray-800");
          contentDiv.innerHTML = `
            <p class="text-gray-300">${alert.description}</p>
            <p class="mt-1 text-gray-400">Reported by: ${alert.reported_by || "Unknown"}</p>
            <p class="mt-1">${formatHazardDetails(alert.hazard_details)}</p>
            <p class="mt-1">
              <a href="/alert/${alert.id}" target="_blank" class="text-indigo-400 hover:underline">
                More Details
              </a>
            </p>
            <p class="mt-1 text-xs text-gray-400">
              <em>Created on: ${new Date(alert.created_at).toLocaleString()}</em>
            </p>
            <button class="show-map-btn mt-2 px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700 focus:outline-none"
              data-lat="${alert.location.coordinates[1]}"
              data-lng="${alert.location.coordinates[0]}">
              Show in Map
            </button>
          `;
        
          // Append the summary and content to the details element
          details.appendChild(summary);
          details.appendChild(contentDiv);
        
          // Attach event listener only to the "Show in Map" button
          const mapButton = contentDiv.querySelector(".show-map-btn");
          mapButton.addEventListener("click", function(event) {
            // Prevent the event from bubbling up to the details element if needed
            event.stopPropagation();
            const lat = parseFloat(alert.location.coordinates[1]);
            const lng = parseFloat(alert.location.coordinates[0]);
            if (typeof map !== 'undefined') {
              map.setView([lat, lng], 13);
            }
            const mapElement = document.getElementById('map');
            if (mapElement) {
              mapElement.scrollIntoView({ behavior: 'smooth' });
            }
          });
        
          // Append the details element to the alerts list container
          alertsList.appendChild(details);
        });

        // Update current page and pagination display
        currentPage = data.page;
        totalPages = data.num_pages;
        updatePaginationControls(data.page, data.num_pages);
      })
    .catch(error => console.error("Error fetching alerts:", error));

  }

  // Format hazard details for display
  function formatHazardDetails(details) {
    if (!details) return "No hazard details available.";
    let detailsArray = [];
    for (const key in details) {
      if (details.hasOwnProperty(key)) {
        if(key === "id") continue;
        // Replace underscores with spaces and capitalize each word
        let formattedKey = key.replace(/_/g, ' ')
                              .split(' ')
                              .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                              .join(' ');
        let value = details[key] === null ? "Not Provided" : details[key];
        detailsArray.push(`${formattedKey}: ${value}`);
      }
    }
    return detailsArray.join('<br>');
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
  const alertElements = document.querySelectorAll('.show-map-btn');

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


// Format hazard details for display
function formatHazardDetails(details) {
  if (!details) return "No hazard details available.";
  let detailsArray = [];
  for (const key in details) {
    if (details.hasOwnProperty(key)) {
      if(key === "id") continue;
      // Replace underscores with spaces and capitalize each word
      let formattedKey = key.replace(/_/g, ' ')
                            .split(' ')
                            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                            .join(' ');
      let value = details[key] === null ? "Not Provided" : details[key];
      detailsArray.push(`${formattedKey}: ${value}`);
    }
  }
  return detailsArray.join('<br>');
}

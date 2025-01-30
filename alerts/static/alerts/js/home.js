// home.js

// Initialize the map
var map = L.map("map").setView([20, 0], 2); 
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "Map data &copy; <a href='https://openstreetmap.org'>OpenStreetMap</a> contributors",
}).addTo(map);

fetch("/geojson/")
.then(response => response.json())
.then(data => {
  data.features.forEach(feature => {
    const coords = feature.geometry.coordinates; // [lng, lat]
    const { title, description, hazard_type } = feature.properties;
    
    
    L.marker([coords[1], coords[0]])
    .addTo(map)
    .bindPopup(`
      <b>${title || "No Title"}</b><br>
      ${description || ""}<br>
      <i>${hazard_type || "Unknown Hazard"}</i>
      `);
    });
  })
.catch(error => console.error("Error loading alerts:", error));
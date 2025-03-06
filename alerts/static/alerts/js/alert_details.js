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
    })
};

const lat = parseFloat(data_Lat);
const lng = parseFloat(data_Lng);

// Initialize the map
var map = L.map("map").setView([data_Lat, data_Lng], 10);

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {}
).addTo(map);

// Get appropriate icon based on hazard type
const icon = hazardIcons[hazard_type?.toLowerCase()] || hazardIcons.default

const marker = L.marker([lat, lng], { icon })

L.layerGroup([marker]).addTo(map); 

const circle = L.circle([lat, lng], {
    radius: effect_radius,
    color: '#ff0000',
    fillColor: '#f03',
    fillOpacity: 0.2
}).addTo(map);

// Function to show the Edit Alert form
function showEditForm(){
    document.getElementById("edit-form").style.display = "block";
}
  
// Function to hide the Edit Alert form
function hideEditForm(){
document.getElementById("edit-form").style.display = "none";
}
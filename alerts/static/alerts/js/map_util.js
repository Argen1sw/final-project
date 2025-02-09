// Fetch and display all existing alerts in the map using the geojson endpoint
export function fetchAlerts(map, layerGroups, circleLayer, hazardIcons) {
    fetch("/geojson/")
    .then((response) => response.json())
    .then((data) => {
        
        // const alertsList = document.getElementById("alertsList");

        // Loop through each alert and add a marker to the map
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
    .catch((error) => console.error("Error fetching alerts:", error));
}
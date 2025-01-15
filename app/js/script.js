mapboxgl.accessToken = 'pk.eyJ1Ijoiam9hby1tZ2YiLCJhIjoiY2xmaG4zemY1MDY3ZDN1c3llaTBsaXlveCJ9.xI_gQ3o6Ddlz5BeQ0ggz4Q';

var defaultPosition = [-9.138715,38.736782];
var currentPosition = null;
var destinationSlot = null;
var destTime = null;
var destDistance = null;
var slots;
  

// Add map
var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/streets-v9',
    center: defaultPosition, // initial position
    zoom: 13, // initial zoom
    minZoom: 1
});

// Add geocoder
var geocoder = new MapboxGeocoder({
    accessToken: mapboxgl.accessToken,
    mapboxgl: mapboxgl
    });
map.addControl(geocoder);

// Geocoder actions
geocoder.on('result', function(e) { nearestSlot(e.result.center); });
geocoder.on('clear', removeRoute);
    

// Add geolocate control
var geolocate = new mapboxgl.GeolocateControl({
    positionOptions: {
        enableHighAccuracy: true
    },
    trackUserLocation: true,
    showUserHeading: true
    })
map.addControl(geolocate);


// Update current position
geolocate.on('geolocate', function(e) {
    var lon = e.coords.longitude;
    var lat = e.coords.latitude
    currentPosition = [lon, lat];

    // Update route to destination, if it exists
    updateRoute();
});

// Load map on initial user position
map.on('load', function() {
	geolocate.trigger();
    updateSlots();
    setInterval(updateSlots, 15000); // Update slots every 15s
});


// Load parking slots on the map
function updateSlots () {
    // Get slots
    fetch('http://127.0.0.1:5000/slots')
        .then(function(data) {
            return data.json()
        }).then(function(data) {            
            slots = data;
            updateMarkers();
        }) 
}


function updateMarkers () {
    // Remove current slots
    const elements = document.getElementsByClassName('slot-marker');
    while(elements.length > 0){
        elements[0].parentNode.removeChild(elements[0]);
    }

    // add markers to map
    for (const slot of slots) {
        const markerEl = document.createElement('div');
        markerEl.id = 'slot-' + slot.slot_id;

        const infoEl = document.createElement('div');
        const button = document.createElement('div');
        var innerHtmlContent = 'Parking slot #' + slot.slot_id + '<br>';

        // Current destination
        if (destinationSlot != null && slot.slot_id == destinationSlot.slot_id) {
            markerEl.className = 'slot-marker slot-selected';
            innerHtmlContent += 'Selected' + '<br>' + destDistance + ' km | ' + destTime + ' min';

            button.innerHTML = `<button>Cancel</button>`;
            button.addEventListener('click', (e) => {
                removeRoute();
                popup.remove();
            });
    
        } else {
            let state;
            if (slot.slot_state == "reserved") {
                state = "occupied";
            } else {
                state = slot.slot_state;
            }
            markerEl.className = 'slot-marker slot-' + state;
            innerHtmlContent += state;

            if (slot.slot_state == "free") {
                button.innerHTML = `<button>Go</button>`;
                button.addEventListener('click', (e) => {
                    selectDest(slot);
                    popup.remove();
                });
            } else {
                button.innerHTML = `<button>Find nearest free slot</button>`;
                button.addEventListener('click', (e) => {
                    nearestSlot([slot.slot_longitude, slot.slot_latitude]);
                    popup.remove();
                });
            }
        }

        infoEl.innerHTML = innerHtmlContent;
        infoEl.appendChild(button);

        // Add popup
        const popup = new mapboxgl.Popup({
            offset: 25,
            anchor: 'top',
            closeButton: false
        }).setDOMContent(infoEl);

        new mapboxgl.Marker(markerEl).setLngLat([slot.slot_longitude, slot.slot_latitude]).setPopup(popup).addTo(map);

        // On click
        markerEl.addEventListener('click', () => {
            onSlotClick(slot);
        })
    }   

}

function onSlotClick (slot) {
    updateSlots (); // Update slots
    map.flyTo({
        center: [slot.slot_longitude, slot.slot_latitude],
        zoom: 19
    });
}


// Distance between 2 points
function distance ([from_lon, from_lat], [to_lon, to_lat]) {
    return Math.sqrt((from_lon - to_lon)**2 + (from_lat - to_lat)**2);
}


// Show nearest available slot
function nearestSlot(coords) {
    updateSlots ();

    let closest = null;
    let min_dist = Infinity;

    for (const slot of slots) {
        let slot_coords = [slot.slot_longitude, slot.slot_latitude];
        if (slot.slot_state == "free" && distance(coords, slot_coords) < min_dist) {
            closest = slot;
            min_dist = distance(coords, slot_coords);
        }
    }

    if (closest != null) {
        document.getElementById('slot-' + closest.slot_id).click();
        onSlotClick(closest);
    }
}


// select slot as destination and update route
function selectDest(slot) {
    removeRoute();
    destinationSlot = slot;  
    updateRoute();
    updateSlots();
}


// Update route from current position to destination
function updateRoute() {
    if (destinationSlot != null && currentPosition != null) {
        let coords = [destinationSlot.slot_longitude, destinationSlot.slot_latitude];
        getRoute(coords);
    } else {
        removeRoute();
    }
}


// Directions request
function getRoute(dest) {
    var route = currentPosition + ';' + dest;
    var url = 'https://api.mapbox.com/directions/v5/mapbox/driving-traffic/' + route
        +'?geometries=geojson&steps=true&access_token=' + mapboxgl.accessToken;
    var req = new XMLHttpRequest();
    req.responseType = 'json';
    req.open('GET', url, true);
    req.onload  = function() {
        var jsonResponse = req.response;
        var distance = jsonResponse.routes[0].distance*0.001;
        var time = jsonResponse.routes[0].duration/60;
        var coords = jsonResponse.routes[0].geometry;

        // If slot is more than 30 min away, don't reserve it
        if (time > 30) {
            destinationSlot = null;
            updateSlots();
            return;
        }

        destTime = time.toFixed(2);
        destDistance = distance.toFixed(2);

        // Reserve slot
        var formdata = new FormData();
        formdata.append("slot_id", destinationSlot.slot_id);
        formdata.append("state", "reserved");
        formdata.append("time", Math.ceil(time));

        var requestOptions = {
        method: 'POST',
        body: formdata,
        redirect: 'follow'
        };

        fetch("http://127.0.0.1:5000/slots", requestOptions)
        .then(response => response.text())
        .then(() => {
            updateSlots();
        })
        .catch(error => console.log('error', error));
        

        // add the route to the map
        addRoute(coords);
    };
    req.send();
}


// adds the route as a layer on the map
function addRoute (coords) {
    // check if the route is already loaded
    if (map.getSource('route')) {
        map.removeLayer('route');
        map.removeSource('route')
    } else{
        map.addLayer({
            "id": "route",
            "type": "line",
            "source": {
                "type": "geojson",
                "data": {
                    "type": "Feature",
                    "properties": {},
                    "geometry": coords
                }
            },
            "layout": {
                "line-join": "round",
                "line-cap": "round"
            },
            "paint": {
                "line-color": "#1db7dd",
                "line-width": 8,
                "line-opacity": 0.8
            }
        });
    };
}

// remove the layer if it exists
function removeRoute () {
    if (destinationSlot != null) {

        // Free slot
        var formdata = new FormData();
        formdata.append("slot_id", destinationSlot.slot_id);
        formdata.append("state", "free");

        var requestOptions = {
        method: 'POST',
        body: formdata,
        redirect: 'follow'
        };

        fetch("http://127.0.0.1:5000/slots", requestOptions)
        .then(response => response.text())
        .then(() => {
            updateSlots();
        })
        .catch(error => console.log('error', error));
    }
    destinationSlot = null;

    // remove route from the map
    if (map.getSource('route')) {
        map.removeLayer('route');
        map.removeSource('route');
    } else  {
        return;
    }
}

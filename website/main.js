// import 'bootstrap';

import OLControlFullScreen from "ol/control/fullscreen";

const NSMap = require("./nsmap");
const NSStations = require("./map_stations");

const DATA_DIR = "./nsmaps-data/";

// http://stackoverflow.com/a/4234006
$.ajaxSetup({
    beforeSend: function(xhr) {
        if (xhr.overrideMimeType) {
            xhr.overrideMimeType("application/json");
        }
    }
});


const nsmap = NSMap.createNsmap(DATA_DIR);


$.getJSON(DATA_DIR + "stations.json", function(json) {
    nsmap.stations = json.stations;
    NSStations.addStationsLayer(json.stations, nsmap, nsmap.stationFeaturesSelectable);

    const stationNames = [];
    for (let i in nsmap.stations) {
        stationNames.push(json.stations[i].names.long);
        if (json.stations[i].names.long !== json.stations[i].names.short) {
            stationNames.push(json.stations[i].names.short);
        }
    }

    document.getElementById('view-deperature-station-button').onclick = nsmap.showAndPanToStation;

    // autocomplete via typeahead
    $('#the-basics .typeahead').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: 'station_names',
        source: substringMatcher(stationNames)
    });

    let initialStationId = url('?station');
    if (!initialStationId) {
        initialStationId = "UT";
    }
    nsmap.showStationContours(initialStationId);  // initial contours of Utrecht Centraal
    nsmap.moveToStation(initialStationId);
});


// Controls
// nsmap.addControl(new OLControlFullScreen());

// Tooltip
$('#info').hide();

const displayFeatureInfo = function(pixel) {
    const info = $('#info');
    info.css({
        left: (pixel[0] + 10) + 'px',
        top: (pixel[1] - 50) + 'px'
    });

    const feature = nsmap.forEachFeatureAtPixel(pixel, function(feature, layer) {
        return feature;
    });

    if (feature) {
        const tooltipText = feature.get('title');
        if (tooltipText !== '') {
            info.text(tooltipText);
            info.show();
        } else {
            info.hide();
        }
    } else {
        info.hide();
    }
};

nsmap.on('pointermove', function(evt) {
    if (evt.dragging) {
        $('#info').hide();
        return;
    }
    displayFeatureInfo(nsmap.getEventPixel(evt.originalEvent));
});


const substringMatcher = function(strs) {
    return function findMatches(q, cb) {
        let matches, substringRegex;

        // an array that will be populated with substring matches
        matches = [];

        // regex used to determine if a string contains the substring `q`
        const substrRegex = new RegExp(q, 'i');

        // iterate through the pool of strings and for any string that
        // contains the substring `q`, add it to the `matches` array
        $.each(strs, function(i, str) {
            if (substrRegex.test(str)) {
                matches.push(str);
            }
        });

        cb(matches);
    };
};


$("#clear-station-input-button").click(function(){
    $("#departure-station-input").val('');
});


$('#departure-station-input').keypress(function(event){
    const keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode === '13'){
        nsmap.showAndPanToStation();
    }
});

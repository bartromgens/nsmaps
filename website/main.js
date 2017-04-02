
// http://stackoverflow.com/a/4234006
$.ajaxSetup({
    beforeSend: function(xhr){
        if (xhr.overrideMimeType)
        {
            xhr.overrideMimeType("application/json");
        }
    }
});

var dataDir = "./nsmaps-data/";

nsmap = createNsmap();

$.getJSON(dataDir + "stations.json", function(json) {
    nsmap.stations = json.stations;
    addStationsLayer(json.stations, nsmap, nsmap.stationFeaturesSelectable);

    var stationNames = [];
    for (var i in nsmap.stations)
    {
        stationNames.push(json.stations[i].names.long);
        if (json.stations[i].names.long != json.stations[i].names.short) {
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

    var initialStationId = url('?station');
    if (!initialStationId) {
        initialStationId = "UT";
    }
    nsmap.showStationContours(initialStationId);  // initial contours of Utrecht Centraal
    nsmap.moveToStation(initialStationId);
});


// Controls

StationNameLabel = function(opt_options) {
    var options = opt_options || {};

    var station_label = document.createElement('a');
    station_label.innerHTML = 'Click on a station';

    var element = document.createElement('div');
    element.className = 'station-name ol-control';
    element.appendChild(station_label);

    ol.control.Control.call(this, {
        element: element
    });

    this.setText = function (text) {
        station_label.innerHTML = text;
    };
};

ol.inherits(StationNameLabel, ol.control.Control);

nsmap.addControl(new StationNameLabel());
nsmap.addControl(new ol.control.FullScreen());


// Tooltip
$('#info').hide();

var displayFeatureInfo = function(pixel) {
    var info = $('#info');
    info.css({
        left: (pixel[0] + 10) + 'px',
        top: (pixel[1] - 50) + 'px'
    });

    var feature = nsmap.forEachFeatureAtPixel(pixel, function(feature, layer) {
        return feature;
    });

    if (feature) {
        var tooltipText = feature.get('title');
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


var substringMatcher = function(strs) {
    return function findMatches(q, cb) {
        var matches, substringRegex;

        // an array that will be populated with substring matches
        matches = [];

        // regex used to determine if a string contains the substring `q`
        substrRegex = new RegExp(q, 'i');

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
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13'){
        nsmap.showAndPanToStation();
    }
});

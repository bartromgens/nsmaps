
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

var typeScales = {
    'megastation': 9,
    'knooppuntIntercitystation': 7,
    'intercitystation': 6,
    'sneltreinstation': 5,
    'knooppuntSneltreinstation': 5,
    'knooppuntStoptreinstation': 4,
    'stoptreinstation': 4,
    'facultatiefStation': 4,
};

var nsmap = (function() {
    var map = new ol.Map({
        target: 'map',
        //    loadTilesWhileAnimating: true,
        //    loadTilesWhileInteracting: true,
    });

    var lon = '5.1';
    var lat = '142.0';
    var view = new ol.View( {center: ol.proj.fromLonLat([lon, lat]), zoom: 10, projection: 'EPSG:3857'} );
    map.setView(view);

    var osmSource = new ol.source.OSM("OpenCycleMap");
    osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png ");
    var osmLayer = new ol.layer.Tile({source: osmSource});
    map.addLayer(osmLayer);
    map.stationFeaturesSelectable = [];
    map.contourLayers = [];
    map.stations = [];

    map.moveToStation = function(stationId) {
        var station = maps.getStationById(stationId);
        if (!station) {
            console.log("ERROR: station not found, id:", stationId);
            return;
        }

        var pan = ol.animation.pan({
            duration: 300,
            source: /** @type {ol.Coordinate} */ (view.getCenter())
        });

        nsmap.beforeRender(pan);
        view.setCenter(ol.proj.fromLonLat([station.lon, station.lat]));
    };

    map.getStationById = function(stationId) {
        for (var i in nsmap.stations) {
            if (nsmap.stations[i].id == stationId) {
                return nsmap.stations[i];
            }
        }
        return null;
    };

    map.getStationByName = function(stationName) {
        for (var i in nsmap.stations) {
            if (nsmap.stations[i].names.long == stationName) {
                return nsmap.stations[i];
            }
            if (nsmap.stations[i].names.short == stationName) {
                return nsmap.stations[i];
            }
        }
        return null;
    };

    map.showAndPanToStation = function() {
        var statioName = document.getElementById('departure-station-input').value;
        var station = map.getStationByName(statioName);
        if (station) {
            map.showStationContours(station.id);
            map.moveToStation(station.id);
        } else {
            console.log("ERROR: station not found");
        }
    };

    map.showStationContours = function(stationId) {
        for (var i = 0; i < nsmap.contourLayers.length; ++i)
        {
            var removedLayer = nsmap.removeLayer(nsmap.contourLayers[i]);
        }
        nsmap.contourLayers.length = 0;
        station = maps.getStationById(stationId);
        document.getElementById('departure-station-input').value = station.names.long;
        var geojsonUrl = dataDir + "contours/" + stationId + '_minor.geojson';
        addContourLayer(geojsonUrl, nsmap, nsmap.contourLayers);
        updateColorBarLegend(stationId);
        this.selectStationFeature(stationId);
        //    current_station_control_label.setText(selected_station_name);
    };

    map.getStationStyle = function(feature, circleColor) {
        var strokeColor = 'black';
        if (feature.get('selectable'))
        {
            strokeColor = 'black';
            circleColor = '#2293ff';
        }

        var circleStyle = new ol.style.Circle(({
            fill: new ol.style.Fill({color: circleColor}),
            stroke: new ol.style.Stroke({
                color: strokeColor,
                width: 3,
            }),
            radius: typeScales[feature.get('type')]
        }));

        return new ol.style.Style({
            image: circleStyle,
        });
    };

    map.getSelectedStationStyle = function(feature) {
        var strokeColor = 'lightgreen';
        var circleColor = 'green';

        var circleStyle = new ol.style.Circle(({
            fill: new ol.style.Fill({color: circleColor}),
            stroke: new ol.style.Stroke({color: strokeColor, width: 3}),
            radius: typeScales[feature.get('type')] * 1.5
        }));

        return new ol.style.Style({
            image: circleStyle,
        });
    };

    map.selectStationFeature = function(stationId) {
        for (var i in map.stationFeaturesSelectable) {
            var feature = map.stationFeaturesSelectable[i];
            if (feature.get('id') == stationId)
            {
                feature.setStyle(map.getSelectedStationStyle(feature));
            }
            else {
                feature.setStyle(map.getStationStyle(feature));
            }
        }
    };

    return map;
})();


$.getJSON(dataDir + "stations.json", function(json) {
    nsmap.stations = json.stations;
    addStationsLayer(json.stations, nsmap, nsmap.stationsFeaturesSelectable);

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

    nsmap.showStationContours("UT");  // initial contours of Utrecht Centraal
});




var updateColorBarLegend = function(stationId) {
    var colorBarImage = document.getElementById('colorbar-legend');
    var imageUrl = dataDir + "contours/" + stationId + "_top_colorbar.png";
    colorBarImage.style.backgroundImage = "url(" + imageUrl + ")";
};


function componentToHex(comp) {
    var hex = comp.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}


function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}





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

var current_station_control_label = new StationNameLabel();
nsmap.addControl(current_station_control_label);
nsmap.addControl(new ol.control.FullScreen());


// Tooltip
var info = $('#info');
info.hide();

var displayFeatureInfo = function(pixel) {
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
        info.hide();
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

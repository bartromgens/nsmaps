
// http://stackoverflow.com/a/4234006
$.ajaxSetup({beforeSend: function(xhr){
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

var map = new ol.Map({
    target: 'map',
//    loadTilesWhileAnimating: true,
//    loadTilesWhileInteracting: true,
});

var view = new ol.View( {center: [0, 0], zoom: 10, projection: 'EPSG:3857'} );
map.setView(view);

var osmSource = new ol.source.OSM("OpenCycleMap");
osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png ");
var osmLayer = new ol.layer.Tile({source: osmSource});

map.addLayer(osmLayer);

var stationFeatures = [];
var contourLayers = [];

var stations = [];

var getStationByName = function(stationName) {
    for (var i in stations) {
        if (stations[i].names.long == stationName) {
            return stations[i];
        }
        if (stations[i].names.short == stationName) {
            return stations[i];
        }
    }
    return null;
};

var getStationById = function(stationId) {
    for (var i in stations) {
        if (stations[i].id == stationId) {
            return stations[i];
        }
    }
    return null;
};


var moveToStation = function(stationId) {
    var station = getStationById(stationId);
    if (!station) {
        console.log("ERROR: station not found, id:", stationId);
        return;
    }

    var pan = ol.animation.pan({
        duration: 300,
        source: /** @type {ol.Coordinate} */ (view.getCenter())
    });

    map.beforeRender(pan);
    view.setCenter(ol.proj.fromLonLat([station.lon, station.lat]));
};


var showAndPanToStation = function() {
    var statioName = document.getElementById('departure-station-input').value;
    var station = getStationByName(statioName);
    if (station) {
        showStationContours(station.id);
        moveToStation(station.id);
    } else {
        console.log("ERROR: station not found");
    }
};

$.getJSON(dataDir + "stations.json", function(json) {
    var lon = '5.1';
    var lat = '142.0';
    view.setCenter(ol.proj.fromLonLat([lon, lat]));

    stations = json.stations;
    createStationLayer(typeScales, json.stations);

    var stationNames = [];
    for (var i in stations)
    {
        stationNames.push(json.stations[i].names.long);
        if (json.stations[i].names.long != json.stations[i].names.short) {
            stationNames.push(json.stations[i].names.short);
        }
    }

    document.getElementById('view-deperature-station-button').onclick = showAndPanToStation;

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

    showStationContours("UT");  // initial contours of Utrecht Centraal
});


var showStationContours = function(stationId) {
    for (var i = 0; i < contourLayers.length; ++i)
    {
        var removedLayer = map.removeLayer(contourLayers[i]);
    }
    contourLayers.length = 0;
    station = getStationById(stationId);
    document.getElementById('departure-station-input').value = station.names.long;
    createContoursLayer(stationId);
    selectStationFeature(stationId);
//    current_station_control_label.setText(selected_station_name);
};

var stationFeaturesSelectable = [];

var selectStationFeature = function(stationId) {
    for (var i in stationFeaturesSelectable) {
        var feature = stationFeaturesSelectable[i];
        if (feature.get('id') == stationId)
        {
            feature.setStyle(getSelectedStationStyle(feature));
        }
        else {
            feature.setStyle(getStationStyle(feature));
        }
    }
};


var onSelectStationFeature = function(evt) {
    evt.deselected.forEach(function(feature){
        feature.setStyle(getStationStyle(feature));
    });

    if (!evt.selected[0])
    {
        return;
    }

    evt.selected.forEach(function(feature){
        feature.setStyle(getSelectedStationStyle(feature));
    });
    var stationId = evt.selected[0].get('id');
    showStationContours(stationId);
//        moveToStation(stationId);
};

function createStationLayer(typeScales, stations)
{
    var stationFeaturesUnselectable = [];

    for (var i in stations)
    {
        var station = stations[i];
        var lat = parseFloat(station.lat);
        lat = lat + 90.0;
        var lonLat = [station.lon, lat.toString()];
        station.selectable = station.travel_times_available;
        var stationFeature = createStationFeature(station, lonLat);
        stationFeatures.push(stationFeature);
        if (station.selectable)
        {
            stationFeaturesSelectable.push(stationFeature);
        }
        else
        {
            stationFeaturesUnselectable.push(stationFeature);
        }
    }

    for (var j in stationFeatures)
    {
        stationFeatures[j].setStyle(getStationStyle(stationFeatures[j], 'yellow'));
    }

    var stationSelectableSource = new ol.source.Vector({
        features: stationFeaturesSelectable
    });

    var stationUnselectableSource = new ol.source.Vector({
        features: stationFeaturesUnselectable
    });

    var stationsSelectableLayer = new ol.layer.Vector({
        source: stationSelectableSource
    });

    var stationsUnselectableLayer = new ol.layer.Vector({
        source: stationUnselectableSource
    });

    stationsSelectableLayer.setZIndex(99);
    stationsUnselectableLayer.setZIndex(10);

    map.addLayer(stationsSelectableLayer);
    map.addLayer(stationsUnselectableLayer);

    // Select features
    var select = new ol.interaction.Select({
        layers: [stationsSelectableLayer],
        condition: ol.events.condition.click
    });

    select.on('select', onSelectStationFeature);

    map.addInteraction(select);
}


var getSelectedStationStyle = function(feature) {
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


function getStationStyle(feature, circleColor) {
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

//    var textStyle = new ol.style.Text({
//        text: feature.get('text'),
//        scale: typeScales[feature.get('type')] * 2.0,
//        offsetY: 20,
//        fill: new ol.style.Fill({color: '#000'})
//    });

    return new ol.style.Style({
        image: circleStyle,
//        text: textStyle
    });
}


function createStationFeature(station, lonLat) {
    return new ol.Feature({
        geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
        title: station.names.long,
        id: station.id,
        type: station.type,
        text: station.names.short,
        selectable: station.selectable
    });
}


var lineStyleFunction = function(feature, resolution) {
    var lineWidth = feature.get('stroke-width')/2.0;// /200.0 * Math.pow(map.getView().getZoom(), 2.0);
    var lineStyle = new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: feature.get('stroke'),
            width: lineWidth,
//            lineDash: [20.0, 8.0], //or other combinations
        })
    });
    return lineStyle;
};

function createContoursLayer(stationId) {
    console.log('create contour layger for station.id', stationId);
    var tilespath = dataDir + "contours/" + stationId + '/tiles/{z}/{x}/{y}.geojson';
//    var extent = ol.extent.applyTransform([2.0, 49.5, 10.0, 54.5], ol.proj.getTransform("EPSG:4326", "EPSG:3857"));
//    console.log(extent);

    var contourLayer = new ol.layer.VectorTile({
        source: new ol.source.VectorTile({
            url: tilespath,
            format: new ol.format.GeoJSON(),
            projection: 'EPSG:3857',
            tileGrid: ol.tilegrid.createXYZ({
//                extent: extent,
                maxZoom: 11,
                minZoom: 1,
                tileSize: [256, 256]
            }),
        }),
        style: lineStyleFunction
    });

//    contourLayer.setZIndex(99);
    map.addLayer(contourLayer);
    contourLayers.push(contourLayer);

    // increase contour line width when zooming
    map.getView().on('change:resolution', function(evt) {
        contourLayer.setStyle(lineStyleFunction);
    });

    updateColorBarLegend(stationId);
}

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
map.addControl(current_station_control_label);
map.addControl(new ol.control.FullScreen());


// Tooltip
var info = $('#info');
info.hide();

var displayFeatureInfo = function(pixel) {
    info.css({
        left: (pixel[0] + 10) + 'px',
        top: (pixel[1] - 50) + 'px'
    });

    var feature = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
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

map.on('pointermove', function(evt) {
    if (evt.dragging) {
        info.hide();
        return;
    }
    displayFeatureInfo(map.getEventPixel(evt.originalEvent));
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
       showAndPanToStation();
    }
});

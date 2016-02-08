
// http://stackoverflow.com/a/4234006
$.ajaxSetup({beforeSend: function(xhr){
    if (xhr.overrideMimeType)
    {
      xhr.overrideMimeType("application/json");
    }
}
});


var typeScales = {
                  'megastation': 9,
                  'intercitystation': 7,
                  'knooppuntIntercitystation': 7,
                  'sneltreinstation': 5,
                  'knooppuntSneltreinstation': 5,
                  'knooppuntStoptreinstation': 4,
                  'stoptreinstation': 4,
                  'facultatiefStation': 4,
                  };

var map = new ol.Map({target: 'map'});
var view = new ol.View( {center: [0, 0], zoom: 10, projection: 'EPSG:3857'} );
map.setView(view);

var osmSource = new ol.source.OSM("OpenCycleMap");
osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png ");
var osmLayer = new ol.layer.Tile({source: osmSource});

map.addLayer(osmLayer);

var stationFeatures = [];
var contourLayers = []


$.getJSON("./data/stations.json", function(json) {
    var lon = '5.1';
    var lat = '142.0';
    view.setCenter(ol.proj.fromLonLat([lon, lat]));

    createStationLayer(typeScales, json.stations);

    addContours("UT");  // initial contours of Utrecht Centraal
});


function addContours(station_id)
{
    $.getJSON("./data/contours_" + station_id + ".json", function(json) {
        var contours = json.contours;
        createContoursLayer(contours, "Travel time");
    });
}


function createStationLayer(typeScales, stations)
{
    var stationFeaturesUnselectable = [];
    var stationFeaturesSelectable = [];
    
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
        stationFeatures[j].setStyle(getStationStyle(stationFeatures[j], 'black'));
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
    stationsUnselectableLayer.setZIndex(0);

    map.addLayer(stationsSelectableLayer);
    map.addLayer(stationsUnselectableLayer);
}


function getStationStyle(feature, circleColor) {
    //var iconStyle = new ol.style.Icon(({
    //    opacity: 0.75,
    //    scale: typeScales[feature.get('type')] / 1.5,
    //    src: 'http://www.ns.nl/static/generic/1.21.1/images/nslogo.svg'
    //}));

    var strokeColor = 'black';
    circleColor = 'yellow'
    if (feature.get('selectable'))
    {
        strokeColor = 'black';
        circleColor = '#2293ff'
    }

    var circleStyle = new ol.style.Circle(({
        fill: new ol.style.Fill({color: circleColor}),
        stroke: new ol.style.Stroke({color: strokeColor, width: 3}),
        radius: typeScales[feature.get('type')]
    }));

    var textStyle = new ol.style.Text({
        text: feature.get('text'),
        scale: typeScales[feature.get('type')] * 2.0,
        offsetY: 20,
        fill: new ol.style.Fill({color: '#000'})
    });

    return new ol.style.Style({
        image: circleStyle,
//        text: textStyle
    });
}


function createStationFeature(station, lonLat) {
    return new ol.Feature({
        geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
        name: station.names.long,
        id: station.id,
        type: station.type,
        text: station.names.short,
        selectable: station.selectable
    });
}


function createContoursLayer(contours, name) {
    console.log('create new contour layers');
    console.log(contours.length + ' contours');

    // each contour can have multiple (including zero) paths.
    for (var k = 0; k < contours.length; ++k)
    {
        var paths = contours[k].paths;
        for (var j = 0; j < paths.length; ++j)
        {
            var markers = [];
            for (var i = 0; i < paths[j].x.length; ++i)
            {
                var lonLat = [paths[j].x[i], paths[j].y[i]];
                markers.push(ol.proj.fromLonLat(lonLat));
            }

            var color = [paths[j].linecolor[0]*255, paths[j].linecolor[1]*255, paths[j].linecolor[2]*255, 0.8];
            var lineWidth = 3;
            if ((k+1) % 6 == 0)
            {
                lineWidth = 8;
            }

            var lineStyle = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: color,
                    width: lineWidth
                })
            });

            var layerLines = new ol.layer.Vector({
                source: new ol.source.Vector({
                    features: [new ol.Feature({
                        geometry: new ol.geom.LineString(markers, 'XY'),
                        name: paths[j].label
                    })]
                }),
                style: lineStyle
            });
            contourLayers.push(layerLines);
            map.addLayer(layerLines);
        }
    }
}


function componentToHex(comp) {
    var hex = comp.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}


function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

// Select features

var select = new ol.interaction.Select({
    condition: ol.events.condition.click
});

select.on('select', function(evt) {
    if (!evt.selected[0])
    {
        return;
    }
    for (var i = 0; i < contourLayers.length; ++i)
    {
        var removedLayer = map.removeLayer(contourLayers[i]);
    }
    contourLayers.length = 0;
    var station_id = evt.selected[0].get('id');
    var selected_station_name = evt.selected[0].get('name')
    current_station_control_label.setText("Loading...");
    addContours(station_id);
    current_station_control_label.setText(selected_station_name);
});

map.addInteraction(select);

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
  }

};
ol.inherits(StationNameLabel, ol.control.Control);

var current_station_control_label = new StationNameLabel()
map.addControl(current_station_control_label);
map.addControl(new ol.control.FullScreen());


// Tooltip

var info = $('#info');

var displayFeatureInfo = function(pixel) {
  info.css({
    left: (pixel[0] + 10) + 'px',
    top: (pixel[1] - 50) + 'px'
  });

  var feature = map.forEachFeatureAtPixel(pixel, function(feature, layer) {
    return feature;
  });

  if (feature) {
    info.text(feature.get('name'));
    info.show();
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
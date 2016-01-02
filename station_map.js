
// http://stackoverflow.com/a/4234006
$.ajaxSetup({beforeSend: function(xhr){
  if (xhr.overrideMimeType)
  {
    xhr.overrideMimeType("application/json");
  }
}
});


var typeScales = {'stoptreinstation': 0.5,
                  'megastation': 1.1,
                  'knooppuntIntercitystation': 0.9,
                  'sneltreinstation': 0.8,
                  'intercitystation': 0.9,
                  'knooppuntStoptreinstation': 0.6,
                  'facultatiefStation': 0.4,
                  'knooppuntSneltreinstation': 0.8
                  };

var map = new ol.Map({target: 'map'});
var view = new ol.View( {center: [0, 0], zoom: 10, projection: 'EPSG:3857'} );
map.setView(view);

var osmSource = new ol.source.OSM("OpenCycleMap");
osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png ");
var osmLayer = new ol.layer.Tile({source: osmSource});

map.addLayer(osmLayer);

var stationFeatures = [];


$.getJSON("./data/stations.json", function(json) {
    var lon = '5.1';
    var lat = '142.0';
    view.setCenter(ol.proj.fromLonLat([lon, lat]));

    createStationLayer(typeScales, json.stations);

    //addTravelTimeColoring();
    addContours();
});


function addTravelTimeColoring()
{
    $.getJSON("./data/traveltimes_from_utrecht.json", function(json) {
        var stations = json.stations;
        for (var i in stations)
        {
            var station = stations[i];
            for (var j in stationFeatures)
            {
                var feature = stationFeatures[j];
                if (station.name == feature.get('name'))
                {
                    var score = station.travel_time_min*4;
                    var red = 0;
                    var green = 255 - score;
                    var blue = 0;
                    if (score > 255)
                    {
                        green = 0;
                        red = score-255;
                    }
                    var color = jQuery.Color( red, green, blue );
                    feature.set('text', station.travel_time_planned);
                    feature.setStyle( getStationStyle(feature, color.toHexString()) );
                }
            }
        }
    });
}


function addContours()
{
    $.getJSON("./data/contours.json", function(json) {
        var contours = json.contours;
        //console.log(contours);
        createContoursLayer(contours, "Travel time");
    });
}


function createStationLayer(typeScales, stations)
{
    for (var i in stations)
    {
        var station = stations[i];
        var lat = parseFloat(station.lat);
        lat = lat + 90.0;
        var lonLat = [station.lon, lat.toString()];

        var stationFeature = createStationFeature(station, lonLat);
        stationFeatures.push(stationFeature);
    }

    for (var j in stationFeatures)
    {
        stationFeatures[j].setStyle(getStationStyle(stationFeatures[j], 'black'));
    }

    var vectorSource = new ol.source.Vector({
        features: stationFeatures
    });

    var vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });

    map.addLayer(vectorLayer);
}


function getStationStyle(feature, circleColor) {
    //var iconStyle = new ol.style.Icon(({
    //    opacity: 0.75,
    //    scale: typeScales[feature.get('type')] / 1.5,
    //    src: 'http://www.ns.nl/static/generic/1.21.1/images/nslogo.svg'
    //}));

    var circleStyle = new ol.style.Circle(({
        fill: new ol.style.Fill({color: circleColor}),
        radius: typeScales[feature.get('type')] * 10
    }));

    var textStyle = new ol.style.Text({
        text: feature.get('text'),
        scale: typeScales[feature.get('type')] * 2.0,
        offsetY: 20,
        fill: new ol.style.Fill({color: '#000'})
    });

    return new ol.style.Style({
        image: circleStyle,
        text: textStyle
    });
}


function createStationFeature(station, lonLat) {
    return new ol.Feature({
        geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
        name: station.names.long,
        type: station.type,
        text: station.names.short
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

            color = [paths[j].linecolor[0]*255, paths[j].linecolor[1]*255, paths[j].linecolor[2]*255, 0.8]

            var lineStyle = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: color,
                    width: 5
                })
            });

            var layerLines = new ol.layer.Vector({
                source: new ol.source.Vector({
                    features: [new ol.Feature({
                        geometry: new ol.geom.LineString(markers, 'XY'),
                        name: 'Line'
                    })]
                }),
                style: lineStyle
            });
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
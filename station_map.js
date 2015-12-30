
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
var view = new ol.View( {center: [0, 0], zoom: 12, projection: 'EPSG:3857'} );
map.setView(view);


$.getJSON("stations.json", function(json) {
    var lon = '5.1';
    var lat = '142.0';
    view.setCenter(ol.proj.fromLonLat([lon, lat]));

    createStationLayers(typeScales, json.stations);
});


var osmSource = new ol.source.OSM("OpenCycleMap");
osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png ");
var osmLayer = new ol.layer.Tile({source: osmSource});
map.addLayer(osmLayer);


function createStationLayers(typeScales, stations)
{
    var stationFeatures = [];

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
        stationFeatures[j].setStyle(getStationStyle(stationFeatures[j]));
    }

    var vectorSource = new ol.source.Vector({
        features: stationFeatures
    });

    var vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });

    map.addLayer(vectorLayer);
}


function getStationStyle(feature) {
    //var iconStyle = new ol.style.Icon(({
    //    opacity: 0.75,
    //    scale: typeScales[feature.get('type')] / 1.5,
    //    src: 'http://www.ns.nl/static/generic/1.21.1/images/nslogo.svg'
    //}));

    var circleStyle = new ol.style.Circle(({
        fill: new ol.style.Fill({color: 'black'}),
        radius: typeScales[feature.get('type')] * 5
    }));

    var textStyle = new ol.style.Text({
        text: feature.get('text'),
        scale: typeScales[feature.get('type')] * 1.0,
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

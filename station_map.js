
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
                  'knooppuntSneltreinstation': 0.8,
                  };

var map = new ol.Map({target: 'map'});
var view = new ol.View( {center: [0, 0], zoom: 12, projection: 'EPSG:3857'} );
map.setView(view);


$.getJSON("stations.json", function(json) {
    var lon = '5.1';
    var lat = '142.0';
    view.setCenter(ol.proj.fromLonLat([lon, lat]))

    createStationLayers(typeScales, json.stations);
});


var osmSource = new ol.source.OSM("OpenCycleMap - Grayscale");
var osmLayer = new ol.layer.Tile({source: osmSource});
map.addLayer(osmLayer);


function createStationLayers(typeScales, stations)
{
    var stationFeaturesMap = {};
    var stationTitleFeaturesMap = {};
    for (type in typeScales)
    {
        stationFeaturesMap[type] = [];
        stationTitleFeaturesMap[type] = []
    }

    for (index in stations)
    {
        var station = stations[index];
        var lat = parseFloat(station.lat);
        lat = lat + 90.0;
        var lonLat = [station.lon, lat.toString()];

        var iconFeature = createStationFeature(station, lonLat);
        stationFeaturesMap[station.type].push(iconFeature);
    }

    for (type in stationFeaturesMap)
    {
        features = stationFeaturesMap[type];

        for (index in features)
        {
            features[index].setStyle(getStationStyle(features[index]))
        }

        var vectorSource = new ol.source.Vector({
            features: features,
        });

        var vectorLayer = new ol.layer.Vector({
            source: vectorSource,
        });

        map.addLayer(vectorLayer);
    }
}


function getStationStyle(feature) {
    var iconStyle = new ol.style.Style({
        image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
            opacity: 0.75,
            scale: typeScales[type]/1.5,
            src: 'http://www.ns.nl/static/generic/1.21.1/images/nslogo.svg',
        })),
        text: new ol.style.Text({
            text: feature.get('text'),
            scale: typeScales[type]*2.0,
            offsetY: 20,
            fill: new ol.style.Fill({
                color: '#000',
            })
        })
    });
    return iconStyle;
}


function createStationFeature(station, lonLat) {
    var iconFeature = new ol.Feature({
        geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
        name: station.names.long,
        type: station.type,
        text: station.names.long,
    });
    return iconFeature;              // The function returns the product of p1 and p2
}
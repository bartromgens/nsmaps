
// http://stackoverflow.com/a/4234006
$.ajaxSetup({beforeSend: function(xhr){
  if (xhr.overrideMimeType)
  {
    xhr.overrideMimeType("application/json");
  }
}
});


var map = new ol.Map({target: 'map'});
var view = new ol.View( {center: [0, 0], zoom: 10, projection: 'EPSG:3857'} );
map.setView(view);


$.getJSON("stations.json", function(json) {
    console.log(json); // this will show the info it in firebug console

    var lon = '5.2';
    var lat = '142.0';
    console.log(lat + ' ' + lon);
    view.setCenter(ol.proj.fromLonLat([lon, lat]))

    var iconFeatures=[];

    var stations = json.stations;
    for (index in stations)
    {
        var station = stations[index];
        var names = station.names;
        console.log(names.long);
        console.log(lonLat);
        var lat = parseFloat(station.lat);
        lat = lat + 90.0;
        var lonLat = [station.lon, lat.toString()];
        var iconFeature = new ol.Feature({
            geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
            name: names.long,
            type: station.type,
            scale: 0.5,
        });

        iconFeatures.push(iconFeature);
    }

    var vectorSource = new ol.source.Vector({
        features: iconFeatures //add an array of features
    });

    var iconStyle = new ol.style.Style({
        image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
//          anchor: [0.5, 46],
//            anchorXUnits: 'fraction',
//            anchorYUnits: 'pixels',
            opacity: 0.75,
            scale: 0.5,
            src: 'http://www.ns.nl/static/generic/1.21.1/images/nslogo.svg',
        }))
    });


    var vectorLayer = new ol.layer.Vector({
        source: vectorSource,
        style: iconStyle
    });

    map.addLayer(vectorLayer);
});


var osmSource = new ol.source.OSM("OpenStreetMap");
var osmLayer = new ol.layer.Tile({source: osmSource});
map.addLayer(osmLayer);
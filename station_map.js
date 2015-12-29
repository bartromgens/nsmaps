
// http://stackoverflow.com/a/4234006
$.ajaxSetup({beforeSend: function(xhr){
  if (xhr.overrideMimeType)
  {
    xhr.overrideMimeType("application/json");
  }
}
});


var map = new ol.Map({target: 'map'});
var view = new ol.View( {center: [0, 0], zoom: 12, projection: 'EPSG:3857'} );
map.setView(view);


$.getJSON("stations.json", function(json) {
    console.log(json); // this will show the info it in firebug console

    var lon = '5.1';
    var lat = '142.0';
    console.log(lat + ' ' + lon);
    view.setCenter(ol.proj.fromLonLat([lon, lat]))

    var stopTrainIcons = [];
    var intercityTrainIcons = [];
    var iconFeatures = [];
    var scales = [];

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

        var iconFeature = createStationFeature(station, lonLat)

        if (station.type == 'stoptreinstation')
        {
            stopTrainIcons.push(iconFeature);
        }
        else if (station.type == 'megastation')
        {
            intercityTrainIcons.push(iconFeature);
        }
    }

    iconFeatures.push(stopTrainIcons);
    scales.push(0.4);
    iconFeatures.push(intercityTrainIcons);
    scales.push(1.0);

    for (index in iconFeatures)
    {
        features = iconFeatures[index];
        var vectorSource = new ol.source.Vector({
            features: features //add an array of features
        });

        var iconStyle = new ol.style.Style({
            image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
                opacity: 0.75,
                scale: scales[index],
                src: 'http://www.ns.nl/static/generic/1.21.1/images/nslogo.svg',
            }))
        });

        var vectorLayer = new ol.layer.Vector({
            source: vectorSource,
            style: iconStyle
        });

        map.addLayer(vectorLayer);
    }

});


var osmSource = new ol.source.OSM("OpenStreetMap");
var osmLayer = new ol.layer.Tile({source: osmSource});
map.addLayer(osmLayer);


function createStationFeature(station, lonLat) {
    var iconFeature = new ol.Feature({
        geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
        name: station.names.long,
        type: station.type,
    });
    return iconFeature;              // The function returns the product of p1 and p2
}
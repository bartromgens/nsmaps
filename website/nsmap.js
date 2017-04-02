function createNsmap() {
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
//    osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png");  // needs an API key
    osmSource.setUrl("https://a.tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=52962bab91de4e789491bc1f5ed4956e");

    var osmLayer = new ol.layer.Tile({source: osmSource});
    map.addLayer(osmLayer);
    map.stationFeaturesSelectable = [];
    map.contourLayers = [];
    map.stations = [];

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

    map.moveToStation = function(stationId) {
        var station = map.getStationById(stationId);
        if (!station) {
            console.log("ERROR: station not found, id:", stationId);
            return;
        }

        view.animate({
            center: ol.proj.fromLonLat([station.lon, station.lat]),
            duration: 300
        });
    };

    map.getStationById = function(stationId) {
        for (var i in map.stations) {
            if (map.stations[i].id == stationId) {
                return map.stations[i];
            }
        }
        return null;
    };

    map.getStationByName = function(stationName) {
        for (var i in map.stations) {
            if (map.stations[i].names.long == stationName) {
                return map.stations[i];
            }
            if (map.stations[i].names.short == stationName) {
                return map.stations[i];
            }
        }
        return null;
    };

    map.showAndPanToStation = function() {
        console.log('showAndPanToStation');
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
        function updateColorBarLegend(stationId) {
            var colorBarImage = document.getElementById('colorbar-legend');
            var imageUrl = dataDir + "contours/" + stationId + "_colorbar.png";
            colorBarImage.style.backgroundImage = "url(" + imageUrl + ")";
        }

        for (var i = 0; i < map.contourLayers.length; ++i)
        {
            var removedLayer = map.removeLayer(map.contourLayers[i]);
        }
        map.contourLayers.length = 0;
        station = map.getStationById(stationId);
        document.getElementById('departure-station-input').value = station.names.long;
        var geojsonUrl = dataDir + "contours/" + stationId + '.geojson';
        addContourLayer(geojsonUrl, map, map.contourLayers);
        updateColorBarLegend(stationId);
        map.selectStationFeature(stationId);
        //    current_station_control_label.setText(selected_station_name);
    };

    map.stationStyleFunction = function(feature, resolution) {
        var zoom = map.getView().getZoom();
        var zoomFactor = zoom*zoom/100.0;
        var strokeColor = 'black';
        var circleColor = 'yellow';
        if (feature.get('selectable'))
        {
            strokeColor = 'black';
            circleColor = '#2293ff';
        }

        var circleStyle = new ol.style.Circle(({
            fill: new ol.style.Fill({color: circleColor}),
            stroke: new ol.style.Stroke({
                color: strokeColor,
                width: 3*zoomFactor,
            }),
            radius: typeScales[feature.get('type')]*zoomFactor
        }));

        return new ol.style.Style({
            image: circleStyle,
        });
    };

    map.getSelectedStationStyle = function(feature, resolution) {
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
                feature.setStyle(map.stationStyleFunction);
            }
        }
    };

    return map;
}

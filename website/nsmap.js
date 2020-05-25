import Map from 'ol/map'
import View from 'ol/view'

import SourceOSM from "ol/source/osm";
import Tile from "ol/layer/tile";
import olproj from "ol/proj";

import Circle from 'ol/style/circle'
import Style from 'ol/style/style'
import Stroke from 'ol/style/stroke'
import Fill from 'ol/style/fill'

const NSMapCountours = require("./map_contours");


export function createNsmap(dataDir) {
    console.log('createNsmap');
    const map = new Map({
        target: 'map',
        //    loadTilesWhileAnimating: true,
        //    loadTilesWhileInteracting: true,
    });

    const lon = '5.1';
    const lat = '142.0';
    const view = new View( {center: olproj.fromLonLat([lon, lat]), zoom: 10, projection: 'EPSG:3857'} );
    map.setView(view);

    const osmSource = new SourceOSM("OpenCycleMap");
//    osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png");  // needs an API key
    osmSource.setUrl("https://a.tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=52962bab91de4e789491bc1f5ed4956e");

    const osmLayer = new Tile({source: osmSource});
    map.addLayer(osmLayer);
    map.stationFeaturesSelectable = [];
    map.contourLayers = [];
    map.stations = [];

    const typeScales = {
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
        const station = map.getStationById(stationId);
        if (!station) {
            console.log("ERROR: station not found, id:", stationId);
            return;
        }

        view.animate({
            center: olproj.fromLonLat([station.lon, station.lat]),
            duration: 300
        });
    };

    map.getStationById = function(stationId) {
        for (var i in map.stations) {
            if (map.stations[i].id === stationId) {
                return map.stations[i];
            }
        }
        return null;
    };

    map.getStationByName = function(stationName) {
        for (var i in map.stations) {
            if (map.stations[i].names.long === stationName) {
                return map.stations[i];
            }
            if (map.stations[i].names.short === stationName) {
                return map.stations[i];
            }
        }
        return null;
    };

    map.showAndPanToStation = function() {
        console.log('showAndPanToStation');
        const stationName = document.getElementById('departure-station-input').value;
        const station = map.getStationByName(stationName);
        if (station) {
            map.showStationContours(station.id);
            map.moveToStation(station.id);
        } else {
            console.log("ERROR: station not found");
        }
    };

    map.showStationContours = function(stationId) {
        function updateColorBarLegend(stationId) {
            const colorBarImage = document.getElementById('colorbar-legend');
            const imageUrl = dataDir + "contours/" + stationId + "_colorbar.png";
            colorBarImage.style.backgroundImage = "url(" + imageUrl + ")";
        }

        for (let i = 0; i < map.contourLayers.length; ++i) {
            map.removeLayer(map.contourLayers[i]);
        }
        map.contourLayers.length = 0;
        const station = map.getStationById(stationId);
        document.getElementById('departure-station-input').value = station.names.long;
        $("#navbar-trainstation").text(station.names.long);
        var geojsonUrl = dataDir + "contours/" + stationId + '.geojson';
        NSMapCountours.addContourLayer(geojsonUrl, map, map.contourLayers);
        updateColorBarLegend(stationId);
        map.selectStationFeature(stationId);
        //    current_station_control_label.setText(selected_station_name);
    };

    map.stationStyleFunction = function(feature, resolution) {
        const zoom = map.getView().getZoom();
        const zoomFactor = zoom * zoom / 100.0;
        let strokeColor = 'black';
        let circleColor = 'yellow';
        if (feature.get('selectable')) {
            strokeColor = 'black';
            circleColor = '#2293ff';
        }

        const circleStyle = new Circle(({
            fill: new Fill({color: circleColor}),
            stroke: new Stroke({
                color: strokeColor,
                width: 3 * zoomFactor,
            }),
            radius: typeScales[feature.get('type')] * zoomFactor
        }));

        return new Style({
            image: circleStyle,
        });
    };

    map.getSelectedStationStyle = function(feature, resolution) {
        var strokeColor = 'lightgreen';
        var circleColor = 'green';

        var circleStyle = new Circle(({
            fill: new Fill({color: circleColor}),
            stroke: new Stroke({color: strokeColor, width: 3}),
            radius: typeScales[feature.get('type')] * 1.5
        }));

        return new Style({
            image: circleStyle,
        });
    };

    map.selectStationFeature = function(stationId) {
        for (var i in map.stationFeaturesSelectable) {
            var feature = map.stationFeaturesSelectable[i];
            if (feature.get('id') === stationId)
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

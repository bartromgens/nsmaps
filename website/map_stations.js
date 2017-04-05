function addStationsLayer(stations, map, stationFeaturesSelectable) {
    console.log('createStationLayer');
    var stationFeaturesUnselectable = [];

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

    var stationFeatures = [];

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
        stationFeatures[j].setStyle(map.stationStyleFunction);
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

    var onSelectStationFeature = function(evt) {
        evt.deselected.forEach(function(feature){
            feature.setStyle(map.stationStyleFunction);
        });

        if (!evt.selected[0])
        {
            return;
        }

        evt.selected.forEach(function(feature){
            feature.setStyle(map.getSelectedStationStyle(feature));
        });
        var stationId = evt.selected[0].get('id');
        map.showStationContours(stationId);
        history.pushState(null, null, '?station=' + stationId);
        $("#click-tip").hide();
        //        moveToStation(stationId);
    };

    select.on('select', onSelectStationFeature);

    map.addInteraction(select);
}

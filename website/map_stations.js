import OLSourceVector from 'ol/source/vector';
import OLLayerVector from 'ol/layer/vector';

import OLFeature from 'ol/feature';
import OLPoint from 'ol/geom/point';

import olproj from 'ol/proj';
import OLSelect from 'ol/interaction/select';
import olcondition from 'ol/events/condition';


export function addStationsLayer(stations, map, stationFeaturesSelectable) {
    console.log('createStationLayer');
    const stationFeaturesUnselectable = [];

    function createStationFeature(station, lonLat) {
        return new OLFeature({
            geometry: new OLPoint(olproj.fromLonLat(lonLat)),
            title: station.names.long,
            id: station.id,
            type: station.type,
            text: station.names.short,
            selectable: station.selectable
        });
    }

    for (const station of stations) {
        let lat = parseFloat(station.lat);
        lat = lat + 90.0;
        const lonLat = [station.lon.toFixed(5), lat.toFixed(5)];
        station.selectable = station.travel_times_available;
        const stationFeature = createStationFeature(station, lonLat);
        if (station.selectable) {
            stationFeaturesSelectable.push(stationFeature);
        }
        else {
            stationFeaturesUnselectable.push(stationFeature);
        }
    }

    const stationSelectableSource = new OLSourceVector({
        features: stationFeaturesSelectable
    });

    const stationUnselectableSource = new OLSourceVector({
        features: stationFeaturesUnselectable
    });

    const stationsSelectableLayer = new OLLayerVector({
        source: stationSelectableSource,
        style: map.stationStyleFunction
    });

    const stationsUnselectableLayer = new OLLayerVector({
        source: stationUnselectableSource,
        style: map.stationStyleFunction
    });

    stationsSelectableLayer.setZIndex(99);
    stationsUnselectableLayer.setZIndex(10);

    map.addLayer(stationsSelectableLayer);
    map.addLayer(stationsUnselectableLayer);

    // Select features
    const select = new OLSelect({
        layers: [stationsSelectableLayer],
        condition: olcondition.click
    });

    const onSelectStationFeature = function(evt) {
        evt.deselected.forEach(function(feature){
            feature.setStyle(map.stationStyleFunction);
        });

        if (!evt.selected[0]) {
            return;
        }

        evt.selected.forEach(function(feature){
            feature.setStyle(map.getSelectedStationStyle(feature));
        });
        const stationId = evt.selected[0].get('id');
        map.showStationContours(stationId);
        history.pushState(null, null, '?station=' + stationId);
        $('#click-tip').hide();
        //        moveToStation(stationId);
    };

    select.on('select', onSelectStationFeature);

    map.addInteraction(select);
}

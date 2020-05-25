import OLProjection from "ol/proj/projection";

import OLSourceVectorTile from "ol/source/vectortile";
import OLLayerVectorTile from "ol/layer/vectortile";

import OLStyle from "ol/style/style";
import OLStroke from "ol/style/stroke";
import OLGeoJSON from "ol/format/geojson";

import oltilegrid from "ol/tilegrid";


export function addContourLayer(geojsonUrl, map, layerCollection) {
    console.log('addContourLayer', geojsonUrl);

    const replacer = function(key, value) {
        if (value.geometry) {
            var type;
            var rawType = value.type;
            var geometry = value.geometry;

            if (rawType === 1) {
                type = geometry.length === 1 ? 'Point' : 'MultiPoint';
            } else if (rawType === 2) {
                type = geometry.length === 1 ? 'LineString' : 'MultiLineString';
            } else if (rawType === 3) {
                type = geometry.length === 1 ? 'Polygon' : 'MultiPolygon';
            }

            return {
                'type': 'Feature',
                'geometry': {
                    'type': 'MultiLineString',
                    'coordinates': geometry,
                },
                'properties': value.tags
            };
        } else {
            return value;
        }
    };

    const tilePixels = new OLProjection({
        code: 'TILE_PIXELS',
        units: 'tile-pixels'
    });

    return fetch(geojsonUrl).then(function(response) {
        return response.json();
    }).then(function(json) {
        const tileIndex = geojsonvt(json, {
            extent: 4096,
            debug: 1,
            indexMaxPoints: 100000
        });

        const vectorSource = new OLSourceVectorTile({
            format: new OLGeoJSON(),
            tileGrid: oltilegrid.createXYZ(),
            tilePixelRatio: 16,
            tileLoadFunction: function(tile) {
                const format = tile.getFormat();
                const tileCoord = tile.getTileCoord();
                const data = tileIndex.getTile(tileCoord[0], tileCoord[1], -tileCoord[2] - 1);

                const features = format.readFeatures(
                    JSON.stringify({
                        type: 'FeatureCollection',
                        features: data ? data.features : []
                    }, replacer));
                    tile.setLoader(function() {
                        tile.setFeatures(features);
                        tile.setProjection(tilePixels);
                    });
                },
            url: 'data:' // arbitrary url, we don't use it in the tileLoadFunction
        });

        function lineStyleFunction(feature, resolution) {
            const strokeWidth = feature.get('stroke-width');
            const zoom = map.getView().getZoom();
            let lineWidth = strokeWidth;
            const value = feature.get('level-value');
            let color = feature.get('stroke');
            // var color = ol.color.asArray(feature.get('stroke'));
            // color[3] = 0.8;
            const scaleFactor = 0.7;
            const zoomFactor = zoom * zoom / 100.0;
            const zoomLevelShow10 = 9;
            const zoomLevelShow5 = 11;

            if (value % 60 === 0) {
                lineWidth = strokeWidth * 3.0;
            }
            else if (value % 30 === 0) {
                lineWidth = strokeWidth * 2.0;
            }
            else if (value % 15 === 0 && zoom < (zoomLevelShow10)) {
                lineWidth = strokeWidth;
            }
            else if (value % 10 === 0) {
                if (zoom < zoomLevelShow10) {
                    color = 'rgba(0,0,0,0)';
                }
                else {
                    lineWidth = strokeWidth;
                }
            }
            else if (value % 5 === 0) {
                if (zoom < zoomLevelShow5) {
                    color = 'rgba(0,0,0,0)';
                }
                else {
                    lineWidth = strokeWidth/2.5;
                }
            }

            if (zoom <= 8) {
                lineWidth *= 0.9;
            }

            return new OLStyle({
                stroke: new OLStroke({
                    color: color,
                    width: lineWidth * scaleFactor * zoomFactor,
                    opacity: 0.4
                })
            });
        }

        var vectorLayer = new OLLayerVectorTile({
            source: vectorSource,
            style: lineStyleFunction,
            updateWhileInteracting: false,
            updateWhileAnimating: false,
            renderMode: 'vector',  // other options stop loading tiles after zooming on large resolutions (OL bug?)
            //preload: 2,
        });

        map.addLayer(vectorLayer);
        layerCollection.push(vectorLayer);
    });
}

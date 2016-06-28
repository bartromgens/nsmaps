#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps


DATA_DIR = './website/nsmaps-data'


def test():
    stations = nsmaps.station.Stations(DATA_DIR)

    departure_station_name = 'Utrecht Centraal'
    departure_station = stations.find_station(departure_station_name)
    assert os.path.exists(os.path.join(DATA_DIR, 'contours/'))

    test_config = nsmaps.contourmap.ContourPlotConfig()
    # test_config = nsmaps.contourmap.TestConfig()
    # test_config.print_bounding_box()

    create_contour_tiles_for_station(departure_station, stations, test_config)


def create_contour_tiles_for_station(departure_station, stations, config):
    max_zoom = 12
    filepaths = []
    contourmap = nsmaps.contourmap.Contour(departure_station, stations, config, DATA_DIR)
    filepath = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_major.geojson')
    if os.path.exists(filepath):
        print('WARNING: skipping station ' + departure_station.get_code() + ', files already exist.')
        return
    filepaths.append(filepath)
    contourmap.create_contour_data(filepath)
    contourmap.create_geojson(filepath, min_zoom=0, max_zoom=max_zoom, stroke_width=9, n_contours=21)
    filepath = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_minor.geojson')
    filepaths.append(filepath)
    contourmap.create_geojson(filepath, min_zoom=max_zoom - 1, max_zoom=max_zoom, stroke_width=3, n_contours=41)
    tile_dir = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '/tiles/')
    contourmap.create_geojson_tiles(filepaths, tile_dir=tile_dir, min_zoom=0, max_zoom=max_zoom)


def create_all():
    stations = nsmaps.station.Stations(DATA_DIR)

    # test_config = nsmaps.contourmap.TestConfig()
    config = nsmaps.contourmap.ContourPlotConfig()

    for departure_station in stations:
        if departure_station.has_travel_time_data():
            create_contour_tiles_for_station(departure_station, stations, config)


if __name__ == "__main__":
    # test()
    create_all()
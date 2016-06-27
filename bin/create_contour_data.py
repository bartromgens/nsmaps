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

    filepaths = []

    test_config = nsmaps.contourmap.ContourPlotConfig()
    # test_config = nsmaps.contourmap.TestConfig()
    test_config.print_bounding_box()

    contourmap = nsmaps.contourmap.Contour(departure_station, stations, test_config, DATA_DIR)

    filepath = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_major.geojson')
    filepaths.append(filepath)
    contourmap.create_contour_data(filepath)
    contourmap.create_geojson(filepath, min_zoom=0, max_zoom=12, stroke_width=9, n_contours=11)

    filepath = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_minor.geojson')
    filepaths.append(filepath)
    contourmap.create_geojson(filepath, min_zoom=10, max_zoom=12, stroke_width=3, n_contours=51)

    tile_dir = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '/tiles/')
    contourmap.create_geojson_tiles(filepaths, tile_dir=tile_dir, min_zoom=0, max_zoom=12)


def create_all():
    stations = nsmaps.station.Stations(DATA_DIR)

    # test_config = nsmaps.contourmap.TestConfig()
    config = nsmaps.contourmap.ContourPlotConfig()

    for station in stations:
        if station.has_travel_time_data():
            contourmap = nsmaps.contourmap.Contour(station, stations, config, DATA_DIR)
            contourmap.create_contour_data(filepath_out)
            contourmap.create_geojson_tiles(filepath_out)


if __name__ == "__main__":
    test()
    # create_all()
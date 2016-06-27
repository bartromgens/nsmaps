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

    # test_config = nsmaps.contourmap.ContourPlotConfig()
    test_config = nsmaps.contourmap.TestConfig()
    test_config.print_bounding_box()
    contourmap = nsmaps.contourmap.Contour(departure_station, stations, test_config, DATA_DIR)
    filepath = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '.geojson')
    filepaths.append(filepath)
    contourmap.create_contour_data(filepath, min_zoom=9, max_zoom=12, stroke_width=3)

    # test_major_config = nsmaps.contourmap.ContourPlotConfig(n_contours=11)
    test_major_config = nsmaps.contourmap.TestConfig(n_contours=11)
    contourmap_major = nsmaps.contourmap.Contour(departure_station, stations, test_major_config, DATA_DIR)
    filepath = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_major.geojson')
    filepaths.append(filepath)
    contourmap_major.create_contour_data(filepath, min_zoom=0, max_zoom=12, stroke_width=9)

    # test_minor_config = nsmaps.contourmap.ContourPlotConfig(n_contours=81)
    test_minor_config = nsmaps.contourmap.TestConfig(n_contours=81)
    contourmap_minor = nsmaps.contourmap.Contour(departure_station, stations, test_minor_config, DATA_DIR)
    filepath = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_minor.geojson')
    filepaths.append(filepath)
    contourmap_minor.create_contour_data(filepath, min_zoom=12, max_zoom=12, stroke_width=1)

    tile_dir = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '/tiles/')
    contourmap_major.create_geojson_tiles(filepaths, tile_dir=tile_dir, min_zoom=0, max_zoom=12)


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
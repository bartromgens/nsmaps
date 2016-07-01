#!/usr/bin/env python3

import sys
import os

import numpy

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
    test_config.print_bounding_box()

    create_contour_tiles_for_station(departure_station, stations, test_config)


def create_contour_tiles_for_station(departure_station, stations, config):
    max_zoom = 11
    max_level = 180
    filepaths = []
    contourmap = nsmaps.contourmap.Contour(departure_station, stations, config, DATA_DIR)

    filepath_major = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_major.geojson')
    if os.path.exists(filepath_major):
        print('WARNING: skipping station ' + departure_station.get_code() + ', files already exist.')
        return
    filepaths.append(filepath_major)
    contourmap.create_contour_data(filepath_major)
    levels = numpy.linspace(0, max_level, num=13)
    contourmap.create_geojson(filepath_major, min_zoom=0, max_zoom=max_zoom-2, stroke_width=8, levels=levels)

    filepath_minor = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_minor.geojson')
    filepaths.append(filepath_minor)
    levels_minor = numpy.linspace(0, max_level, num=19)
    contourmap.create_geojson(filepath_minor, min_zoom=max_zoom-1, max_zoom=max_zoom, stroke_width=8, levels=levels_minor)

    filepath_top = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '_top.geojson')
    filepaths.append(filepath_top)
    levels_top = numpy.linspace(0, max_level, num=7)
    contourmap.create_geojson(filepath_top, min_zoom=0, max_zoom=max_zoom, stroke_width=16, levels=levels_top)

    tile_dir = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '/tiles/')
    contourmap.create_geojson_tiles(filepaths, tile_dir=tile_dir, min_zoom=0, max_zoom=max_zoom)


def create_all():
    stations = nsmaps.station.Stations(DATA_DIR)

    # config = nsmaps.contourmap.TestConfig()
    config = nsmaps.contourmap.ContourPlotConfig()

    for departure_station in stations:
        if departure_station.has_travel_time_data():
            # if departure_station.get_type() == 'megastation':
            create_contour_tiles_for_station(departure_station, stations, config)


if __name__ == "__main__":
    # test()
    create_all()
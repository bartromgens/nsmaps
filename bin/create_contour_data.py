#!/usr/bin/env python3

import sys
import os

import numpy

sys.path.append('../nsmaps')

import nsmaps
from nsmaps.logger import logger


DATA_DIR = './website/nsmaps-data'


def test():
    stations = nsmaps.station.Stations(DATA_DIR)

    departure_station_name = 'Utrecht Centraal'
    departure_station = stations.find_station(departure_station_name)
    assert os.path.exists(os.path.join(DATA_DIR, 'contours/'))

    # test_config = nsmaps.contourmap.ContourPlotConfig()
    test_config = nsmaps.contourmap.TestConfig()
    test_config.print_bounding_box()

    create_contours_for_station(departure_station, stations, test_config, overwrite_existing=True)


def create_contours_for_station(departure_station, stations, config, overwrite_existing=False, use_saved_data=False):
    logger.info(departure_station)
    max_level = 180
    filepaths = []
    contourmap = nsmaps.contourmap.Contour(departure_station, stations, config)

    filepath_geojson = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '.geojson')
    if not overwrite_existing and os.path.exists(filepath_geojson):
        print('WARNING: skipping station ' + departure_station.get_code() + ', files already exist.')
        return
    filepaths.append(filepath_geojson)
    if use_saved_data:
        contourmap.load()
    else:
        contourmap.create_contour_data()
        contourmap.save()
    levels_minor = numpy.linspace(0, max_level, num=37)
    contourmap.create_geojson(filepath_geojson, stroke_width=4, levels=levels_minor, overwrite=overwrite_existing)


def create_all():
    stations = nsmaps.station.Stations(DATA_DIR)

    # config = nsmaps.contourmap.TestConfig()
    config = nsmaps.contourmap.ContourPlotConfig()

    for departure_station in stations:
        if departure_station.has_travel_time_data():
            # if departure_station.get_type() == 'megastation':
            create_contours_for_station(departure_station, stations, config, overwrite_existing=False, use_saved_data=False)


if __name__ == "__main__":
    # test()
    create_all()
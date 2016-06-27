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
    filepath_out = os.path.join(DATA_DIR, 'contours/' + departure_station.get_code() + '.geojson')
    test_config = nsmaps.contourmap.ContourPlotConfig()
    test_config.print_bounding_box()

    contourmap = nsmaps.contourmap.Contour(departure_station, stations, test_config, DATA_DIR)
    # contourmap.create_contour_data(filepath_out)
    contourmap.create_geojson_tiles(filepath_out)

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
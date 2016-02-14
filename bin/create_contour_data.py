#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps


DATA_DIR = './website/data'


def test():
    departure_station_name = 'Utrecht Centraal'
    stations = nsmaps.station.Stations()
    departure_station = stations.find_station(departure_station_name)
    filepath_out = os.path.join(DATA_DIR, 'contours_' + departure_station.get_code() + '.json')
    test_config = nsmaps.contourmap.TestConfig()
    contourmap = nsmaps.contourmap.Contour(departure_station, stations, test_config, DATA_DIR)
    contourmap.create_contour_data(filepath_out)


def create_all():
    stations = Station.from_json('./data/stations.json')
    for station in stations:
        nsmaps.contourmap.create_contour_plot(stations, station)  # TODO: fix config


if __name__ == "__main__":
    test()
    # create_all()
#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

from nsmaps.station import Station
from nsmaps.contourmap import TestConfig
import nsmaps.contourmap

DATA_DIR = './website/data'


def test():
    departure_station_name = 'Utrecht Centraal'
    stations = Station.from_json(os.path.join(DATA_DIR, 'stations.json'))
    departure_station = Station.find_station(stations, departure_station_name)
    filepath_out = os.path.join(DATA_DIR, 'contours_' + departure_station.id + '.json')
    test_config = TestConfig()
    contourmap = nsmaps.contourmap.Contour(departure_station, stations, test_config, DATA_DIR)
    contourmap.create_contour_data(filepath_out)


def create_all():
    stations = Station.from_json('./data/stations.json')
    for station in stations:
        nsmaps.contourmap.create_contour_plot(stations, station)  # TODO: fix config


if __name__ == "__main__":
    test()
    # create_all()
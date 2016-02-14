#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps


DATA_DIR = './website/data'


def main():
    stations = nsmaps.station.Stations()
    stations.update_station_data(DATA_DIR, 'stations.json')


if __name__ == "__main__":
    main()
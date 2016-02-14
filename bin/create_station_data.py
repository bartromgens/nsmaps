#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps


DATA_DIR = './website/data'


def main():
    stations = nsmaps.station.Stations(DATA_DIR)
    stations.update_station_data('stations.json')


if __name__ == "__main__":
    main()
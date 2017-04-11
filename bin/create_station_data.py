#!/usr/bin/env python3

import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)

import nsmaps


DATA_DIR = './website/nsmaps-data'


def main():
    stations = nsmaps.station.Stations(DATA_DIR)
    stations.update_station_data('stations.json')


if __name__ == "__main__":
    main()
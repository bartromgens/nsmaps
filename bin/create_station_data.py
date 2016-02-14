#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps.station


DATA_DIR = './website/data'


def main():
    nsmaps.station.update_station_data(DATA_DIR, 'stations.json')


if __name__ == "__main__":
    main()
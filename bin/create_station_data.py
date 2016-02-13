#!/usr/bin/env python3

import sys
import os

sys.path.insert(1, '../nsmaps')

from nsmaps.station import update_station_data


DATA_DIR = './website/data'


def main():
    update_station_data(DATA_DIR, 'stations.json')


if __name__ == "__main__":
    main()
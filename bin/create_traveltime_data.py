#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import ns_api

from nsmaps.local_settings import USERNAME, APIKEY
from nsmaps.duration_data_from_station import create_traveltimes_data
from nsmaps.duration_data_from_station import recreate_missing_destinations
from nsmaps.duration_data_from_station import get_major_stations

DATA_DIR = './website/data'


def main():
    nsapi = ns_api.NSAPI(USERNAME, APIKEY)
    stations = nsapi.get_stations()
    major_stations = get_major_stations(stations)
    create_traveltimes_data(major_stations, DATA_DIR)
    recreate_missing_destinations(DATA_DIR, False)


if __name__ == "__main__":
    main()
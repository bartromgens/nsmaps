#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import ns_api

from nsmaps.local_settings import USERNAME, APIKEY
import nsmaps.station

DATA_DIR = './website/data'


def main():
    nsapi = ns_api.NSAPI(USERNAME, APIKEY)
    stations = nsapi.get_stations()
    major_stations = nsmaps.station.get_major_stations(stations)
    nsmaps.station.create_traveltimes_data(major_stations, DATA_DIR)
    nsmaps.station.recreate_missing_destinations(DATA_DIR, False)


if __name__ == "__main__":
    main()
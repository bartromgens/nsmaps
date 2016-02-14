#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps
from nsmaps.station import StationType

DATA_DIR = './website/data'


def main():
    os.path
    stations = nsmaps.station.Stations(DATA_DIR)
    major_station_types = (
        StationType.intercitystation,
        StationType.knooppuntIntercitystation,
        StationType.megastation,
        # StationType.knooppuntSneltreinstation,
        # StationType.sneltreinstation,
    )
    major_stations = stations.get_stations_for_types(major_station_types)
    stations.create_traveltimes_data(major_stations)
    stations.recreate_missing_destinations(DATA_DIR, False)


if __name__ == "__main__":
    main()
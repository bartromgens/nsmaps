#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps
from nsmaps.station import StationType

DATA_DIR = './website/data'

MAX_STATIONS = 60


def main():
    stations = nsmaps.station.Stations(DATA_DIR)
    major_station_types = (
        StationType.intercitystation,
        StationType.knooppuntIntercitystation,
        StationType.megastation,
        StationType.knooppuntSneltreinstation,
        StationType.sneltreinstation,
        StationType.knooppuntStoptreinstation,
        StationType.stoptreinstation
    )
    stations_options = stations.get_stations_for_types(major_station_types)

    stations_todo = []

    n_stations = 0
    for station in stations_options:
        if n_stations >= MAX_STATIONS:
            break
        if not station.has_travel_time_data() and station.get_country_code() == 'NL':
            stations_todo.append(station)
            n_stations += 1
            print(station)

    timestamp = "19-04-2016 08:00"
    stations.create_traveltimes_data(stations_todo, timestamp)
    stations.recreate_missing_destinations(DATA_DIR, timestamp, False)


if __name__ == "__main__":
    main()
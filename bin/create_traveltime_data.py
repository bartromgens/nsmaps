#!/usr/bin/env python3

import sys
import os

sys.path.append('../nsmaps')

import nsmaps
from nsmaps.station import StationType

DATA_DIR = './website/nsmaps-data'

MAX_STATIONS = 60

TRAVEL_DATETIME = "19-04-2017 08:00"


def main():
    stations = nsmaps.station.Stations(DATA_DIR, test=False)

    major_station_types = (
        StationType.megastation,
        StationType.knooppuntIntercitystation,
        StationType.intercitystation,
        StationType.knooppuntSneltreinstation,
        StationType.sneltreinstation,
        StationType.knooppuntStoptreinstation,
        StationType.stoptreinstation
    )
    stations_options = stations.get_stations_for_types(major_station_types)

    stations_todo = []

    n_stations = 0
    for station in stations_options:
        print(station.get_name())
        if n_stations >= MAX_STATIONS:
            break
        if not station.has_travel_time_data() and station.get_country_code() == 'NL':
            print(station.get_travel_time_filepath())
            stations_todo.append(station)
            n_stations += 1
            print(station)

    stations.create_traveltimes_data(stations_todo, TRAVEL_DATETIME)
    # stations.recreate_missing_destinations(timestamp, False)

if __name__ == "__main__":
    main()

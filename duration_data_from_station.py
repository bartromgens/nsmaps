import json
from datetime import datetime
import time
import os

import requests
import ns_api

from local_settings import USERNAME, APIKEY
from station import Station, StationType
from logger import logger


def get_station_id(station_name, stations):
    for station in stations:
        if station.names['long'] == station_name:
            return station.code
    return None


def create_trip_data_from_station(station_from, stations):
    data = {'stations': []}

    timestamp = "12-01-2016 08:00"
    via = ""

    data['stations'].append({'name': station_from.names['long'],
                             'id': station_from.code,
                             'travel_time_min': 0,
                             'travel_time_planned': "0:00"})

    filename_out = './data/traveltimes_from_' + station_from.code + '.json'
    if os.path.exists(filename_out):
        logger.warning('File ' + filename_out + ' already exists. Will not overwrite by default. Return.')
        return

    for station in stations:
        if station.country != "NL":
            continue
        if station.code == station_from.code:
            continue
        trips = []
        try:
            trips = nsapi.get_trips(timestamp, station_from.code, via, station.code)
        except TypeError as error:
            # this is a bug in ns-api, should return empty trips in case there are no results
            logger.error('Error while trying to get trips for destination: ' + station.names['long'] + ', from: ' + station_from.names['long'])
            continue
        except requests.exceptions.HTTPError as error:
            # 500: Internal Server Error does always happen for some stations (example are Eijs-Wittem and Kerkrade-West)
            logger.error('HTTP Error while trying to get trips for destination: ' + station.names['long'] + ', from: ' + station_from.names['long'])
            continue

        if not trips:
            continue

        shortest_trip = trips[0]
        for trip in trips:
            travel_time = datetime.strptime(trip.travel_time_planned, "%H:%M").time()
            trip.travel_time_min = travel_time.hour * 60 + travel_time.minute
            if trip.travel_time_min < shortest_trip.travel_time_min:
                shortest_trip = trip

        logger.info(shortest_trip.departure + ' - ' + shortest_trip.destination)
        data['stations'].append({'name': shortest_trip.destination,
                                 'id': get_station_id(shortest_trip.destination, stations),
                                 'travel_time_min': shortest_trip.travel_time_min,
                                 'travel_time_planned': shortest_trip.travel_time_planned})
        time.sleep(0.3)  # balance load on the NS server

    json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    with open(filename_out, 'w') as fileout:
        fileout.write(json_data)


if __name__ == "__main__":
    nsapi = ns_api.NSAPI(USERNAME, APIKEY)
    stations = nsapi.get_stations()
    major_stations = []
    major_station_types = (StationType.intercitystation,
                           StationType.knooppuntIntercitystation,
                           StationType.megastation)
    for station in stations:
        if station.country != "NL":
            continue
        for station_type in major_station_types:
            if station.stationtype == station_type.name:
                major_stations.append(station)

    for major_station in major_stations:
        create_trip_data_from_station(major_station, stations)

    # station_from_id = "UT"  # example: Utrecht Centraal
    # create_trip_data_from_station(station_from_id)

import json
from datetime import datetime
import time
import os

import requests
import ns_api

from local_settings import USERNAME, APIKEY
from station import Station, StationType
from logger import logger


def main():
    nsapi = ns_api.NSAPI(USERNAME, APIKEY)
    stations = nsapi.get_stations()
    major_stations = get_major_stations(stations)
    for major_station in major_stations:
        filename_out = './data/traveltimes_from_' + major_station.code + '.json'
        if os.path.exists(filename_out):
            logger.warning('File ' + filename_out + ' already exists. Will not overwrite by default. Return.')
            continue
        json_data = create_trip_data_from_station(major_station, stations)
        with open(filename_out, 'w') as fileout:
            fileout.write(json_data)


def recreate_missing_destinations(dry_run):
    nsapi = ns_api.NSAPI(USERNAME, APIKEY)
    stations = nsapi.get_stations()
    ignore_station_ids = ['HRY', 'WTM', 'KRW', 'VMW', 'RTST', 'WIJ', 'SPV', 'SPH']
    for station in stations:
        filename = './data/traveltimes_from_' + station.code + '.json'
        if not os.path.exists(filename):
            continue
        # if station.code != "ZL":
        #     continue
        stations_missing = get_missing_destinations(filename, stations)
        stations_missing_filtered = []
        for station_missing in stations_missing:
            if station_missing.id not in ignore_station_ids:
                stations_missing_filtered.append(stations_missing)
                logger.info(station.names['long'] + ' has missing station: ' + station_missing.name)
        if stations_missing_filtered and not dry_run:
            json_data = create_trip_data_from_station(station, stations)
            with open(filename, 'w') as fileout:
                fileout.write(json_data)
        else:
            logger.info('No missing destinations for ' + station.names['long'] + ' with ' + str(len(ignore_station_ids)) + ' ignored.')


def get_station_id(station_name, stations):
    for station in stations:
        if station.names['long'] == station_name:
            return station.code
    return None


def create_trip_data_from_station(station_from, stations):
    data = {'stations': []}

    timestamp = "13-01-2016 08:00"
    via = ""

    data['stations'].append({'name': station_from.names['long'],
                             'id': station_from.code,
                             'travel_time_min': 0,
                             'travel_time_planned': "0:00"})

    nsapi = ns_api.NSAPI(USERNAME, APIKEY)
    for station in stations:
        if station.country != "NL":
            continue
        if station.code == station_from.code:
            continue
        # if station.code != 'AMF':
        #     continue
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
        # time.sleep(0.3)  # balance load on the NS server

    json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    return json_data


def get_major_stations(stations):
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
    return major_stations


def get_missing_destinations(filename_json, stations):
    stations = Station.from_json()
    Station.travel_times_from_json(stations,  filename_json)
    missing_stations = []
    for station in stations:
        if station.travel_time_min == None:
            missing_stations.append(station)
    return missing_stations


if __name__ == "__main__":
    dry_run = False
    recreate_missing_destinations(dry_run)
    # main()

    # station_from_id = "UT"  # example: Utrecht Centraal
    # create_trip_data_from_station(station_from_id)

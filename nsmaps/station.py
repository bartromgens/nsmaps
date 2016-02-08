import json
from enum import Enum


class StationType(Enum):
    stoptreinstation = 1
    megastation = 2
    knooppuntIntercitystation = 3
    sneltreinstation = 4
    intercitystation = 5
    knooppuntStoptreinstation = 6
    facultatiefStation = 7
    knooppuntSneltreinstation = 8


class Station(object):
    def __init__(self, id, name, lon, lat, travel_time_min=None):
        self.id = id
        self.name = name
        self.lon = float(lon)
        self.lat = float(lat)
        self.travel_time_min = travel_time_min

    def __str__(self):
        return self.name + ' (' +  self.id + ')' + ', travel time: ' + str(self.travel_time_min)

    @staticmethod
    def from_json(filename='./data/stations.json'):
        stations_new = []
        with open(filename) as file:
            stations = json.load(file)['stations']
            for station in stations:
                stations_new.append(Station(station['id'], station['names']['long'], station['lon'], station['lat']))
        return stations_new

    @staticmethod
    def travel_times_from_json(stations, filename):
        with open(filename) as file:
            travel_times = json.load(file)['stations']
            for travel_time in travel_times:
                station_name = travel_time['name']
                station = Station.find_station(stations, station_name)
                if station:
                    station.travel_time_min = int(travel_time['travel_time_min'])

    @staticmethod
    def find_station(stations, name):
        for station in stations:
            if station.name == name:
                return station
        return None
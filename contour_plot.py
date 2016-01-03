import math
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import utilgeo
from scipy.spatial import KDTree

from contour_to_json import contour_to_json


class Station(object):
    def __init__(self, name, lon, lat, travel_time_min=0.0):
        self.name = name
        self.lon = float(lon)
        self.lat = float(lat)
        self.travel_time_min = travel_time_min

    def __str__(self):
        return self.name + ' (' + str(self.lon) + ', ' + str(self.lat) + ')' + ', travel time: ' + str(self.travel_time_min)

    @staticmethod
    def from_json(filename):
        stations_new = []
        with open(filename) as file:
            stations = json.load(file)['stations']
            for station in stations:
                stations_new.append(Station(station['names']['long'], station['lon'], station['lat']))
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


def create_contour_plot(stations, filename):
    np.set_printoptions(3, threshold=100, suppress=True)  # .3f

    delta = 0.005
    n_contours = 41

    delta_deg = 6
    lonmin = 3.0
    latmin = 50.5
    lonmax = lonmin + delta_deg
    latmax = latmin + delta_deg / 2

    cycle_speed_kmh = 18.0
    n_nearest = 15  # check N nearest stations as best start for cycle route

    print('starting spatial interpolation')

    altitude = 0.0
    gps = utilgeo.GPS()
    positions = []
    lonrange = np.arange(lonmin, lonmax, delta)
    latrange = np.arange(latmin, latmax, delta / 2.0)
    Z = np.zeros((int(lonrange.shape[0]), int(latrange.shape[0])))

    for station in stations:
        x, y, z = gps.lla2ecef([station.lat, station.lon, altitude])
        positions.append([x, y, z])

    # tree to find nearest neighbors
    tree = KDTree(positions)

    for i, lat in enumerate(latrange):
        if i % (len(latrange) / 10) == 0:
            print(str(int(i / len(latrange) * 100)) + '%')
        for j, lon in enumerate(lonrange):
            x, y, z = gps.lla2ecef([lat, lon, altitude])
            distances, indexes = tree.query([x, y, z], n_nearest)
            min_travel_time = sys.float_info.max
            for distance, index in zip(distances, indexes):
                if stations[index].travel_time_min == 0:
                    continue
                travel_time = stations[index].travel_time_min + distance / 1000.0 / cycle_speed_kmh * 60.0
                if travel_time < min_travel_time:
                    min_travel_time = travel_time
            Z[i][j] = min_travel_time

    print('finished spatial interpolation')

    figure = plt.figure()
    ax = figure.add_subplot(111)
    levels = np.linspace(0, 160, num=n_contours)
    # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
    contours = ax.contour(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet)
    cbar = figure.colorbar(contours, format='%.1f')
    plt.savefig('./data/contour_example.png', dpi=150)
    contour_to_json(contours, filename)


if __name__ == "__main__":
    stations = Station.from_json('./data/stations.json')
    Station.travel_times_from_json(stations, './data/traveltimes_from_utrecht.json')

    # stations = []
    # stations.append(Station('Utrecht Centraal', 5.11027765274048, 52.0888900756836, 100))
    # stations.append(Station('Rotterdam Centraal', 4.46888875961304, 51.9249992370605, 500))
    # stations.append(Station('Leeuwarden', 5.79222202301025, 53.1958351135254, 1))
    # stations.append(Station('test', 5.6, 51.8, 1))

    for station in stations:
        print(station)
    create_contour_plot(stations, './data/contours.json')

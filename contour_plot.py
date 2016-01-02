import math
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import utilgeo
from scipy.interpolate import Rbf
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

    delta = 0.01
    NCONTOURS = 30

    delta_deg = 6
    lonmin = 3.0
    latmin = 50.5
    lonmax = lonmin + delta_deg
    latmax = latmin + delta_deg / 2
    cycle_speed_kmh = 18.0

    lonrange = np.arange(lonmin, lonmax, delta)
    latrange = np.arange(latmin, latmax, delta / 2.0)

    Z = np.zeros((int(lonrange.shape[0]), int(latrange.shape[0])))

    gps = utilgeo.GPS()
    alt = 0.0

    print('starting spatial interpolation')

    n_stations = len(stations)
    x_known = np.zeros(n_stations)
    y_known = np.zeros(n_stations)
    z_known = np.zeros(n_stations)
    values = np.zeros(n_stations)

    i = 0
    positions = []
    for station in stations:
        lon = station.lon
        lat = station.lat
        travel_time = station.travel_time_min
        x, y, z = gps.lla2ecef([lat, lon, alt])
        positions.append([x, y, z])
        x_known[i] = x
        y_known[i] = y
        z_known[i] = z
        values[i] = travel_time
        i += 1

    tree = KDTree(positions)
    print(tree.data)

    for i, lat in enumerate(latrange):
        if i % (len(latrange) / 10) == 0:
            print(str(int(i / len(latrange) * 100)) + '%')
        for j, lon in enumerate(lonrange):
            x, y, z = gps.lla2ecef([lat, lon, alt])
            distances, indexes = tree.query([x, y, z], 20)
            min_travel_time = sys.float_info.max
            for distance, index in zip(distances, indexes):
                if stations[index].travel_time_min == 0:
                    continue
                travel_time = stations[index].travel_time_min + distance / 1000.0 / cycle_speed_kmh * 60.0
                if travel_time < min_travel_time:
                    min_travel_time = travel_time
            Z[i][j] = min_travel_time

    print('finished spatial interpolation')
    print(Z)

    figure = plt.figure()
    levels = np.linspace(0, 170, num=NCONTOURS)
    # cs = plt.contour(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet, norm = LogNorm())
    # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
    contours = plt.contour(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet)
    plt.colorbar(contours, format='%.1f')
    plt.savefig('./data/contour_example.png', dpi=300)
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

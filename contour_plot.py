import math
import sys

from timeit import default_timer as timer
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue, Pool
import utilgeo
from scipy.spatial import KDTree
from scipy import ndimage

from station import Station
from contour_to_json import contour_to_json


class ContourData:
    def __init__(self):
        self.Z = None
        self.index_begin = 0


def create_contour_plot(stations, filename):
    start = timer()
    np.set_printoptions(3, threshold=100, suppress=True)  # .3f

    n_processes = 4

    delta = 0.01
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

    queue = Queue()
    processes = []
    for i in range(0, n_processes):
        begin = i * len(latrange)/n_processes
        end = (i+1)*len(latrange)/n_processes
        latrange_part = latrange[begin:end]
        process = Process(target=interpolate_travel_time, args=(queue, i, tree, gps, latrange_part, lonrange, altitude, n_nearest, cycle_speed_kmh))
        processes.append(process)

    for process in processes:
        process.start()

    # get from the queue and append the values
    for i in range(0, n_processes):
        data = queue.get()
        index_begin = data.index_begin
        begin = index_begin*len(latrange)/n_processes
        end = (index_begin+1)*len(latrange)/n_processes
        Z[0:][begin:end] = data.Z

    for process in processes:
        process.join()

    end = timer()
    print('finished spatial interpolation in ' + str(end - start) + ' [sec]')

    # zoomFactor = 1
    # Z = ndimage.zoom(Z, zoomFactor)
    # lonrange = ndimage.zoom(lonrange, zoomFactor)
    # latrange = ndimage.zoom(latrange, zoomFactor)

    figure = plt.figure()
    ax = figure.add_subplot(111)
    levels = np.linspace(0, 200, num=n_contours)
    # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
    contours = ax.contour(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet)
    cbar = figure.colorbar(contours, format='%.1f')
    plt.savefig('./data/contour_example.png', dpi=150)
    contour_to_json(contours, filename)


def interpolate_travel_time(q, position, kdtree, gps, latrange, lonrange, altitude, n_nearest, cycle_speed_kmh):
    print('interpolate_travel_time')
    Z = np.zeros((int(latrange.shape[0]), int(lonrange.shape[0])))
    for i, lat in enumerate(latrange):
        if i % (len(latrange) / 10) == 0:
            print(str(int(i / len(latrange) * 100)) + '%')

        for j, lon in enumerate(lonrange):
            x, y, z = gps.lla2ecef([lat, lon, altitude])
            distances, indexes = kdtree.query([x, y, z], n_nearest)
            min_travel_time = sys.float_info.max
            for distance, index in zip(distances, indexes):
                if stations[index].travel_time_min < 0.0:
                    continue
                travel_time = stations[index].travel_time_min + distance / 1000.0 / cycle_speed_kmh * 60.0
                if travel_time < min_travel_time:
                    min_travel_time = travel_time
            Z[i][j] = min_travel_time
    data = ContourData()
    data.index_begin = position
    data.Z = Z
    q.put(data)
    print('end interpolate_travel_time')
    return


if __name__ == "__main__":
    departure_station = 'utrecht'
    stations = Station.from_json('./data/stations.json')
    Station.travel_times_from_json(stations, './data/traveltimes_from_' + departure_station + '.json')

    # stations = []
    # stations.append(Station('Utrecht Centraal', 5.11027765274048, 52.0888900756836, 100))
    # stations.append(Station('Rotterdam Centraal', 4.46888875961304, 51.9249992370605, 500))
    # stations.append(Station('Leeuwarden', 5.79222202301025, 53.1958351135254, 1))
    # stations.append(Station('test', 5.6, 51.8, 1))

    for station in stations:
        print(station)
    create_contour_plot(stations, './data/contours_' + departure_station + '.json')

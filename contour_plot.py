import sys
import os.path
from timeit import default_timer as timer
from multiprocessing import Process, Queue

import numpy
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from scipy import ndimage

import utilgeo
from station import Station
from contour_to_json import contour_to_json


class ContourData:
    def __init__(self):
        self.Z = None
        self.index_begin = 0


class ContourPlotConfig(object):
    def __init__(self):
        self.stepsize_deg = 0.01
        self.n_processes = 4
        self.cycle_speed_kmh = 18.0
        self.n_nearest = 15
        self.lon_start = 3.0
        self.lat_start = 50.5
        self.delta_deg = 6
        self.lon_end = self.lon_start + self.delta_deg
        self.lat_end = self.lat_start + self.delta_deg / 2
        self.n_contours = 41
        self.min_angle_between_segments = 4


class TestConfig(ContourPlotConfig):
    def __init__(self):
        super().__init__()
        self.stepsize_deg = 0.005
        self.n_processes = 4
        self.lon_start = 4.8
        self.lat_start = 52.0
        self.delta_deg = 1.0
        self.lon_end = self.lon_start + self.delta_deg
        self.lat_end = self.lat_start + self.delta_deg / 2
        self.n_contours = 41
        self.min_angle_between_segments = 4


def create_contour_plot(stations, filename, config):
    start = timer()
    numpy.set_printoptions(3, threshold=100, suppress=True)  # .3f

    altitude = 0.0
    lonrange = numpy.arange(config.lon_start, config.lon_end, config.stepsize_deg)
    latrange = numpy.arange(config.lat_start, config.lat_end, config.stepsize_deg / 2.0)
    Z = numpy.zeros((int(lonrange.shape[0]), int(latrange.shape[0])))
    gps = utilgeo.GPS()

    positions = []
    for station in stations:
        x, y, z = gps.lla2ecef([station.lat, station.lon, altitude])
        positions.append([x, y, z])

    print('starting spatial interpolation')

    # tree to find nearest neighbors
    tree = KDTree(positions)

    queue = Queue()
    processes = []
    for i in range(0, config.n_processes):
        begin = i * len(latrange)/config.n_processes
        end = (i+1)*len(latrange)/config.n_processes
        latrange_part = latrange[begin:end]
        process = Process(target=interpolate_travel_time, args=(queue, i, tree, gps, latrange_part,
                                                                lonrange, altitude, config.n_nearest, config.cycle_speed_kmh))
        processes.append(process)

    for process in processes:
        process.start()

    # get from the queue and append the values
    for i in range(0, config.n_processes):
        data = queue.get()
        index_begin = data.index_begin
        begin = index_begin*len(latrange)/config.n_processes
        end = (index_begin+1)*len(latrange)/config.n_processes
        Z[0:][begin:end] = data.Z

    for process in processes:
        process.join()

    end = timer()
    print('finished spatial interpolation in ' + str(end - start) + ' [sec]')

    # zoomFactor = 2
    # Z = ndimage.zoom(Z, zoomFactor)
    # lonrange = ndimage.zoom(lonrange, zoomFactor)
    # latrange = ndimage.zoom(latrange, zoomFactor)

    figure = plt.figure()
    ax = figure.add_subplot(111)
    levels = numpy.linspace(0, 200, num=config.n_contours)
    # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
    contours = ax.contour(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet)
    cbar = figure.colorbar(contours, format='%.1f')
    plt.savefig('./data/contour_example.png', dpi=150)
    contour_to_json(contours, filename, config.min_angle_between_segments)


def interpolate_travel_time(q, position, kdtree, gps, latrange, lonrange, altitude, n_nearest, cycle_speed_kmh):
    # n_nearest: check N nearest stations as best start for cycle route
    print('interpolate_travel_time')
    Z = numpy.zeros((int(latrange.shape[0]), int(lonrange.shape[0])))
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


def test():
    departure_station_name = 'Utrecht Centraal'
    stations = Station.from_json('./data/stations.json')
    departure_station = Station.find_station(departure_station_name, stations)
    Station.travel_times_from_json(stations, './data/traveltimes_from_' + departure_station.id + '.json')
    filename = './data/contours_' + departure_station.id + '.json'
    default_config = ContourPlotConfig()
    test_config = TestConfig()
    default_config.cycle_speed_kmh = 18.0
    default_config.n_nearest = 30
    create_contour_plot(stations, filename, default_config)


if __name__ == "__main__":
    stations = Station.from_json('./data/stations.json')
    for station in stations:
        filename_traveltimes = './data/traveltimes_from_' + station.id + '.json'
        if os.path.exists(filename_traveltimes):
            Station.travel_times_from_json(stations, './data/traveltimes_from_' + station.id + '.json')
            filename = './data/contours_' + station.id + '.json'
            default_config = ContourPlotConfig()
            default_config.cycle_speed_kmh = 18.0
            default_config.n_nearest = 30
            create_contour_plot(stations, filename, default_config)
        else:
            print('Input file ' + filename_traveltimes + ' not found. Skipping station.')

    # stations = []
    # stations.append(Station('Utrecht Centraal', 5.11027765274048, 52.0888900756836, 100))
    # stations.append(Station('Rotterdam Centraal', 4.46888875961304, 51.9249992370605, 500))
    # stations.append(Station('Leeuwarden', 5.79222202301025, 53.1958351135254, 1))
    # stations.append(Station('test', 5.6, 51.8, 1))

import sys
import os
import json
import math

from timeit import default_timer as timer
from multiprocessing import Process, Queue

import numpy
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

import nsmaps.utilgeo
from nsmaps.station import Station
from nsmaps.logger import logger


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))

def length(v):
    return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


class ContourData(object):
    def __init__(self):
        self.Z = None
        self.index_begin = 0


class ContourPlotConfig(object):
    def __init__(self):
        self.stepsize_deg = 0.005
        self.n_processes = 4
        self.cycle_speed_kmh = 18.0
        self.n_nearest = 20
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


class Contour(object):
    def __init__(self, departure_station, stations, config, data_dir):
        self.departure_station = departure_station
        self.stations = stations
        self.config = config
        self.data_dir = data_dir

    def create_contour_data(self, filepath):
        filepath_traveltimes = os.path.join(self.data_dir, 'traveltimes_from_' + self.departure_station.id + '.json')
        if os.path.exists(filepath_traveltimes):
            Station.travel_times_from_json(self.stations, filepath_traveltimes)
            if os.path.exists(filepath):
                logger.warning('Output file ' + filepath + ' already exists. Will not override.')
                return
        else:
            logger.warning('Input file ' + filepath_traveltimes + ' not found. Skipping station.')

        start = timer()
        numpy.set_printoptions(3, threshold=100, suppress=True)  # .3f

        altitude = 0.0
        lonrange = numpy.arange(self.config.lon_start, self.config.lon_end, self.config.stepsize_deg)
        latrange = numpy.arange(self.config.lat_start, self.config.lat_end, self.config.stepsize_deg / 2.0)
        Z = numpy.zeros((int(lonrange.shape[0]), int(latrange.shape[0])))
        gps = nsmaps.utilgeo.GPS()

        positions = []
        for station in self.stations:
            x, y, z = gps.lla2ecef([station.lat, station.lon, altitude])
            positions.append([x, y, z])

        logger.info('starting spatial interpolation')

        # tree to find nearest neighbors
        tree = KDTree(positions)

        queue = Queue()
        processes = []
        for i in range(0, self.config.n_processes):
            begin = i * len(latrange)/self.config.n_processes
            end = (i+1)*len(latrange)/self.config.n_processes
            latrange_part = latrange[begin:end]
            process = Process(target=self.interpolate_travel_time, args=(queue, i, self.stations, tree, gps, latrange_part,
                                                                         lonrange, altitude, self.config.n_nearest, self.config.cycle_speed_kmh))
            processes.append(process)

        for process in processes:
            process.start()

        # get from the queue and append the values
        for i in range(0, self.config.n_processes):
            data = queue.get()
            index_begin = data.index_begin
            begin = index_begin*len(latrange)/self.config.n_processes
            end = (index_begin+1)*len(latrange)/self.config.n_processes
            Z[0:][begin:end] = data.Z

        for process in processes:
            process.join()

        end = timer()
        logger.info('finished spatial interpolation in ' + str(end - start) + ' [sec]')

        figure = plt.figure()
        ax = figure.add_subplot(111)
        levels = numpy.linspace(0, 200, num=self.config.n_contours)
        # contours = plt.contourf(lonrange, latrange, Z, levels=levels, cmap=plt.cm.plasma)
        contours = ax.contour(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet)
        # cbar = figure.colorbar(contours, format='%.1f')
        # plt.savefig('contour_example.png', dpi=150)
        ndigits = len(str(int(1.0/self.config.stepsize_deg)))+1
        contour_to_json(contours, filepath, levels, self.config.min_angle_between_segments, ndigits)

    @staticmethod
    def interpolate_travel_time(q, position, stations, kdtree, gps, latrange, lonrange, altitude, n_nearest, cycle_speed_kmh):
        # n_nearest: check N nearest stations as best start for cycle route
        logger.info('interpolate_travel_time')
        Z = numpy.zeros((int(latrange.shape[0]), int(lonrange.shape[0])))
        for i, lat in enumerate(latrange):
            if i % (len(latrange) / 10) == 0:
                logger.debug(str(int(i / len(latrange) * 100)) + '%')

            for j, lon in enumerate(lonrange):
                x, y, z = gps.lla2ecef([lat, lon, altitude])
                distances, indexes = kdtree.query([x, y, z], n_nearest)
                min_travel_time = sys.float_info.max
                for distance, index in zip(distances, indexes):
                    if stations[index].travel_time_min is None:
                        continue
                    travel_time = stations[index].travel_time_min + distance / 1000.0 / cycle_speed_kmh * 60.0
                    if travel_time < min_travel_time:
                        min_travel_time = travel_time
                Z[i][j] = min_travel_time
        data = ContourData()
        data.index_begin = position
        data.Z = Z
        q.put(data)
        logger.info('end interpolate_travel_time')
        return


def contour_to_json(contour, filename, contour_labels, min_angle=2, ndigits=5):
    # min_angle: only create a new line segment if the angle is larger than this angle, to compress output
    collections = contour.collections
    with open(filename, 'w') as fileout:
        total_points = 0
        total_points_original = 0
        collections_json = []
        contour_index = 0
        assert len(contour_labels) == len(collections)
        for collection in collections:
            paths = collection.get_paths()
            color = collection.get_edgecolor()
            paths_json = []
            for path in paths:
                v = path.vertices
                x = []
                y = []
                v1 = v[1] - v[0]
                x.append(round(v[0][0], ndigits))
                y.append(round(v[0][1], ndigits))
                for i in range(1, len(v) - 2):
                    v2 = v[i + 1] - v[i - 1]
                    diff_angle = math.fabs(angle(v1, v2) * 180.0 / math.pi)
                    if diff_angle > min_angle:
                        x.append(round(v[i][0], ndigits))
                        y.append(round(v[i][1], ndigits))
                        v1 = v[i] - v[i - 1]
                x.append(round(v[-1][0], ndigits))
                y.append(round(v[-1][1], ndigits))
                total_points += len(x)
                total_points_original += len(v)

                # x = v[:,0].tolist()
                # y = v[:,1].tolist()
                paths_json.append({u"x": x, u"y": y, u"linecolor": color[0].tolist(), u"label": str(int(contour_labels[contour_index])) + ' min'})
            contour_index += 1

            if paths_json:
                collections_json.append({u"paths": paths_json})
        collections_json_f = {}
        collections_json_f[u"contours"] = collections_json
        fileout.write(json.dumps(collections_json_f, sort_keys=True))  # indent=2)
        logger.info('total points: ' + str(total_points) + ', compression: ' + str(int((1.0 - total_points / total_points_original) * 100)) + '%')

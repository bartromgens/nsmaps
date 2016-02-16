import sys
import os
import shutil
import unittest
import hashlib

import numpy
import matplotlib as mpl
mpl.use('Agg')  # create plots without running X-server
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import ns_api

import nsmaps
from nsmaps.local_settings import USERNAME, APIKEY


class TestNSApi(unittest.TestCase):
    """ Test case of basic communication with the NS API via the nsapi package. """

    def setUp(self):
        self.nsapi = ns_api.NSAPI(USERNAME, APIKEY)

    def test_get_station_info(self):
        stations = self.nsapi.get_stations()
        self.assertEqual(len(stations), 620)

    # def test_trip_stop_without(self):
    #     """ Tests https://github.com/aquatix/ns-api/issues/14 """
    #     timestamp = "04-02-2016 08:00"
    #     start = "Rotterdam Blaak"
    #     via = ""
    #     destination = "Amsterdam Centraal"
    #     trips = self.nsapi.get_trips(timestamp, start, via, destination)
    #
    # def test_no_trips_found(self):
    #     """ Tests https://github.com/aquatix/ns-api/issues/12 """
    #     timestamp = "12-01-2016 08:00"
    #     start = "Utrecht Centraal"
    #     via = ""
    #     destination = "Amsterdam Van der Madeweg"
    #     trips = self.nsapi.get_trips(timestamp, start, via, destination)
    #     self.assertEqual(trips, None)


class TestStationData(unittest.TestCase):
    """ Test case for nsmaps station data """

    def test_update_stations(self):
        fileout = 'test_stations.json'
        data_dir = '.'
        stations = nsmaps.station.Stations(data_dir)
        stations.update_station_data(fileout)
        for station in stations:
            str(station)
        self.assertTrue(os.path.exists(fileout))
        os.remove(fileout)


class TestStations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testdir = './test/'
        os.mkdir(cls.testdir)
        cls.stations = nsmaps.station.Stations(cls.testdir, test=True)
        utrecht = cls.stations.find_station("Utrecht Centraal")
        if os.path.exists(utrecht.get_travel_time_filepath()):
            os.remove(utrecht.get_travel_time_filepath())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.testdir)

    def test_create_stations(self):
        stations = nsmaps.station.Stations('.')
        self.assertTrue(len(stations.stations) > 0)

    def test_iterate_stations(self):
        for station in self.stations:
            station.has_travel_time_data()
            str(station)

    def test_find_station(self):
        for station in self.stations:
            station_found = self.stations.find_station(station.get_name())
            self.assertTrue(station_found)
            self.assertEqual(station.get_code(), station_found.get_code())

    def test_get_station_for_types(self):
        types = (
            nsmaps.station.StationType.intercitystation,
            nsmaps.station.StationType.sneltreinstation,
            nsmaps.station.StationType.stoptreinstation,
        )
        stations_of_type = self.stations.get_stations_for_types(types)
        self.assertTrue(stations_of_type)

    def test_create_travel_times_data(self):
        utrecht = self.stations.find_station("Utrecht Centraal")
        self.assertTrue(utrecht)
        self.stations.create_traveltimes_data([utrecht])
        self.assertTrue(os.path.exists(utrecht.get_travel_time_filepath()))
        self.assertTrue(utrecht.has_travel_time_data())
        self.stations.travel_times_from_json(utrecht.get_travel_time_filepath())
        for station in self.stations:
            self.assertNotEqual(station.travel_time_min, None)
            if station.get_code() != "UT":
                self.assertTrue(station.travel_time_min > 0)
        os.remove(utrecht.get_travel_time_filepath())
        self.assertFalse(utrecht.has_travel_time_data())


class TestContourToJSON(unittest.TestCase):
    """ Test case for writing a contour to JSON. """
    filename_out = 'test_contour.json'
    checksum = '39d2ff2f5cbc9a768e816109f41b3288'

    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.filename_out):
            os.remove(cls.filename_out)  # remove file from any previous tests
        # taken from http://matplotlib.org/examples/pylab_examples/contour_demo.html
        figure = plt.figure()
        ax = figure.add_subplot(111)
        delta = 0.025
        x = numpy.arange(-3.0, 3.0, delta)
        y = numpy.arange(-2.0, 2.0, delta)
        X, Y = numpy.meshgrid(x, y)
        Z1 = mlab.bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
        Z2 = mlab.bivariate_normal(X, Y, 1.5, 0.5, 1, 1)
        Z = 10.0 * (Z2 - Z1)
        cls.levels = numpy.linspace(0, 100, num=10)
        cls.contour_plot = ax.contour(X, Y, Z, levels=cls.levels, cmap=plt.cm.jet)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.filename_out):
            os.remove(cls.filename_out)  # remove file from any previous tests

    def test_create_json(self):
        min_angle = 10
        ndigits = 5
        nsmaps.contourmap.contour_to_json(self.contour_plot, self.filename_out, self.levels, min_angle, ndigits)
        self.assertTrue(os.path.exists(self.filename_out))
        with open(self.filename_out, 'rb') as jsonfile:
            checksum = hashlib.md5(jsonfile.read()).hexdigest()
            self.assertEqual(checksum, self.checksum)


if __name__ == '__main__':
    unittest.main()

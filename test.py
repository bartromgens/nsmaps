import sys
import os
import unittest
import hashlib

import numpy
import matplotlib as mpl
mpl.use('Agg')  # create plots without running X-server
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import ns_api

from local_settings import USERNAME, APIKEY
from contour_to_json import contour_to_json
import contour_plot
from logger import logger


class TestNSApi(unittest.TestCase):
    """ Test case of basic communication with the NS API via the nsapi package. """

    def setUp(self):
        self.nsapi = ns_api.NSAPI(USERNAME, APIKEY)

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


class TestContourToJSON(unittest.TestCase):
    """ Test case for writing a contour to JSON. """
    filename_out = 'test_contour.json'
    checksum = '39d2ff2f5cbc9a768e816109f41b3288'

    @classmethod
    def setUpClass(cls, ):
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
        # difference of Gaussians
        Z = 10.0 * (Z2 - Z1)
        cls.levels = numpy.linspace(0, 100, num=10)
        cls.contour_plot = ax.contour(X, Y, Z, levels=cls.levels, cmap=plt.cm.jet)

    def test_create_json(self):
        contour_to_json(self.contour_plot, self.filename_out, self.levels, 10)
        self.assertTrue(os.path.exists(self.filename_out))
        with open(self.filename_out, 'rb') as jsonfile:
            checksum = hashlib.md5(jsonfile.read()).hexdigest()
            self.assertEqual(checksum, self.checksum)


if __name__ == '__main__':
    unittest.main()
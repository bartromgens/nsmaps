import unittest

import numpy
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

import ns_api

from local_settings import USERNAME, APIKEY


class TestNSApi(unittest.TestCase):

    def setUp(self):
        self.nsapi = ns_api.NSAPI(USERNAME, APIKEY)

    def testTripStopWithoutTime(self):
        timestamp = "04-02-2016 08:00"
        start = "Rotterdam Blaak"
        via = ""
        destination = "Amsterdam Centraal"
        trips = self.nsapi.get_trips(timestamp, start, via, destination)


if __name__ == '__main__':
    unittest.main()

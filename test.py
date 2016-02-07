import unittest

import ns_api

from local_settings import USERNAME, APIKEY


class TestNSApi(unittest.TestCase):
    """ Test case of basic communication with the NS API via the nsapi package. """

    def setUp(self):
        self.nsapi = ns_api.NSAPI(USERNAME, APIKEY)

    def test_trip_stop_without(self):
        """ Tests https://github.com/aquatix/ns-api/issues/14 """
        timestamp = "04-02-2016 08:00"
        start = "Rotterdam Blaak"
        via = ""
        destination = "Amsterdam Centraal"
        trips = self.nsapi.get_trips(timestamp, start, via, destination)

    def test_no_trips_found(self):
        """ Tests https://github.com/aquatix/ns-api/issues/12 """
        timestamp = "12-01-2016 08:00"
        start = "Utrecht Centraal"
        via = ""
        destination = "Amsterdam Van der Madeweg"
        trips = self.nsapi.get_trips(timestamp, start, via, destination)
        self.assertEqual(trips, None)


if __name__ == '__main__':
    unittest.main()

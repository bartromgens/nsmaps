import json
import os.path

from ns_api import Station, NSAPI

from local_settings import USERNAME, APIKEY
from logger import logger


def update_station_data():
    logger.debug("start")
    nsapi = NSAPI(USERNAME, APIKEY)
    stations = nsapi.get_stations()

    data = {'stations': []}
    for station in stations:
        # if station.country == "NL" and "Utrecht" in station.names['long']:
        if station.country == "NL":
            travel_times_available = os.path.exists('./data/traveltimes_from_' + station.code + '.json')
            contour_avaiable = os.path.exists('./data/contours_' + station.code + '.json')
            data['stations'].append({'names': station.names,
                                     'id': station.code,
                                     'lon': station.lon,
                                     'lat': station.lat,
                                     'type': station.stationtype,
                                     'travel_times_available': travel_times_available and contour_avaiable})

    json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    with open('./data/stations.json', 'w') as fileout:
        fileout.write(json_data)


if __name__ == "__main__":
    update_station_data()

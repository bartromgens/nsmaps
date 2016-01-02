import math
import numpy as np
import matplotlib.pyplot as plt
import utilgeo
from scipy.interpolate import Rbf

from contour_to_json import contour_to_json


def create_contour_plot(cities, filename):
    np.set_printoptions(3, threshold=100, suppress=True)  # .3f

    delta = 0.05
    NCONTOURS = 50

    delta_deg = 1
    lonmin = -6.0
    latmin = 52.0
    lonmax = lonmin + delta_deg
    latmax = latmin + delta_deg / 2

    lonrange = np.arange(lonmin, lonmax, delta)
    latrange = np.arange(latmin, latmax, delta / 2.0)

    print(str(len(lonrange)) + 'x' + str(len(latrange)) + ' = ' + str(len(latrange) * len(lonrange)) + ' interpolations')

    Z = np.zeros((int(lonrange.shape[0]), int(latrange.shape[0])))

    gps = utilgeo.GPS()
    alt = 0.0

    print('starting spatial interpolation')

    n_cities = len(cities)
    x_known = np.zeros(n_cities)
    y_known = np.zeros(n_cities)
    z_known = np.zeros(n_cities)
    values = np.zeros(n_cities)

    i = 0
    for city in cities:
        lat = city['lat']
        lon = city['lon']
        value = city['value']
        x, y, z = gps.lla2ecef([lat, lon, alt])
        x_known[i] = x
        y_known[i] = y
        z_known[i] = z
        values[i] = value
        i += 1

    rbfi = Rbf(x_known, y_known, z_known, values, function='linear')

    for i, lat in enumerate(latrange):
        if i % (len(latrange) / 10) == 0:
            print(str(int(i / len(latrange) * 100)) + '%')
        for j, lon in enumerate(lonrange):
            x, y, z = gps.lla2ecef([lat, lon, alt])
            Z[i][j] = rbfi(x, y, z)

    print('finished spatial interpolation')

    print(Z)

    figure = plt.figure()
    levels = np.linspace(0, 10, num=NCONTOURS)
    # cs = plt.contour(lonrange, latrange, Z, levels=levels, cmap=plt.cm.jet, norm = LogNorm())
    contours = plt.contour(lonrange, latrange, Z, levels=levels)
    contour_to_json(contours, './data/contour.json')
    plt.colorbar(contours, format='%.1f')
    plt.savefig('./data/contour_example.png')


if __name__ == "__main__":
    cities = []
    cities.append({'lat': 52.1, 'lon': -5.53, 'value': 5.0})
    cities.append({'lat': 52.2, 'lon': -5.8, 'value': 5.0})
    cities.append({'lat': 52.4, 'lon': -5.13, 'value': 5.0})
    create_contour_plot(cities, 'contour.json')

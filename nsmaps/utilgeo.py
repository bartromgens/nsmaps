from math import sqrt, pi, sin, cos, log, atan, atan2


def deg2rad(deg):
    """Converts degrees to radians"""
    return deg * pi / 180


def rad2deg(rad):
    """Converts radians to degrees"""
    return rad * 180 / pi
  

class WGS84:
    """General parameters defined by the WGS84 system"""
    #Semimajor axis length (m)
    a = 6378137.0
    #Semiminor axis length (m)
    b = 6356752.3142
    #Ellipsoid flatness (unitless)
    f = (a - b) / a
    #Eccentricity (unitless)
    e = sqrt(f * (2 - f))
    #Speed of light (m/s)
    c = 299792458.
    #Relativistic constant
    F = -4.442807633e-10
    #Earth's universal gravitational constant
    mu = 3.986005e14
    #Earth rotation rate (rad/s)
    omega_ie = 7.2921151467e-5

    def g0(self, L):
        """acceleration due to gravity at the elipsoid surface at latitude L"""
        return 9.7803267715 * (1 + 0.001931851353 * sin(L)**2) / \
                        sqrt(1 - 0.0066943800229 * sin(L)**2)
                      

class GPS:
    """Working class for GPS module"""
    wgs84 = WGS84()
    fGPS = 1023
    fL1 = fGPS * 1.54e6
    fL2 = fGPS * 1.2e6
    
    def lla2ecef(self, lla):
        """Convert lat, lon, alt to Earth-centered, Earth-fixed coordinates.
Input: lla - (lat, lon, alt) in (decimal degrees, decimal degees, m)
Output: ecef - (x, y, z) in (m, m, m)
"""
        #Decompose the input
        lat = deg2rad(lla[0])
        lon = deg2rad(lla[1])
        alt = lla[2]
        #Calculate length of the normal to the ellipsoid
        N = self.wgs84.a / sqrt(1 - (self.wgs84.e * sin(lat))**2)
        #Calculate ecef coordinates
        x = (N + alt) * cos(lat) * cos(lon)
        y = (N + alt) * cos(lat) * sin(lon)
        z = (N * (1 - self.wgs84.e**2) + alt) * sin(lat)
        #Return the ecef coordinates
        return (x, y, z)

    def ecef2lla(self, ecef, tolerance=1e-9):
        """Convert Earth-centered, Earth-fixed coordinates to lat, lon, alt.
Input: ecef - (x, y, z) in (m, m, m)
Output: lla - (lat, lon, alt) in (decimal degrees, decimal degrees, m)
"""
        #Decompose the input
        x = ecef[0]
        y = ecef[1]
        z = ecef[2]
        #Calculate lon
        lon = atan2(y, x)
        #Initialize the variables to calculate lat and alt
        alt = 0
        N = self.wgs84.a
        p = sqrt(x**2 + y**2)
        lat = 0
        previousLat = 90
        #Iterate until tolerance is reached
        while abs(lat - previousLat) >= tolerance:
            previousLat = lat
            sinLat = z / (N * (1 - self.wgs84.e**2) + alt)
            lat = atan((z + self.wgs84.e**2 * N * sinLat) / p)
            N = self.wgs84.a / sqrt(1 - (self.wgs84.e * sinLat)**2)
            alt = p / cos(lat) - N
        #Return the lla coordinates
        return (rad2deg(lat), rad2deg(lon), alt)

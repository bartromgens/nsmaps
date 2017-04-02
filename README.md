## nsmaps

[![Build Status](https://travis-ci.org/bartromgens/nsmaps.svg?branch=master)](https://travis-ci.org/bartromgens/nsmaps)
[![Coverage Status](https://coveralls.io/repos/github/bartromgens/nsmaps/badge.svg?branch=master)](https://coveralls.io/github/bartromgens/nsmaps?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/bartromgens/nsmaps/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/bartromgens/nsmaps/?branch=master)
[![Dependency Status](https://gemnasium.com/bartromgens/nsmaps.svg)](https://gemnasium.com/bartromgens/nsmaps)  
Interactive contour maps visualising Dutch railways (NS) traveltime information. 

nsmaps uses [nsapi](https://github.com/aquatix/ns-api) to get Dutch railways travel information. 
[matplotlib](https://github.com/matplotlib/matplotlib) is used to create contour plots, which are converted to geojson lines with [geojsoncontour](https://github.com/bartromgens/geojsoncontour). 
The geojson contours are drawn on an interactive [OpenLayers 3](https://github.com/openlayers/ol3) map where [geojson-vt](https://github.com/mapbox/geojson-vt) is used to create vector tiles.  

Requires Python 3.4+.

### Demo

[nsmaps.romgens.com](http://nsmaps.romgens.com)

### Maps

#### Contour travel times

Color contours showing travel times from station A to any location in the Netherlands using a bicycle for the last leg of the trip. 

#### NS API key 

You need to set an API username and key in `local_settings.py`. 
Request one [here](http://www.ns.nl/en/travel-information/ns-api).
Please note that the NS offers a limited number of requests per day. 

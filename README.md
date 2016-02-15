## nsmaps

[![Build Status](https://travis-ci.org/bartromgens/nsmaps.svg?branch=master)](https://travis-ci.org/bartromgens/nsmaps)
[![Coverage Status](https://coveralls.io/repos/github/bartromgens/nsmaps/badge.svg?branch=master)](https://coveralls.io/github/bartromgens/nsmaps?branch=master)
[![Dependency Status](https://gemnasium.com/bartromgens/nsmaps.svg)](https://gemnasium.com/bartromgens/nsmaps)  
Generate maps visualising Dutch railways (NS) travel information. 

Uses [nsapi](https://github.com/aquatix/ns-api) to get the data, and [OpenLayers 3](https://github.com/openlayers/ol3) to create the maps. 

Python 3.4+

### Demo

[nsmaps.romgens.com](http://nsmaps.romgens.com)

### Maps

#### Contour travel times

Color contours showing travel times from station A to any location in the Netherlands using a bicycle for the last leg of the trip. 

#### NS API key 

You need to set an API username and key in `local_settings.py`. 
You can request a [here](http://www.ns.nl/en/travel-information/ns-api).

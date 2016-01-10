## NS-Maps

Generate maps visualising Dutch railways (NS) travel information. 

Uses [nsapi](https://github.com/aquatix/ns-api) to get the data, and [OpenLayers 3](https://github.com/openlayers/ol3) to create the maps. 

Note: This is a work in progess!

### Maps

#### Contour travel times

Color contours showing travel times from station A to any location in the Netherlands using a bicycle for the last leg of the trip. 

![Contour travel times demo. Overview.](https://github.com/bartromgens/ns-maps/tree/master/images/demo/contour_travel_times_utrecht_overview.jpg)

![Contour travel times demo. Detailed view.](https://github.com/bartromgens/ns-maps/tree/master/images/demo/contour_travel_times_utrecht_detail.jpg)

#### NS API key 

You need to set an API username and key in `local_settings.py`. 
You can request a [here](http://www.ns.nl/en/travel-information/ns-api).

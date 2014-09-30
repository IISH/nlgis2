#!/usr/bin/python

import urllib2
import simplejson
import json
import sys

# Example of polygon
#co1 = {"type": "Polygon", "coordinates": [
#    [(-102.05, 41.0),
#     (-102.05, 37.0),
#     (-109.05, 37.0),
#     (-109.05, 41.0)]]}

year = None
code = None
if sys.argv[1]:
    code = sys.argv[1]
if len(sys.argv) > 2:
    year = sys.argv[2]

try:
     code
except NameError:
     code = 119949
try:
     year
except NameError:
     year = str(1812)

amscode= "gemeenten." + str(code)
jsondataurl = "http://node-128.dev.socialhistoryservices.org/api/maps?year=" + year + "&format=geojson"

req = urllib2.Request(jsondataurl)
opener = urllib2.build_opener()
f = opener.open(req)
datapolygons = simplejson.load(f)

def coordinates(polygons, amscode):
    for key in polygons:
        if key == 'features':
	    data = polygons[key]
	    for key in data:
		response = json.dumps(key)
		dict = json.loads(response)
		for key in dict:
		    if dict[key] == amscode:
		        co = dict['geometry']

    return co['coordinates']

geometry = coordinates(datapolygons, amscode)
print geometry
exit(0)
lon, lat = zip(*co['coordinates'][0])
from pyproj import Proj
pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")

x, y = pa(lon, lat)
cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
from shapely.geometry import shape
size = shape(cop).area  
print size

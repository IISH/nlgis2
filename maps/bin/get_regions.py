#!/usr/bin/python

import urllib2
import simplejson
import json
import sys
from shapely.geometry import shape, Polygon, MultiPolygon
#from shapely.geometry.multipolygon import shape

# Example of polygon
co1 = {"type": "Polygon", "coordinates": [
    [(-102.05, 41.0),
     (-102.05, 37.0),
     (-109.05, 37.0),
     (-109.05, 41.0)]]}

year = None
code = None
if sys.argv[1]:
    code = sys.argv[1]
if len(sys.argv) > 2:
    year = sys.argv[2]

try:
     code
except NameError:
     code = 10426
try:
     year
except NameError:
     year = str(1812)

amscode= str(code)
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
		    #print key['properties']
		    if key == 'properties':
			maincode = str(dict[key]['amsterdamcode'])
			if maincode == amscode:
		             co = dict['geometry']
    return co 

geometry = coordinates(datapolygons, amscode)
#geometry = co1
size = shape(geometry).area / 27878400
print size;
print shape(geometry).type;

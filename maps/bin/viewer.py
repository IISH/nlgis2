
# coding: utf-8

# In[1]:

#!/usr/bin/python

import urllib2
import simplejson
import json
import sys
from shapely.geometry import shape, Polygon, MultiPolygon
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pylab import *

# Example of polygon
co1 = {"type": "Polygon", "coordinates": [
    [(-102.05, 41.0),
     (-102.05, 37.0),
     (-109.05, 37.0),
     (-109.05, 41.0)]]}

varyear = None
varcode = None
if sys.argv[1]:
    varcode = sys.argv[1]
if len(sys.argv) > 2:
    varyear = sys.argv[2]
    


# In[5]:

# Default
debug = 0
varcode = 10426
varyear = 1997
varname = "Amsterdam"
apiurl = "http://node-128.dev.socialhistoryservices.org/api/maps"

def getmap(apiurl, code, year, cityname):
    amscode = str(code)
    if cityname:
        amscode = ''
    jsondataurl = apiurl + "?year=" + str(year) + "&format=geojson"
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    datapolygons = simplejson.load(f)

    def coordinates(polygons, amscode, cityname):
        for key in polygons:
            if key == 'features':
                data = polygons[key]
                for key in data:
                    response = json.dumps(key)
                    dict = json.loads(response)
                    for key in dict:                    
                        if key == 'properties':
                            maincode = str(dict[key]['amsterdamcode'])
                            mainname = dict[key]['name']
                            if maincode == amscode:
                                 co = dict['geometry']['coordinates']
                            if mainname.encode('utf-8') == cityname:
                                 co = dict['geometry']['coordinates']
                            
        return co

    coords = coordinates(datapolygons, amscode, cityname)
    x = [i for i,j in coords[0][0]]
    y = [j for i,j in coords[0][0]]

    return (x,y)

colors = ['red', 'green', 'orange', 'brown', 'purple']
(x,y) = getmap(apiurl, varcode, varyear, varname)
fig = plt.figure() 
ax = fig.gca() 
ax.plot(x,y)
ax.axis('scaled')
fig.savefig('myplot.png')
plt.show()

#from pyproj import Proj
#pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
#lon, lat = zip(x[0],y[0])
cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
#x, y = pa(lon, lat)
debug = 1
if debug:
    print cop                                          
#shape = shape(cop)
#print shape.type
#print shape.area



# In[ ]:




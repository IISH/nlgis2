#!/usr/bin/python

# Perfect use case to get boundaries of the city in time
# (C) Vyacheslav Tykhonov
# International Institute of Social History
# https://iisg.amsterdam

#get_ipython().magic(u'matplotlib inline')
import os
os.environ['MPLCONFIGDIR'] = "/tmp"
import matplotlib
matplotlib.use("Agg")
import urllib2
import simplejson
import json
import sys
from shapely.geometry import shape, Polygon, MultiPolygon
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
from collections import defaultdict
from random import randint

varyear = None
varcode = None
savefile = None
varcode = 10426
max = 0
x = {}
y = {}

if sys.argv[1]:
    varcode = sys.argv[1]
if len(sys.argv) >= 2:
    varyear = sys.argv[2]
    if len(sys.argv) > 2:
        savefile = sys.argv[3]

#varyear = 1812
#savefile = "lastmap.png"
# In[ ]:


# In[2]:

# Default
debug = 0
varname = "Utrecht"
apiurl = "http://node-128.dev.socialhistoryservices.org/api/maps"
colors = ['red', 'green', 'orange', 'brown', 'purple', 'blue', 'cyan']
#colors = ['#334433', '#6699aa', '#88aaaa', '#aacccc', '#447799']
#colors = ['#bbaa66','#ffaa55','#ffcc77','#eecc77','#bbcc99']

def drawmap(x,y):
    fig, ax = subplots(figsize=(5,5))
    ax = fig.gca()
    ax.plot(x,y)
    ax.axis('scaled')
    if savefile:
        fig.savefig(savefile + '.png')
    plt.show()
    return

def coordinates(polygons, amscode, cityname):
    fullmappolygon = defaultdict(list)
    z = 1
    co = {}
    if cityname:
        amscode = ''
    for key in polygons:
        if key == 'features':
            data = polygons[key]

            for key in data:
                response = json.dumps(key)
                dict = json.loads(response)
                for key in dict:
                   if key == 'properties':
                      maincode = str(dict[key]['amsterdamcode'])
                      intcode = dict[key]['amsterdamcode']
                      mainname = dict[key]['name']
                      #fullmappolygon[intcode] = dict['geometry']['coordinates']
                      x = [i for i,j in dict['geometry']['coordinates'][0][0]]
                      y = [j for i,j in dict['geometry']['coordinates'][0][0]]

                      fullmappolygon[intcode].append(x)
                      fullmappolygon[intcode].append(y)
                      z = z + 1
                      if z == 0:
                            print intcode
                            print fullmappolygon[intcode][0]
                            print fullmappolygon[intcode][1]

                      if maincode == amscode:
                         co = dict['geometry']['coordinates']
                      if mainname.encode('utf-8') == cityname:
                         co = dict['geometry']['coordinates']

    return (co, fullmappolygon)

def load_api_map(apiurl, code, year):
    amscode = str(code)
    jsondataurl = apiurl + "?year=" + str(year) + "&format=geojson"
    if debug:
        print jsondataurl

    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    datapolygons = simplejson.load(f)
    return datapolygons

def getcoords(datapolygons, amscode, cityname):
    (coords, fullmap) = coordinates(datapolygons, amscode, cityname)
    x = []
    y = []
        #x = [i for i,j in coords[0][0]]
        #y = [j for i,j in coords[0][0]]
    
    return fullmap

fullmappoly = load_api_map(apiurl, varcode, varyear)
varcity = ''
(map) = getcoords(fullmappoly, varcode, varcity)



# In[3]:

count = 0
#fig, ax = subplots(figsize=(8,8), dpi=300)
fig = plt.figure(figsize=(14,10),dpi=100,frameon=False)
ax = fig.gca()
#ax.axes.get_xaxis().set_visible(False)
#ax.axes.get_yaxis().set_visible(False)
ax.set_axis_off()

def plot_polygon(ax, poly, color='red'):
    a = np.asarray(poly.exterior)
    ax.add_patch(Polygon(a, facecolor=color, alpha=0.3))
    ax.plot(a[:, 0], a[:, 1], color='black')

for code in map:
    x = map[code][0]
    y = map[code][1]
    thiscolor = 'black'

    if code == varcode:
        if debug:
            print varcode
        thiscolor = 'green'
        ax.add_patch(Polygon(zip(x,y), facecolor=thiscolor, alpha=0.3))
    else:
        colorID = randint(0,4)
        ax.add_patch(Polygon(zip(x,y), facecolor=colors[colorID], alpha=0.3))

    ax.plot(x, y, color=thiscolor)
    count = count + 1
    if count == 0:
        coords = zip(x,y)
        print coords

ax.axis('scaled')
if savefile:
    filename = savefile
    fig.savefig(filename)
plt.show()


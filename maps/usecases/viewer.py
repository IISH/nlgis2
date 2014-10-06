
# coding: utf-8

# In[1]:

#!/usr/bin/python

# Perfect use case to get boundaries of the city in time
# (C) Vyacheslav Tykhonov vty@iisg.nl
# International Institute of Social History 
# http://socialhistory.org

get_ipython().magic(u'matplotlib inline')
import urllib2
import simplejson
import json
import sys
from shapely.geometry import shape, Polygon, MultiPolygon
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pylab import *
from collections import defaultdict

varyear = None
varcode = None
savefile = None
if sys.argv[1]:
    varcode = sys.argv[1]
if len(sys.argv) > 2:
    varyear = sys.argv[2]
    


# In[ ]:

# Default
debug = 0
varcode = 10426
varyear = 1997
varname = "Utrecht"
apiurl = "http://node-128.dev.socialhistoryservices.org/api/maps"
colors = ['red', 'green', 'orange', 'brown', 'purple', 'blue', 'cyan']

def drawmap(x,y):
    fig, ax = subplots(figsize=(12,12))
    ax = fig.gca() 
    ax.plot(x,y)
    ax.axis('scaled')
    if savefile:
        fig.savefig('map.png')
    plt.show()
    return

def coordinates(polygons, amscode, cityname):
    fullmappolygon = defaultdict(list)
    z = 0
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
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    datapolygons = simplejson.load(f)
    return datapolygons
    
def getcoords(datapolygons, amscode, cityname):
    (coords, fullmap) = coordinates(datapolygons, amscode, cityname)
    x = [i for i,j in coords[0][0]]
    y = [j for i,j in coords[0][0]]

    return (x,y,fullmap)


# Let's draw boundaries for Utrecht in 1997 first

# In[ ]:

varyear = 1997
fullmappoly = load_api_map(apiurl, varcode, varyear)
(x,y,map) = getcoords(fullmappoly, varcode, varname)
drawmap(x,y)


# Boundaries of Utrecht in 1948

# In[ ]:

varyear = 1948
fullmappoly = load_api_map(apiurl, varcode, varyear)
(x,y,map) = getcoords(fullmappoly, varcode, varname)
drawmap(x,y)


# And finally boundaries of Utrecht more than 200 years ago

# In[ ]:

varyear = 1812
fullmappoly = load_api_map(apiurl, varcode, varyear)
(x,y,map) = getcoords(fullmappoly, varcode, varname)
drawmap(x,y)


# In[ ]:

# 'red', 'green', 'orange', 'brown', 'purple'
cities = ["Utrecht" ,"Amsterdam", "Rotterdam", "Den Haag", "Purmerend", "Apeldoorn", "Almere", "Alkmaar"]
max = 0
varyear = 1997
fullmappoly = load_api_map(apiurl, varcode, varyear)
for city in cities:
    try:
        (x[max],y[max],map) = getcoords(fullmappoly, varcode, city)
        max = max + 1
    except:
        notfound = city
    
fig, ax = subplots(figsize=(12,12))
ax = fig.gca() 
i = 0
for row in range(max+1):
    if x[i]:
        try: 
            thiscolor = colors[i]
        except:
            thiscolor = 'black'
                
        ax.plot(x[i], y[i], color=thiscolor)
        print cities[i] + ' = ' + thiscolor 
    i=i+1

ax.axis('scaled')
if savefile:
    fig.savefig('map.png')
plt.show()


# Let's build complete map with all locations to see boundaries of Netherlands in 1878

# In[ ]:

varyear = 1878
fullmappoly = load_api_map(apiurl, varcode, varyear)
count = 0
fig, ax = subplots(figsize=(15,30))
ax = fig.gca() 

def plot_polygon(ax, poly, color='red'):
    a = np.asarray(poly.exterior)
    ax.add_patch(Polygon(a, facecolor=color, alpha=0.3))
    ax.plot(a[:, 0], a[:, 1], color='black')
    
for code in map:
    x = map[code][0]
    y = map[code][1]
    thiscolor = 'black'                
    
    if code == varcode:
        print varcode
        thiscolor = 'green'
        ax.add_patch(Polygon(zip(x,y), facecolor=thiscolor, alpha=0.3))
        
    ax.plot(x, y, color=thiscolor)
    count = count + 1
    if count == 0:
        coords = zip(x,y)
        print coords

ax.axis('scaled')
if savefile:
    filename = str(varyear) + '.png'
    fig.savefig(filename)
plt.show()


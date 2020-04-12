#!/usr/bin/python
# NLGIS2 municipalities loader
# (C) Vyacheslav Tykhonov
# International Institute of Social History 
# https://iisg.amsterdam

import urllib2
import simplejson
import json
import sys
import pandas as pd
import random
import vincent
import codecs
from vincent import Axis, AxisProperties, PropertySet, ValueRef
from subprocess import Popen, PIPE, STDOUT

# Global settings
provinceurl = "http://www.gemeentegeschiedenis.nl/provincie/json/"
geoapiurl = 'http://node-128.dev.socialhistoryservices.org/api/maps?format=geojson&year='
#thisprovince = 'Noord-Holland'
#thisprovince = 'Flevoland'

def load_remote_data(apiurl, param):
    jsondataurl = apiurl + param
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

provlist = ["Groningen", "Friesland", "Drenthe", "Overijssel", "Flevoland", "Gelderland", "Utrecht", "Noord-Holland", "Zuid-Holland", "Zeeland", "Noord-Brabant", "Limburg"]
provincies = {}
amscodes = {}
#if thisprovince:
    #provlist = []
    #provlist.append(thisprovince)
    
for province in provlist:
    print province
    data = load_remote_data(provinceurl, province)
    provincelist = []
    loclist = ''
    for item in data:
        locations = {}
        #print item['amco'] + ' ' + item['provincie'] + ' ' + item['startjaar'] + ' ' + item['eindjaar'] + ' ' + item['naam']
        loclist = loclist + str(item['amco']) + ', '
        locations['amsterdamcode'] = item['amco']
        locations['name'] = item['naam']
        locations['start'] = item['startjaar']
        locations['end'] = item['eindjaar']
        amscodes[locations['amsterdamcode']] = item['startjaar']
        locations['cbscode'] = item['cbscode']
        provincelist.append(locations)
    loclist = loclist.replace(' ', '')[:-1].upper()
    provincies[province] = loclist
    
#years = [1980, 1997]
years = []
for i in sorted(range(1812, 1997)):
    years.append(i)
mapjson = {}
dir = "/home/nlgis/nlgis2/maps/provincie/json"
outdir = dir + "/../provinces"
country = 'nld'
for province in provlist:
    loclist = provincies[province]
    for year in years:
        try:
            # Get geojson from GEO API
            data = load_remote_data(geoapiurl, str(year))
            filename = dir + '/' + str(year) + '.json'
            outfile = outdir + '/geojson_' + str(year) + '_' + province + '.json'
            topofile = outdir + '/topojson_' + str(year) + '_' + province + '.json'
            file = codecs.open(filename, "w", "utf-8")
            file.write(json.dumps(data, encoding="utf-8", sort_keys=True, indent=4))
            file.close()
            # Extract polygons for specific province
            cmd = "/usr/bin/ogr2ogr   -f GeoJSON   -where \"amsterdamcode in (" + loclist + ") \"  " + outfile + " " + filename
	    # Convert to topojson
	    toporun = '/usr/bin/topojson -o ' + topofile + ' --id-property=+amsterdamcode -p -- ' + outfile
	    cmd = cmd + ';' + toporun
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            response = p.stdout.read()    
            print response
        except:
            print "Warning: can't read geojson for " + str(year)
    
mapjson


#!/usr/bin/python
# Use case for NLGIS2 geo api service
# (C) Vyacheslav Tykhonov vty@iisg.nl
# International Institute of Social History 
# http://socialhistory.org

#%matplotlib inline
import urllib2
import simplejson
import json
import sys
import pandas as pd
import random
#import vincent
import codecs
#from vincent import Axis, AxisProperties, PropertySet, ValueRef
from subprocess import Popen, PIPE, STDOUT

# Global settings
provinceurl = "http://www.gemeentegeschiedenis.nl/provincie/json/"
geoapiurl = 'http://node-128.dev.socialhistoryservices.org/api/maps?format=geojson&year='
thisprovince = 'Noord-Holland'
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
if thisprovince:
    provlist = []
    provlist.append(thisprovince)
    
for province in provlist:
    data = load_remote_data(provinceurl, province)
    #data
    provincelist = []
    for item in data:
        locations = {}
        #print item['amco'] + ' ' + item['provincie'] + ' ' + item['startjaar'] + ' ' + item['eindjaar'] + ' ' + item['naam']
        locations['amsterdamcode'] = item['amco']
        locations['name'] = item['naam']
        locations['start'] = item['startjaar']
        locations['end'] = item['eindjaar']
        amscodes[locations['amsterdamcode']] = item['startjaar']
        locations['cbscode'] = item['cbscode']
        provincelist.append(locations)
    provincies[province] = provincelist
    
years = [1997]
mapjson = {}
dir = "/home/slava/nlgis2/maps/provincie/json"
outdir = dir + "/../provinces"
country = 'nld'
for year in years:
    data = load_remote_data(geoapiurl, str(year))
    filename = dir + '/' + str(year) + '.json'
    outfile = outdir + '/out' + str(year) + '_' + thisprovince + '.json'
    file = codecs.open(filename, "w", "utf-8")
    file.write(json.dumps(data, encoding="utf-8", sort_keys=True, indent=4))
    file.close()
    cmd = "ogr2ogr   -f GeoJSON   -where \"amsterdamcode in (11150,10822) \"  " + outfile + " " + filename
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = p.stdout.read()    
    print response
mapjson

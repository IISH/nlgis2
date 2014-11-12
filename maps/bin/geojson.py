#!/usr/bin/python

from pymongo import MongoClient
import sys
import json
import ast
import re

vardb = ''
year = sys.argv[1]
if sys.argv[2]:
    vardb = sys.argv[2]
country = 'NLD'
defaultdb = 'geojson'
if vardb:
    dbcol = vardb 
else:
    dbcol = defaultdb

client = MongoClient()
db = client[globals()['dbcol']]  # use a database called boundaries to store json
collection = db.json   # and inside that DB, a collection called "files"

polygons = collection.find({ 'year': year }) 

polygons1 = ()
for jsonstr in polygons:
	newjson = dict(jsonstr.items())
	for key in newjson:
	    if key == 'json':
		response = newjson[key] 
		#new_string = re.sub(r'cts\"\:\{\"1812', r'cts":{"NLD', response)	
		replace = 'cts\"\:\{\"'+str(year)
		new_string = re.sub(replace, r'cts":{"nld', response)
	        print new_string.encode('utf8')


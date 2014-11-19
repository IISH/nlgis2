#!/usr/bin/python

from pymongo import MongoClient
import sys
import json
import ast
import re
import sys, os
#sys.setdefaultencoding('utf-8')

year = sys.argv[1]
province = sys.argv[2]
paramformat = sys.argv[3]
country = 'NLD'

client = MongoClient()
db = client.provinces  # use a database called boundaries to store json
collection = db.json   # and inside that DB, a collection called "files"
thisformat = 'topojson'
if paramformat:
    thisformat = paramformat

polygons = collection.find({ 'year': year, 'province': province, 'format': thisformat }) 
for jsonstr in polygons:
	newjson = dict(jsonstr.items())
	for key in newjson:
	    if key == 'json':
		response = newjson[key] 
		#new_string = re.sub(r'cts\"\:\{\"1812', r'cts":{"NLD', response)	
		replace = 'cts\"\:\{\".+?\"'
		new_string = re.sub(replace, r'cts":{"nld"', response)
	        print new_string


#!/usr/bin/python

from pymongo import MongoClient
import sys
import json
import ast
import re

year = sys.argv[1]
country = 'NLD'

client = MongoClient()
db = client.histboundaries  # use a database called boundaries to store json
collection = db.json   # and inside that DB, a collection called "files"

polygons = collection.find({ 'year': year }) 
for jsonstr in polygons:
	newjson = dict(jsonstr.items())
	for key in newjson:
	    if key == 'json':
		response = newjson[key] 
		#new_string = re.sub(r'cts\"\:\{\"1812', r'cts":{"NLD', response)	
		replace = 'cts\"\:\{\"'+str(year)
		new_string = re.sub(replace, r'cts":{"nld', response)
	        print new_string


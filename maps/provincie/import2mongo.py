#!/usr/bin/python

import re
from os import listdir
from os.path import isfile, join
from pymongo import MongoClient
import sys
import os

def parse_filename(filename):
    result = re.findall('(topojson|geojson)_(\d+)_(.+)\.json', filename)  
    try:
        output = result[0]
    except:
        output = ''
    return (output)

jsonpath = "/home/nlgis/nlgis2/maps/provincie/provinces"
country = "nld"
client = MongoClient()
db = client.provinces  # use a database called boundaries to store json
collection = db.json   # and inside that DB, a collection called "files"

files = [ f for f in listdir(jsonpath) if isfile(join(jsonpath,f)) ]
for file in files:
        filepath = jsonpath + '/' + file
        items = parse_filename(filepath)
        if items:
            (iformat, year, province) = items
            print iformat + ' ' + province + ' ' + year + ' ' + filepath
            f = open(filepath)  # open a file
            text = f.read()    # read the entire contents, should be UTF-8 text
            f.close()
            # build a document to be inserted
	    try:
                text_file_doc = {"province": province, "format": iformat, "year": year, "country": country, "file_name": filepath, "json" : text }
                collection.insert(text_file_doc)
	    except:
		failed = text_file_doc
        
#filename = "topojson_1996_Groningen_T.json"
#(format, year, province) = parse_filename(filename)
#print province

#!/usr/bin/python

from pymongo import MongoClient
import sys

year = sys.argv[1]
country = 'NLD'

client = MongoClient()
db = client.histboundaries  # use a database called boundaries to store json
collection = db.json   # and inside that DB, a collection called "files"

polygons = collection.find({ 'year': year }) 
for json in polygons:
	print json

#!/usr/bin/python

from pymongo import MongoClient
import sys

filename = sys.argv[1]
year = sys.argv[2]
country = 'NLD'

client = MongoClient()
db = client.histboundaries  # use a database called boundaries to store json
collection = db.json   # and inside that DB, a collection called "files"

f = open(filename)  # open a file
text = f.read()    # read the entire contents, should be UTF-8 text
f.close()

# build a document to be inserted
text_file_doc = {"year": year, "country": country, "file_name": filename, "json" : text }
# insert the contents into the "file" collection
collection.insert(text_file_doc)

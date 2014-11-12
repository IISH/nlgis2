#!/usr/bin/python

from os import listdir
from os.path import isfile, join
import sys
import re
import os
import subprocess

mypath = sys.argv[1]
topoloader = "./geojson2mongodb.py"
topodir = '../topojson.amscode'
driver = ''
if driver:
    loader = driver
else:
    loader = topoloader

if not os.path.exists(topodir):
    os.makedirs(topodir)

files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for file in files:
	filepath = mypath + '/' + file
	m = re.search('(\d+)', file)
	year = m.group(0)
	topopath = topodir + '/' + year + '.json'

        upload = 'geojson2mongodb.py ' + filepath + ' ' + year
	# topojson -o topojson.json --id-property=+amsterdamcode -p -- ./geojson.json
	toporun = '/usr/bin/topojson -o ' + topopath + ' --id-property=+amsterdamcode -p -- ' + filepath
	process = subprocess.Popen(toporun, shell=True,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)

	# wait for the process to terminate
	out, err = process.communicate()
	errcode = process.returncode
	#subprocess.call(["/usr/bin/topojson", "-o", topopath + '--id-property=+amsterdamcode -p -- ' + filepath])

	if os.path.isfile(topopath) and os.access(topopath, os.R_OK):
        	subprocess.call([loader, topopath, year])
	print upload


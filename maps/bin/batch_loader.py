#!/usr/bin/python

from os import listdir
from os.path import isfile, join
import sys
import re
import os
import subprocess

mypath = sys.argv[1]
topodir = '../topojson'

if not os.path.exists(topodir):
    os.makedirs(topodir)

files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for file in files:
	filepath = mypath + '/' + file
	m = re.search('(\d+)', file)
	year = m.group(0)
	topopath = topodir + '/' + year + '.json'

        upload = 'json2mongodb.py ' + filepath + ' ' + year
	toporun = '/usr/bin/topojson -o ' + topopath + ' ' + filepath
	print toporun
	subprocess.call(["/usr/bin/topojson", "-o", topopath, filepath])
	if os.path.isfile(topopath) and os.access(topopath, os.R_OK):
        	subprocess.call(["./json2mongodb.py", topopath, year])
	print upload


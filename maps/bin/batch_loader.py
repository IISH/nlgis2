#!/usr/bin/python

from os import listdir
from os.path import isfile, join
import sys
import re
from subprocess import call
call(["ls", "-l"])

mypath = sys.argv[1]

files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for file in files:
	filepath = mypath + '/' + file
	m = re.search('(\d+)', file)
	year = m.group(0)

        upload = 'json2mongodb.py ' + filepath + ' ' + year
        call(["./json2mongodb.py", filepath, year])
	print upload


# Copyright (C) 2014 International Institute of Social History.
# @author Vyacheslav Tykhonov <vty@iisg.nl>
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception, the copyright holders give permission to link the
# code of portions of this program with the OpenSSL library under certain
# conditions as described in each individual source file and distribute
# linked combinations including the program with the OpenSSL library. You
# must comply with the GNU Affero General Public License in all respects
# for all of the code used other than as permitted herein. If you modify
# file(s) with this exception, you may extend this exception to your
# version of the file(s), but you are not obligated to do so. If you do not
# wish to do so, delete this exception statement from your version. If you
# delete this exception statement from all source files in the program,
# then also delete it in the license file.

from flask import Flask, Response, request, send_from_directory
from twisted.web import http
import json
import simplejson
import urllib2
import glob
import csv
import xlwt
import os
import sys
import psycopg2
import psycopg2.extras
import pprint
import collections
import getopt
import numpy as np
import pandas as pd
import random
import ConfigParser
from subprocess import Popen, PIPE, STDOUT
from random import randint
import brewer2mpl
import string
import re

def connect(custom):
        cparser = ConfigParser.RawConfigParser()
        cpath = "/etc/apache2/nlgiss2.config"
        cparser.read(cpath)
        options = {}
        dataoptions = cparser.items( "dataoptions" )
        for key, value in dataoptions:
            options[key] = value

 	database = cparser.get('config', 'dbname')
  	if request.args.get('custom'):
	    database = cparser.get('config', 'customdbname')
	if custom:
	    database = cparser.get('config', 'customdbname')

	conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (cparser.get('config', 'dbhost'), database, cparser.get('config', 'dblogin'), cparser.get('config', 'dbpassword'))

    	# get a connection, if a connect cannot be made an exception will be raised here
    	conn = psycopg2.connect(conn_string)

    	# conn.cursor will return a cursor object, you can use this cursor to perform queries
    	cursor = conn.cursor()

	if custom:
	    options = conn_string
	return (cursor, options)

def json_generator(c, jsondataname, data):
	sqlnames = [desc[0] for desc in c.description]
        jsonlist = []
        jsonhash = {}
        
        for valuestr in data:    
            datakeys = {}
            for i in range(len(valuestr)):
               name = sqlnames[i]
               value = valuestr[i]
               datakeys[name] = value
               #print "%s %s", (name, value)
            jsonlist.append(datakeys)
        
        jsonhash[jsondataname] = jsonlist;
        json_string = json.dumps(jsonhash, encoding="utf-8", sort_keys=True, indent=4)

        return json_string

def analyze_data(cursor, catnum):
        data = {}
        debug = ''
        query = "select value from datasets.data WHERE 1 = 1 ";
        query = sqlfilter(query)
        if debug:
            print "DEBUG " + query + " <br>\n"
        query += ' order by id asc'
        if debug:
            return query

        # execute
        cursor.execute(query)
        i = 0
        values = []
        # retrieve the records from the database
        records = cursor.fetchall()
        for row in records:
                i = i + 1
                values.append(row[0])
                data[i] = row

        # Calculate ranges based on percentile
        qwranges = []
        finalcatnum = 0
        try:
            if values:
                df = pd.DataFrame(values)
                colormap = []
                p = buildcategories(catnum)
                result = percentile(df, p)
                # Trying to find right categories: 8, 7, ... 1
                for thiscat in reversed(range(catnum+1)):
                    if finalcatnum == 0:
                        if thiscat > 0:
                            p = buildcategories(thiscat)
                            finalcatnum = percentile(df, p)
        except:
            return 3

        return finalcatnum
def load_years(cursor):
        data = {}
        sql = "select * from datasets.years where 1=1";
	sql = "select year, count(*) as count  from datasets.data where 1=1"
	sql = sqlfilter(sql)
	sql = sql + ' group by year order by year asc';
        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
	jsondata = json_generator(cursor, 'years', data)

        return jsondata

def sqlfilter(sql):
        items = ''
        sqlparams = ''

	for key, value in request.args.items():
	    #sql = sql + '  ' +key + '=' + value + '<br>'
            items = request.args.get(key, '')
            itemlist = items.split(",")
	    itemparams = ''
            for item in itemlist:
		#sql = sql + ' ' + item + ' = ' + '<br>' 
                sqlparams = "\'%s\'" % item
            #sqlparams = sqlparams[:-1]
	    if key != 'datarange':
		if key != 'output':
		    if key != 'custom':
		        if key != 'scales':
			    if key != 'categories':
			        if key != 'csv':
                                    sql += " AND %s in (%s)" % (key, sqlparams)
	return sql

def load_locations(cursor, year, indicator):
        data = {}

	sql = "select naam, amsterdam_code, year, count(*) from datasets.data where 1=1 "
        limit = 0
	sql = sqlfilter(sql)
        sql = sql + ' group by naam, year, amsterdam_code'

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'locations', data)

        return jsondata

def list_topics(cursor):
	data = {}

	# Before the list of topics will be available a few sql statements should be run
	# update datasets.topics set count=subquery.as_count from (select code as as_code, count(*) as as_count from datasets.data group by as_code) as subquery where topic_code=subquery.as_code;
  	#update datasets.topics set startyear=subquery.startyear from (select code as as_code, min(year) as startyear from datasets.data group by as_code) as subquery where topic_code=subquery.as_code;
	# update datasets.topics set totalyears=subquery.total from (select count(DISTINCT year) as total, code as as_code from datasets.data group by as_code) as subquery where topic_code=subquery.as_code;
	sql = "select topic_name, topic_code, count, startyear, totalyears from datasets.topics where startyear > 0 order by count desc"
        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        
        topics = {}
	maxvalue = -1
        for topic in data:
            topicdata = {}
            letter = 'A'
            for i, field in enumerate(columns):
                topicdata[field] = topic[i]
                if field == 'topic_code':
                    mletter = re.match("^(\w)", topicdata[field])
                    letter = mletter.group(0)
		if maxvalue == -1:
		    if field == 'count':
		 	findindex = columns.index('totalyears')
		        if topic[findindex] < 10:
			    maxvalue = topicdata[field] 
		            topicdata['max'] = maxvalue
            topicdata['letter'] = letter
	    topicdata['max'] = maxvalue
            topics[topicdata['topic_code']] = topicdata
            
        #jsondata = json_generator(cursor, 'topics', topics)
        jsondata = json.dumps(topics, encoding="utf-8", sort_keys=True, indent=4)

        return jsondata

def load_topics(cursor, year, indicator):
        data = {}

	sql = "select code, indicator, topic_name, count(*) as count from datasets.data as d, datasets.topics as t where d.code=t.topic_code "
	limit = 0

	sql = sqlfilter(sql) 
	try:
            if limit:
                sql = sql + ' limit ' + str(limit)
	except:
	    limit = 0
	sql = sql + ' group by code, indicator, t.topic_name'

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'codes', data)
        
        return jsondata

def load_classes(cursor):
        data = {}
	sql = "select topic_code, topic_name from datasets.topics where 1=1"
        sql = sqlfilter(sql)

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'indicators', data)

        return jsondata

def load_regions(cursor):
        data = {}
        sql = "select * from datasets.regions where 1=1";
	sql = sqlfilter(sql)
	sql = sql + ';'
        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
	jsondata = json_generator(cursor, 'regions', data)

        return jsondata

def medianlimits(dataframe):
    scale = []
    frame1 = []
    frame2 = []
    avg = dataframe.median()
    for value in dataframe:
        if value <= avg:
            frame1.append(value)
        else:
            frame2.append(value)
    avg1 = pd.DataFrame(frame1).median()
    avg2 = pd.DataFrame(frame2).median()
    
    return (dataframe.min(), int(avg1), int(avg), int(avg2), dataframe.max())

def combinerange(map):
    rangestr = ''
    rangearr = []
    for i in reversed(range(len(map))):
        if i > 0:
            id = i - 1
            min = map[id]
            max = map[i]
            rangestr = rangestr + str(min) + ' - ' + str(max) + ', '
            rangearr.append(str(min) + ' - ' + str(max))
    rangestr = rangestr[:-2]
    return (rangearr, rangestr)

def buildcategories(num):
    step = 100 / float(num)
    print step
    p = []
    for i in range(num+1):
        if i:
            p.append(i * step)
        else:
            p.append(i)
    return p

def meanlimits(dataframe):
    scale = []
    frame1 = []
    frame2 = []
    avg = dataframe.mean()
    for value in dataframe:
        if value <= avg:
            frame1.append(value)
        else:
            frame2.append(value)
    avg1 = pd.DataFrame(frame1).mean()
    avg2 = pd.DataFrame(frame2).mean()

    return (dataframe.min(), int(avg1), int(avg), int(avg2), dataframe.max())

def load_data(cursor, year, datatype, region, datarange, output, debug, dataframe, catnum, options, csvexport):
        data = {}
	colors = ['red', 'green', 'orange', 'brown', 'purple', 'blue', 'cyan']
	colormap = 'Paired'
 	#colormap = 'Green'
	if not catnum:
	    try:
	        catnumint = int(options['defaultcategories'])
	        if catnumint:
	    	    catnum = catnumint 
	    except:
	        catnum = 8
	bmap = brewer2mpl.get_map(colormap, 'Qualitative', catnum)
	colors = bmap.hex_colors
	maxColor = 0

        # execute our Query
	#    for key, value in request.args.iteritems():
	#        extra = "%s<br>%s=%s<br>" % (extra, key, value)

        query = "select * from datasets.data WHERE 1 = 1 ";
	if output:
 	    query = "select amsterdam_code, value from datasets.data WHERE 1 = 1 ";
	
	query = sqlfilter(query)
        if debug:
            print "DEBUG " + query + " <br>\n"
        query += ' order by id asc'
	if debug:
	    return query 

        # execute
        cursor.execute(query)
	columns = [i[0] for i in cursor.description]
	thiscount = 0
	index = 0
	for col in columns:
    	   if col == 'value':
        	index = thiscount
    		thiscount = thiscount + 1

        # retrieve the records from the database
        records = cursor.fetchall()
        if csvexport:
            return (records, columns, '')

 	# Data upload
        i = 0
        values = []
        index = 6
        for row in records:
                i = i + 1
                values.append(row[index])
                data[i] = row

	# Calculate ranges based on percentile
        qwranges = []
        if values:
            df = pd.DataFrame(values)
	    pval = 0
            colormap = []
	    known = []
            p = buildcategories(catnum)
            for i in p:
                val = round(np.percentile(df, i), 2)
                qwranges.append(val)

	# Calculate real none repeatable ranges
        xranges = []
	realcat = 0
        for val in qwranges:
            if val in xranges:
                skip = 1
            else:
                xranges.append(val)
	 	realcat = realcat + 1

	if realcat < catnum:
            qwranges = xranges
	    catnum = realcat
	    newcolors = []
	    for cID, color in enumerate(colors):
	        if cID < catnum:
		    newcolors.append(color)
	    colors = newcolors
	# DBQ1
	#return (str(catnum), 'test')
	#return (json.dumps(colors), 'test')

	fulldata = {}
	fulldataarray = []
	#for i in xrange(cursor.rowcount):
	i = 0
	for dataline in records:
	    dataset = {}
	    index = 0
	    amscode = ''

	    for item in dataline:
		fieldname = columns[index]
                #dataset[fieldname] = dataline[index]
		#if fieldname == 'value':
		#   value = float(dataline[index])
		if fieldname == 'amsterdam_code':
		   amscode = str(dataline[index])
		else:
		   dataset[fieldname] = dataline[index]
		k = item
		index = index + 1

	    # Select colors
	    #if datarange == 'random':
	        #colorID = randint(0, catnum)
		#dataset['color'] = colors[colorID]
	    #if datarange == 'binary':
		#colorID = 0
	        #dataset['color'] = colors[colorID]

	    if not datarange:
	        datarange = 'calculate'

	    if datarange == 'calculate':
		if dataset['value']:
		    colorID = 0 
		    dataset['color'] = colors[colorID]
		    dataset['r'] = 0
		    for validx in qwranges:
		        if dataset['value'] > validx:
			    dataset['r'] = validx
		            dataset['color'] = colors[colorID]	 
			colorID = colorID + 1

	    #return (json.dumps(colors), 'test')
	    try:
	        if amscode:
	            fulldata[amscode] = []
	            fulldata[amscode] = dataset
	        if dataset:
	            fulldataarray.append(dataset)
	    except:
		donothing = 1
	    i = i + 1
	#return (json.dumps(colors), 'test')
	#return json.dumps(fulldataarray)
	jsondata = json.dumps(fulldata, ensure_ascii=False, sort_keys=True, indent=4)

        row_count = 0
        i = 0
	values = []
	index = 6
	#activecolors = []
	#for i, color in enumerate(colors):
	#    if i < maxColor:
	#        activecolors.append(color)
	#catnum = maxColor
	#if maxColor:
	#    colors = activecolors
	# DBQW
	#return (str(maxColor), 'test')
	#return (json.dumps(qwranges), json.dumps(colors), catnum)

        for row in records:
                i = i + 1
		#row['color'] = 'red'
		values.append(row[index])
                data[i] = row
#               print row[0]
	#jsondata = json_generator(fulldataarray)
	if dataframe:
	    return (qwranges, colors, catnum)
	    df = pd.DataFrame(values)
	    colormap = []
	    p = buildcategories(catnum)
	    qw = []
	    for i in p:
    	   	val = round(np.percentile(df, i), 2)
    		qw.append(val)

	    if dataframe == 'mean':
	        colormap = meanlimits(df[0])
	    else:
		colormap = medianlimits(df[0])
	    #colormap = [0, 1, 2, 3]
	    return qw
	    #return json_generator(cursor, 'ranges', colormap)

	if year:
	    return (jsondata, colors, catnum)
	else:
	    return (json_generator(cursor, 'data', records), colors, catnum)

app = Flask(__name__)

@app.route('/')
def test():
    description = 'nlgis2 API Service v.0.1<br>/api/maps (map polygons)<br>/api/data (data services)<br>'
    return description

@app.route('/demo')
def demo():
    sql = "select * from datasets.topics where 1=1";
    sql = sqlfilter(sql)
    return sql

@app.route('/topicslist')
def topicslist():
    (cursor, options) = connect('')
    data = list_topics(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/topics')
def topics():
    (cursor, options) = connect('')
    data = load_topics(cursor, 0, 0)
    return Response(data,  mimetype='application/json')

def load_province_data(apiurl, province):
    jsondataurl = apiurl + province
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

@app.route('/clean')
def clean():
    cleanall = ''
    custom = ''
    exceptdb = ''
    (cursor, options) = connect(custom)

    cmd = ''
    if request.args.get('all'):
        cleanall = 'yes'
    if request.args.get('except'):
        exceptdb = request.args.get('except')

    cparser = ConfigParser.RawConfigParser()
    cpath = "/etc/apache2/nlgiss2.config"
    cparser.read(cpath)
    imagepathloc = cparser.get('config', 'imagepathloc')

    ext = ["png", "svg", "PDF", "gz", "csv", "tar", "jpg"]
    for extension in ext:
       thiscmd = "/bin/rm -rf " + imagepathloc + "/*." + extension + ";"
       cmd = cmd + thiscmd
    # clean custom
    customcmd = "/bin/rm -rf " + imagepathloc + "/custom/*";
    cmd = cmd + customcmd
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = json.dumps(p.stdout.read())

    # Clean custom datasets database
    if exceptdb:
	sql = "delete from datasets.data where 1=1"
	sql = sql + ' and indicator<>\'' + exceptdb + '\''
    else:
	sql = "truncate table datasets.data"
    cursor.execute(sql)
    sql = "truncate table datasets.topics"
    cursor.execute(sql)

    return 'All files and custom databases cleaned. ' 

@app.route('/provincies')
def provincies():
    thisprovince = ''
    provinceurl = "http://www.gemeentegeschiedenis.nl/provincie/json/"
    paramprovince = request.args.get('province');
    if paramprovince:
	thisprovince = paramprovince

    provlist = ["Groningen", "Friesland", "Drenthe", "Overijssel", "Flevoland", "Gelderland", "Utrecht", "Noord-Holland", "Zuid-Holland", "Zeeland", "Noord-Brabant", "Limburg"]
    provincies = {}
    if thisprovince:
        provlist = []
        provlist.append(thisprovince)
    
    for province in provlist:
        data = load_province_data(provinceurl, province)
        provincelist = []
        for item in data:
            locations = {}
            #print item['amco'] + ' ' + item['provincie'] + ' ' + item['startjaar'] + ' ' + item['eindjaar'] + ' ' + item['naam']
            locations['amsterdamcode'] = item['amco']
            locations['name'] = item['naam']
            locations['start'] = item['startjaar']
            locations['end'] = item['eindjaar']
            locations['cbscode'] = item['cbscode']
            provincelist.append(locations)
        provincies[province] = provincelist

    jsondata = json.dumps(provincies, ensure_ascii=False, sort_keys=True, indent=4)
    return Response(jsondata,  mimetype='application/json')

@app.route('/locations')
def locations():
    (cursor, options) = connect('')
    data = load_locations(cursor, 0, 0)
    return Response(data,  mimetype='application/json')

@app.route('/indicators')
def classes():
    (cursor, options) = connect('')
    data = load_classes(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/years')
def years():
    (cursor, options) = connect('')
    data = load_years(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/regions')
def regions():
    (cursor, options) = connect('')
    data = load_regions(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/scales')
def scales():
    (cursor, options) = connect('')
    year = 0
    datatype = '1.01'
    region = 0
    debug = 0
    datarange = 'random'
    output = ''

    # Read parameters grom GET
    paramrange = request.args.get('datarange');
    paramyear = request.args.get('year')
    paramoutput = request.args.get('output');
    paramscales = request.args.get('scales');
    paramcat = request.args.get('categories');
    catnum = 8
    if paramrange:
        datarange = paramrange
    if paramyear:
        year = paramyear
    if paramoutput:
        output = paramoutput
    if options['defaultcategories']:
        catnumint = int(options['defaultcategories'])
    if paramcat:
        catnumint = paramcat
        try:
            catnum = int(catnumint)
        except:
            catnum = catnumint

    realcatnum = analyze_data(cursor, catnum)
    if realcatnum:
        if realcatnum < catnum:
            catnumX = realcatnum

    paramscales = 'scale'
    try:
        (data, colors, catnum) = load_data(cursor, year, datatype, region, datarange, output, debug, paramscales, catnum, options, '')
    except:
	data = []
	colors = []
    # DEBUGSCALE
    #return json.dumps(data)
    (rangearr, rangestr) = combinerange(data)
    colormap = []
    cID = 0
    # Remove extra colors if less than 8 categories
    if catnum < 8:
	colors.pop()
    for color in reversed(colors):
	if cID >= 0:
	    colormap.append(color)
	    output = output + ' ' + color
	cID = cID + 1
    output = ''
    id = 0 
    #return str(catnum) + ' ' + json.dumps(rangearr) + json.dumps(colormap)
    #return json.dumps(data) + ' ' + json.dumps(colors) + ' ' + str(catnum)
    scales = {}
    for thisrange in rangearr:
	output = output + ' ' + thisrange + '=' + str(id) + '<br>'
	color = colormap[id]
	savecolor = {}
	savecolor['color'] = color
	thisid = catnum - id
	savecolor['range'] = thisrange
	#savecolor['max'] = data[thisid]
	savecolor['sector'] = id
	scales[id] = savecolor
	id = id + 1

    # Add no data in scale
    if id:
	savecolor = {}
	savecolor['color'] = '#ffffff'
	savecolor['range'] = 'no data'
	scales[id] = savecolor

    jsondata = json.dumps(scales, ensure_ascii=False, sort_keys=True, indent=4)
    return Response(jsondata,  mimetype='application/json')

@app.route('/data')
def data():
    (cursor, options) = connect('')
    year = 0
    datatype = '1.01'
    region = 0
    debug = 0
    datarange = 'random'
    csvexport = ''
    output = ''
    code = ''
    paramrange = request.args.get('datarange');
    paramyear = request.args.get('year')
    paramoutput = request.args.get('output');
    paramscales = request.args.get('scales'); 
    paramcat = request.args.get('categories');
    catnum = 8 
    if paramrange:
        datarange = paramrange
    if paramyear:
	year = paramyear
    if paramoutput:
	output = paramoutput
    if options['defaultcategories']:
        catnumint = int(options['defaultcategories'])
        #catnum = catnumint
    if request.args.get('csv'):
        csvexport = 'yes'
    if request.args.get('code'):
        code = request.args.get('code')
    if paramcat:
        catnumint = paramcat
        try:
            catnum = int(catnumint)
        except:
            catnum = catnumint

    realcatnum = analyze_data(cursor, catnum)
    if realcatnum:
        if realcatnum < catnum:
            catnumX = realcatnum

    (data, colors, catnum) = load_data(cursor, year, datatype, region, datarange, output, debug, paramscales, catnum, options, csvexport)
    dataset = data
    if csvexport:
        cparser = ConfigParser.RawConfigParser()
        cpath = "/etc/apache2/nlgiss2.config"
        cparser.read(cpath)
        imagepathloc = cparser.get('config', 'imagepathloc')
        # CSV
        localfile = 'dataset_' + code + '.csv'
        fullpath = imagepathloc + '/' + localfile

        f = csv.writer(open(fullpath, "wb+"))
        f.writerow(colors)
        #m = dataset['data']
        for dataset in data:
            f.writerow(dataset)
        return send_from_directory(imagepathloc, localfile, as_attachment=True)

    if paramscales:
	#dataset = paramscales
	(rangearr, rangestr) = combinerange(dataset)
	output = ''
	id = 0
	for i in dataset:
	    if output:
	        output = output + ',' + str(i) #+ colors[id]
	    else:
		output = str(i)
	    id = id + 1

	json_response = rangestr
	return Response(json_response) #, mimetype='application/json')
    else:
	return Response(dataset, mimetype='application/json')

    #json_response = json.loads(data)
    #return Response(data,  mimetype='application/json;charset=utf-8')
    return Response(dataset, mimetype='application/json')

@app.route('/maps')
def maps():

    cparser = ConfigParser.RawConfigParser()
    cpath = "/etc/apache2/nlgiss2.config"
    cparser.read(cpath)
    path = cparser.get('config', 'path')
    geojson = cparser.get('config', 'geojson')

    # Default year 
    year = cparser.get('config', 'year')
    cmdgeo = ''
    provcmd = ''
    thisformat = 'topojson'
    # get year from API call
    paramyear = request.args.get('year');
    # format for polygons: geojson, topojson, kml 
    paramformat = request.args.get('format');
    paramprovince = request.args.get('province');
    if paramyear:
	year = paramyear
    if paramformat == 'geojson':
	cmdgeo = path + "/maps/bin/geojson.py " + str(year) + " " + geojson
	thisformat = paramformat
    if paramprovince:
	provcmd = path + '/maps/bin/topoprovince.py ' + str(year) + " " + paramprovince + " " + thisformat	

    pythonpath = '/usr/bin/python '
    cmd = pythonpath + path + "/maps/bin/topojson.py " + str(year)
    if cmdgeo:
	cmd = pythonpath + cmdgeo
    if provcmd:
	cmd = pythonpath + provcmd

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = json.dumps(p.stdout.read())
    #"objects":{"1812
    #new_string = re.sub(r'"{\"1812"', r'{\"NLD', response)
    json_response = json.loads(response)

    return Response(json_response,  mimetype='application/json;charset=utf-8')

if __name__ == '__main__':
    app.run()

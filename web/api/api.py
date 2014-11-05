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

from flask import Flask, Response, request
from twisted.web import http
import json
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

def connect():
        cparser = ConfigParser.RawConfigParser()
        cpath = "/etc/apache2/nlgiss2.config"
        cparser.read(cpath)

 	database = cparser.get('config', 'dbname')
  	if request.args.get('custom'):
	    database = cparser.get('config', 'customdbname')

	conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (cparser.get('config', 'dbhost'), database, cparser.get('config', 'dblogin'), cparser.get('config', 'dbpassword'))

    	# get a connection, if a connect cannot be made an exception will be raised here
    	conn = psycopg2.connect(conn_string)

    	# conn.cursor will return a cursor object, you can use this cursor to perform queries
    	cursor = conn.cursor()

    	#(row_count, dataset) = load_regions(cursor, year, datatype, region, debug)
	return cursor

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
            rangestr = rangestr + str(min) + '-' + str(max) + ', '
            rangearr.append(str(min) + '-' + str(max))
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

def load_data(cursor, year, datatype, region, datarange, output, debug, dataframe, catnum):
        data = {}
	colors = ['red', 'green', 'orange', 'brown', 'purple', 'blue', 'cyan']

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

	fulldata = {}
	#fulldata['data'] = []
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
		if fieldname == 'amsterdam_code':
		   amscode = str(dataline[index])
		else:
		   dataset[fieldname] = dataline[index]
		k = item
		index = index + 1
	    if datarange == 'random':
	        colorID = randint(0,4)
	    if datarange == 'binary':
		colorID = 0
	    dataset['color'] = colors[colorID]
	    fulldata[amscode] = []
	    fulldata[amscode] = dataset
	    fulldataarray.append(dataset)
	    i = i + 1
	#return json.dumps(fulldataarray)
	jsondata = json.dumps(fulldata, ensure_ascii=False, sort_keys=True, indent=4)

        row_count = 0
        i = 0
	values = []
	index = 6
        for row in records:
                i = i + 1
		#row['color'] = 'red'
		values.append(row[index])
                data[i] = row
#               print row[0]
	#jsondata = json_generator(fulldataarray)
	if dataframe:
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
	    return jsondata
	else:
	    return json_generator(cursor, 'data', records)

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

@app.route('/topics')
def topics():
    cursor = connect()
    data = load_topics(cursor, 0, 0)
    return Response(data,  mimetype='application/json')

@app.route('/locations')
def locations():
    cursor = connect()
    data = load_locations(cursor, 0, 0)
    return Response(data,  mimetype='application/json')

@app.route('/indicators')
def classes():
    cursor = connect()
    data = load_classes(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/years')
def years():
    cursor = connect()
    data = load_years(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/regions')
def regions():
    cursor = connect()
    data = load_regions(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/data')
def data():
    cursor = connect()
    year = 0
    datatype = '1.01'
    region = 0
    debug = 0
    datarange = 'random'
    catnum = 8
    output = ''
    paramrange = request.args.get('datarange');
    paramyear = request.args.get('year')
    paramoutput = request.args.get('output');
    paramscales = request.args.get('scales'); 
    paramcat = request.args.get('categories');
    if paramrange:
        datarange = paramrange
    if paramyear:
	year = paramyear
    if paramoutput:
	output = paramoutput
    if paramcat:
	catnum = int(paramcat) 

    data = load_data(cursor, year, datatype, region, datarange, output, debug, paramscales, catnum)
    dataset = data
    if paramscales:
	#dataset = paramscales
	(rangearr, rangestr) = combinerange(dataset)
	output = ''
	for i in dataset:
	    if output:
	        output = output + ',' + str(i)
	    else:
		output = str(i)

	return Response(rangestr)
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
    # get year from API call
    paramyear = request.args.get('year');
    # format for polygons: geojson, topojson, kml 
    paramformat = request.args.get('format');
    if paramyear:
	year = paramyear
    if paramformat == 'geojson':
	cmdgeo = path + "/maps/bin/geojson.py " + str(year) + " " + geojson;

    cmd = path + "/maps/bin/topojson.py " + str(year)
    if cmdgeo:
	cmd = cmdgeo

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = json.dumps(p.stdout.read())
    #"objects":{"1812
    #new_string = re.sub(r'"{\"1812"', r'{\"NLD', response)
    json_response = json.loads(response)

    return Response(json_response,  mimetype='application/json;charset=utf-8')

if __name__ == '__main__':
    app.run()

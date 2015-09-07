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
import logging
import datetime

Provinces = ["Groningen", "Friesland", "Drenthe", "Overijssel", "Flevoland", "Gelderland", "Utrecht", "Noord-Holland", "Zuid-Holland", "Zeeland", "Noord-Brabant", "Limburg"]
Keys = ['datarange', 'output', 'custom', 'scales', 'categories', 'csv']
pipes = '[\|;><\%`&()$]'

debug_mode = 1
defaultYearIfYearIncorrect = 1982
categoriesPattern = '^[0-9]{0,4}$'
customPattern = '^[A-Za-z0-9]{0,20}$'
datarangePattern = '^[A-Za-z0-9]{0,20}$'
exceptPattern = '^[A-Za-z0-9_\-]{0,20}$'
formatPattern = '^[A-Za-z0-9]{0,20}$'
outputPattern = '^[A-Za-z0-9_\-]{0,20}$'
scalesPattern = '^[A-Za-z0-9]{0,20}$'
topicCodePattern = '^[A-Za-z0-9]{0,20}$'
yearPattern = '^[0-9]{0,4}$'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_value(value, label = ''):
    if value is None:
        valueLogOutput = '-empty-'
        valueLength = 0
    else:
        valueLogOutput = str(value)
        valueLogOutput = valueLogOutput.strip()
        valueLength = len(valueLogOutput)

    if debug_mode == 1:
        logger.info("LOG-" + label + ": " + str(valueLogOutput) + ' (length: ' + str(valueLength) + ')')

def check_value_pattern(value, pattern = '', valueIfPatternIncorrect = '', label = ''):
    if value is None:
        valueLogOutput = '-empty-'
        valueLength = 0
    else:
        valueCheck = str(value)
        valueCheck = valueCheck.strip()

        if pattern != '':
            p = re.compile(pattern)
            m = p.match( valueCheck )
            if not m:
                log_value( pattern, 'REGEXP incorrect: pattern' )
                log_value( valueCheck, 'REGEXP incorrect: value (before)' )
                value = valueIfPatternIncorrect
                log_value( value, 'REGEXP incorrect: value (after)' )

        valueLogOutput = str(value)
        valueLength = len(valueLogOutput)

    if debug_mode == 1:
        logger.info("RAG-PATTERN-" + label + ": " + str(valueLogOutput) + ' (length: ' + str(valueLength) + ')')

    return value

def check_value_inarray(value, arr, valueIfNotFoundInArray = '', label = ''):
    if value is None:
        valueLogOutput = '-empty-'
        valueLength = 0
    else:
        value = str(value)
        value = value.strip()

        if arr:
            if len(value) > 0 :
                if value not in arr:
                    log_value( value, 'NOT IN ARRAY incorrect: value (before)' )
                    value = valueIfNotFoundInArray
                    log_value( value, 'NOT IN ARRAY incorrect: value (after)' )

        valueLogOutput = str(value)
        valueLength = len(valueLogOutput)

    if debug_mode == 1:
        logger.info("RAG-INARRAY-" + label + ": " + str(valueLogOutput) + ' (length: ' + str(valueLength) + ')')

    return value

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

    log_value (cparser.get('config', 'dbname'), "DATABASE (api.py)")
    log_value (cparser.get('config', 'dblogin'), "DBLOGIN (api.py)")
    #log_value (cparser.get('config', 'dbpassword'), "DBPASSWORD (api.py)")

    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (cparser.get('config', 'dbhost'), database, cparser.get('config', 'dblogin'), cparser.get('config', 'dbpassword'))

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(conn_string)

    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()

    if custom:
        options = conn

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
        jsonlist.append(datakeys)
        
    jsonhash[jsondataname] = jsonlist;
    json_string = json.dumps(jsonhash, encoding="utf-8", sort_keys=True, indent=4)

    return json_string

def analyze_data(cursor, catnum):
    data = {}
    debug = ''
    query = "select value from datasets.data WHERE 1=1 ";
    query = sqlfilter(query)
    query += ' order by id asc'
    log_value(query, 'DEBUG query analyze_data')
    #if debug:
    #    return query

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
            #colormap = []
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

def load_notes(cursor):
    data = {}
    sql = "select * from datasets.notes where 1=1";

    for key, value in request.args.items():
        log_value(key, '002key')
        log_value(value, '002value')

        # TODO PROTECT GETPOST VALUE
        items = request.args.get(key, '')
        itemlist = items.split(",")
        locstr = ''

        for item in itemlist:
            item.replace(" ","")
            locstr = locstr + "'" + item + "',"

        locstr = locstr[:-1]

        log_value(locstr, '002locstr')

        sql += " AND %s in (%s)" % (key, locstr)

    #
    cursor.execute(sql)

    # retrieve the records from the database
    data = cursor.fetchall()
    jsondata = json_generator(cursor, 'notes', data)

    return jsondata

def load_sources(cursor):
    data = {}
    sql = "select * from datasets.sources where 1=1";

    for key, value in request.args.items():

        log_value(key, '004key')
        log_value(value, '004value')

        # TODO PROTECT GETPOST VALUE
        items = request.args.get(key, '')
        itemlist = items.split(",")
        locstr = ''

        for item in itemlist:
            locstr = locstr + "'" + item + "',"

        locstr = locstr[:-1]

        log_value(locstr, '004locstr')

        sql += " AND %s in (%s)" % (key, locstr)

    # execute
    cursor.execute(sql)

    # retrieve the records from the database
    data = cursor.fetchall()
    jsondata = json_generator(cursor, 'sources', data)

    return jsondata

def load_years(cursor):
    data = {}
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
    #items = ''
    sqlparams = ''

    for key, value in request.args.items():
        items = request.args.get(key, '')
        itemlist = items.split(",")

        for item in itemlist:
            if key == 'year':
                item = check_value_pattern(item, yearPattern, defaultYearIfYearIncorrect, '05item-year')
            elif key == 'categories':
                item = check_value_pattern(item, categoriesPattern, '', '05item-categories')
            elif key == 'code':
                item = check_value_pattern(item, topicCodePattern, '', '05item-code')
            elif key == 'scales':
                item = check_value_pattern(item, scalesPattern, '', '05item-scales')
            elif key == 'custom':
                item = check_value_pattern(item, customPattern, '', '05item-custom')
            else:
                log_value(key, 'UNPROTECTED_KEY 05item')

            sqlparams = "\'%s\'" % item

        if key not in Keys:
            sql += " AND %s in (%s)" % (key, sqlparams)

    log_value(sql, 'sqlfilter')

    return sql

def load_locations(cursor, year, indicator):
    data = {}

    sql = "select naam, amsterdam_code, year, count(*) from datasets.data where 1=1 "
    #limit = 0
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
    # update datasets.topics set startyear=subquery.startyear from (select code as as_code, min(year) as startyear from datasets.data group by as_code) as subquery where topic_code=subquery.as_code;
    # update datasets.topics set totalyears=subquery.total from (select count(DISTINCT year) as total, code as as_code from datasets.data group by as_code) as subquery where topic_code=subquery.as_code;
    # IND
    if request.args.get('custom'):
        sql = "select topic_name, topic_code from datasets.topics "
    else:
        sql = "select topic_name, topic_code, count, startyear, totalyears, s.sourcename, notes from datasets.topics as t, datasets.sources as s where s.sourceid=t.sourceid and startyear > 0 order by count desc"

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

    jsondata = json.dumps(topics, encoding="utf-8", sort_keys=True, indent=4)

    return jsondata

def load_topics(cursor, year, indicator):
    data = {}

    # Indicatorsinfo
    if request.args.get('custom'):
        sql = "select code, indicator, topic_name, count(*) as count from datasets.data as d, datasets.topics as t where d.code=t.topic_code"
    else:
        sql = "select code, indicator, topic_name, count(*) as count, s.sourcename, t.notes from datasets.sources as s, datasets.data as d, datasets.topics as t where d.code=t.topic_code and t.sourceid=s.sourceid "

    #limit = 0

    sql = sqlfilter(sql)
    #try:
    #    if limit:
    #        sql = sql + ' limit ' + str(limit)
    #except:
    #    limit = 0

    if request.args.get('custom'):
        sql = sql + ' group by code, indicator, t.topic_name'
    else:
        sql = sql + ' group by code, indicator, t.topic_name,  s.sourcename, t.notes'

    log_value(sql, 'show sql (1)')

    log_value("0000\n\n", "0000")

    # execute
    cursor.execute(sql)

    log_value("1111\n\n", "1111")

    # retrieve the records from the database
    data = cursor.fetchall()

    log_value("2222\n\n", "2222")

    jsondata = json_generator(cursor, 'codes', data)

    log_value("3333\n\n", "3333")

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
    #sql = sql + ';'

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

def floattodec(s):
    try:
        c = float(s)
        if int(c) == c:
            return int(c)
        else:
            if c > 10:
                return int(round(c))
            else:
                return s
    except ValueError:
        return s

def combinerange(map):
    rangestr = ''
    rangearr = []
    for i in reversed(range(len(map))):
        if i > 0:
            id = i - 1
            min = map[id]
            max = map[i]
            rangestr = rangestr + str(min) + ' - ' + str(max) + ', '
            rangearr.append(str(floattodec(min)) + ' - ' + str(floattodec(max)))
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

def round_it(x):
    g = round(x)

    paramcode = check_value_pattern(request.args.get('code'), topicCodePattern, '', '10code')
    #if request.args.get('code'):
    if paramcode:
        m = r'LCI'
        isindex = re.match(m, paramcode)
        if isindex:
            g = float("{0:.5f}".format(x))
    return g

def load_data(cursor, year, datatype, region, datarange, output, debug, dataframe, catnum, options, csvexport):
    data = {}
    colors = ['red', 'green', 'orange', 'brown', 'purple', 'blue', 'cyan']
    colormap = 'Paired'

    if not catnum:
        try:
            catnumint = int(options['defaultcategories'])
            if catnumint:
                catnum = catnumint
        except:
            catnum = 8

    bmap = brewer2mpl.get_map(colormap, 'Qualitative', catnum)
    colors = bmap.hex_colors
    #maxColor = 0

    # create query
    query = "select * from datasets.data WHERE 1=1 ";

    if output:
        query = "select amsterdam_code, value from datasets.data WHERE 1=1 ";

    query = sqlfilter(query)
    query += ' order by id asc'
    log_value(query, "loaddata")

    #if debug:
    #    return query

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

    fulldata = {}
    fulldataarray = []
    #for i in xrange(cursor.rowcount):
    i = 0
    for dataline in records:
        dataset = {}
        index = 0
        amscode = ''

        LOCCODE = 'amsterdam_code'

        if request.args.get('db'):
            LOCCODE = 'location'

        for item in dataline:
            fieldname = columns[index]
            if fieldname == LOCCODE:
               amscode = str(dataline[index])
            elif fieldname == 'value':
               # Round to 3 digits after dot
               dataset[fieldname] = round_it(dataline[index])
            else:
               dataset[fieldname] = dataline[index]
            k = item
            index = index + 1

        if not datarange:
            datarange = 'calculate'

        if datarange == 'calculate':
            if dataset['value'] != 'NA':
                colorID = 0
                dataset['color'] = colors[colorID]
                dataset['r'] = 0
                for validx in qwranges:
                    if dataset['value'] > validx:
                        dataset['r'] = validx
                        dataset['color'] = colors[colorID]
                    colorID = colorID + 1

        try:
            if amscode:
                fulldata[amscode] = []
                fulldata[amscode] = dataset
            if dataset:
                fulldataarray.append(dataset)
        except:
            donothing = 1

        i = i + 1

    jsondata = json.dumps(fulldata, ensure_ascii=False, sort_keys=True, indent=4)

    #row_count = 0
    i = 0
    values = []
    index = 6

    for row in records:
        i = i + 1
        values.append(row[index])
        data[i] = row

    if dataframe:
        return (qwranges, colors, catnum)

        # TODO this part unreachable???
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

        return qw

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
    custom = ''
    exceptdb = ''
    (cursor, options) = connect('custom')

    cmd = ''

    ragExcept = check_value_pattern(request.args.get('except'), exceptPattern, '', '14except')
    #if request.args.get('except'):
    if ragExcept:
        #exceptdb = request.args.get('except')
        exceptdb = ragExcept

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
    semicolon = re.split(pipes, cmd)
    cmd = semicolon[0]
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = json.dumps(p.stdout.read())

    # Clean custom datasets database
    if exceptdb:
        sql = "delete from datasets.data where 1=1"
        sql = sql + ' and indicator<>\'' + exceptdb + '\''
    else:
        sql = "delete from datasets.data where code<>'NLSTR';"

    # execute query
    cursor.execute(sql)

    # delete query
    sql = "delete from datasets.topics where topic_code<>'NLSTR';"
    cursor.execute(sql)

    if options:
        options.commit()

    return 'All files and custom databases cleaned. ' 

@app.route('/provincies')
def provincies():
    thisprovince = ''
    provinceurl = "http://www.gemeentegeschiedenis.nl/provincie/json/"

    #paramprovince = request.args.get('province')
    paramprovince = check_value_inarray(request.args.get('province'), Provinces, '', '16province')

    if paramprovince:
        thisprovince = paramprovince

    provincies = {}
    if thisprovince:
        provlist = []
        provlist.append(thisprovince)
    
    for province in provlist:
        data = load_province_data(provinceurl, province)
        provincelist = []

        for item in data:
            locations = {}
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

@app.route('/sources')
def sources():
    (cursor, options) = connect('')
    data = load_sources(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/notes')
def notes():
    (cursor, options) = connect('')
    data = load_notes(cursor)
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

    # Read parameters from GET
    #paramrange = request.args.get('datarange')
    paramrange = check_value_pattern(request.args.get('datarange'), datarangePattern, '', '17datarange')
    #paramyear = request.args.get('year')
    paramyear = check_value_pattern(request.args.get('year'), yearPattern, defaultYearIfYearIncorrect, '17year')
    #paramoutput = request.args.get('output')
    paramoutput = check_value_pattern(request.args.get('output'), outputPattern, '', '17output')
    #paramscales = request.args.get('scales')
    paramscales = check_value_pattern(request.args.get('scales'), scalesPattern, '', '17scales')
    #paramcat = request.args.get('categories')
    paramcat = check_value_pattern(request.args.get('categories'), categoriesPattern, '', '17categories')

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

    #realcatnum = analyze_data(cursor, catnum)
    #if realcatnum:
        #if realcatnum < catnum:
            #catnumX = realcatnum

    paramscales = 'scale'
    try:
        (data, colors, catnum) = load_data(cursor, year, datatype, region, datarange, output, debug, paramscales, catnum, options, '')
    except:
        data = []
        colors = []

    # DEBUGSCALE
    (rangearr, rangestr) = combinerange(data)
    colormap = []
    cID = 0

    # Remove extra colors if less than 8 categories
    log_value(catnum, "catnum")
    #if catnum < 8:
    for x in range(1, 8-catnum+1):
        if len(colors) > 0:
            colors.pop()

    for color in reversed(colors):
        if cID >= 0:
            colormap.append(color)
            output = output + ' ' + color
        cID = cID + 1

    output = ''
    id = 0
    scales = {}
    for thisrange in rangearr:
        output = output + ' ' + thisrange + '=' + str(id) + '<br>'
        color = colormap[id]
        savecolor = {}
        savecolor['color'] = color
        savecolor['range'] = thisrange
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
    #paramrange = request.args.get('datarange')
    paramrange = check_value_pattern(request.args.get('datarange'), datarangePattern, '', '18datarange')
    #paramyear = request.args.get('year')
    paramyear = check_value_pattern(request.args.get('year'), yearPattern, defaultYearIfYearIncorrect, '18year')
    #paramoutput = request.args.get('output')
    paramoutput = check_value_pattern(request.args.get('output'), outputPattern, '', '18output')
    #paramscales = request.args.get('scales')
    paramscales = check_value_pattern(request.args.get('scales'), scalesPattern, '', '18scales')
    #paramcat = request.args.get('categories')
    paramcat = check_value_pattern(request.args.get('categories'), categoriesPattern, '', '18categories')
    catnum = 8

    if paramrange:
        datarange = paramrange

    if paramyear:
        year = paramyear

    if paramoutput:
        output = paramoutput

    if options['defaultcategories']:
        catnumint = int(options['defaultcategories'])

    if request.args.get('csv'):
        csvexport = 'yes'

    paramcode = check_value_pattern(request.args.get('code'), topicCodePattern, '', '19code')
    #if request.args.get('code'):
    if paramcode:
        #code = request.args.get('code')
        code = paramcode

    if paramcat:
        catnumint = paramcat
        try:
            catnum = int(catnumint)
        except:
            catnum = catnumint

    #realcatnum = analyze_data(cursor, catnum)
    #if realcatnum:
        #if realcatnum < catnum:
            #catnumX = realcatnum

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
        return Response(json_response)
    else:
        return Response(dataset, mimetype='application/json')

    #return Response(dataset, mimetype='application/json')

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
    #paramyear = request.args.get('year')
    paramyear = check_value_pattern(request.args.get('year'), yearPattern, defaultYearIfYearIncorrect, '21year')
    # format for polygons: geojson, topojson, kml
    #paramformat = request.args.get('format')
    paramformat = check_value_pattern(request.args.get('format'), formatPattern, '', '21format')
    #paramprovince = request.args.get('province')
    paramprovince = check_value_inarray(request.args.get('province'), Provinces, '', '21province')

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

    semicolon = re.split(pipes, cmd)
    cmd = semicolon[0]
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = json.dumps(p.stdout.read())
    json_response = json.loads(response)

    return Response(json_response,  mimetype='application/json;charset=utf-8')

if __name__ == '__main__':
    app.run()

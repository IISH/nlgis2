from flask import Flask, render_template
from flask import g
from flask import Response, make_response, request
from twisted.web import http
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required
import json
import urllib2
import glob
import csv
import sys
import psycopg2
import psycopg2.extras
import pprint
import getopt
import ConfigParser
import HTMLParser
from subprocess import Popen, PIPE, STDOUT
import simplejson

def connect():
        cparser = ConfigParser.RawConfigParser()
        cpath = "/etc/apache2/nlgiss2.config"
        cparser.read(cpath)

        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (cparser.get('config', 'dbhost'), cparser.get('config', 'dbname'), cparser.get('config', 'dblogin'), cparser.get('config', 'dbpassword'))

        # get a connection, if a connect cannot be made an exception will be raised here
        conn = psycopg2.connect(conn_string)

        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        cursor = conn.cursor()

        #(row_count, dataset) = load_regions(cursor, year, datatype, region, debug)
        return cursor

def readglobalvars():
    cparser = ConfigParser.RawConfigParser()
    cpath = "/etc/apache2/nlgiss2.config"
    cparser.read(cpath)
    path = cparser.get('config', 'path')
    geojson = cparser.get('config', 'geojson')
    website = cparser.get('config', 'website')
    server =  cparser.get('config', 'serverip')
    api_topics_url = server + '/api/topics?'

    # Default year from configuration
    configyear = cparser.get('config', 'year')
    # or year from cookies
    cookieyear = request.cookies.get('year')
    configcode = cparser.get('config', 'code')
    cookiecode = request.cookies.get('code')
    cookiedatarange = request.cookies.get('datarange')
    viewerpath = cparser.get('config', 'viewerpath')
    imagepathloc = cparser.get('config', 'imagepathloc')
    imagepathweb = cparser.get('config', 'imagepathweb')
    viewerpath = cparser.get('config', 'viewerpath')
    path = cparser.get('config', 'path')
    geojson = cparser.get('config', 'geojson')
    configdatarange = cparser.get('config', 'range')

    cmdgeo = ''

    # get year from API call
    paramyear = request.args.get('year')
    # format for polygons: geojson, topojson, kml
    paramcode = request.args.get('code')
    paramdatarange = request.args.get('datarange')
    year = configyear
    code = configcode
    datarange = configdatarange
    if cookieyear:
       year = cookieyear
    if cookiecode:
       code = cookiecode
    if cookiedatarange:
       datarange = cookiedatarange
    if paramyear:
       year = paramyear
    if paramcode:
       code = paramcode
    if paramdatarange:
       datarange = paramdatarange

    return (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange)

def load_api_data(apiurl, code, year):
    amscode = str(code)
    jsondataurl = apiurl 
    if code:
        jsondataurl = jsondataurl + "&code=" + str(code)
    if year:
        jsondataurl = jsondataurl + '&year=' + str(year)
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def loadcodes(api_topics_url, code, year):
    codes = []
    data = load_api_data(api_topics_url, '', year)
    apicodes = []
    indicators = {}
    for item in data['codes']:
       apicodes.append(item['code'])
       indicators[item['code']] = item['topic_name']

    if apicodes:
       codes = apicodes
    else:
       codes.append(code);
    return (codes, indicators)

def load_topics(cursor):
        data = {}
        sql = "select distinct code, indicator from datasets.data";
        #sql = sqlfilter(sql)

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'data', data)

        return jsondata


app = Flask(__name__)
#Bootstrap(app)

@app.route('/info')
def test():
    description = 'nlgis2 API Service v.0.1<br>/api/maps (map polygons)<br>/api/data (data services)<br>/demo web demo<br>'
    return description

@app.route('/slider')
def slider():
    #return 'slider'
    return render_template('slider.html')

@app.route('/d3map')
def d3map(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    (codes, indicators) = loadcodes(api_topics_url, code, year)
    resp = make_response(render_template('d3colored.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code, indicators=indicators))
    return resp

@app.route('/site')
def d3site(settings=''):
    selectedcode = {}
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    (codes, indicators) = loadcodes(api_topics_url, code, year)
    selectedcode[code] = indicators[code]
    indicators.pop(code, "none");
    resp = make_response(render_template('site.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, indicators=indicators, datarange=datarange, selectedcode=selectedcode))
    return resp

@app.route('/history')
def history(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    codes = loadcodes(api_topics_url, code, year)
    resp = make_response(render_template('site_history.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code))
    return resp

@app.route('/developers')
def developers(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    codes = loadcodes(api_topics_url, code, year)
    resp = make_response(render_template('site_developers.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code))
    return resp

@app.route('/index')
def d3index(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    resp = make_response(render_template('index.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year))
    return resp

@app.route('/d3movie')
def d3movie(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    resp = make_response(render_template('d3movie.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year))
    return resp

@app.route('/advanced')
def advanced(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()

    for name in request.cookies:
	settings = settings + ' ' + name + '=' + request.cookies[name]	
    #return settings

    image = imagepathweb + '/' + year + '.png';

    settings = ''
    resp = make_response(render_template('advanced.html', image=image, settings=settings, r=request.cookies))
  
    # Cookie revision
    for name in request.cookies:
	on = request.cookies[name]
        try: 
	    if request.args[name]: 
	        i = 1
	except:
	    if on == 'on':
		erase[name] = on
	        resp.set_cookie(name, '')

    for name in request.args:
        resp.set_cookie(name, request.args[name])

    return resp

@app.route('/', methods=['GET', 'POST'])
def index(year=None,code=None):
    cmdgeo = ''
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange) = readglobalvars()
    api_topics_url = server + '/api/topics?'

    str = 'Website will be developed to render maps'
    html_code = '<select name=code>' + '<option value\=' + code + '>' + code + '</option>' '</select>'
    year_code = '&nbsp;<input type=text name=year value=' + year + '>&nbsp;<input type=submit name="Submit">';
    #  /home/slava/nlgis2/maps/usecases/maprender.py '10426' 1997 /etc/apache2/htdocs/images/1111

    cmd = viewerpath + ' ' + '""' + ' ' + year + ' ' + imagepathloc + '/' + year + '.png'  
    #cmd = '/bin/echo test'

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    #response = json.dumps(p.stdout.read()
    result = p.communicate()[0]
    #return cmd
    html = result + '<form>' + html_code + year_code + '<br>' + '<img width=1024 src=\"' + imagepathweb + '/' + year + '.png\">' + '</form>'
    image = imagepathweb + '/' + year + '.png';
    codes = loadcodes(api_topics_url, code, year)

    resp = make_response(render_template('demo.html', codes=codes, year=year, image=image))
    for name in request.args:
       resp.set_cookie(name, request.args[name])

    resp.set_cookie('year', year)
    resp.set_cookie('code', code)
    return resp

if __name__ == '__main__':
    app.run()

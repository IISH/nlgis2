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

from flask import Flask, render_template
from flask import g
from flask import Response, make_response, request, send_from_directory
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
import re
import os
from werkzeug import secure_filename

Provinces = ["Groningen","Friesland","Drenthe","Overijssel","Flevoland","Gelderland","Utrecht","Noord-Holland","Zuid-Holland","Zeeland","Noord-Brabant","Limburg"]

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
    custom = ''

    # get year from API call
    paramyear = request.args.get('year')
    # format for polygons: geojson, topojson, kml
    paramcode = request.args.get('code')
    paramdatarange = request.args.get('datarange')
    year = configyear
    code = configcode
    datarange = configdatarange
    if request.args.get('custom'):
       custom = request.args.get('custom')
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

    try:
	if int(year) > 1997:
	    year = '1982'
    except:
	donothing = 1

    return (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom)

def load_api_data(apiurl, code, year, custom, scales, catnum):
    if code:
       amscode = str(code)
    jsondataurl = apiurl 
    if code:
        jsondataurl = jsondataurl + "&code=" + code
    if year:
        jsondataurl = jsondataurl + '&year=' + str(year)
    if custom:
	jsondataurl = jsondataurl + '&custom=' + custom
    if scales:
        jsondataurl = jsondataurl + '&scales=' + scales
    if catnum:
	jsondataurl = jsondataurl + '&categories=' + str(catnum)
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    if scales:
        dataframe = urllib2.urlopen(req).read()
    else:
        dataframe = simplejson.load(f)
    return dataframe

def loadyears(api_years_url, code, year, custom):
    years = []
    data = load_api_data(api_years_url, code, '', custom, '', '')
    apiyears = []
    indicators = {}
    for item in data['years']:
       apiyears.append(item['year'])
       indicators[item['year']] = item['count']

    if apiyears:
       apiyears = apiyears
    else:
       years.append(year);

    return (apiyears, indicators)

def loadcodes(api_topics_url, code, year, custom):
    codes = []
    data = load_api_data(api_topics_url, '', year, custom, '', '')
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

@app.route('/info')
def test():
    description = 'nlgis2 API Service v.0.1<br>/api/maps (map polygons)<br>/api/data (data services)<br>/demo web demo<br>'
    return description

@app.route('/slider')
def slider():
    #return 'slider'
    return render_template('slider.html')

@app.route('/members')
def members():
    return render_template('members.html')

@app.route('/d3map')
def d3map(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    (codes, indicators) = loadcodes(api_topics_url, code, year, custom)
    resp = make_response(render_template('d3colored.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code, indicators=indicators))
    return resp

ALLOWED_EXTENSIONS = set(['xls', 'xlsx', 'csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(upload_folder, path):
    upload_folder = upload_folder + '/custom'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
	    datafile = upload_folder + '/' + filename
	    cmd = path + "/scripts/etl/custom_import.pl " + datafile
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            result = p.communicate()[0]
            return datafile 
    return

@app.route('/site', methods=['GET', 'POST'])
def d3site(settings=''):
    selectedcode = {}
    custom_selectedcode = {}
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    #custom = ''
    province = ''
    provinces = Provinces
    apiurl = '/api/maps?' #year=' + year
    dataurl = '/api/data?'
    scaleurl = '/api/scales?'
    mapscale = 6050
    dataapiurl = dataurl + 'code=' + code
    api_topics_url = server + '/api/topics?'
    upload_file(imagepathloc, path)
    thiscustom = custom
    thiscode = code
    if not custom:
        thiscustom = ''
        #thiscode = ''

    (codes, indicators) = loadcodes(api_topics_url, thiscode, year, thiscustom)
    if thiscode:
        selectedcode[thiscode] = indicators[thiscode]
        indicators.pop(thiscode, "none");
    api_years_url = server + '/api/years?'
    (years, yearsinfo) = loadyears(api_years_url, code, '', thiscustom)

    # for custom datasets
    intcustom = 'on'
    if custom:
        intcustom = ''
	#code = ''
    (custom_codes, custom_indicators) = loadcodes(api_topics_url, code, year, intcustom)
#    custom_selectedcode[code] = custom_indicators[code]
    custom_indicators.pop(code, "none");
    (custom_years, custom_yearsinfo) = loadyears(api_years_url, code, '', intcustom)

    showlegend='true';
    if request.args.get('nolegend'):
	showlegend = ''
    
    template = 'site_tabs.html'
    if custom:
        template = 'site_tabs_custom.html'

    legendscales = ["100-200","50-99", "10-49", "1-9", "0-1"]
    # DATAAPI
    scale = 'mean'
    catnum = 8 
    thisscale = load_api_data(server + scaleurl, code, year, thiscustom, scale, catnum)
    ranges = json.loads(thisscale)
    colors = []
    scales = []
    out = ''
    for sector in sorted(ranges):
        dataitem = ranges[sector]
        colors.append(dataitem['color'])
        scales.append(dataitem['range'])
	out = out + ' ' + dataitem['color']

    urlvar = '' #api_years_url + code
    ranges = thisscale.split(', ')
    if thisscale:
	legendscales = scales
	legendcolors = colors

    if request.args.get('province'):
	province = request.args.get('province')
	provinces.remove(province)
	mapscale = mapscale * 2

    resp = make_response(render_template(template, topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, indicators=indicators, datarange=datarange, selectedcode=selectedcode, thiscode=code, showlegend=showlegend, allyears=years, custom=custom, custom_indicators=custom_indicators, custom_allyears=custom_years, legendscales=legendscales, legendcolors=legendcolors, urlvar=urlvar, categories=catnum, province=province, provinces=provinces, mapscale=mapscale))
    return resp

@app.route('/download')
def download(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    year = str(year)
    format = 'png'
    svgfileout = ''
    province = ''
    pdffile = ''
    shapefile = ''
    paramformat = request.args.get('format')
    if paramformat:
        format = paramformat
    if request.args.get('province'):
        province = request.args.get('province')

    filesvg = imagepathloc + '/' + year + '_' + code + '_' + "map.svg"
    if format == 'shapefile':
	year = year
    else:
        cmd = path + "/node_modules/phantomjs/lib/phantom/bin/phantomjs " + path + "/web/demo/static/renderHTML.js '" + website + "/site?nolegend=yes&year=" + year + "&code=" + code + "&province=" + province + "&custom=" + custom + "'"
        #cmd = '/bin/echo test'

        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        html = p.communicate()[0]
        result = re.findall(r'<svg.+?</svg>', html, re.DOTALL)
        if year:
            svgfile = open(filesvg, "w")
            svgfile.write(result[0])
            svgfile.close()

    size = str(1524);
    if format == 'SVG':
        svgfileout = '/get?svg=' + year + '_' + code + '_' + "map.svg"
        return "<a href=\"" + svgfileout + "\">Download SVG file</a>"
        fileonweb = ''

    if format == 'png':
        outfile = year + '_' + code + '_' + 'map.png'
        outdirfile = imagepathloc + '/' + outfile
        cmd = "/usr/bin/inkscape " + filesvg + " -e " + outdirfile + " -h " + size + " -D -b '#ffffff'"
	fileonweb = '/get?image=' + outfile

    if format == 'shapefile':
	thisfilter = year + '_' + code + '_'
	infile = year + '_' + code + '_' + 'tmp.json'
        outfile = year + '_' + code + '_' + 'tmp.shp'
	indirfile = imagepathloc + '/' + infile
        outdirfile = imagepathloc + '/' + outfile
	webapicmd = website + "/api/maps?format=geojson&year=" + year 
	if province:
	    webapicmd = webapicmd + "&province=" + province
	
	cmd = "/usr/bin/wget \"" + webapicmd +"\" -O " + indirfile
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = p.communicate()[0]
	cmd = "/usr/bin/ogr2ogr -f \"ESRI Shapefile\" " + outdirfile + " " + indirfile
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = p.communicate()[0]
	if outdirfile:
	   cmd = "cd " + imagepathloc + ";tar -cf " + thisfilter + ".tar *" + thisfilter + "*;gzip " + thisfilter + ".tar;rm -rf *" + thisfilter + "*tmp*" 
	   shapefile = '/get?nlgis=' + thisfilter + ".tar.gz"

    if format == 'pdf':
        outfile = year + '_' + code + '_' + 'map.PDF'
        outdirfile = imagepathloc + '/' + outfile	
	cmd = "/usr/bin/inkscape " + filesvg + " --export-pdf=" + outdirfile + " -D -b '#ffffff'"
	fileonweb = ''
	pdffile = '/get?pdf=' + outfile

    if cmd:
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = p.communicate()[0]
        image = outfile

    if shapefile:
        return "<a href=\"" + shapefile + "\">Download ShapeFile</a>"
    resp = make_response(render_template('download.html', image=fileonweb, svgfile=svgfileout, pdffile=pdffile))
    return resp

@app.route('/history')
def history(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    codes = loadcodes(api_topics_url, code, year, custom)
    resp = make_response(render_template('menu_history.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code))
    return resp

@app.route('/tabs')
def tabs(settings=''):
    selectedcode = {}
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    #custom = ''
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    upload_file(imagepathloc, path)
    (codes, indicators) = loadcodes(api_topics_url, code, year, custom)
    selectedcode[code] = indicators[code]
    indicators.pop(code, "none");
    api_years_url = server + '/api/years?'
    (years, yearsinfo) = loadyears(api_years_url, code, '', custom)

    showlegend='true';
    if request.args.get('nolegend'):
        showlegend = ''

    resp = make_response(render_template('tabs.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, indicators=indicators, datarange=datarange, selectedcode=selectedcode, thiscode=code, showlegend=showlegend, allyears=years, custom=custom))
    return resp

@app.route('/developers')
def developers(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    codes = loadcodes(api_topics_url, code, year, custom)
    resp = make_response(render_template('menu_developers.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code, website=website))
    return resp

@app.route('/presentation')
def presentation(settings=''):
    resp = make_response(render_template('menu_presentation.html'))
    return resp

@app.route('/')
def start(settings=''):
    resp = make_response(render_template('menu_start.html'))
    return resp

@app.route('/about')
def about(settings=''):
    resp = make_response(render_template('menu_about.html'))
    return resp

@app.route('/get')
def get(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    image = request.args.get('image')
    gzip = request.args.get('nlgis')
    svg = request.args.get('svg')
    pdf = request.args.get('pdf')
    outfile = ''

    thismimetype='image'
    if image:
	outfile = image
    if gzip:
	thismimetype = 'application/x-gzip'
	outfile = gzip
    if svg:
	thismimetype = 'text/plain'
	outfile = svg
    if pdf:
	thismimetype = 'application/pdf'
	outfile = pdf
  	
    if image:
        return send_from_directory(imagepathloc, outfile, mimetype=thismimetype)
    else:
	return send_from_directory(imagepathloc, outfile, as_attachment=True)
 	#return outfile + ' not found'

@app.route('/datasets')
def datasets(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    topicapiurl = website + "/api/topicslist"
    topicstats = load_api_data(topicapiurl, '', '', '', '', '')
    localfile = 'index.csv'
    filename = imagepathloc + '/' + localfile
    f = csv.writer(open(filename, "wb+"))

    varlist = []
    firstline = 0
    for code in sorted(topicstats):
        dataset = topicstats[code]
        mapurl = website + "/site?code=" + dataset['topic_code'] + "&year=" + str(dataset['startyear'])
        dataurl = website + '/api/data?code=' + dataset['topic_code']
        topicstats[code]['urlmap'] = mapurl
        topicstats[code]['urldata'] = dataurl
        datarow = []    
        if firstline == 0:
            for row in sorted(dataset):
                varlist.append(row)    
            f.writerow(varlist)
            firstline = 1
        
        for row in sorted(dataset):        
            datarow.append(dataset[row])
        f.writerow(datarow) 
    return send_from_directory(imagepathloc, localfile, as_attachment=True)

@app.route('/index')
def d3index(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    topicapiurl = website + "/api/topicslist"
    topicstats = load_api_data(topicapiurl, '', '', '', '', '')
    topiclist = []
    thisletter = ''
    letters = []
    if topicstats:
        for code in sorted(topicstats):
	    topiclist.append(topicstats[code])
            dataset = topicstats[code]
	    letter = dataset['letter']
            url = "/site?code=" + dataset['topic_code'] + "&year=" + str(dataset['startyear'])
	    topicstats[code]['url'] = url
	    if thisletter == letter:
		topicstats[code]['letter'] = ''
	    else:
	        thisletter = letter
		letters.append(letter)

    resp = make_response(render_template('datasetlist.html', letters=letters, topiclist=topiclist))
    return resp

@app.route('/d3movie')
def d3movie(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    resp = make_response(render_template('d3movie.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year))
    return resp

@app.route('/advanced')
def advanced(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()

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

@app.route('/old', methods=['GET', 'POST'])
def index(year=None,code=None):
    cmdgeo = ''
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
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
    codes = loadcodes(api_topics_url, code, year, custom)

    resp = make_response(render_template('demo.html', codes=codes, year=year, image=image))
    for name in request.args:
       resp.set_cookie(name, request.args[name])

    resp.set_cookie('year', year)
    resp.set_cookie('code', code)
    return resp

if __name__ == '__main__':
    app.run()

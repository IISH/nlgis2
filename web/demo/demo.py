from flask import Flask, render_template
from flask import Response, request
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
    description = 'nlgis2 API Service v.0.1<br>/api/maps (map polygons)<br>/api/data (data services)<br>'
    return description

@app.route('/')
def index():
    #cursor = connect()
    #data = load_topics(cursor)
    cparser = ConfigParser.RawConfigParser()
    cpath = "/etc/apache2/nlgiss2.config"
    cparser.read(cpath)
    path = cparser.get('config', 'path')
    geojson = cparser.get('config', 'geojson')

    # Default year
    year = cparser.get('config', 'year')
    code = cparser.get('config', 'code')
    imagepath = cparser.get('config', 'imagepath')
    cmdgeo = ''
    # get year from API call
    paramyear = request.args.get('year');
    # format for polygons: geojson, topojson, kml
    paramcode = request.args.get('code');
    if paramyear:
        year = paramyear
    if paramcode:
 	code = paramcode
    #return 'test1'

    str = 'Website will be developed to render maps'
    html_code = '<select option=1>' + code + '</select>'
    #showyear = str(year)
    html = html_code + year + '<br>' + '<img width=1024 src=\"/images/1997.png\">'
    return html

if __name__ == '__main__':
    app.run()

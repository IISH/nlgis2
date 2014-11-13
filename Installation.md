# NLGIS Installation
## Installing prerequisites

sudo apt-get install build-essential

## Installation instructions
```
apt-get install postgresql-8.4
apt-get install postgresql-server-dev-8.4
apt-get install mongodb
apt-get install apache2
apt-get install libapache2-mod-wsgi
apt-get install git
apt-get install python-pip
apt-get install gdal-bin
apt-get install python-dev
apt-get install python-gdal
apt-get install g++
apt-get install inkscape
sudo apt-get update
sudo apt-get install python-software-properties python g++ make
sudo add-apt-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
sudo npm install -g topojson
To verify the two installations, try
which ogr2ogr
which topojson
```
This should print /usr/local/bin/ogr2ogr and /usr/local/bin/topojson

## Python packages
```
pip install flask
pip install twisted
pip install flask_bootstrap
pip install flask_appconfig
pip install flask_wtf
pip install psycopg2
pip install simplejson
pip install xlwt
pip install numpy --upgrade
pip install pandas
pip install pymongo
pip install brewer2mpl
```

### Change default encoding:
sudo vi /usr/lib/python2.7/site.py
Change
encoding = "ascii"
to
encoding = "utf8"

## NLGIS installation from github

useradd -m nlgis
passwd nlgis
su - nlgis
git clone https://github.com/rlzijdeman/nlgis2.git
NLGIS source code will be installed in /home/nlgis/nlgis2 folder.
cd nlgis2
sudo npm install phantomjs
should produce output:
"Done. Phantomjs binary available at /home/nlgis/nlgis2/node_modules/phantomjs/lib/phantom/bin/phantomjs"

Create folder for temporary files (images, PDFs, etc) on hard drive, for example /var/www/tmp (variable imagepathloc in configuration file)
mkdir /var/www/tmp
chmod 755 /var/www/tmp

## Configure the Apache Web server

cd /etc/apache2/available-sites
vi default
Add lines there after DocumentRoot section:
WSGIScriptAlias /api /home/nlgis/nlgis2/web/api/api.wsgi
WSGIScriptAlias /demo /home/nlgis/nlgis2/web/demo/demo.wsgi
WSGIProcessGroup api
WSGIProcessGroup demo
WSGIApplicationGroup %{GLOBAL}
vi /etc/apache2/apache2.conf
Add lines below:
WSGISocketPrefix /var/run/wsgi
WSGIDaemonProcess api user=nlgis group=nlgis processes=5 threads=25
WSGIDaemonProcess demo user=nlgis group=nlgis processes=5 threads=25
/etc/init.d/apache2 restart

## Creating and importing NLGIS2 database

/etc/init.d/mongodb start
/etc/init.d/postgresql start
su - postgres
createdb nlgis_data
createdb nlgis_test
createuser nlgisuser
wget node-128.dev.socialhistoryservices.org/tmp/nlgis_data.dump.gz
gzip -cd nlgis_data.dump.gz > nglis_data.dump
wget node-128.dev.socialhistoryservices.org/tmp/nlgis_test.dump.gz
gzip -cd nlgis_test.dump.gz > nlgis_test.dump
psql nlgis_data -f ./nlgis_data.dump
psql nlgis_test -f ./nlgis_test.dump
exit

### Make changes in postgresql configuration
sudo vi /etc/postgresql/8.4/main/postgresql.conf
and change line
#listen_addresses = 'localhost'
to
listen_addresses = '*'
sudo vi /etc/postgresql/8.4/main/pg_hba.conf
Change "md5" to "trust":
# IPv4 local connections:
host all all 127.0.0.1/32 trust
/etc/init.d/postgresql restart

## Loading GIS data to MongoDB

cd /home/nlgis/nlgis2/data
wget node-128.dev.socialhistoryservices.org/tmp/mongo.tar
tar xvf mongo.tar
mongorestore

## NLGIS2 configuration 

Configuration file can be stored in /etc/apache2/nlgiss2.config
[config]
website =  http://your-nlgis.nl
serverip = http://192.168.1.1
path = /home/nlgis/nlgis2
year = 1997
code = TXGE
imagepathloc = /var/www/tmp
imagepathweb = /tmp
viewerpath = /home/nlgis/nlgis2/maps/usecases/maprender.py
geojson = geojson
dbhost = localhost
dbname = nlgis_your_data
customdbname = nlgis_your_test
dblogin = nlgisyouruser
dbpassword = nlgiss_yourpassword
range = calculate
[dataoptions]
missingdata = #ffffdd
colormaps = Paired, Greens, Blues
datanature = Qualitative, sequential, diverging
defaultcategories = 4
defaultnature = Qualitative
defaultmap = Paired
reverse = false

## Test Data API and GEO API

Go to http://your-nlgis.nl/api/data?code=TXVV
You should be able to see data from dataset.

Go to http://your-nlgis.nl/api/maps?year=1997
You should see json output with map polygons

Finally open website 
http://your-nlgis.nl/demo/site?code=TXCE&year=1986
Website with list of indicators and rendered map should be shown.

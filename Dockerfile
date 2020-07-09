FROM ubuntu:12.04
LABEL Description="nlgis2 " Version="1.0"

ENV NLGIS_PROXY_DOMAIN="127.0.0.1"
ENV NLGIS_PROXY_PROTOCOL="http"
ENV NLGIS_USER="nlgis"
ENV NLGIS_PASSWORD="nlgis"

RUN apt-get update && \
    apt-get -y install wget build-essential postgresql-9.1 postgresql-server-dev-9.1 mongodb apache2 \
    libapache2-mod-wsgi gdal-bin python-software-properties python python-dev python-gdal g++ make inkscape && \
    wget "https://bootstrap.pypa.io/get-pip.py" -O /opt/get-pip.py && python /opt/get-pip.py && \
    add-apt-repository ppa:chris-lea/node.js -y && \
    apt-get update && \
    apt-get -y install nodejs && \
    npm install -g topojson && \
    sed -i -e 's/encoding = "ascii"/encoding = "utf8"/g' /usr/lib/python2.7/site.py && \
    mkdir -p /data/db /var/www/tmp/custom /var/run/apache2 /var/run/postgresql && touch /etc/apache2/nlgiss2.config && touch /var/run/apache2.pid && \
    useradd -ms /bin/bash ${NLGIS_USER} && useradd -m nlgis_test && \
    mv /etc/ssl/private/ssl-cert-snakeoil.key /var/lib/postgresql/9.1/main/server.key && \
    rm /etc/apache2/sites-enabled/* && \
    chown -R nlgis:nlgis /etc/init.d/apache2 /var/run/apache2.pid /var/log/apache2 /var/run/apache2 /var/log/postgresql /etc/init.d/postgresql \
        /var/run/postgresql /var/lib/postgresql /usr/share/postgresql-common /etc/apache2/nlgiss2.config /data \
        /etc/hosts /etc/postgresql/9.1 /var/lib/postgresql /etc/apache2/nlgiss2.config

COPY . /home/${NLGIS_USER}/nlgis2

RUN cp /home/${NLGIS_USER}/nlgis2/conf/nlgis.conf /etc/apache2/sites-available/nlgis.conf && \
    cp /home/${NLGIS_USER}/nlgis2/conf/envvars.txt /etc/apache2/envvars && \
    ln -s /etc/apache2/sites-available/nlgis.conf /etc/apache2/sites-enabled/nlgis.conf && \
    echo "Listen 8080" > /etc/apache2/ports.conf && \
    echo "nojournal = true" > /etc/mongodb.conf

RUN chmod -R 777 /var/www/tmp && \
    cd /home/${NLGIS_USER}/nlgis2 && npm install phantomjs && \
    pip install -r requirements.txt --ignore-installed && pip install numpy --upgrade && \
    chown -R ${NLGIS_USER}:${NLGIS_USER} /home/${NLGIS_USER} /var/www/tmp && chmod 744 /home/${NLGIS_USER}/nlgis2/run.sh

EXPOSE 8080

USER ${NLGIS_USER}
CMD ["/home/nlgis/nlgis2/run.sh"]
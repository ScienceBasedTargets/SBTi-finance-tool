FROM python:3.6

COPY requirements.txt config/config.yaml setup.py /project/

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install uwsgi \
 && pip3 install -r /project/requirements.txt \
 && rm -r /root/.cache

ARG uid=210
ARG gid=210

RUN groupadd -g ${gid} dock_sbtiapi \
 && useradd -u ${uid} -g ${gid} dock_sbtiapi \
 && mkdir /home/dock_sbtiapi \
 && chown -R dock_sbtiapi:dock_sbtiapi /home/dock_sbtiapi

RUN rm /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default \
 && mkdir -p /vol/log/nginx /vol/tmp/nginx /vol/tmp/uwsgi \
 && touch /vol/log/nginx/{access.log,error.log} \
 && rm -rf /var/log/nginx \
 && ln -s /vol/log/nginx /var/log/nginx

COPY app /project/app
COPY SBTi /project/SBTi
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/flask-site-nginx.conf /etc/nginx/sites-available/flask-site-nginx.conf
COPY config/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY config/supervisord.conf /etc/supervisord.conf


RUN ln -s /etc/nginx/sites-available/flask-site-nginx.conf /etc/nginx/sites-enabled/flask-site-nginx.conf \
 && chown -R dock_sbtiapi:dock_sbtiapi /project /vol

WORKDIR /project
RUN python /project/setup.py install

USER dock_sbtiapi
EXPOSE 80
CMD ["/usr/bin/supervisord"]

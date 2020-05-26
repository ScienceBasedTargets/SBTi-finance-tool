FROM python:3.6

COPY requirements.txt config.yaml setup.py /project/

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libatlas-base-dev gfortran nginx supervisor \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install uwsgi \
 && pip3 install -r /project/requirements.txt \
 && rm -r /root/.cache

ARG uid=210
ARG gid=210

RUN groupadd -g ${gid} dock_wigapi \
 && useradd -u ${uid} -g ${gid} dock_wigapi \
 && mkdir /home/dock_wigapi \
 && chown -R dock_wigapi:dock_wigapi /home/dock_wigapi

RUN rm /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default \
 && mkdir -p /vol/log/nginx /vol/tmp/nginx /vol/tmp/uwsgi \
 && touch /vol/log/nginx/{access.log,error.log} \
 && rm -rf /var/log/nginx \
 && ln -s /vol/log/nginx /var/log/nginx

COPY nginx.conf /etc/nginx/nginx.conf
COPY flask-site-nginx.conf /etc/nginx/sites-available/flask-site-nginx.conf
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY supervisord.conf /etc/supervisord.conf
COPY app /project/app
COPY wig /project/wig

RUN python /project/setup.py develop

RUN ln -s /etc/nginx/sites-available/flask-site-nginx.conf /etc/nginx/sites-enabled/flask-site-nginx.conf \
 && chown -R dock_wigapi:dock_wigapi /project /vol

USER dock_wigapi

WORKDIR /project

CMD ["/usr/bin/supervisord"]

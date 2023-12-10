FROM python:3.10-alpine

# This hack is widely applied to avoid python printing issues in docker containers.
# See: https://github.com/Docker-Hub-frolvlad/docker-alpine-python3/pull/13
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
        freetype \
        libpng \
        libjpeg-turbo \
        freetype-dev \
        libpng-dev \
        jpeg-dev \
        libjpeg \
        libjpeg-turbo-dev \
        sqlite && \
    pip install --upgrade pip setuptools virtualenv && \
    rm -r /root/.cache

WORKDIR /app

VOLUME /app

RUN virtualenv ./env
RUN ./env/bin/pip install pytz dateutils

COPY ./wnframework ./wnframework
COPY ./wnframework-modules ./wnframework-modules
COPY ./server.py .
COPY ./startup.sh .

RUN chmod a+x ./startup.sh
RUN chmod a+x ./wnframework/v170/index.py
RUN chmod a+x ./wnframework/v170/cgi-bin/getfile.py
RUN chmod a+x ./wnframework/v170/cgi-bin/getjsfile.py


EXPOSE 8000

CMD ["sh", "/app/startup.sh"]
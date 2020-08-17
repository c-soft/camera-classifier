ARG BUILD_FROM=homeassistant/armv7-base-debian:latest   
FROM $BUILD_FROM

ENV LANG C.UTF-8

# Install requirements for add-on
#RUN apk add --no-cache python3 py3-pip
#RUN apk update && apk upgrade && apk add --no-cache python3 py3-pip make automake gcc g++ python3-dev 
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-setuptools python3-dev \    
    libpng-dev python3-opencv python3-scipy libhdf5-dev libatlas-base-dev libtiff5 libjpeg62 libsm6 libxext6 libxrender-dev libwebp-dev libglib2.0-0 make automake gcc g++ 
        
WORKDIR /app
COPY . /app

COPY pip.conf /etc/pip.conf

RUN pip3 install --upgrade pip
RUN pip3 install setuptools --upgrade
RUN pip3 install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/app/start.sh"]

LABEL io.hass.version="VERSION" io.hass.type="addon" io.hass.arch="armhf|aarch64|i386|amd64"

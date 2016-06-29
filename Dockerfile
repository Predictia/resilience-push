FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y wget python-numpy python-dateutil python-dev netcdf-bin libnetcdf-dev libhdf5-serial-dev
RUN wget https://netcdf4-python.googlecode.com/files/netCDF4-1.0.7.tar.gz && tar -xzvf netCDF4-1.0.7.tar.gz && cd netCDF4-1.0.7 && cp setup.cfg.template setup.cfg && sed -i '/\[options\]/a ncconfig=/usr/bin/nc-config' setup.cfg && sed -i '/\[options\]/a use_ncconfig=True' setup.cfg && python setup.py build && python setup.py install
RUN apt-get install -y python-requests

VOLUME ["/code", "/tmp"]
WORKDIR /code
ENTRYPOINT python run.py

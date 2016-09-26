FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y wget python-numpy python-dateutil python-dev netcdf-bin libnetcdf-dev libhdf5-serial-dev
RUN apt-get install -y python-requests python-pip
RUN pip install netCDF4==1.2.4

VOLUME ["/code", "/tmp"]
WORKDIR /code
ENTRYPOINT python run.py

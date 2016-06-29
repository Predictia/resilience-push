from common import *

import csv
import numpy as np
from numpy import arange, dtype
import netCDF4
from netCDF4 import num2date, date2num
from datetime import datetime, timedelta
import glob
import json

def read_data(global_file_location, json_file_location):
    data = {}
    with open(global_file_location) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            data[int(row['cellID'])] = row
    print "Readed CSV file ..."
    for json_file in glob.glob(json_file_location):
        with open(json_file) as data_file:
            json_data = json.load(data_file)
            row = data[json_data['id']]
            for observation in json_data['observations']:
                if not 'observations' in row.keys():
                    row['observations'] = []
                row['observations'].append(observation)
    print "Readed JSON files ..."
    return data

def write_observations_nc(out_location, global_file_location, json_file_location):
    data = read_data(global_file_location, json_file_location)
    rtimes = []
    for cell_id,row in data.items():
        if 'observations' in row.keys():
            for observation in row['observations']:
                rtimes.append(datetime(observation['year'], 1, 1))
            break
    rtimes = sorted(set(rtimes))
    rlons = np.array(sorted(set(map(lambda (key, row) : float(row['lon']), data.items()))))
    rlons = np.linspace(min(rlons),max(rlons),num=len(rlons))
    rlats = np.array(sorted(set(map(lambda (key, row) : float(row['lat']), data.items()))))
    rlats = np.linspace(min(rlats),max(rlats),num=len(rlats))
    ncout = create_nc(out_location, rlats, rlons, min(rtimes), max(rtimes))
    projection = create_projection(ncout)
    lats = ceate_latitude(ncout, rlats)
    lons = ceate_longitude(ncout, rlons)
    times = create_time(ncout, rtimes)
    ncvar = ncout.createVariable('windSpeed',np.float32,('time', 'latitude','longitude'), fill_value=9999)
    ncvar.grid_mapping = "projection"
    ncvar.units = "ms-1"
    arr = np.full((len(rtimes), len(rlats), len(rlons)), 9999, dtype=float)
    for cell_id,row in data.items():
        latIdx = (np.abs(rlats-float(row['lat']))).argmin()
        lonIdx = (np.abs(rlons-float(row['lon']))).argmin()
        if 'observations' in row.keys():
            for observation in row['observations']:
                timeIdx = rtimes.index(datetime(observation['year'], 1, 1))
                arr[timeIdx, latIdx, lonIdx] = observation['value']
    print "Defined data array ..."
    ncvar[:,:,:] = arr
    ncout.close()

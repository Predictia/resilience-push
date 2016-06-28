from common import *

import csv
import numpy as np
from numpy import arange, dtype
import netCDF4
from netCDF4 import num2date, date2num
from datetime import datetime, timedelta

def read_data(global_file_location):
    data = []
    with open('globalstats.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            data.append(row)
    return data

def write_global_nc(out_location, global_file_location, vtime):
    data = read_data(global_file_location)
    rlons = np.array(sorted(set(map(lambda row : float(row['lon']), data))))
    rlons = np.linspace(min(rlons),max(rlons),num=len(rlons))
    rlats = np.array(sorted(set(map(lambda row : float(row['lat']), data))))
    rlats = np.linspace(min(rlats),max(rlats),num=len(rlats))
    vtimes = [vtime]
    min_time = min(vtimes)
    max_time = max(vtimes) + timedelta(3*365/12)
    ncout = create_nc(out_location, rlats, rlons, min_time, max_time)
    projection = create_projection(ncout)
    lats = ceate_latitude(ncout, rlats)
    lons = ceate_longitude(ncout, rlons)
    times = create_time(ncout, vtimes)
    variables = []
    variables.append({'variableName': 'meanPrediction', 'unit': 'ms-1', 'type': np.float32, 'fill_value' : 9999})
    variables.append({'variableName': 'meanHistoric', 'unit': 'ms-1', 'type': np.float32, 'fill_value' : 9999})
    variables.append({'variableName': 'rpss', 'unit': None, 'type': np.float32, 'fill_value' : 9999})
    variables.append({'variableName': 'ocean', 'unit': None, 'type': np.int16, 'fill_value' : 255})
    variables.append({'variableName': 'power', 'unit': 'KW', 'type': np.float32, 'fill_value' : 9999})
    for variable in variables:
        variable['ncvar'] = ncout.createVariable(variable['variableName'],variable['type'],('time', 'latitude','longitude'), fill_value=variable['fill_value'])
        variable['ncvar'].grid_mapping = "projection"
        if variable['unit']:
            variable['ncvar'].units = variable['unit']
        if variable['type'] == np.int16:
            variable['arr'] = np.full((1, len(rlats), len(rlons)), variable['fill_value'], dtype=int)
        else:
            variable['arr'] = np.full((1, len(rlats), len(rlons)), variable['fill_value'], dtype=float)
    for row in data:
        latIdx = (np.abs(rlats-float(row['lat']))).argmin()
        lonIdx = (np.abs(rlons-float(row['lon']))).argmin()
        timeIdx = 0
        for variable in variables:
            value = float(row[variable['variableName']])
            if variable['type'] == np.int16:
                value = int(round(value))
            variable['arr'][timeIdx, latIdx, lonIdx] = value
    for variable in variables:
        variable['ncvar'][:, :, :] = variable['arr']

    ncout.close()

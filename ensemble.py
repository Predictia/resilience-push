from common import *

import csv
import numpy as np
from numpy import dtype
import glob
import json
from datetime import datetime, timedelta

def write_ensemble_nc(out_location, global_file_location, json_file_location, vtime):
    data = read_data(global_file_location, json_file_location)
    rlons = np.array(sorted(set(map(lambda (key, row) : float(row['lon']), data.items()))))
    rlons = np.linspace(min(rlons),max(rlons),num=len(rlons))
    rlats = np.array(sorted(set(map(lambda (key, row) : float(row['lat']), data.items()))))
    rlats = np.linspace(min(rlats),max(rlats),num=len(rlats))
    rmembers = []
    for cell_id,row in data.items():
        if not rmembers and row['forecasts']:
            rmembers = range(1, 1 + len(row['forecasts']))
            break
    vtimes = [vtime]
    min_time = min(vtimes)
    max_time = max(vtimes) + timedelta(3*365/12)
    ncout = create_nc(out_location, rlats, rlons, min_time, max_time)
    projection = create_projection(ncout)
    lats = ceate_latitude(ncout, rlats)
    lons = ceate_longitude(ncout, rlons)
    times = create_time(ncout, vtimes)
    ensemble = create_ensemble(ncout, rmembers)
    ncvar = ncout.createVariable('windSpeed',np.float32,('time', 'ensemble', 'latitude', 'longitude'), fill_value=9999)
    ncvar.grid_mapping = "projection"
    ncvar.unit = "ms-1"
    arr = np.full((1, len(rmembers), len(rlats), len(rlons)), 9999, dtype=float)
    for cell_id,row in data.items():
        latIdx = (np.abs(rlats-float(row['lat']))).argmin()
        lonIdx = (np.abs(rlons-float(row['lon']))).argmin()
        if 'forecasts' in row.keys():
            eIdx = 0
            for forecast in row['forecasts']:
                arr[0, eIdx, latIdx, lonIdx] = forecast
                eIdx = eIdx + 1
    print "Defined data array ..."
    ncvar[:,:,:,:] = arr
    ncout.close()

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
            row['forecasts'] = json_data['forecasts'][0]['values']
    print "Readed JSON files ..."
    return data

write_ensemble_nc("/tmp/enb.nc", "globalstats.csv", "*.json", datetime(2015,12,01))

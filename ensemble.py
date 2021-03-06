from common import *

import csv
import numpy as np
from numpy import dtype
import glob
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

def write_ensemble_nc(out_location, global_file_location, json_file_location):
    data = read_data(global_file_location, json_file_location)
    rlons = np.array(sorted(set(map(lambda (key, row) : float(row['lon']), data.items()))))
    rlons = np.linspace(min(rlons),max(rlons),num=len(rlons))
    rlats = np.array(sorted(set(map(lambda (key, row) : float(row['lat']), data.items()))))
    rlats = np.linspace(min(rlats),max(rlats),num=len(rlats))
    rmembers = []
    rtimes = []
    for cell_id,row in data.items():
        if 'forecasts' in row.keys():
            rtimes = sorted(set(row['forecasts'].keys()))
            firstRtimeFrcs = row['forecasts'][rtimes[0]]
            rmembers = range(1, 1 + len(firstRtimeFrcs))
            break
    vtimes = map(lambda rtime : rtime + relativedelta(months=1), rtimes)
    min_time = min(vtimes)
    max_time = max(vtimes) + relativedelta(months=3)
    ncout = create_nc(out_location, rlats, rlons, min_time, max_time)
    projection = create_projection(ncout)
    lats = ceate_latitude(ncout, rlats)
    lons = ceate_longitude(ncout, rlons)
    times = create_time(ncout, vtimes)
    ensemble = create_ensemble(ncout, rmembers)
    ncvar = ncout.createVariable('windSpeed',np.float32,('time', 'ensemble', 'latitude', 'longitude'), fill_value=9999)
    ncvar.grid_mapping = "projection"
    ncvar.units = "ms-1"
    arr = np.full((len(rtimes), len(rmembers), len(rlats), len(rlons)), 9999, dtype=float)
    for cell_id,row in data.items():
        if 'forecasts' in row.keys():
            latIdx = (np.abs(rlats-float(row['lat']))).argmin()
            lonIdx = (np.abs(rlons-float(row['lon']))).argmin()
            for rtime in row['forecasts'].keys():
                tIdx = rtimes.index(rtime)
                eIdx = 0
                for forecast in row['forecasts'][rtime]:
                    arr[tIdx, eIdx, latIdx, lonIdx] = forecast
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
            row['forecasts'] = {}
            for json_frcs in json_data['forecasts']:
                time = datetime.strptime(json_frcs['metadata']['predictionStartDate'], "%Y%m%d%H%MZ" )
                row['forecasts'][time] = json_frcs['values']
    print "Readed JSON files ..."
    return data

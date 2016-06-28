import csv
import numpy as np
from numpy import arange, dtype
import netCDF4
from netCDF4 import num2date, date2num
from datetime import datetime, timedelta
import glob
import json

data = {}
with open('globalstats.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    for row in reader:
        data[int(row['cellID'])] = row

print "Readed CSV file ..."

rlons = np.array(sorted(set(map(lambda (key, row) : float(row['lon']), data.items()))))
rlons = np.linspace(min(rlons),max(rlons),num=len(rlons))
rlats = np.array(sorted(set(map(lambda (key, row) : float(row['lat']), data.items()))))
rlats = np.linspace(min(rlats),max(rlats),num=len(rlats))
rmembers = []

for json_file in glob.glob("*.json"):
    with open(json_file) as data_file:
        json_data = json.load(data_file)
        row = data[json_data['id']]
        row['forecasts'] = json_data['forecasts'][0]['values']
        if not rmembers:
            rmembers = range(1, 1 + len(row['forecasts']))
        if len(rmembers) != len(row['forecasts']):
            print "Encontrados " + len(row['forecasts'])

print "Readed JSON files ..."

ncout = netCDF4.Dataset('/tmp/enb.nc','w')
vtimes = (datetime(2015,12,01))

ncout.createDimension('longitude', len(rlons))
ncout.createDimension('latitude', len(rlats))
ncout.createDimension('ensemble', len(rmembers))
ncout.createDimension('time', None)

ncout.Conventions = "CF-1.5"
ncout.institution = "IC3"

lats = ncout.createVariable('latitude',np.float64,('latitude',))
lats[:] = rlats
lats.units = 'degrees_north'
lats.standard_name = 'latitude'
lons = ncout.createVariable('longitude',np.float64,('longitude',))
lons[:] = rlons
lons.units = 'degrees_east'
lons.standard_name = 'longitude'
times = ncout.createVariable('time', np.float64, ('time',))
times.units = 'hours since 2000-01-01 00:00:00'
times.calendar = 'gregorian'
times[:] = date2num(vtimes, units = times.units, calendar = times.calendar)

ensemble = ncout.createVariable('ensemble',np.int16,('ensemble',))
ensemble[:] = rmembers
ensemble.standard_name = 'ensemble'

projection = ncout.createVariable('projection', np.float64)
projection.grid_mapping_name = "latitude_longitude"
projection.earth_radius = 6367470.0
projection.proj4 = "+proj=longlat +a=6367470 +e=0 +no_defs"

ncvar = ncout.createVariable('windSpeed',np.float32,('time', 'latitude', 'longitude', 'ensemble'), fill_value=9999)
ncvar.grid_mapping = "projection"
ncvar.unit = "ms-1"

from random import randint


arr = np.full((1, len(rlats), len(rlons), len(rmembers)), 9999, dtype=float)
for cell_id,row in data.items():
    latIdx = (np.abs(rlats-float(row['lat']))).argmin()
    lonIdx = (np.abs(rlons-float(row['lon']))).argmin()
    if 'forecasts' in row.keys():
        eIdx = 0
        for forecast in row['forecasts']:
            arr[0, latIdx, lonIdx, eIdx] = forecast
            eIdx = eIdx + 1

print "Defined data array ..."

ncvar[:,:,:,:] = arr

ncout.close()

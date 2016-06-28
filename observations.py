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
rtimes = []

for json_file in glob.glob("*.json"):
    with open(json_file) as data_file:
        json_data = json.load(data_file)
        row = data[json_data['id']]
        for observation in json_data['observations']:
            if 'observations' not in row.keys():
                row['observations'] = []
            rtimes.append(datetime(observation['year'], 1, 1))
            row['observations'].append(observation)

rtimes = sorted(set(rtimes))

print "Readed JSON files ..."

ncout = netCDF4.Dataset('/tmp/obs.nc','w')

ncout.createDimension('longitude', len(rlons))
ncout.createDimension('latitude', len(rlats))
ncout.createDimension('time', len(rtimes))

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
times[:] = date2num(rtimes, units = times.units, calendar = times.calendar)

projection = ncout.createVariable('projection', np.float64)
projection.grid_mapping_name = "latitude_longitude"
projection.earth_radius = 6367470.0
projection.proj4 = "+proj=longlat +a=6367470 +e=0 +no_defs"

ncvar = ncout.createVariable('windSpeed',np.float32,('time', 'latitude','longitude'), fill_value=9999)
ncvar.grid_mapping = "projection"
ncvar.unit = "ms-1"

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

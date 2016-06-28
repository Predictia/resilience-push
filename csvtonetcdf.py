import csv
import numpy as np
from numpy import arange, dtype
import netCDF4
from netCDF4 import num2date, date2num
from datetime import datetime, timedelta

data = []
with open('/home/kktuax/Downloads/globalstats.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    for row in reader:
        data.append(row)

rlons = np.array(sorted(set(map(lambda row : float(row['lon']), data))))
rlons = np.linspace(min(rlons),max(rlons),num=len(rlons))
rlats = np.array(sorted(set(map(lambda row : float(row['lat']), data))))
rlats = np.linspace(min(rlats),max(rlats),num=len(rlats))

ncout = netCDF4.Dataset('/tmp/out.nc','w')
vtimes = (datetime(2015,12,01))

ncout.createDimension('longitude', len(rlons))
ncout.createDimension('latitude', len(rlats))
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

projection = ncout.createVariable('projection', np.float64)
projection.grid_mapping_name = "latitude_longitude"
projection.earth_radius = 6367470.0
projection.proj4 = "+proj=longlat +a=6367470 +e=0 +no_defs"

variables = []
variables.append({'variableName': 'meanPrediction', 'unit': 'ms-1', 'type': np.float32, 'fill_value' : 9999})
variables.append({'variableName': 'meanHistoric', 'unit': 'ms-1', 'type': np.float32, 'fill_value' : 9999})
variables.append({'variableName': 'rpss', 'unit': None, 'type': np.float32, 'fill_value' : 9999})
variables.append({'variableName': 'ocean', 'unit': None, 'type': np.int16, 'fill_value' : 255})
variables.append({'variableName': 'power', 'unit': 'KW', 'type': np.float32, 'fill_value' : 9999})

for variable in variables:
    variable['ncvar'] = ncout.createVariable(variable['variableName'],variable['type'],('time', 'latitude','longitude'), fill_value=variable['fill_value'])
    variable['ncvar'][:,:,:] = variable['fill_value']
    variable['ncvar'].grid_mapping = "projection"
    if variable['unit']:
        variable['ncvar'].unit = variable['unit']
for row in data:
    latIdx = (np.abs(rlats-float(row['lat']))).argmin()
    lonIdx = (np.abs(rlons-float(row['lon']))).argmin()
    timeIdx = 0
    for variable in variables:
        value = float(row[variable['variableName']])
        if variable['type'] == np.int8:
            value = int(round(value))
        variable['ncvar'][timeIdx, latIdx, lonIdx] = value
ncout.close()

import csv
import numpy as np
from numpy import arange, dtype
import netCDF4
from netCDF4 import num2date, date2num
from datetime import datetime, timedelta
import glob
import json

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
    ncout = create_nc(out_location, rlats, rlons, vtimes)
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

def create_nc(out_location, rlats, rlons, vtimes):
    ncout = netCDF4.Dataset(out_location, 'w')
    ncout.Conventions = "CF-1.5"
    ncout.institution = "IC3"
    ncout.title = "Ensemble forecasts for wind speed at December to February season"
    ncout.description = "Ensemble forecasts for wind speed at December to February season"
    ncout.summary = "Ensemble forecasts for wind speed at December to February season"
    ncout.keywords = "EUPORIAS, IC3, resilience, wind-speed"
    ncout.activity = "EUPORIAS"
    ncout.project_id = "EUPORIAS"
    ncout.driving_model_id = "ECMWF S4"
    ncout.contact_email = "isadora.jimenez@bsc.es<mailto:isadora.jimenez@bsc.es>"
    ncout.time_coverage_start = min(vtimes).isoformat()
    ncout.time_coverage_end = (max(vtimes) + timedelta(3*365/12)).isoformat()
    ncout.geospatial_resolution = "0.7 degrees"
    ncout.geospatial_lat_min = min(rlats)
    ncout.geospatial_lat_max = max(rlats)
    ncout.geospatial_lon_min = min(rlons)
    ncout.geospatial_lon_max = max(rlons)
    return ncout

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

def ceate_latitude(ncout, rlats):
    ncout.createDimension('latitude', len(rlats))
    lats = ncout.createVariable('latitude',np.float64,('latitude',))
    lats[:] = rlats
    lats.units = 'degrees_north'
    lats.standard_name = 'latitude'
    return lats

def ceate_longitude(ncout, rlons):
    ncout.createDimension('longitude', len(rlons))
    lons = ncout.createVariable('longitude',np.float64,('longitude',))
    lons[:] = rlons
    lons.units = 'degrees_east'
    lons.standard_name = 'longitude'
    return lons

def create_time(ncout, vtimes):
    ncout.createDimension('time', None)
    times = ncout.createVariable('time', np.float64, ('time',))
    times.units = 'hours since 2000-01-01 00:00:00'
    times.calendar = 'gregorian'
    times[:] = date2num(vtimes, units = times.units, calendar = times.calendar)
    return times

def create_ensemble(ncout, rmembers):
    ncout.createDimension('ensemble', len(rmembers))
    ensemble = ncout.createVariable('ensemble',np.int16,('ensemble',))
    ensemble[:] = rmembers
    ensemble.standard_name = 'ensemble'
    return ensemble

def create_projection(ncout):
    projection = ncout.createVariable('projection', np.float64)
    projection.grid_mapping_name = "latitude_longitude"
    projection.earth_radius = 6367470.0
    projection.proj4 = "+proj=longlat +a=6367470 +e=0 +no_defs"
    return projection

write_ensemble_nc("/tmp/enb.nc", "globalstats.csv", "*.json", datetime(2015,12,01))

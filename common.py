import netCDF4
from netCDF4 import num2date, date2num
import numpy as np

def create_nc(out_location, rlats, rlons, min_time, max_time):
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
    ncout.time_coverage_start = min_time.isoformat()
    ncout.time_coverage_end = max_time.isoformat()
    ncout.geospatial_resolution = "0.7 degrees"
    ncout.geospatial_lat_min = min(rlats)
    ncout.geospatial_lat_max = max(rlats)
    ncout.geospatial_lon_min = min(rlons)
    ncout.geospatial_lon_max = max(rlons)
    return ncout

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

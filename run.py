from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
from summary import write_global_nc
from observations import write_observations_nc
from ensemble import write_ensemble_nc
from download import download_from_api
from upload import ftp_upload

work_dir = "/tmp/resilience-push"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

global_file_location = work_dir + "/globalstats.csv"
json_dir_location = work_dir + "/json"
json_file_location = json_dir_location + "/*.json"
if not os.path.exists(json_dir_location):
    os.makedirs(json_dir_location)

global_out_location = work_dir + "/out.nc"
ensemble_out_location = work_dir + "/enb.nc"
observations_out_location = work_dir + "/obs.nc"

ftime = datetime(2015,11,01)
vtime = ftime + relativedelta(months=1)

download_from_api("http://api.euporias.eu/", "RESILIENCE.ro", "4e975e24-2124-4572-8b74-f6264907093e", "6", ftime, global_file_location, json_dir_location)
write_global_nc(global_out_location, global_file_location, vtime)
write_observations_nc(observations_out_location, global_file_location, json_file_location)
write_ensemble_nc(ensemble_out_location, global_file_location, json_file_location)
ftp_upload(global_out_location, ensemble_out_location, observations_out_location)

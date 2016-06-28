from summary import write_global_nc
from observations import write_observations_nc
from ensemble import write_ensemble_nc
from datetime import datetime

write_global_nc("/tmp/out.nc", "globalstats.csv", datetime(2015,12,01))
write_observations_nc("/tmp/obs.nc", "globalstats.csv", "*.json")
write_ensemble_nc("/tmp/enb.nc", "globalstats.csv", "*.json", datetime(2015,12,01))

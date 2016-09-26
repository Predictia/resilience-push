from ftplib import FTP
import os

def ftp_upload(global_out_location, ensemble_out_location, observations_out_location):
    with FTP("opendap.knmi.nl") as ftp:
        ftp.login('predictia', os.environ['FTP_PASS'])
        with open(global_out_location, 'rb') as global_out_file:
            ftp.storbinary('STOR resilience.globalstats.nc', global_out_file)
        with open(observations_out_location, 'rb') as observations_out_file:
            ftp.storbinary('STOR resilience.observations.nc', observations_out_file)
        with open(ensemble_out_location, 'rb') as ensemble_out_file:
            ftp.storbinary('STOR resilience.forecast.nc', ensemble_out_file)

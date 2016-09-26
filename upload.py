from ftplib import FTP
import os

def ftp_upload(global_out_location, ensemble_out_location, observations_out_location):
    ftp = FTP("opendap.knmi.nl")
    ftp.login('predictia', os.environ['FTP_PASS'])
    try:
        with open(global_out_location, 'rb') as global_out_file:
            ftp.storbinary('STOR resilience.globalstats.nc', global_out_file)
        with open(observations_out_location, 'rb') as observations_out_file:
            ftp.storbinary('STOR resilience.observations.nc', observations_out_file)
        with open(ensemble_out_location, 'rb') as ensemble_out_file:
            ftp.storbinary('STOR resilience.historic-forecast.nc', ensemble_out_file)
    finally:
        ftp.quit()

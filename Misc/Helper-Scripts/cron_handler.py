import os

CRON_PATHS = ['/etc/cron.d', 
              '/etc/cron.daily', 
              '/etc/cron.hourly', 
              '/etc/cron.weekly']

def disable_cron_jobs():
    for path in CRON_PATHS:
        os.system(f'sudo chmod -x {path}')  # remove execute permissions

def enable_cron_jobs():
    for path in CRON_PATHS:
        os.system(f'sudo chmod +x {path}')  # add execute permissions



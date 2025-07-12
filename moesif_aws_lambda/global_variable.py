"""This module is to declare global objects."""
from datetime import datetime
from moesifapi.app_config.app_config import AppConfig
from moesifapi.moesif_api_client import *
import os

# MoesifAPI Client
global api_client
api_client = None

# App Config class
global app_config
app_config = None

# App Config
global config
config = None

# App Config sampling percentage
global sampling_percentage
sampling_percentage = 100

# App Config eTag
global config_etag
config_etag = None

# App Config last updated time
global last_updated_time
last_updated_time = datetime.utcnow()

# the delta time for refreshing config, if the last update time is greater than this
global refresh_config_time_seconds
refresh_config_time_seconds = 2 * 60

# initialize the config first time on cold start.
print("[moesif] start init - config")

# Initialize the client
if os.environ.get("MOESIF_APPLICATION_ID"):
    api_client = MoesifAPIClient(os.environ["MOESIF_APPLICATION_ID"]).api
else:
    raise Exception('Moesif Application ID is required in settings')

app_config = AppConfig()
config = app_config.get_config(api_client, True)

print("[moesif] end init - config")

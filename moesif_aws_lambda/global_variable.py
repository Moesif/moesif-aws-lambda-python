"""This module is to declare global objects."""
from datetime import datetime
from moesifpythonrequest.app_config.app_config import AppConfig
from moesifapi.moesif_api_client import *
import os

# MoesifAPI Client
global api_client_incoming
api_client_incoming = None

# App Config class
global app_config_incoming
app_config_incoming = None

# App Config
global config_incoming
config_incoming = None

# App Config sampling percentage
global sampling_percentage_incoming
sampling_percentage_incoming = 100

# App Config eTag
global config_etag_incoming
config_etag_incoming = None

# App Config last updated time
global last_updated_time_incoming
last_updated_time_incoming = datetime.utcnow()


# initialize the config first time on cold start.
print("------------------ start init - config...")

# Initialize the client
if os.environ.get("MOESIF_APPLICATION_ID"):
    api_client_incoming = MoesifAPIClient(os.environ["MOESIF_APPLICATION_ID"]).api
else:
    raise Exception('Moesif Application ID is required in settings')

app_config_incoming = AppConfig()
config_incoming = app_config_incoming.get_config(api_client_incoming, True)

print("------------------  end init  - config")

#
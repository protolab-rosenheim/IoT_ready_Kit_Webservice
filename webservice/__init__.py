from pathlib import Path
import os
import ast

import yaml


# ENV only used if we run the code outside docker
try:
    config_folder = os.environ['VOLUME_DIR'] + '/irk_webservice'
except KeyError:
    config_folder = '/usr/src/app/conf'

try:
    webservice_conf_path = Path(config_folder + '/webservice.yml')
    with open(webservice_conf_path) as f:
        webservice_conf = yaml.safe_load(f)
except FileNotFoundError:
    webservice_conf = {}

# DB setup
db_drivername = os.environ['DATABASE_DIALECT']
db_username = os.environ['DATABASE_USER']
db_password = os.environ['DATABASE_PASSWORD']
db_host = os.environ['DATABASE_HOSTNAME']
db_port = os.environ['DATABASE_PORT']
db_database = os.environ['DATABASE_NAME']

# Webservice
debug_mode = ast.literal_eval(os.environ['DEBUG_MODE'])
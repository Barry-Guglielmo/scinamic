# Global configurations
# You need to have the customer Whitelist the instance IP address
prod_url = "https://<company>.scinamic.com:9010"
test_url = "https://<company-test>.scinamic.com:9011"

SCINAMIC_API_CONFIG = {
                        "url": prod_url, # provided by the customer
                        "user": 'service-act', # this will be setup by the customer
                        "password": "somePW123!", # this comes from the customer side
                        "ld_ip":"optional" # optional: LD whitelisted IP 
                        }


SIMPLE_SCHEMA_DB_CONFIG = {
                           "database":"scinamic", 
                           "user":'postgres', 
                           "password":'postgres', 
                           "host":'127.0.0.1', 
                           "port": '3247' # on production 3247 on local probably 5432
                           }
# Configure for Image Service
BASE_URL = 'https://<company>.onschrodinger.com'
API_UPLOAD_URL = BASE_URL + '/livedesign/images/upload'
API_CHECK_URL = BASE_URL + '/livedesign/images/check'
# with k8s this will be set to cloud sql or persistant volume
IMAGE_SERVICE_DB_CONFIG = {
                            'path':'plots.db'
                          }

# NOTE: Change in names on LD side will break this! Only specified Projects will be brought over
# No automated system for creating LD projects. Please create project manually.
# Need to write this so there can be a list of LD projects as well

# Map Scinamic Project (PK) to LD (NAME). Ex. 1234:[LD_Proj1, LD_Proj2]
SCINAMIC_PROJECTS_CONFIG = {   # Scinamic Project PK : [LD Proj Name,...],
                                'GLOBAL': ['Scinamic'], # All data will go to this project
                    }
# Pivot conditions for assay data.
PIVOT_CONDITIONS={
                 # 'TR-FRET': ['protein'],
                 }

# will be used in pivot name
PIVOT_DELIMITER = " "

# Alias assay or pivoted assays
ASSAY_ALIAS = {}

# log level decisions
import logging
from logging.handlers import TimedRotatingFileHandler

# Configure the logging settings with a timed rotating file handler
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
timed_rotating_handler = TimedRotatingFileHandler('../seurat/pro_serv/scinamic_integration/logs/scinamic.log', when='midnight', interval=1, backupCount=30)
timed_rotating_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(timed_rotating_handler)

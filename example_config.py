# Global configurations
# You need to have the customer Whitelist the instance IP address
prod_url = "https://<name>.scinamic.com:9010"
test_url = "https://<name>.scinamic.com:9011"

SCINAMIC_API_CONFIG = {
                        "url": test_url, # provided by the customer
                        "user": 'sa_schrodinger', # this will be setup by the customer
                        "password": "", # this comes from the customer side
                        "ld_ip":"optional" # optional: LD whitelisted IP 
                        }

SIMPLE_SCHEMA_DB_CONFIG = {
                           "database":"scinamic", 
                           "user":'postgres', 
                           "password":'postgres', 
                           "host":'127.0.0.1', 
                           "port": '5432' # on production 3427 on local probably 5432
                           }

# with k8s this will be set to cloud sql or persistant volume
IMAGE_SERVICE_DB_CONFIG = {
                            'path':'plots.db'
                          }

# will be used in pivot name
PIVOT_DELIMITER = " "

# Alias assay or pivoted assays
ASSAY_ALIAS = {}

# NOTE: Change in names on LD side will break this! Only specified Projects will be brought over
# No automated system for creating LD projects. Please create project manually.
SCINAMIC_PROJECTS_CONFIG = {
                    integer_scinamic_project_key:"ld_project_1_name",
                    ...

                    }
PIVOT_CONDITIONS = {
                    # 'NAME OF STUDY': [' PIVOT FIELD 1',...]
                    'TR-FRET': ['protein']
                    }

# Global configurations
# You need to have the customer Whitelist the instance IP address
prod_url = "https://aleksia.scinamic.com:9010"
test_url = "https://aleksia.scinamic.com:9011"
"""
The configuration file uses dictionaries and should be clean to use.
"""
SCINAMIC_API_CONFIG = {
                        "url": prod_url, # provided by the customer
                        "user": 'sa_schrodinger', # this will be setup by the customer
                        "password": "011ZLJml", # this comes from the customer side
                        "ld_ip":"optional" # optional: LD whitelisted IP 
                        }


SIMPLE_SCHEMA_DB_CONFIG = {
                           "database":"scinamic", 
                           "user":'postgres', 
                           "password":'postgres', 
                           "host":'127.0.0.1', 
                           "port": '5432' # on production 3247 on local probably 5432
                           }


# NOTE: Change in names on LD side will break this! Only specified Projects will be brought over
# No automated system for creating LD projects. Please create project manually.
# Need to write this so there can be a list of LD projects as well

# For Now Projects are 1:1
# we rely on them to have data in multiple projects in Scinamic
SCINAMIC_PROJECTS_CONFIG = {   # Scinamic Project PK : LD Proj Name
                                6784367: 'CCNE',
                                6744140: 'CDK2',
                                6752506: 'MEN1',
                                6784366: 'PIK3CA',
                                6777306: 'PIK3CD',
                                6777305: 'PKMYT1',
                                6744929: 'Cov Lys Lib',
                                6743812: 'Library NC',
                                # 827071: 'NONE',
                                6777304: 'LifeChem Cys Cov Lib',
                                6818265: 'A&CSP1',
                                6818266: 'EPP Set',
                                6827765: 'MiscProbes',
                                6744066: 'Library Cov',
                                7080986: 'AKT E17K'
                    }


PIVOT_CONDITIONS = {
                    # 'NAME OF STUDY OR TYPE?': [' PIVOT FIELD 1',...]
                    'TR-FRET': ['protein'],
                    'AlphaLISA':['cellline']
                    }
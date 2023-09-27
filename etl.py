"""
this file uses the api script functions to export data from
scinamic api then format it to be loaded into simpleschema
NOTE: the most important part here is getting the hash for
Updates to scinaptic, that way we only bring in what is new.
"""

import psycopg2
from api import *
from config import *
from map import *


def create_cursor(SIMPLE_SCHEMA_DB_CONFIG):
    '''
      Connect to Simple Schema -- 
      Mostly used for scinamic_audit table queies as it is a custom table information
    '''

    conn = psycopg2.connect(
    database=SIMPLE_SCHEMA_DB_CONFIG["database"], 
    user=SIMPLE_SCHEMA_DB_CONFIG["user"], 
    password=SIMPLE_SCHEMA_DB_CONFIG["password"], 
    host=SIMPLE_SCHEMA_DB_CONFIG["host"], 
    port= SIMPLE_SCHEMA_DB_CONFIG["port"]
    )
    cursor = conn.cursor()
    return conn, cursor

def ld_last_audit_record(cursor):
    query = "SELECT * FROM scinamic_audit ORDER BY datetime DESC LIMIT 1;"
    cursor.execute(query)
    audit = cursor.fetchone()
    return audit[1]

def ss_is_empty():
    '''
    TBD: Check if simple schema is empty
    '''
    return False



def etl(sci_session, ss_session, cursor, etl_run_type = 'audit'):
    '''
    Run the ETL pipeline on appropriate data points (All or Updated)
    '''

    print("Starting the Scinamic to LiveDesign ETL")
    #ld_last_audit = ld_last_audit_record(cursor)
    print("ETL Run Type:" + etl_run_type)

    if etl_run_type == 'full_reload':
        # put in nuking the db
        compounds = Scinamic_Compounds(sci_session)
        compounds.get_all_data()
        # map compounds to projects and make projects if needed
        compound_map(compounds)
        # map assay data
        results = Scinamic_Results(sci_session)
        results.get_all_data()
        assay_map(results)
        # update audit
    elif etl_run_type == 'assay_only':
        results = Scinamic_Results(sci_session)
        results.get_all_data()
        assay_map(results)
    else:
        audit = Audit(sci_session, ld_last_audit)
        return "starting at hash record %s"%ld_last_audit

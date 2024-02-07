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
        # get most recent audit pk
        audits = Audit(sci_session)
        n = 0
        # we may have to pageniate
        if len(audits.audits) == 1000000:
            while len(audits.audits) == 1000000:
                audits = Audit(sci_session, audits.most_recent_audit)
        update_last_audit(audits.most_recent_audit)
        # put in nuking the db
        compounds = Scinamic_Compounds(sci_session)
        # map compounds to projects and make projects if needed
        compound_map(compounds.data)
        if len(compounds.chunk_pks) > 1:
            for i in range(0,len(compounds.chunk_pks)):
                compounds.cycle()
                compound_map(compounds.data)
        # map assay data
        results = Scinamic_Results(sci_session)
        assay_map(results.data)
        if len(results.chunk_pks) > 1:
            for i in range(0,len(results.chunk_pks)):
                results.cycle()
                assay_map(results.data)
        # curves -- need to add in decision here
        #curves = Scinamic_Curves(sci_session)
        #curves.render_all_to_db()
    elif etl_run_type == 'assay_only':
        results = Scinamic_Results(sci_session)
        results.get_all_data()
        assay_map(results)
    elif etl_run_type == 'curves_only':
        curves = Scinamic_Curves(sci_session)
        curves.render_all_to_db()
    elif etl_run_type == 'audit':
        audits = Audit(sci_session, get_last_audit())
        audit_map(audits)
        update_last_audit(audits.most_recent_audit)
        print("starting at hash record %s"%ld_last_audit)

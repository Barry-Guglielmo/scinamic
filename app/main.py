from api import *
from etl import *
from scinamic_api_wrappers import *
import argparse
from simpleschema.models import *
from scinamic_utils import *


parser = argparse.ArgumentParser(
                    prog='Scinamic Integration',
                    description='ETL From Scinamic to LD',
                    epilog='Please See README for more details. See Confluence for SA usage.')

parser.add_argument('-f', '--full_reload',action='store_true', required=False)          # Do a full reload of the data to simple schema
parser.add_argument('-d', '--delete_data',action='store_true', required=False)          # Delete data in SimpleSchema Scinamic DB
parser.add_argument('-a', '--assays_only',action='store_true', required=False)          # Load in all assay data only
parser.add_argument('-c', '--curves_only',action='store_true', required=False)          # curves only (curves are heavy)
parser.add_argument('-i', '--incremental_load',action='store_true', required=False)     # incremental loading (set after initial load is complete)
parser.add_argument('-cmpd', '--compounds_only',action='store_true', required=False)    # compounds only

args = parser.parse_args()


if __name__ == '__main__':

    # Postgres connection (psycopg2)
    conn, cursor = create_cursor(SIMPLE_SCHEMA_DB_CONFIG)

    # start Scinamic API session and login
    sci_session = Scinamic_Session(SCINAMIC_API_CONFIG)

    # SimpleSchema Session
    ss_session = SimpleSchema_Session(SIMPLE_SCHEMA_DB_CONFIG)

    if args.delete_data == True:
       ss_session.clear_all()
    # Make Projects in SS if needed see scinamic_utils.py
    # Note: you still need to manually add projects to LD*
    add_projects_to_ss()

    # Full Reload if arg is set
    if args.full_reload == True:
        etl(sci_session, ss_session, cursor, etl_run_type='full_reload')
    elif args.compounds_only == True:
        etl(sci_session, ss_session, cursor, etl_run_type='compounds_only') 
    elif args.assays_only == True:
        etl(sci_session, ss_session, cursor, etl_run_type='assay_only')
    elif args.curves_only == True:
        etl(sci_session, ss_session, cursor, etl_run_type='curves_only')
    elif args.incremental_load == True:
        etl(sci_session, ss_session, cursor, etl_run_type='incremental')
    else:
        # Note: Full reload will occur if there isn't an Audit > 0 in the scinamic_audit table in SimpleSchema
        logger.error('No Valid ETL Run Type Entered...')
    # Close SimpleSchema Session
    conn.close()

    # Close Scinamic Session
    # ss_session.logout()
    sci_session.logout()
    # Ended not = Success
    logger.info('Scinamic ETL Scripts Ended...')


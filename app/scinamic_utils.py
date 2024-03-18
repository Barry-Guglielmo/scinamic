from config import *
from api import *
from simpleschema.models import Project, Experiment
import psycopg2
from psycopg2 import sql

def get_last_audit():
    # Database connection parameters
    connection = psycopg2.connect(**SIMPLE_SCHEMA_DB_CONFIG)
    cursor = connection.cursor()
    query = sql.SQL("SELECT audit_id FROM scinamic_audit ORDER BY datetime DESC LIMIT 1")
    cursor.execute(query)
    latest_entry = cursor.fetchone()
    cursor.close()
    connection.close()
    return latest_entry[0]
def update_last_audit(most_recent_audit):
    # Database connection parameters
    connection = psycopg2.connect(**SIMPLE_SCHEMA_DB_CONFIG)
    cursor = connection.cursor()
    query = "INSERT INTO scinamic_audit (audit_id) VALUES (%s)"
    cursor.execute(query, (most_recent_audit,))
    connection.commit()
    cursor.close()
    connection.close()

def add_projects_to_ss():
    # customer_key = scinamic_project_pk, 
    # key = ld_project_name

    SimpleSchema_Session(SIMPLE_SCHEMA_DB_CONFIG)
    for k,v in SCINAMIC_PROJECTS_CONFIG.items():
        if str(k) != 'GLOBAL':
            try:
                mp = Project.get(key = v[0]).execute()
            except:
                try:
                    Project.register(customer_key = k, key = v[0])
                except:
                    print("error creating projects")
        else:
            i = 1
            for j in v:
                 try:
                     mp = Project.get(key = j).execute()
                 except:
                     try:
                        Project.register(customer_key = i, key = j)
                     except:
                         print("error creating projects")
                 i+=1
# TBD Not sure how it relates
def add_studies_to_ss():
    # customer_key = scinamic_project_pk, 
    # key = ld_project_name

    SimpleSchema_Session(SIMPLE_SCHEMA_DB_CONFIG)
    for d in Scinamic_Studies.get_all_data().data:
        try:
            mp = Experiment.get(key = d['id']).execute()
        except:
            try:
                Experiment.register(customer_key = d['pk'], key = d['id'])
            except:
                print("error")
def add_assay_to_ss():
    Assay.register(key = i['document'])
    # assay = Assay.get(key=i['document'])

def create_plots_db():
    conn = sqlite3.connect(IMAGE_SERVICE_DB_CONFIG['path'])
    cursor = conn.cursor()
    table_schema = """
                    CREATE TABLE IF NOT EXISTS images (
                        top_folder TEXT,
                        middle_folder TEXT,
                        bottom_folder TEXT,
                        image_data BLOB
                    );
                    """
    cursor.execute(table_schema)
    conn.commit()
    conn.close()

from config import *
from api import *
from simpleschema.models import Project, Experiment

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

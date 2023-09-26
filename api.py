# this is the general connection to scinamic and an explination of some of the fields

import requests
import json
from scinamic_api_wrappers import *
from config import *
from simpleschema.schemas import SimpleSchema

# https://scinamic.com/wiki/doku.php?id=webapi:get_audits

def SimpleSchema_Session(SIMPLE_SCHEMA_DB_CONFIG):
    return SimpleSchema(SIMPLE_SCHEMA_DB_CONFIG["database"],
                        user=SIMPLE_SCHEMA_DB_CONFIG["user"],
                        password=SIMPLE_SCHEMA_DB_CONFIG["password"],
                        port=SIMPLE_SCHEMA_DB_CONFIG["port"], 
                        host=SIMPLE_SCHEMA_DB_CONFIG["host"])

def Scinamic_Session(config):
        session = Session(config["url"],config["user"],config["password"])
        session.login()
        return session

class Scinamic_Compounds:
    '''
           {'pk': '7249403', 'id': 'ALK-0005548', 
            'creation_user': 'cquesnelle', 
            'creation_date': '2023-05-04 16:48:02', 
            'lastedit_user': '', 
            'projects': 'A&CSP1', 
            'mw': '843.9121', 
            'exact_mass': '843.2911', 
            'formula': 'C42H41N11O7S', 
            'smiles': '', 
            'stereochemistry': 'RACEMIC', 
            'lg_formula': 'NA', 
            'hb_donor_count': '3', 
            'ring_count': '8', 
            'aromatic_ring_count': '6', 
            'xlogp': '2.93', 
            'alogp': '3.3698', 
            'tpsa': '250.72', 
            'lipinski_failures': '3', 
            'active': 'true', 
            'group': 'A&CSP1', 
            'entity': 'Compound'}
    '''
    def __init__(self, session):
        # we may need multiple calls, but lets start simple
        self.session = session
        self.pks = session.search_records("compound","pks",["mw > 0"]).data
        self.ids = session.search_records("compound","ids",["mw > 0"]).data
        self.count = session.search_records("compound","count",["mw > 0"]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_ids = [self.ids[i * n:(i + 1) * n] for i in range((len(self.ids) + n - 1) // n )]
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]


    def get_all_data(self):
        data = []
        for i in self.chunk_pks:
            chunk = self.session.get_records(i).data
            data+=chunk
        self.data = data

class Audit:
    """
      {'record': 1664067, 
      'pk': 3465808, 
      'time': '2021-05-17 02:39:23', 
      'type': 'D', 
      'user': 'admin'}

    This is a good one to start from 4054032
    """
    def __init__(self, session, min_audit_pk = None):
        self.session = session
        if min_audit_pk != None:
            self.audits = session.get_audits(min_audit_pk=min_audit_pk).data
            self.most_recent_audit = self.audits[-1]['pk']
            self.records = [i['record'] for i in self.audits]
            n = 1000 # the size of chunk (1000 is the max)
            self.chunk_records = [self.records[i * n:(i + 1) * n] for i in range((len(self.records) + n - 1) // n )] 
        else:
            self.audits = None

    def get_all_data(self):
        """
        This is broken right now. For some reason I get 'permission denied' if any of the list is permission denied
            Status:  error
            Message:  Permission denied.
            Data:  None
        """
        data = []
        for i in self.chunk_records:
            chunk = self.session.get_records(i).data
            data+=chunk
        self.data = data
        self.audit_record_pks = [i['pk'] for i in self.data]

class Scinamic_Analysis:
    '''Returns Analysis, Results, CompoundBatch Data'''
    def __init__(self, session):
        # we may need multiple calls, but lets start simple
        self.session = session
        # Results PK
        self.pks = session.search_records("analysis","pks",[""]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
        
    def get_all_data(self):
        self.data = []
        for i in self.chunk_pks:
            chunk = self.session.get_records(i).data
            self.data+=chunk
        
class Scinamic_Results:
    '''Returns Analysis, Results, CompoundBatch Data'''
    def __init__(self, session):
        # we may need multiple calls, but lets start simple
        self.session = session
        # Results PK
        self.pks = session.search_records("result","pks",[""]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
       
    def get_all_data(self):
        self.data = []
        for i in self.chunk_pks:
            chunk = self.session.get_records(i).data
            self.data+=chunk
        
class Scinamic_CompoundBatches:
    '''Returns Analysis, Results, CompoundBatch Data'''
    def __init__(self, session):
        # we may need multiple calls, but lets start simple
        self.session = session
        # Results PK
        self.pks = session.search_records("compoundbatch","pks",[""]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
        
    def get_all_data(self):
        self.data = []
        for i in self.chunk_pks:
            chunk = self.session.get_records(i).data
            self.data+=chunk
       
class Scinamic_Projects:
    """Returns Projects
    
    {'pk': '6784367',
    'id': 'CCNE',
    'creation_user': 'epark',
    'creation_date': '2022-07-12 09:45:31',
    'lastedit_user': 'epark',
    'lastedit_date': '2022-07-12 16:01:08',
    'alias': 'CCNE1',
    'active': 'true',
    'external_id': 'ALK-P005',
    'entity': 'Project'}
    """
    def __init__(self, session):
        # we may need multiple calls, but lets start simple
        self.session = session
        # Results PK
        self.pks = session.search_records("project","pks",[""]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]

        
    def get_all_data(self):
        self.data = []
        for i in self.chunk_pks:
            chunk = self.session.get_records(i).data
            self.data+=chunk
        self.name = {}
        for i in self.data:
            self.name[i['id']]=i
            
class Scinamic_Studies:
    """Returns Studies
    
    {'pk': '6780427',
    'id': 'Caco-2 Permeability',
    'creation_user': 'klazarski',
    'creation_date': '2022-07-01 14:29:02',
    'lastedit_user': '',
    'tags': 'Permeability, ADME',
    'entity': 'Study'}
    """
    def __init__(self, session):
        # we may need multiple calls, but lets start simple
        self.session = session
        # Results PK
        self.pks = session.search_records("study","pks",[]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
        
    def get_all_data(self):
        self.data = []
        for i in self.chunk_pks:
            chunk = self.session.get_records(i).data
            self.data+=chunk
# search_records("compoundbatch","pks",[""]).data
# import base64
# from PIL import Image
# import io
# import sqlite3

# class Scinamic_Curve:
#     def __init__(self, session):
#         # we may need multiple calls, but lets start simple
#         self.session = session
#         # Results PK
#         self.curve_data = session.get_curve(6927177).data
#         decoded_data = base64.b64decode(self.curve_data)

#         # Create an in-memory stream
#         image_stream = io.BytesIO(decoded_data)

#         # Open the image stream using PIL
#         image = Image.open(image_stream)
#     def insert_image_into_database(image, top_folder, middle_folder, bottom_folder):
#         conn = sqlite3.connect('../plots.db')  # Replace with your database name
#         cursor = conn.cursor()

#         cursor.execute('INSERT INTO images (top_folder,middle_folder,bottom_folder, image_data) VALUES (?, ?, ?, ?)', (top_folder,middle_folder,bottom_folder, image))

#         conn.commit()
#         conn.close()

#     insert_image_into_database(image, 'a','b','c')

# this is the general connection to scinamic and an explination of some of the fields

import requests
import json
import base64
from PIL import Image
import io
import sqlite3
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

def Scinamic_Session(SCINAMIC_API_CONFIG):
        session = Session(SCINAMIC_API_CONFIG["url"],SCINAMIC_API_CONFIG["user"],SCINAMIC_API_CONFIG["password"])
        session.login()
        return session

class Scinamic_Compounds:
    '''
    Python class that stores compound data.

    :param session: This takes a Scinamic_Session
    :type session: scinamic_api_wrappers.Session
    :return: returns a python Class for Scinamic Compounds
    :rtype: class

    Example usage:

    >>> s = Scinamic_Session(SCINAMIC_API_CONFIG)
    >>> compounds = Scinamic_Compounds(s) # Returns first 1K
    >>> compounds.data[0] # first compund info as dict
    >>> compounds.cycle() # get next 1K compounds
    '''
    def __init__(self, session, offset = 0):
        # we may need multiple calls, but lets start simple
        self.session = session
        self.pks = session.search_records("compound","pks",["mw > 0"]).data
        self.ids = session.search_records("compound","ids",["mw > 0"]).data
        self.count = session.search_records("compound","count",["mw > 0"]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_ids = [self.ids[i * n:(i + 1) * n] for i in range((len(self.ids) + n - 1) // n )]
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
        self.offset = offset
        self.data = self.session.get_records(self.chunk_pks[self.offset]).data

    def cycle(self):
        self.offset += 1
        self.data = self.session.get_records(self.chunk_pks[self.offset]).data

class Audit:
    """
    This will pick up the audit trail for Scinamic. If None it currently only returns first 1M results.

    This will typically only be a few calls to get to endo of groups that have been using scinamic for years.
    We will use the 'entity' field to decide what to do with each of these audits in mapping steps.

    Types 'N' for new, 'U' for update, and 'D' for deleted
    """
    def __init__(self, session, min_audit_pk = None):
        self.session = session
        if min_audit_pk != None:
            # A single audit call will not capture everything
            self.audits = session.get_audits(min_audit_pk=min_audit_pk).data
            self.most_recent_audit = self.audits[-1]['pk']
            self.records = [i['record'] for i in self.audits]
            n = 1000 # the size of chunk (1000 is the max)
            self.chunk_records = [self.records[i * n:(i + 1) * n] for i in range((len(self.records) + n - 1) // n )]
        else:
            # get first 1M audits, will update to get all and most recent later
            self.audits = session.get_audits().data # record, pk, time, type, user
            self.most_recent_audit = self.audits[-1]['pk']
            self.most_recent_audit_data = self.audits[-1]
            self.records = [i['record'] for i in self.audits]
            n = 1000 # the size of chunk (1000 is the max)
            self.chunk_records = [self.records[i * n:(i + 1) * n] for i in range((len(self.records) + n - 1) // n )]

class Scinamic_Analysis:
    '''
    Python class that stores Analysis Data
    '''
    def __init__(self, session, offset=0):
        self.session = session
        self.pks = session.search_records("analysis","pks",[""]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
        self.offset = offset
        self.data = self.session.get_records(self.chunk_pks[0]).data
    def cycle(self):
        self.offset += 1
        self.data = self.session.get_records(self.chunk_pks[self.offset]).data

class Scinamic_Results:
    '''
    Python class that stores Results data in batches of 1K. This is mostly used for Full Reloads.
    '''
    def __init__(self, session, offset = 0):
        # we may need multiple calls, but lets start simple
        self.session = session
        # Results PK
        self.pks = session.search_records("result","pks",[""]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
        self.offset = offset
        self.data = self.session.get_records(self.chunk_pks[0]).data
    def cycle(self):
        self.offset += 1
        self.data = self.session.get_records(self.chunk_pks[self.offset]).data

class Scinamic_CompoundBatches:
    '''
     Python class that returns CompoundBatch Data
    '''
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
    """
    Python class Returns Projects data
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
    """
    Python class Returns Studies data
    """
    def __init__(self, session):
        self.session = session
        self.pks = session.search_records("study","pks",[]).data
        n = 1000 # the size of chunk (1000 is the max)
        self.chunk_pks = [self.pks[i * n:(i + 1) * n] for i in range((len(self.pks) + n - 1) // n )]
        
    def get_all_data(self):
        self.data = []
        for i in self.chunk_pks:
            chunk = self.session.get_records(i).data
            self.data+=chunk


class Scinamic_Curves:
    '''
    Python class to import, convert, and upload curves to the livedesign image_service
    '''
    def __init__(self, session):
        self.session = session
        self.pks = session.search_records("ResultCurve","pks",[]).data

    def render(self, curve_pk, show = False):
        curve_string = self.session.render_resultcurve(curve_pk)
        decoded_data = base64.b64decode(curve_string.data)
        image_stream = io.BytesIO(decoded_data)
        if show == True:
            image = Image.open(image_stream)
        return image_stream.read()

    def render_to_db(self, curve_pk):
        image_data = self.render(curve_pk)
        data = {"first": "scinamic", "second": 'curves'}
        file = {'file': (str(curve_pk), image_data)}
        requests.post(API_UPLOAD_URL, files=file, data=data )

    def check_db(self, curve_pk):
        # broken for now
        data = {"first": "scinamic", "second": 'curves'}
        response = requests.get(API_CHECK_URL, data=data)
        if response.text == 'True':
           return True
        else:
           return False

    def render_all_to_db(self):
        for i in self.pks:
            # if nothing returned from db insert it
            if self.check_db(i) == False:
                try:
                    self.render_to_db(i)
                except:
                    print('error')

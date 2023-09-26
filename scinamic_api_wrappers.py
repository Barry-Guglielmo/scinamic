import requests

# This file was provided by Scinamic it makes it much easier to interact with their API
# You will need permissions to access the web page below
# https://scinamic.com/wiki/doku.php?id=webapi:start

class Response:
	def __init__(self,response=None,errorMessage=None):
		if response !=None:
			self.status = response['status']
			self.message = response['message']
			self.data = response['data']
		else:
			self.status = "error";
			self.message = errorMessage;

	def show(self):
		print ("Status: ",self.status)
		print ("Message: ",self.message)
		print ("Data: ",self.data)

class Session:
	def __init__(self,url,user,password):
		self.url = url
		self.user = user
		self.password = password

	def post(self, function, parameters, filepath=None):
		parameters["response_format"]="json"
		if filepath != None:
			files = {'file': open(filepath.format(filepath), 'rb')}
			r = requests.post(url = self.url+"/"+function, data = parameters, files = files)
		else:
			r = requests.post(url = self.url+"/"+function, data = parameters)
		if r.status_code!=200:
			r = Response(errorMessage=str(r.status_code) + " " + r.reason)
		else:
			r = Response(response=r.json())
		if not r.status == 'ok':
			r.show()
		return r
        
	def login(self):
		r = self.post('login',{'user':self.user,'password':self.password})
		self.auth_token = r.data

	def logout(self):
		r = self.post('logout',{'auth_token':self.auth_token})

	def search_records(self,entity_id,result_type,field_filter):
		params = {'auth_token':self.auth_token,
			'entity_id':entity_id,
			'result_type':result_type,
			'field_filter':field_filter,
			}
		return self.post('search_records',params);
    
	def get_audits(self, record_pk=None, entity_id=None,entity_pk=None,min_audit_pk=None,fields=None):
		params = {'auth_token':self.auth_token,
			'record_pk':record_pk,
			'entity_id':entity_id,
			'entity_pk':entity_pk,
			'min_audit_pk':min_audit_pk,
            'fields':fields}
		return self.post('get_audits',params);

	def get_record(self,pk):
		params = {'auth_token':self.auth_token,
			'record_pk':pk}
		return self.post('get_record',params);

	def get_records(self,pks):
		params = {'auth_token':self.auth_token,
			'record_pks':pks,
			'record_error_handling':'ignore'}
		return self.post('get_records',params);

	def get_record_pk_by_id(self,entity_id,record_id):
		params = {'auth_token':self.auth_token,
			'entity_id':entity_id,
			'record_id':record_id}
		return self.post('get_record_pk_by_id',params);
    
	def get_record_by_id(self,entity_id,record_id):
		params = {'auth_token':self.auth_token,
			'entity_id':entity_id,
			'record_id':record_id}
		return self.post('get_record_by_id',params);
    
	def get_record_field_by_id(self,entity_id,field_name,record_id):
		params = {'auth_token':self.auth_token,
			'entity_id':entity_id,
			'record_id':record_id,
			'field_name':field_name}
		return self.post('get_record_field_by_id',params);

	def get_record_field(self,field_name,record_pk):
		params = {'auth_token':self.auth_token,
			'record_pk':record_pk,
			'field_name':field_name}
		return self.post('get_record_field',params);

	def update_record(self,pk,fields):
		params = {'auth_token':self.auth_token,
			'record_pk':pk}
		for k,v in iter(fields.items()):
			params[k]= v 
		return self.post('update_record',params);

	def insert_record(self,entity_id,fields):
		params = {'auth_token':self.auth_token,
			'entity_id':entity_id}
		for k,v in fields.items():
			params[k]= v 
		return self.post('insert_record',params);
    
	def add_attachment(self, pk, filepath):
		params = {'auth_token':self.auth_token,
			'record_pk':pk}
		return self.post('add_attachment',params,filepath); 
    
	def get_attachments(self,pk):
		params = {'auth_token':self.auth_token,
			'record_pk':pk}
		return self.post('get_attachments',params);

	def get_audits_by_record(self, record_pk):
		params = {'auth_token':self.auth_token,
			'record_pk':record_pk}
		return self.post('get_audits_by_record',params); 
    
	def upload_document(self, filepath, description=None):     
		params = {'auth_token':self.auth_token,
			'description': description}
		return self.post('upload_document',params,filepath);  

	def render_resultcurve(self,pk):
		params = {'auth_token':self.auth_token,
			'resultcurve_pk':pk,
			'width':400,
			'height':300,
			'x_axis_scale':'log(10)'}
		return self.post('render_resultcurve',params);



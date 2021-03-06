import xmlrpc.client
import ssl
import grp

import gettext
gettext.textdomain('lliurex-freeradius')
_ = gettext.gettext

DEBUG=True

class N4dManager:
	
	def __init__(self):
		
		self.user_info=""
		self.configured=False
		self.all_groups=[]
		self.allowed_groups=[]
	
	#def __init__
	
	
	def dprint(self,data):
		
		if DEBUG:
			data="[LliurexFreeRadius.N4dManager] %s"%data
			print(data)
			
	#def dprint
	
	
	def set_server(self,server):
		
		context=ssl._create_unverified_context()
		self.n4d=xmlrpc.client.ServerProxy("https://%s:9779"%server,allow_none=True,context=context)
		
	#def set_server

	
	def validate_user(self,user,password):
		
		self.dprint("Validating user...")
		groups=["adm","admins"]
		
		try:
		
			ret,ret_groups=self.n4d.validate_user(user,password)
			
			if ret:
				for g in groups:
					if g in ret_groups:
						self.user_info=(user,password)
						self.is_configured()
						self.get_all_groups()
						self.get_allowed_groups()
						return (True,"")
				return (False,_("User not allowed to run this application"))
				
			return (False,_("User or Password error"))
			
		except Exception as e:
			self.dprint(e)
			return (False,str(e))
		
	#def 
	
	
	def is_configured(self):
		
		self.dprint("Is configured query...")
		
		try:
			self.configured=self.n4d.is_configured("","FreeRadiusManager")
			return self.configured
		except Exception as e:
			self.dprint(e)
			return False
			
		
	#def is_configured
	
	
	def get_all_groups(self):
		
		ret=grp.getgrall()
		groups=[]
		
		for g in ret:
			if g.gr_gid > 10000 and g.gr_gid < 15000:
				groups.append(g.gr_name)
				
		self.all_groups=groups
		return self.all_groups
		
	#def get_all_groups
	
	
	def get_allowed_groups(self):
		
		self.dprint("Get allowed groups...")
		
		try:
			ret=self.n4d.get_allowed_groups(self.user_info,"FreeRadiusManager")
			if ret["status"]:
				self.allowed_groups=ret["msg"]
				
		except Exception as e:
			self.dprint(e)
	
		return self.allowed_groups
	
	#def get_allowed_groups
	
	
	def is_filter_enabled(self):
		
		self.dprint("Is filter enabled query...")
		
		try:
			variable=self.n4d.get_variable("","VariablesManager","FREERADIUS")
			return variable["groups_filter"]["enabled"]
		except Exception as e:
			self.dprint(e)
			return False
		
	#def is_filter_enabled
	
	
	def is_eap_enabled(self):
		
		self.dprint("Is EAP enabled query...")
		
		try:
			variable=self.n4d.get_variable("","VariablesManager","FREERADIUS")
			if variable["groups_filter"]["default_auth"]!=None:
				return True
			return False
			
		except Exception as e:
			self.dprint(e)
			return False
		
	#def is_eap_enabled
	
	
	def get_switches_status(self):
		
		self.dprint("Switches status query...")
		
		ret={}
		ret["eap"]=False
		ret["filter"]=False
		
		try:
			variable=self.n4d.get_variable("","VariablesManager","FREERADIUS")
			ret["filter"]=variable["groups_filter"]["enabled"]
			if variable["groups_filter"]["default_auth"]!=None:
				ret["eap"]=True
			
		except Exception as e:
			self.dprint(e)
		
		return ret
		
	#def get_switches_status
	
	
	def set_eap_auth(self,state):
		
		self.dprint("%s eap auth..."%("Enabling" if state else "Disabling"))
		
		auth_type=None
		if state:
			auth_type=", Auth-Type := EAP"
			
		try:
			
			self.n4d.set_filter_default_auth(self.user_info,"FreeRadiusManager",auth_type)
			
		except Exception as e:
			self.dprint(e)
			return {"status":False,"msg":str(e)}
		
	#def set_eap_auth

	
	def set_group_filtering(self,state):
		
		if state:
			return self.enable_group_filtering()
		else:
			return self.disable_group_filtering()
		
	#def set_group_filtering
	
	
	def enable_group_filtering(self):
		
		self.dprint("Enable group filtering...")
		
		try:
			return self.n4d.enable_group_filtering(self.user_info,"FreeRadiusManager")
		except Exception as e:
			self.dprint(e)
			return {"status":False,"msg":str(e)}
		
	#def enable_group_filtering
	
	
	def disable_group_filtering(self):
		
		self.dprint("Disable group filtering...")
		
		try:
			return self.n4d.disable_group_filtering(self.user_info,"FreeRadiusManager")
		except Exception as e:
			self.dprint(e)
			return {"status":False,"msg":str(e)}
		
	#def enable_group_filtering
	
	
	def add_group_to_filter(self,group):
		
		self.dprint("Adding %s to filter..."%group)
				
		try:
			return self.n4d.add_group_to_filter(self.user_info,"FreeRadiusManager",group)	
		except Exception as e:
			self.dprint(e)
			return {"status":False,"msg":str(e)}
		
	#def add_group_to_filter
	
	def remove_group_from_filter(self,group):
		
		self.dprint("Removing %s from filter..."%group)
		
		try:
			return self.n4d.remove_group_from_filter(self.user_info,"FreeRadiusManager",group)	
		except Exception as e:
			self.dprint(e)
			return {"status":False,"msg":str(e)}
		
	#def add_group_to_filter
	
	
	def initialize(self,data):
		
		self.dprint("Initializing...")
		
		try:
			ret=self.n4d.install_conf_files(self.user_info,"FreeRadiusManager",data["radius_server"],data["radius_password"],data["ldap_user"],data["ldap_password"],data["router_ip"])
			if ret["status"]:
				self.configured=True
				self.get_all_groups()
				self.get_allowed_groups()
			
			return ret
		except Exception as e:
			self.dprint(e)
			return {"status":False,"msg":str(e)}
		
	#def initialize

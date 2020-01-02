import json
class Load_Modbus_Data(object):
   def __init__( self, app ,auth,request,render_template,qs, site,Generate_Handlers, Redis_RPC_Client ):
       self.app              = app
       self.auth             = auth
       self.request          = request
       self.render_template  = render_template
       self.qs = qs
       self.site  = site
       self.Generate_Handlers = Generate_Handlers
       self.Redis_RPC_Client = Redis_RPC_Client
       
       
       self.rpc_client =  Redis_RPC_Client(qs.get_redis_data_handle())
       self.server_names = self.find_possible_server_names()
      
       
     
       self.get_all_modbus_server_data()
       
        
       a1 = auth.login_required( self.ping_device )
       app.add_url_rule('/ping_devices/<int:modbus_server_id>',"ping_device",a1)
       
       a2 = auth.login_required( self.ajax_ping_modbus_device )
       app.add_url_rule('/ajax/ping_modbus_device',"ajax_ping_modbus_device",a2,methods=["POST"])
       


       a4 = auth.login_required( self.modbus_current_status )
       app.add_url_rule("/modbus_current_status/<int:modbus_server_id>","modbus_current_status",a4)
       
       a5 = auth.login_required( self.modbus_basic_status )
       app.add_url_rule("/modbus_basic_status/<int:modbus_server_id>","modbus_basic_status",a5)
       
       a6 = auth.login_required( self.modbus_device_status )
       app.add_url_rule("/modbus_device_status/<int:modbus_server_id>","modbus_device_status",a6)
 
   def  modbus_current_status(self,modbus_server_id):
        pass

   def modbus_basic_status(self,modbus_server_id):
      pass   

   def modbus_device_status(self,modbus_server_id):
      pass

   def ping_device( self,modbus_server_id ): 
       server_name = self.server_names[modbus_server_id]
       self.rpc_client.set_rpc_queue(self.server_queues[server_name])
       return self.render_template("modbus/modbus_ping",modbus_servers=self.server_names,modbus_server_id=modbus_server_id, remote_devices = self.server_remotes[server_name])
       
   def ajax_ping_modbus_device(self):
      
      param            = self.request.get_json()
      remote           = param["remote"]
      
      try:
          result           = self.rpc_client.send_rpc_message( "ping_message",remote,timeout=30 )
          if result == True:
               return_value = "ping received for remote: "+remote
          else:
               return_value = "ping NOT received for remote: "+remote
      except:
          print("ping exception")
          return_value = "ping NOT received for remote: "+remote
      return json.dumps(return_value)
      
      

#
#
#
#

       
  
       
     
   def find_possible_server_names(self):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site )
       query_list = self.qs.add_match_terminal( query_list, relationship = "PLC_SERVER" )
       sets, sources = self.qs.match_list(query_list)  
       names = []
       for i in sources:
         names.append(i["name"])
       names.sort()
       return names
       
   def get_all_modbus_server_data(self):
      
      self.server_remotes = {}
      self.handlers = {}
      self.server_queues = {}
      for i in self.server_names:
        self.server_remotes[i] = self.find_server_remotes(i)
        handlers , server_queue =self.find_server_data_structures(i)
        self.server_queues[i] = server_queue
     
      
      
 
   def find_server_remotes(self,server_name):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site )
       query_list = self.qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=server_name )
       query_list = self.qs.add_match_terminal( query_list, relationship =  "REMOTE_UNIT" )
       sets, sources = self.qs.match_list(query_list)  
       remotes = []
       for i in sources:
          remotes.append(i["modbus_address"])

       return remotes
        
         
   def find_server_data_structures(self,server_name):
       query_list = []  
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site )
       query_list = self.qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=server_name )
       query_list = self.qs.add_match_terminal( query_list, relationship =  "PACKAGE" )
       sets, package_sources = self.qs.match_list(query_list)
       package = package_sources[0] 
       data_structures = package["data_structures"]
       generate_handlers = self.Generate_Handlers(package,self.qs)       
       handlers = {}
       handlers["PLC_RECENT_DATA"] = generate_handlers.construct_single_element(data_structures["PLC_RECENT_DATA"])
       handlers["PLC_BASIC_STATUS"]  = generate_handlers.construct_hash(data_structures["PLC_BASIC_STATUS"])
       handlers["PLC_REMOTES"]  = generate_handlers.construct_hash(data_structures["PLC_REMOTES"])
       
       server_queue = data_structures["PLC_RPC_SERVER"]["queue"]
       return handlers,server_queue




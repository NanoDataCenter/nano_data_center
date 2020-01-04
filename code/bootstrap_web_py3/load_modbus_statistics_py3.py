import json  
import datetime
from .base_stream_processing_py3 import Base_Stream_Processing
class Load_Modbus_Data(Base_Stream_Processing):
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
       app.add_url_rule("/modbus_device_status/<int:modbus_server_id>/<int:remote_id>","modbus_device_status",a6)
 
 
        
   def  modbus_current_status(self,modbus_server_id):
        server_name = self.server_names[modbus_server_id]
        handlers = self.handlers[server_name]
        working_handler = handlers["PLC_RECENT_DATA"]
        working_data = working_handler.get()
        return self.detail_current_status(modbus_server_id,self.server_names,working_data)

   def modbus_basic_status(self,modbus_server_id):
       server_name = self.server_names[modbus_server_id]
       handlers = self.handlers[server_name]
       working_handler = handlers["PLC_BASIC_STATUS"]
       working_data = working_handler.hgetall()
       
       working_data["MINUTE"] = None
       working_data["SECOND"] = None
       working_data["HOUR"] = None
       working_data["BUSY_TIME"] = None
       working_data["IDLE_TIME"] = None
       working_data["remote_data"] = None
       return self.detail_basic_status(modbus_server_id,self.server_names,working_data)

   def modbus_device_status(self,modbus_server_id,remote_id):
       server_name = self.server_names[modbus_server_id]
       handlers = self.handlers[server_name]
       remotes = self.server_remotes[server_name]
       working_handler = handlers["PLC_REMOTES"]
       working_data = working_handler.hget(remotes[remote_id])
       return self.detail_remote_status(server_name,self.server_names,remote_id,remotes,working_data)

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
# local detailing out web page
#
#
   def detail_current_status(self,modbus_server_id,server_names,working_data):
      print("working_data",working_data)
      return self.render_template("modbus/modbus_current_conditions",modbus_servers=self.server_names,modbus_server_id=modbus_server_id,data=working_data, remotes = working_data["remote_data"])
      
   def sort_remote_data(self,input_data,input_key):
       return_data = {}
       for element in input_data:
           keys = element.keys()
           for i in keys:
              if i not in return_data:
                 return_data[i] = []
              
              return_data[i].append(element[i][input_key])
 
       return return_data    
      
   def detail_basic_status(self,modbus_server_id,server_names,current_data):
       
       ### convert TIME_STAMP from string to second time stamp
       temp = []
       for i in current_data["TIME_STAMP"]:
          temp.append(datetime.datetime.strptime(i, "%b %d %Y %H:%M:%S").timestamp())
       stream_keys = self.generate_stream_keys(current_data)
       current_data["TIME_STAMP"] = temp
       plot_data = self.format_current_data(stream_keys,current_data)
       print(plot_data)
       return self.render_template("modbus/modbus_current_conditions_stream",
                                    modbus_servers=self.server_names,
                                    modbus_server_id=modbus_server_id,
                                    stream_keys_json=json.dumps(stream_keys),
                                    stream_data=json.dumps(plot_data),
                                    stream_keys = stream_keys)
       
       
   def generate_stream_keys(self,current_data):
       return_value = []
       for i in current_data.keys():
           if i != "TIME_STAMP":
              if current_data[i] != None:
                 return_value.append(i)
       return return_value                 

   
   def format_current_data(self,stream_keys,current_data):
       return_value = {}
       for i in stream_keys:
          if i != "TIME_STAMP":
            return_value[i] = self.format_current_data_entry(i,current_data)
       return return_value 
   
   def format_current_data_entry(self,key,current_data):
       return_value = {}
       ntick_x = 20
       ntick_y = 20
       x_axis = {
            "autorange":True,
            "showgrid":True,
            "zeroline":True,
            "ntick": ntick_x,
            "showline":True,
            "title":"TIME_STAMP",
            "mirror":"all"
             }
       y_axis = {
           "autorange":True,
           "showgrid":True,
           "zeroline":True,
           "ntick": ntick_y,
           "showline":True,
           "title":key+"/hour",
           "mirror":"all"
      
            }      
       layout = {
           'title':key+"/hour",
		   'showlegend': False,
		   
            'xaxis':x_axis,
            'yaxis':y_axis,
	        };
       return_value["layout"] = layout
       return_value["type"] ='lines+markers'
       return_value["x"] = current_data["TIME_STAMP"]
       return_value["y"] = current_data[key]
   
       
       return return_value
       
       
 
 
   def detail_remote_status(self,server_name,server_names,remote_id,remotes,current_data):
       print("current_data",current_data)

       return json.dumps("SUCCESS")      

   '''
       temp_data = self.handlers["MQTT_SENSOR_QUEUE"].revrange("+","-" , count=2160) # 1.5 days
       temp_data.reverse()
 
       chart_title = ""
       
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="",title_x="Date")
       stream_keys.sort()      
       
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range ,
                                     max_value = 10000000.,
                                     min_value = -10000000,)
   '''



#
#   local initialization routines
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
        self.handlers[i] = handlers
     
      
      
 
   def find_server_remotes(self,server_name):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.site )
       query_list = self.qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=server_name )
       query_list = self.qs.add_match_terminal( query_list, relationship =  "REMOTE_UNIT" )
       sets, sources = self.qs.match_list(query_list)  
       remotes = []
       for i in sources:
          remotes.append(i["modbus_address"])

       remotes.sort()
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




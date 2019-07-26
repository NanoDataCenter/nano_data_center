#
#
#  File: flask_web_py3.py
#
#
#
import os
import json
import redis


import flask
from flask import Flask
from flask import render_template,jsonify
from flask_httpauth import HTTPDigestAuth
from flask import request, session
from bootstrap_web_py3.load_static_pages_py3     import  Load_Static_Files 
from bootstrap_web_py3.load_eto_management_py3     import  Load_ETO_Management
from bootstrap_web_py3.load_redis_access_py3     import  Load_Redis_Access
from redis_support_py3.graph_query_support_py3 import  Query_Support
from eto_init_py3 import User_Data_Tables
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from core_libraries.irrigation_hash_control_py3 import generate_irrigation_control
from redis_support_py3.load_files_py3  import APP_FILES
from redis_support_py3.load_files_py3  import SYS_FILES
from bootstrap_web_py3.load_app_sys_files_py3 import Load_App_Sys_Files
from bootstrap_web_py3.load_linux_management_py3 import Load_Linux_Management
from bootstrap_web_py3.load_redis_management_py3 import Load_Redis_Management
from bootstrap_web_py3.load_site_map_py3   import Load_Site_Data
from bootstrap_web_py3.load_process_control_py3 import Load_Process_Management
from bootstrap_web_py3.load_configuration_py3 import Load_Configuration_Data
from bootstrap_web_py3.load_irrigation_control_py3 import Load_Irrigation_Pages
from bootstrap_web_py3.load_mqtt_management_py3 import Load_MQTT_Pages
class PI_Web_Server(object):

   def __init__(self , name, redis_site_data ):
       redis_handle_pw = redis.StrictRedis(redis_site_data["host"], 
                                           redis_site_data["port"], 
                                           db=redis_site_data["redis_password_db"], 
                                           decode_responses=True)

       self.redis_site_data = redis_site_data                                       
       startup_dict = redis_handle_pw.hgetall("web")
       self.data_structure_redis_handle =  redis.StrictRedis( host = redis_site_data["host"] , port=redis_site_data["port"], db=redis_site_data["redis_io_db"] ) 
       
       self.qs = Query_Support( redis_server_ip = redis_site_data["host"], redis_server_port=redis_site_data["port"] )
       self.user_table = User_Data_Tables(self.qs,self.data_structure_redis_handle,redis_site_data)
       self.app         = Flask(name) 
       self.auth = HTTPDigestAuth()
       self.auth.get_password( self.get_pw )
       startup_dict["DEBUG"]  = True
       self.startup_dict = startup_dict
      
      
       self.app.template_folder       =   'bootstrap_web_py3/templates'
       self.app.static_folder         =   'bootstrap_web_py3/static'  
       self.app.config['SECRET_KEY']      = startup_dict["SECRET_KEY"]

       self.app.config["DEBUG"]           = True
       self.app.debug                     = True
       self.users                    = json.loads(startup_dict["users"])
       self.redis_file_handle = redis.StrictRedis(redis_site_data["host"], redis_site_data["port"], db=redis_site_data["redis_file_db"] )
       
       self.app_files = APP_FILES(self.data_structure_redis_handle, self.redis_site_data) 
       self.sys_files = SYS_FILES(self.data_structure_redis_handle, self.redis_site_data)          

       Load_Static_Files(self.app,self.auth)
       self.redis_access = Load_Redis_Access(self.app, self.auth, request )
       Load_App_Sys_Files( self.app, self.auth, request, self.app_files, self.sys_files    )
       Load_Site_Data(self.app, self.auth, render_template)
       
       self.load_eto_management()
       self.load_linux_monitoring()
       self.load_redis_monitoring()
       self.load_process_management()
       self.load_configuration_management()
       self.load_irrigation_control()
       self.load_mqtt_management()
      
 

   def get_pw( self,username):
       
       print(username)
       if username in self.users:
           print("sucess")
           return self.users[username]
       return None
    
       
 

   def run_http( self):
       self.app.run(threaded=True , use_reloader=True, host='0.0.0.0',port=80)

   def run_https( self ):
       startup_dict          = self.startup_dict
      
       self.app.run(threaded=True , use_reloader=True, host='0.0.0.0',debug = True,
           port=int(startup_dict["PORT"]) ,ssl_context=(startup_dict["crt_file"], startup_dict["key_file"]))
       
 

   
   def get_pw( self,username):
       
      
       if username in self.users:
           return self.users[username]
       return None

   def load_eto_management(self):
       # from graph get hash tables
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )
       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "WS_STATION" )
                                        
       eto_sets, eto_sources = self.qs.match_list(query_list)                                    
    
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"WEATHER_STATION_DATA"} )
                                           
       package_sets, package_sources = self.qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,self.data_structure_redis_handle)
       self.ds_handlers = {}
       self.ds_handlers["EXCEPTION_VALUES"] = generate_handlers.construct_hash(data_structures["EXCEPTION_VALUES"])
       self.ds_handlers["ETO_VALUES"] = generate_handlers.construct_hash(data_structures["ETO_VALUES"])
       self.ds_handlers["RAIN_VALUES"] = generate_handlers.construct_hash(data_structures["RAIN_VALUES"])
       self.ds_handlers["ETO_CONTROL"] = generate_handlers.construct_hash(data_structures["ETO_CONTROL"])
       self.ds_handlers["ETO_HISTORY"] = generate_handlers.construct_redis_stream_reader(data_structures["ETO_HISTORY"])
       self.ds_handlers["RAIN_HISTORY"] = generate_handlers.construct_redis_stream_reader(data_structures["RAIN_HISTORY"] )
       self.ds_handlers["EXCEPTION_LOG"] = generate_handlers.construct_redis_stream_reader(data_structures["EXCEPTION_LOG"] )
       self.ds_handlers["ETO_ACCUMULATION_TABLE"] = generate_handlers.construct_hash(data_structures["ETO_ACCUMULATION_TABLE"])
       
       self.redis_access.add_access_handlers("ETO_VALUES",self.ds_handlers["ETO_VALUES"],"Redis_Hash_Dictionary") 

       
       self.redis_access.add_access_handlers("RAIN_VALUES",self.ds_handlers["RAIN_VALUES"],"Redis_Hash_Dictionary") 


       
       eto_update_table = self.ds_handlers["ETO_ACCUMULATION_TABLE"]
       self.redis_access.add_access_handlers("eto_update_table",eto_update_table,"Redis_Hash_Dictionary") 
  
       
       Load_ETO_Management(self.app, self.auth,request, app_files=self.app_files, sys_files=self.sys_files,
                  render_template=render_template,redis_access = self.redis_access,eto_update_table = eto_update_table,
                     handlers=self.ds_handlers )    

   def load_linux_monitoring(self):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PROCESSOR" )
                                           
       controller_sets, controller_nodes = self.qs.match_list(query_list)  
       controller_names = []
       for i in controller_nodes:
           controller_names.append(i["name"])
       controller_names.sort()
     
       ds_handlers = []
       for i in controller_names:
          ds_handlers.append(self.assemble_controller_handlers(i))
       Load_Linux_Management(self.app, self.auth,request, app_files=self.app_files, sys_files=self.sys_files,
                  render_template=render_template, handlers=ds_handlers, controllers = controller_names ) 



   def load_mqtt_management(self):
                             
    
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"MQTT_DEVICES_DATA"} )
                                           
       package_sets, package_sources = self.qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,self.data_structure_redis_handle)
       ds_handlers = {}
       ds_handlers["MQTT_CONTACT_LOG"] = generate_handlers.construct_hash(data_structures["MQTT_CONTACT_LOG"])
       ds_handlers["MQTT_REBOOT_LOG"] = generate_handlers.construct_hash(data_structures["MQTT_REBOOT_LOG"])
       ds_handlers["MQTT_UNKNOWN_DEVICES"] = generate_handlers.construct_hash(data_structures["MQTT_UNKNOWN_DEVICES"])
       ds_handlers["MQTT_UNKNOWN_SUBSCRIPTIONS"] = generate_handlers.construct_hash(data_structures["MQTT_UNKNOWN_SUBSCRIPTIONS"])
       ds_handlers["MQTT_PAST_ACTION_QUEUE"] = generate_handlers.construct_redis_stream_reader(data_structures["MQTT_PAST_ACTION_QUEUE"])
 
       Load_MQTT_Pages(self.app, self.auth,request, app_files=self.app_files, sys_files=self.sys_files,
                  render_template=render_template, redis_handle= self.data_structure_redis_handle, handlers= ds_handlers )
                  


   def load_irrigation_control(self):
                             
    
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGIGATION_SCHEDULING_CONTROL_DATA"} )
                                           
       package_sets, package_sources = self.qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,self.data_structure_redis_handle)
       ds_handlers = {}
       ds_handlers["IRRIGATION_JOB_SCHEDULING"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_JOB_SCHEDULING"])
       ds_handlers["IRRIGATION_PENDING"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_PENDING"])
       ds_handlers["IRRIGATION_PAST_ACTIONS"] = generate_handlers.construct_redis_stream_reader(data_structures["IRRIGATION_PAST_ACTIONS"])
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"MQTT_DEVICES_DATA"} )
                                           
       package_sets, package_sources = self.qs.match_list(query_list)
       package = package_sources[0]
       generate_handlers = Generate_Handlers(package,self.data_structure_redis_handle)
       data_structures = package["data_structures"]
       ds_handlers["MQTT_SENSOR_QUEUE"] = generate_handlers.construct_redis_stream_reader(data_structures["MQTT_SENSOR_QUEUE"])
    
       irrigation_control = generate_irrigation_control(self.redis_site_data,self.data_structure_redis_handle,self.qs)
       Load_Irrigation_Pages(self.app, self.auth,request, app_files=self.app_files, sys_files=self.sys_files,
                  render_template=render_template, redis_handle= self.data_structure_redis_handle, handlers= ds_handlers ,irrigation_control=irrigation_control)
                  
       
   def assemble_controller_handlers(self,label ):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_relationship( query_list, relationship = "PROCESSOR", label = label )
       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"SYSTEM_MONITORING"} )
                                           
       package_sets, package_sources = self.qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,self.data_structure_redis_handle)
       ds_handlers = {}
       ds_handlers["FREE_CPU"] = generate_handlers.construct_redis_stream_reader(data_structures["FREE_CPU"])
       ds_handlers["RAM"] = generate_handlers.construct_redis_stream_reader(data_structures["RAM"])
       ds_handlers["DISK_SPACE"] = generate_handlers.construct_redis_stream_reader(data_structures["DISK_SPACE"])
       ds_handlers["TEMPERATURE"] = generate_handlers.construct_redis_stream_reader(data_structures["TEMPERATURE"])
       ds_handlers["PROCESS_VSZ"] = generate_handlers.construct_redis_stream_reader(data_structures["PROCESS_VSZ"])
       ds_handlers["PROCESS_RSS"] = generate_handlers.construct_redis_stream_reader(data_structures["PROCESS_RSS"])
       ds_handlers["PROCESS_CPU"] = generate_handlers.construct_redis_stream_reader(data_structures["PROCESS_CPU"])
       
       ds_handlers["CPU_CORE"] = generate_handlers.construct_redis_stream_reader(data_structures["CPU_CORE"])
       ds_handlers["SWAP_SPACE"] = generate_handlers.construct_redis_stream_reader(data_structures["SWAP_SPACE"])
       ds_handlers["IO_SPACE"] = generate_handlers.construct_redis_stream_reader(data_structures["IO_SPACE"])
       ds_handlers["BLOCK_DEV"] = generate_handlers.construct_redis_stream_reader(data_structures["BLOCK_DEV"])
       ds_handlers["CONTEXT_SWITCHES"] = generate_handlers.construct_redis_stream_reader(data_structures["CONTEXT_SWITCHES"])
       ds_handlers["RUN_QUEUE"] = generate_handlers.construct_redis_stream_reader(data_structures["RUN_QUEUE"])
       ds_handlers["DEV"] = generate_handlers.construct_redis_stream_reader(data_structures["DEV"])
       ds_handlers["SOCK"] = generate_handlers.construct_redis_stream_reader(data_structures["SOCK"])
       ds_handlers["TCP"] = generate_handlers.construct_redis_stream_reader(data_structures["TCP"])
       ds_handlers["UDP"] = generate_handlers.construct_redis_stream_reader(data_structures["UDP"])
       return ds_handlers

   def load_redis_monitoring(self):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )
       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "REDIS_MONITORING" )
                                           
       package_sets, package_sources = self.qs.match_list(query_list)  
      
       package = package_sources[0]
       generate_handlers = Generate_Handlers(package,self.data_structure_redis_handle)
       data_structures = package["data_structures"]     
 
       ds_handlers = {}
       ds_handlers["REDIS_MONITOR_KEY_STREAM"] = generate_handlers.construct_redis_stream_reader(data_structures["REDIS_MONITOR_KEY_STREAM"])
       ds_handlers["REDIS_MONITOR_CLIENT_STREAM"] = generate_handlers.construct_redis_stream_reader(data_structures["REDIS_MONITOR_CLIENT_STREAM"])
       ds_handlers["REDIS_MONITOR_MEMORY_STREAM"] = generate_handlers.construct_redis_stream_reader(data_structures["REDIS_MONITOR_MEMORY_STREAM"])
       ds_handlers["REDIS_MONITOR_CALL_STREAM"] = generate_handlers.construct_redis_stream_reader(data_structures["REDIS_MONITOR_CALL_STREAM"])
       ds_handlers["REDIS_MONITOR_CMD_TIME_STREAM"] = generate_handlers.construct_redis_stream_reader(data_structures["REDIS_MONITOR_CMD_TIME_STREAM"])
       ds_handlers["REDIS_MONITOR_SERVER_TIME"] = generate_handlers.construct_redis_stream_reader(data_structures["REDIS_MONITOR_SERVER_TIME"])

       Load_Redis_Management(self.app, self.auth,request, app_files=self.app_files, sys_files=self.sys_files,
                  render_template=render_template, handlers=ds_handlers )    
  
       
       
   def load_process_management(self): 
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PROCESSOR" )
                                           
       controller_sets, controller_nodes = self.qs.match_list(query_list)  
       controller_names = []
       for i in controller_nodes:
           controller_names.append(i["name"])
       controller_names.sort()
       ds_handlers = []
       for i in controller_names:
          ds_handlers.append(self.assemble_process_controller_handlers(i))

   
       Load_Process_Management(self.app, self.auth, request, render_template, controller_names, ds_handlers) 

 
   def assemble_process_controller_handlers(self,label ):
       query_list = []
       query_list = self.qs.add_match_relationship( query_list,relationship="SITE",label=self.redis_site_data["site"] )

       query_list = self.qs.add_match_relationship( query_list, relationship = "PROCESSOR", label = label )
       query_list = self.qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"DATA_STRUCTURES"} )
                                           
       package_sets, package_sources = self.qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,self.data_structure_redis_handle)
       ds_handlers = {}
       ds_handlers["ERROR_STREAM"]        = generate_handlers.construct_redis_stream_reader(data_structures["ERROR_STREAM"])
       ds_handlers["ERROR_HASH"]        = generate_handlers.construct_hash(data_structures["ERROR_HASH"])
       ds_handlers["WEB_COMMAND_QUEUE"]   = generate_handlers.construct_job_queue_client(data_structures["WEB_COMMAND_QUEUE"])
       
       ds_handlers["WEB_DISPLAY_DICTIONARY"]   =  generate_handlers.construct_hash(data_structures["WEB_DISPLAY_DICTIONARY"])
       return ds_handlers
       
   def load_configuration_management(self):
       Load_Configuration_Data(self.app, self.auth,  render_template,request, self.app_files,self.sys_files)


 
if __name__ == "__main__":

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
  
   redis_site_data = json.loads(data)


   pi_web_server = PI_Web_Server(__name__, redis_site_data  )
   pi_web_server.run_http()
   
   

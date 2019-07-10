
import json
import time
import os
import time
## 1 gallon is 0.133681 ft3
## assuming a 5 foot radius
## a 12 gallon/hour head 0.2450996343 inch/hour
## a 14	gallon/hour head 0.2859495733 inch/hour
## a 16	gallon/hour head 0.3267995123 inch/hour
##
##
##
##
## capacity of soil
## for silt 2 feet recharge rate 30 % recharge inches -- .13 * 24 *.3 = .936 inch 
## for sand 1 feet recharge rate 30 % recharge inches -- .06 * 12 *.3 = .216 inch
##
## recharge rate for is as follows for 12 gallon/hour head:
## sand 1 feet .216/.245 which is 52 minutes
## silt 2 feet recharge rate is 3.820 hours or 229 minutes
##
## {"controller":"satellite_1", "pin": 9,  "recharge_eto": 0.216, "recharge_rate":0.245 },
## eto_site_data
from eto_init_py3 import Generate_Data_Handler
from irrigation_hash_control_py3 import Generate_Hash_Control_Handler

class ETO_Management(object):
   def __init__(self,redis_site,app_files):
 
       self.app_files = app_files
       self.generate_handlers = Generate_Data_Handler( redis_site )
       self.eto_hash_table = self.generate_handlers.get_data_handler()
   
      
      
   def update_eto_values(self,sensor_list):
       self.eto_site_data = self.app_files.load_file( "eto_site_setup.json" )
       for l in  sensor_list:
           j_index = l[0]
           queue_name = l[1]
           j = self.eto_site_data[ j_index ]
           deficient = self.eto_hash_table.hget( queue_name )
           
           if deficient == None:
               deficient = 0
           else:
               deficient = float(deficient)
           recharge_rate = float(j["recharge_rate"])
           deficient = deficient - (recharge_rate/60) # recharge rate is per hour
           if deficient < 0 :
               deficient = 0 
           
           self.eto_hash_table.hset( queue_name , deficient) 
      
   def determine_eto_management(self,run_time, io_list):
      self.eto_site_data = self.app_files.load_file( "eto_site_setup.json" )
      
      sensor_list = self.find_queue_names( io_list )
      if len(sensor_list) == 0:
        return run_time, False,None
      run_time = self.find_largest_runtime(run_time,sensor_list)
      return run_time,True,sensor_list
      
      
      




   def find_queue_names( self, io_list ):
       
       eto_values = []
       for j in io_list:
           controller = j["remote"]
           bits       = j["bits"]
           bit        = bits[0] 
           index = 0
           for m in self.eto_site_data:

               if (m["controller"] == controller) and (int(m["pin"]) in bits): 
                   queue_name = controller+"|"+str(bit)
                   eto_values.append( [index,  queue_name ] )
               index = index +1
       
       return eto_values


   def find_largest_runtime( self, run_time, sensor_list ):
       runtime = 0

       for j in sensor_list:
           index = j[0]
           queue_name = j[1]
           eto_temp = self.eto_site_data[index]
           recharge_eto = float( eto_temp["recharge_eto"] )  # minium eto for sprinkler operation
           recharge_rate = float(eto_temp["recharge_rate"])
           deficient = self.eto_hash_table.hget( queue_name )
           if deficient == None:
              deficient = 0
           if float(deficient) > recharge_eto :
               runtime_temp = (deficient  /recharge_rate)*60
           else:
               runtime_temp =  0
           if runtime_temp > runtime :
               runtime = runtime_temp
       if runtime > run_time:
          runtime = run_time
       return runtime

   def update_eto_queue_minute( self, sensor_list ):
       for l in  sensor_list:
           j_index = l[0]
           queue_name = l[1]
           j = self.eto_site_data[ j_index ]
           deficient = self.self.eto_hash_table.hget(  queue_name )
           
           if deficient == None:
               deficient = 0
           else:
               deficient = float(deficient)
           recharge_rate = float(j["recharge_rate"])
           deficient = deficient - (recharge_rate/60) # recharge rate is per hour
           if deficient < 0 :
               deficient = 0 
           
           self.eto_hash_table.hset(  queue_name, deficient )   

if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json
    import datetime
    import os
    import copy
   
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
    from redis_support_py3.load_files_py3 import APP_FILES
    from redis_support_py3.load_files_py3 import SYS_FILES
    from   py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
    from   py_cf_new_py3.cluster_control_py3 import Cluster_Control
    from   irrigation_control_py3.Incomming_Queue_Management_py3 import Incomming_Queue_Management
    from   irrigation_control_py3.misc_support_py3 import IO_Control
    from   irrigation_control_py3.irrigation_queue_processing_py3 import Irrigation_Queue_Management
    from irrigation_control_py3.master_valve_control_py3 import Master_Valve
   
    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
                            
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGIGATION_SCHEDULING_CONTROL_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)
    package = package_sources[0]    
    data_structures = package["data_structures"]
    generate_handlers = Generate_Handlers(package,redis_site)
    redis_handle = generate_handlers.get_redis_handle()    
    app_files        =  APP_FILES(redis_handle,redis_site)     
    sys_files        =  SYS_FILES(redis_handle,redis_site)
    ds_handlers = {}
    ds_handlers["IRRIGATION_PAST_ACTIONS"] = generate_handlers.construct_redis_stream_writer(data_structures["IRRIGATION_PAST_ACTIONS"] )
   
    ds_handlers["IRRIGATION_CURRENT_CLIENT"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_CURRENT"] )
    ds_handlers["IRRIGATION_CURRENT_SERVER"] = generate_handlers.construct_job_queue_server(data_structures["IRRIGATION_CURRENT"] )
    ds_handlers["IRRIGATION_JOB_SCHEDULING"] = generate_handlers. construct_job_queue_server(data_structures["IRRIGATION_JOB_SCHEDULING"] )
    ds_handlers["IRRIGATION_PENDING_CLIENT"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_PENDING"] )
    ds_handlers["IRRIGATION_PENDING_SERVER"] = generate_handlers.construct_job_queue_server(data_structures["IRRIGATION_PENDING"] )
   
    ds_handlers["IRRIGATION_VALVE_TEST"] = generate_handlers.construct_hash(data_structures["IRRIGATION_VALVE_TEST"])
    ds_handlers["IRRIGATION_TIME_HISTORY"] = generate_handlers.construct_hash(data_structures["IRRIGATION_TIME_HISTORY"])
    ds_handlers["VALVE_JOB_QUEUE_CLIENT"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_VALVE_JOB_QUEUE"] )
    ds_handlers["VALVE_JOB_QUEUE_SERVER"] = generate_handlers.construct_job_queue_server(data_structures["IRRIGATION_VALVE_JOB_QUEUE"] )
    irrigation_hash_control = Generate_Hash_Control_Handler(redis_site)  
  
 
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_terminal( query_list,relationship="CLEANING_VALVES",label="CLEANING_VALVES" )
    control_field, control_field_nodes = qs.match_list(query_list)
    cleaning_valves = control_field_nodes[0] 

    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_terminal( query_list,relationship="MASTER_VALVES",label="MASTER_VALVES" )
    control_field, control_field_nodes = qs.match_list(query_list)
    master_valves = control_field_nodes[0] 

    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_terminal( query_list,relationship="LOGGING_DEPTH",label="LOGGING_DEPTH" )
    control_field, control_field_nodes = qs.match_list(query_list)
    measurement_depths = control_field_nodes[0] 
    
  
    remote_classes = None #construct_classes_py3.Construct_Access_Classes(io_server_ip,io_server_port)
    
     
    cf = CF_Base_Interpreter()
    cluster_control = Cluster_Control(cf)
    eto_management = ETO_Management(redis_site,app_files)

    ##
    ## log entry that go removed
    ##
    ds_handlers["IRRIGATION_CURRENT_CLIENT"].delete_all() # delete current job to prevent circular reboots
    io_control = IO_Control(irrigation_hash_control)
   
    Irrigation_Queue_Management(handlers=ds_handlers,
                               cluster_id = 1, #### not sure what this is
                               cluster_control = cluster_control,
                               cf = cf,
                               app_files = app_files,
                               sys_files = sys_files,
                               manage_eto =eto_management,
                               irrigation_io = io_control,
                               master_valves = master_valves,
                               cleaning_valves = cleaning_valves,
                               measurement_depths =measurement_depths,
                               eto_management = eto_management,
                               irrigation_hash_control = irrigation_hash_control  )
                  
    Incomming_Queue_Management( cf = cf,
                                    handlers = ds_handlers,
                                    app_files = app_files,
                                    sys_files = sys_files,
                                    irrigation_hash_control = irrigation_hash_control,
                                    eto_management = eto_management,
                                     cluster_control = cluster_control,
                                    irrigation_io = io_control )

    Master_Valve("MASTER_VALVE", cf,cluster_control, io_control, ds_handlers)

                            
    #
    #  Instanciate Sub modules
    #  
    #  Instanciate sub modules
    #     Incomming job queue
    #     Job Dispacther
    #     Job Workers
    #         
    
    try:
       ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"REBOOT STARTUP","level":"RED"})
       cf.execute()
    except Exception as tst:
      #
      #Deleting current irrigation job to prevent circular reboots
      #
      print("tst",tst)
      ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"Exception","details":str(tst),"level":"RED"})
      raise ValueError(tst)
     



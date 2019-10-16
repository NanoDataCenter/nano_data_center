
import json
import time
import os
import time


class Generate_Control_Events(object):

   def __init__(self,cf):
       self.cf = cf
       
   def open_cleaning_valve(self):
      self.cf.send_event("IRI_OPEN_CLEANING_VALVE" ) 

   def close_cleaning_valve(self):
       self.cf.send_event("IRI_CLOSE_CLEANING_VALVE" ) 
          
   def change_cleaning_valve_offline(self,*args):
       self.cf.send_event("IRI_CLEANING_VALVE_MONITOR_OFFLINE") 
          
   def change_cleaning_valve_online(self,*args):
       self.cf.send_event("IRI_CLEANING_VALVE_MONITOR_ONLINE") 
           

   def change_master_valve_off(self):
       self.cf.send_event("IRI_CLOSE_MASTER_VALVE") 
          
   def change_master_valve_on(self):
       self.cf.send_event("IRI_OPEN_MASTER_VALVE") 
          
   def change_master_valve_offline(self,*args):
       self.cf.send_event("IRI_MASTER_VALVE_SUSPEND") 
          
   def change_master_valve_online(self,*args):       
       self.cf.send_event("IRI_MASTER_VALVE_RESUME") 
          
   def cancel_timed_state(self):
       self.cf.send_event("IRI_EXTERNAL_CLOSE") 
          
   def change_to_timed_state(self):
       self.cf.send_event("IRI_EXTERNAL_TIMED_OPEN") 
          

def verify_startup(io_control,current_operations,failure_report):
    # check critical systems
    # check current controller
    #self.failure_report(self.current_operation,"MASTER_VALVE","OFF",{"flow_rate":self.master_flow}   )
    #self.failure_report(self.current_operation,"CLEANING_VALVE",None,{"flow_rate":self.cleaning_flow}   )
    #self.failure_report(self.current_operations,"EQUIPMENT_OVER_CURRENT",None,{"value":value,"limit":self.equipment_current_limit})
    #self.failure_report(self.current_operation,"Check_Off",None,{"flow_rate":temp} )
    return True 

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
    from core_libraries.irrigation_hash_control_py3 import get_flow_checking_limits
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
    from redis_support_py3.load_files_py3 import APP_FILES
    from redis_support_py3.load_files_py3 import SYS_FILES
    from   py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
    from   py_cf_new_py3.cluster_control_py3 import Cluster_Control
    from   irrigation_control_py3.Incomming_Queue_Management_py3 import Process_External_Commands
    from   irrigation_control_py3.misc_support_py3 import IO_Control
    from   irrigation_control_py3.irrigation_queue_processing_py3 import Process_Irrigation_Command
    from irrigation_control_py3.master_valve_control_py3 import Master_Valve
    from irrigation_control_py3.cleaning_valve_control_py3 import Cleaning_Valve
    from irrigation_control_py3.eto_management_py3 import ETO_Management
    from irrigation_control_py3.Failure_Report_py3 import Failure_Report
    from core_libraries.irrigation_hash_control_py3 import generate_irrigation_control
    from core_libraries.irrigation_hash_control_py3 import generate_sensor_minute_status
    from core_libraries.irrigation_hash_control_py3 import generate_mqtt_devices
    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
    qs = Query_Support( redis_site )
                            
    irrigation_excessive_flow_limits = get_flow_checking_limits(redis_site,qs)
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGIGATION_SCHEDULING_CONTROL_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)
    package = package_sources[0]    
    data_structures = package["data_structures"]
    
    generate_handlers = Generate_Handlers(package,qs)
    
    app_files        =  APP_FILES(qs.get_redis_data_handle(),redis_site)     
    sys_files        =  SYS_FILES(qs.get_redis_data_handle(),redis_site)
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
    ds_handlers["MQTT_SENSOR_STATUS"] = generate_sensor_minute_status(redis_site,qs)
    ds_handlers["MQTT_CONTACT_LOG"] = generate_mqtt_devices(redis_site,qs)
    irrigation_hash_control = generate_irrigation_control(redis_site,qs)  

 
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
    
    current_operations = {}
    current_operations["state"] = "OFFLINE"
    failure_report_class = Failure_Report(None)  # fill in stream handler later
    failure_report = failure_report_class.failure_report
    
    
    cf = CF_Base_Interpreter()
    cluster_control = Cluster_Control(cf)
    generate_control_events = Generate_Control_Events(cf)
    eto_management = ETO_Management(qs,redis_site,app_files)
    io_control = IO_Control(irrigation_hash_control,generate_control_events)
    ##
    ## indicating irrigation reboot
    ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"REBOOT STARTUP","level":"RED"})
   
    status = ds_handlers["IRRIGATION_CURRENT_CLIENT"].pop()
    irrigation_hash_control.hset("SUSPEND",False)
    if status[0] == True:
       temp = status[1]
       ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"Deleting_Irrigation_Job","details":{"schedule_name":temp["schedule_name"],"step":temp["step"]},"level":"RED"})
    ds_handlers["IRRIGATION_CURRENT_CLIENT"].delete_all() # delete current job to prevent circular reboots



   
    
    while True:
       if verify_startup(io_control,current_operations,failure_report) == True:
          break
          
          
    #
    # Three items are running at the same time
    # 1.  Monitor Commands coming from other processes job queue "IRRIGATION_JOB_SCHEDULING"
    # 2.  Dispatch Commands individual commands from Outside Processes 
    # 3.  Control Master Valve as Master Valve can be controlled individually from schedued irrigation
    #

    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_relationship( query_list,relationship="IRRIGIGATION_SCHEDULING_CONTROL" )
    query_list = qs.add_match_terminal( query_list, 
                                        relationship =  "CURRENT_LIMITS" )
                                        
    limits_sets, limit_sources = qs.match_list(query_list) 
    
    equipment_current_limit =  limit_sources[0]["EQUIPMENT"]
    print("equipment_current_limit",equipment_current_limit)
    
    Process_Irrigation_Command( redis_site_data = redis_site,
                                 handlers=ds_handlers,
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
                                 irrigation_hash_control = irrigation_hash_control,
                                 qs = qs,
                                 generate_control_events = generate_control_events,
                                 failure_report = failure_report,
                                 
                                 current_operations = current_operations )
                                
                                 
               
    Process_External_Commands( cf = cf,
                                    handlers = ds_handlers,
                                    app_files = app_files,
                                    sys_files = sys_files,
                                    irrigation_hash_control = irrigation_hash_control,
                                    eto_management = eto_management,
                                    cluster_control = cluster_control,
                                    irrigation_io = io_control,
                                    generate_control_events = generate_control_events,
                                    failure_report = failure_report,
                                    equipment_current_limit = equipment_current_limit,
                                    current_operations = current_operations )
    
   
    Master_Valve("MASTER_VALVE", cf,cluster_control, io_control, ds_handlers,current_operations,failure_report,irrigation_excessive_flow_limits)
    
    Cleaning_Valve("CLEANING_VALVES",cf,cluster_control, io_control, ds_handlers,current_operations,failure_report,irrigation_excessive_flow_limits)
                            
    #
    #  Instanciate Sub modules
    #  
    #  Instanciate sub modules
    #     Incomming job queue
    #     Job Dispacther
    #     Job Workers
    #         
    
    try:
       
       cf.execute()
    except Exception as tst:
      #
      #Deleting current irrigation job to prevent circular reboots
      #
      print("tst",tst)
      ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"Exception","details":str(tst),"level":"RED"})
      raise ValueError(tst)
     



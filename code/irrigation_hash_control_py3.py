

import time
import redis
import json
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from redis_support_py3.graph_query_support_py3 import  Query_Support


class Generate_Hash_Control_Handler():
   def __init__(self,redis_site_data):
       qs = Query_Support( redis_server_ip = redis_site_data["host"], redis_server_port=redis_site_data["port"] )
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site_data["site"] )

       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGATION_CONTROL_MANAGEMENT"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       
       generate_handlers = Generate_Handlers(package,redis_site_data)
    
       self.handler =  generate_handlers.construct_hash(data_structures["IRRIGATION_CONTROL"])
       self.access_handler = {}
       self.access_handler["RAIN_FLAG"]   = self.set_rain_flag
       self.access_handler["ETO_MANAGEMENT"]   = self.set_eto_management_flag
       self.access_handler["FLOW_CUT_OFF"]   = self.set_flow_cutoff
       self.access_handler["CLEANING_VALVE"]   =   self.set_cleaning_interval
       self.access_handler["MASTER_VALVE"]   =  self.set_master_valve
       self.access_handler["CLEANING_VALVE"]   = self.set_cleaning_valve
       self.access_handler["MASTER_VALVE_SETUP"]   = self.set_master_valve_setup
       self.access_handler["SCHEDULE_NAME"]   = self.set_schedule_name
       self.access_handler["STEP"]   =        self.set_step_number
       self.access_handler["RUN_TIME"]   =   self.set_run_time
       self.access_handler["ELASPED_TIME"]  = self.set_elasped_time
       self.access_handler["TIME_STAMP"]  = self.set_time_stamp
       self.access_handler["SUSPEND"]    = self.set_suspend
       
       
   def get_redis_handle(self):
      return self.redis_handle
 
   def get_all(self):
      return self.handler.hgetall()   
      
   def set_field(self,field,data):
       try:
           self.access_handler[field](data)
       except:
           raise ValueError("Unrecognized field "+field)

   def clear_json_object(self):
       self.set_field("SCHEDULE_NAME","OFFLINE")
       self.set_field("STEP",0)
       self.set_field("RUN_TIME",0)
       self.set_field("ELASPED_TIME",0)
   
   def update_json_object(self,json_object):   
       self.set_field("SCHEDULE_NAME",json_object["schedule_name"])
       self.set_field("STEP",json_object["step"])
       try:
         self.set_field("RUN_TIME",json_object["run_time"])
       except:
         self.set_field("RUN_TIME",0)
       try:
         self.set_field("ELASPED_TIME",json_object["elasped_time"])
       except:
         self.set_field("ELASPED_TIME",0)     
         
   def get_rain_flag(self):
       temp = self.handler.hget("RAIN_FLAG")
       if (temp == 0) or (temp == 1 ):
         return temp
       self.handler.hset("RAIN_FLAG",0)
       return 0
 
   def set_rain_flag(self,data):
       data = int(data)
       if (data == 0) or (data == 1 ):
             self.handler.hset("RAIN_FLAG",data)
        
       else:
           self.handler.hset("RAIN_FLAG",0)
       return 
       
   def get_eto_management_flag(self):
       temp = self.handler.hget("ETO_MANAGEMENT")
       if (temp == 0) or (temp == 1 ):
         return temp
       self.handler.hset("ETO_MANAGEMENT",1)
       return 0
 
   def set_eto_management_flag(self,data):
       data = int(data)
       if (data == 0) or (data == 1 ):
             self.handler.hset("ETO_MANAGEMENT",data)
        
       else:
           self.handler.hset("ETO_MANAGEMENT",1)
       return 
 
 

       
       
   def get_flow_cutoff(self):
      data = self.handler.hget("FLOW_CUT_OFF")
      try:
         data = float(data)
      except:
         data = 30
         self.handler.hset("FLOW_CUT_OFF",data)
      return data
       
       
   def set_flow_cutoff(self,data):
      try:
         data = float(data)
      except:
         data = 30
      self.handler.hset("FLOW_CUT_OFF",data)
   
   def get_cleaning_interval(self):
      data = self.handler.hget("CLEANING_INTERVAL")
      try:
         data = float(data)
      except:
         data = 15000
         self.handler.hset("CLEANING_INTERVAL",data)
      return data
       
       
   def set_cleaning_interval(self,data):
      try:
         data = float(data)
      except:
         data = 15000
      self.handler.hset("CLEANING_INTERVAL",data)
   
  
   
      
   def get_master_valve(self):
       temp = self.handler.hget("MASTER_VALVE")
       if (temp == 0) or (temp == 1 ):
         return temp
       self.handler.hset("MASTER_VALVE",0)
       return 0
 
   def set_master_valve(self,data):
       data = int(data)
       if (data == 0) or (data == 1 ):
             self.handler.hset("MASTER_VALVE",data)
        
       else:
           self.handler.hset("MASTER_VALVE",0)
       return 
 
   def get_cleaning_valve(self):
       temp = self.handler.hget("CLEANING_VALVE")
       if (temp == 0) or (temp == 1 ):
         return temp
       self.handler.hset("CLEANING_VALVE",0)
       return 0
 
   def set_cleaning_valve(self,data):
       data = int(data)
       if (data == 0) or (data == 1 ):
             self.handler.hset("CLEANING_VALVE",data)
        
       else:
           self.handler.hset("CLEANING_VALVE",0)
       return 

   def get_master_valve_setup(self):
       temp = self.handler.hget("MASTER_VALVE_SETUP")
       if (temp == 0) or (temp == 1 ):
         return temp
       self.handler.hset("MASTER_VALVE_SETUP",0)
       return 0
        
   def set_master_valve_setup(self,data):
       data = int(data)
       if (data == 0) or (data == 1 ):
             self.handler.hset("MASTER_VALVE_SETUP",data)
        
       else:
           self.handler.hset("MASTER_VALVE_SETUP",0)
       return  

   def get_run_time(self):
       temp = self.handler.hget("RUN_TIME")
       try:
          temp = int(temp)
       except:
          temp = 0
          self.handler.hset("RUN_TIME",temp)     
       return temp   
       
   def set_run_time(self,data):
 
       data = int(data)
       self.handler.hset("RUN_TIME",data) 
       return  

   def get_step_number(self):
       temp = self.handler.hget("STEP")
       try:
          temp = int(temp)
       except:
          temp = 0
          self.handler.hset("STEP",temp)     
       return temp
        
   def set_step_number(self,data):
  
       data = int(data)
       self.handler.hset("STEP",data) 
       return  

   def get_schedule_name(self):
       temp = self.handler.hget("SCHEDULE_NAME")
       if temp != None:
         return str(temp)
       else:
         return ""
       
       
        
   def set_schedule_name(self,data):
       if data != None:
             self.handler.hset("SCHEDULE_NAME",str(data))
       else:
           self.handler.hset("SCHEDULE_NAME","OFFLINE")
       return  


   def get_elasped_time(self):
       temp = self.handler.hget("STEP")
       try:
          temp = int(temp)
       except:
          temp = 0
          self.handler.hset("ELASPED_TIME",temp)     
       return temp
        
   def set_elasped_time(self,data):
  
       data = int(data)
       self.handler.hset("ELASPED_TIME",data) 
       return  

   def get_time_stamp(self):
       temp = self.handler.hget("TIME_STAMP")
       try:
          temp = float(temp)
       except:
          temp = time.time()
          self.handler.hset("TIME_STAMP",temp)     
       return temp
        
   def set_time_stamp(self,data):
  
       data = float(data)
       self.handler.hset("TIME_STAMP",data) 
       return      
       
       
   def get_suspend(self):
       temp = self.handler.hget("SUSPEND")
       if (temp == 0) or (temp == 1 ):
         return temp
       self.handler.hset("SUSPEND",0)
       return 0
        
   
   def set_suspend(self,data):
       data = int(data)
       if (data == 0) or (data == 1 ):
             self.handler.hset("SUSPEND",data)
        
       else:
           self.handler.hset("SUSPEND",0)
       return  
  
   
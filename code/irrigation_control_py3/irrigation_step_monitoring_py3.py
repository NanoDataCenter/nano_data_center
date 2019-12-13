#Note -- deal with limits
#note -- deal with short irrigation sequences
#note -- deal with bad histories

import time
import math
from statistics import mean
from statistics import median
from statistics import pstdev

class Irrigation_Step_Monitoring(object):


   def __init__(self,handlers,manage_eto,io_manager,cf,irrigation_hash_control,qs,redis_site):
       self.manage_eto = manage_eto
       self.handlers   = handlers
       self.io_manager = io_manager
       self.cf         = cf
       self.irrigation_hash_control = irrigation_hash_control
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="IRRIGIGATION_SCHEDULING_CONTROL",label="IRRIGIGATION_SCHEDULING_CONTROL" )
       query_list = qs.add_match_terminal( query_list, 
                                        relationship =  "IRRIGATION_LOGGING",label = "IRRIGATION_LOGGING" )
       data_sets,data_list = qs.match_list(query_list)                 
       data = data_list[0]
       self.log_length = data["log_length"]
       self.settling_time = data["settling_time"]      
       self.key_list = ["WELL_PRESSURE",
                        "EQUIPMENT_CURRENT",
                        "IRRIGATION_CURRENT",
                        "MAIN_FLOW_METER",
                        "CLEANING_FLOW_METER",
                        "INPUT_PUMP_CURRENT",
                        "OUTPUT_PUMP_CURRENT"]
       self.sensor_list = ["WELL_PRESSURE",
                           "EQUIPMENT_CURRENT",
                           "IRRIGATION_CURRENT",
                           "MAIN_FLOW_METER",
                           "CLEANING_FLOW_METER",
                           "INPUT_PUMP_CURRENT",
                           "OUTPUT_PUMP_CURRENT"
                          ]

   


   def initialize_logging(self,json_object):
       #self.handlers["IRRIGATION_TIME_HISTORY"].delete_all()  # for test purposes only
       self.working_key = self.form_key(json_object)
       self.irrigation_run_history = self.format_entry()


       
           
       


   def step_logging(self, json_object):
       self.get_new_data(self.irrigation_run_history)

  
       
   def finalize_logging(self):
       self.sumarize_data(self.irrigation_run_history)
       self.time_history = self.handlers["IRRIGATION_TIME_HISTORY"].hget(self.working_key)
       
       if self.time_history == None:
          self.time_history = []
       
       self.time_history.append(self.irrigation_run_history)
      
       if len(self.time_history) >= self.log_length:
           self.time_history = self.time_history[1:]
       
       
       self.handlers["IRRIGATION_TIME_HISTORY"].hset(self.working_key,self.time_history)


   def form_key(self,json_object):

     
      key = ""
      for item in json_object["io_setup"]:
         if key == "":
             key = key+item["remote"]+":"+str(item["bits"][0])
         else:
              key = key+"/"+item["remote"]+":"+str(item["bits"][0]) 
      return key
      
   def format_entry(self):
      entry = {}
      for i in self.key_list:
          temp = {}
          temp["mean"] = 0.
          temp["sd"]  = 0.
          temp["data"] = []
          entry[i] = temp
      return entry
      
   def get_new_data(self,current_history):
      new_data = {}
      for i in range(0,len(self.key_list)):
         key = self.key_list[i]
         current_history[key]["data"].append(self.irrigation_hash_control.hget(self.sensor_list[i]))
         
      return new_data
      
     
      
   def sumarize_data(self,current_history):
       try:
          current_history["MAIN_FLOW_METER"]["total"] = sum(current_history[i]["data"])
       except:
           print("total exception")
           current_history["MAIN_FLOW_METER"]["total"] = 0
       for i in self.key_list:
           try:
              
               current_history[i]["mean"] = mean(current_history[i]["data"][self.settling_time:])
               current_history[i]["sd"]  = pstdev(current_history[i]["data"][self.settling_time:])
             
           except:
               print("bad current history")
       return current_history
 

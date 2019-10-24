#Note -- deal with limits
#note -- deal with short irrigation sequences
#note -- deal with bad histories

import time
import math

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


   def initialize_logging(self,json_object):
       self.handlers["IRRIGATION_TIME_HISTORY"].delete_all()  # for test purposes only
       self.working_key = self.form_key(json_object)
       time_history = self.handlers["IRRIGATION_TIME_HISTORY"].hget(self.working_key)
      
       if time_history == None:
          time_history = []
      
       time_history.append(self.format_entry())
      
       if len(time_history) > self.log_length:
           time_history = time_history[1:]

       self.handlers["IRRIGATION_TIME_HISTORY"].hset(self.working_key,time_history)
           
       


   def step_logging(self, json_object):
       time_history = self.handlers["IRRIGATION_TIME_HISTORY"].hget(self.working_key)
       #print("time_history",time_history)
       working_entry = time_history[-1]
       #print("working_entry",working_entry)
       self.add_new_data(working_entry,self.get_new_data())
       #print(self.get_new_data())
       #print(time_history)
       self.handlers["IRRIGATION_TIME_HISTORY"].hset(self.working_key,time_history)
       
   def finalize_logging(self):
       
       time_history = self.handlers["IRRIGATION_TIME_HISTORY"].hget(self.working_key)
       working_entry = time_history[-1]
       self.compute_mean(working_entry)
       self.compute_standard_deviation(working_entry)
       working_entry["summarized"] = True
       #print("time_history",time_history)
       #print("working_entry",working_entry)
       self.handlers["IRRIGATION_TIME_HISTORY"].hset(self.working_key,time_history)


   def form_key(self,json_object):

     
      key = ""
      for item in json_object["io_setup"]:
         key = key+"/"+item["remote"]+":"+str(item["bits"][0])

      return key
      
   def format_entry(self):
      entry = {}
      entry["summarized"] = False
      entry["mean"] = {}
      entry["sd"]  = {}
      entry["data"] = []
      return entry
      
   def get_new_data(self):
      new_data = {}
      new_data["WELL_PRESSURE"]        = self.irrigation_hash_control.hget("WELL_PRESSURE")
      new_data["EQUIPMENT_CURRENT"]    = self.irrigation_hash_control.hget("EQUIPMENT_CURRENT")
      new_data["IRRIGATION_CURRENT"]   = self.irrigation_hash_control.hget("IRRIGATION_CURRENT")
      new_data["MAIN_FLOW_METER"]      = self.irrigation_hash_control.hget("MAIN_FLOW_METER")
      new_data["CLEANING_FLOW_METER"]  = self.irrigation_hash_control.hget("CLEANING_FLOW_METER")
      new_data["INPUT_PUMP_CURRENT"]   = self.irrigation_hash_control.hget("INPUT_PUMP_CURRENT")
      new_data["OUTPUT_PUMP_CURRENT"]  = self.irrigation_hash_control.hget("OUTPUT_PUMP_CURRENT")
      return new_data
      
   def add_new_data(self,entry,new_data):
      entry["data"].append(new_data)   
      
   def compute_mean(self,working_entry):
      temp = working_entry["data"]
      for i in temp[0].keys():
         mean = 0
         if len(temp) > self.settling_time+1:
           for j in range(self.settling_time,len(temp)):
              mean += temp[j][i]
           mean = mean/(len(temp)-self.settling_time)  
           working_entry["mean"][i] = mean
         else:
            working_entry["mean"][i] = 0
         
   def compute_standard_deviation(self,working_entry):
      temp = working_entry["data"]
      for i in temp[0].keys():
         if len(temp) > self.settling_time+1:
            mean = working_entry["mean"][i]
            sd = 0
            for j in range(self.settling_time,len(temp)):
               sd += math.pow((temp[j][i] -mean),2)
           
            sd = sd/(len(temp)-self.settling_time)
            sd = math.sqrt(sd)         
            working_entry["sd"][i] = sd
         else:
           working_entry["sd"][i] = 0





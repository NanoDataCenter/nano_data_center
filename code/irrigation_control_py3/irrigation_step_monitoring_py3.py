#Note -- deal with limits
#note -- deal with short irrigation sequences
#note -- deal with bad histories



class Irrigation_Step_Monitoring(object):


   def __init__(self,handlers,manage_eto,io_manager,cf,irrigation_hash_control,qs):
       self.manage_eto = manage_eto
       self.handlers   = handlers
       self.io_manager = io_manager
       self.cf         = cf
       self.irrigation_hash_control = irrigation_hash_control
       self.qs = qs

   def initialize_monitoring(self,json_object):
       self.working_key = self.form_key(json_object)
       time_history = self.handlers["IRRIGATION_TIME_HISTORY"].hget(self.working_key)
       if time_history == None:
          time_history = []
          
       time_history.append(self.format_entry())
       if len(time_history) > TBD_limit:
           time_history = time_history[1:]
       self.handlers["IRRIGATION_TIME_HISTORY"].hset(self.working_key,time_history)
           
       


   def step_monitoring(self, json_object):
       time_history = self.handlers["IRRIGATION_TIME_HISTORY"].hget(self.working_key)
       working_entry = time_history[-1]
       self.add_new_data(working_entry,self.get_new_data())
       self.handlers["IRRIGATION_TIME_HISTORY"].hset(self.working_key,time_history)
       
   def finalize_run(self):
       time_history = self.handlers["IRRIGATION_TIME_HISTORY"].hget(self.working_key)
       working_entry = time_history[-1]
       self.compute_mean(working_entry)
       self.compute_standard_deviation(working_entry)
       working_entry["summarized"] = True
       self.handlers["IRRIGATION_TIME_HISTORY"].hset(self.working_key,time_history)


   def form_key(self,json_object):
      key = ""
      for i,item in json_object["io"].items():
         key = key+"/"+i+str(item)
      return key
      
   def format_entry(self):
      entry = {}
      entry["summarized"] = False
      entry["mean"] = {}
      entry["sd"]  = {}
      entry["data"] = []
      
   def get_new_data(self):
      new_data = {}
      new_data["WELL_PRESSURE"]        = self.irrigation_hash_control["WELL_PRESSURE"]
      new_data["EQUIPMENT_CURRENT"]    = self.irrigation_hash_control["EQUIPMENT_CURRENT"]
      new_data["IRRIGATION_CURRENT"]   = self.irrigation_hash_control["IRRIGATION_CURRENT"]
      new_data["MAIN_FLOW_METER"]      = self.irrigation_hash_control["MAIN_FLOW_METER"]
      new_data["CLEANING_FLOW_METER"]  = self.irrigation_hash_control["CLEANING_FLOW_METER"]
      new_data["INPUT_PUMP_CURRENT"]   = self.irrigation_hash_control["INPUT_PUMP_CURRENT"]
      new_data["OUTPUT_PUMP_CURRENT"]  = self.irrigation_hash_control["OUTPUT_PUMP_CURRENT"]
      return new_data
      
   def add_new_data(self,entry,new_data):
      entry["data"].append(new_data)   
      
   def compute_mean(self,working_entry):
      temp = working_entry["data"]
      for i in temp[0].keys():
         mean = 0
         for j in range(5,len(temp)):
           mean += temp[j][i]
         mean = mean/len(temp-5)  
         working_entry["mean"][i] = mean

         
   def compute_standard_deviation(self,working_entry):
      temp = working_entry["data"]
      for i in temp[0].keys():
         mean = working_entry["mean"][i]
         sd = 0
         for j in range(5,len(temp)):
           sd += math.pow((temp[j][i] -mean),2)
           
         sd = sd/len(temp-5)
         sd = math.sqrt(sd)         
         working_entry["sd"][i] = sd
  





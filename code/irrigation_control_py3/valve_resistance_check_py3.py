import json

import time

from .irrigation_logging_py3 import Hash_Logging_Object
class Valve_Resistance_Check(object):

   def __init__( self, 
                 cf, 
                 cluster_control,
                 io_control, 
                 handlers,
                 app_files, 
                 sys_files,
                 master_valves,
                 cleaning_valves,
                 measurement_depths,
                 mqtt_current_publish,
                 irrigation_hash_control,
                 Check_Cleaning_Valve,
                 get_json_object):
                 
       self.get_json_object = get_json_object
       self.handlers = handlers
       self.sys_files    = sys_files
       self.app_files    = app_files
       self.cf           = cf
       self.cluster_control = cluster_control
       self.io_control      = io_control
       self.master_valves = master_valves
       self.cleaning_valves = cleaning_valves   
       self.mqtt_current_publish = mqtt_current_publish
       self.irrigation_hash_control = irrigation_hash_control
       self.hash_logging   = Hash_Logging_Object(self.handlers, "IRRIGATION_VALVE_TEST",measurement_depths["valve_depth"] )
       self.Check_Cleaning_Valve = Check_Cleaning_Valve

   def construct_chains( self, cf):

       cf.define_chain("resistance_check",False)        
       cf.insert.send_event("IRI_MASTER_VALVE_SUSPEND",None)
       cf.insert.verify_function_terminate( self, "RELEASE_IRRIGATION_CONTROL" ,None, self.io_control.check_for_all_plcs)
       
       cf.insert.one_step( self.assemble_relevant_valves ) #  
       cf.insert.enable_chains(["test_each_valve"])
       cf.insert.wait_event_count( event = "IR_V_Valve_Check_Done" )
       cf.insert.log("event IR_V_Valve_Check_Done")
       cf.insert.one_step(self.log_valve_check)
       cf.insert.send_event("RELEASE_IRRIGATION_CONTROL" ) 
       #cf.insert.send_event("IRI_MASTER_VALVE_RESUME",None) # done in dispatching thread 
       cf.insert.terminate() 

       cf.define_chain("test_each_valve",False,init_function= self.check_queue)
       cf.insert.wait_event_count( count = 1 ) #synchronize on second tick
       cf.insert.one_step(self.valve_setup)
       cf.insert.wait_event_count(count =1)
       cf.insert.one_step(self.request_measurements)
       cf.insert.wait_event_count(count =6)
       cf.insert.one_step( self.valve_measurement)
       cf.insert.verify_function_terminate(  reset_event = "IR_V_Valve_Check_Done",
                                             reset_event_data=None,
                                             function = self.check_queue) 

       cf.insert.reset()
       self.Check_Cleaning_Valve("resistance_clean_valve",cf,self.handlers,self.io_control,self.irrigation_hash_control,self.get_json_object)
   
       return  ["resistance_check","test_each_valve","resistance_clean_valve"]

 



   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id, ["resistance_check"]  )


   def assemble_relevant_valves(self, *args):
       self.job_dictionary = set()
 
      
       
       
       
       self.handlers["VALVE_JOB_QUEUE_CLIENT"].delete_all()
       sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")

       for j in sprinkler_ctrl:
           schedule = j["name"]
           
           json_data  =self.app_files.load_file(j["link"]) 
           for i in json_data["schedule"]:
             for k in i:
                remote = k[0]
                for pin in k[1]:
                    self.update_entry( remote,pin )

      
      
       for j in self.master_valves["MASTER_VALVES"]:
          remote = j["remote"]
          pins    = j["pins"]
          
          for pin in pins:
             self.update_entry( remote,pin )
          
       for j in self.cleaning_valves["CLEANING_VALVES"]:
          remote = j["remote"]
          pins    = j["pins"]
          
          for pin in pins:
             self.update_entry( remote,pin )
       
               
   def add_resistance_entry( self, remote,pin ):
       entry = str(remote)+":"+str(pin)
       temp = int(pin)
       if entry not in self.job_dictionary:
               self.job_dictionary.add( entry)
               
               json_object = [ remote,pin]
               self.handlers["VALVE_JOB_QUEUE_CLIENT"].push(json_object)
              


   def update_entry( self,remote,pin ):
       
     
       
 
       self.add_resistance_entry( remote, pin)

          
       

   def check_queue( self,*args ):

       length = self.handlers["VALVE_JOB_QUEUE_SERVER"].length()
      
       if length > 0:
           return_value = True
       else:
           
           return_value = False
       
       return return_value

   def valve_setup(self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
          return "CONTINUE" 
       json_object = self.handlers["VALVE_JOB_QUEUE_SERVER"].pop()
       self.valve_object = json_object
       if json_object[0] == True:
          json_object = json_object[1]
          
          self.io_control.load_duration_counters( 1  ) 
          self.io_control.turn_on_valve(  [{"remote": json_object[0], "bits":[int(json_object[1])]}] ) #  {"remote":xxxx,"bits":[] } 
          self.remote = json_object[0]
          self.output = json_object[1]
          self.mqtt_current_publish.clear_max_currents()
          self.mqtt_current_publish.enable_equipment_relay()

   def request_measurements(self, cf_handle, chainObj, parameters, event):
       if event["name"] == "INIT":
          return "CONTINUE"      
       self.mqtt_current_publish.read_max_currents()
       self.mqtt_current_publish.read_relay_states()    
           
   def valve_measurement(self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
          return "CONTINUE"
       # check time stamp
       #
       #
       #
          
       coil_current = self.measure_current()
       
       self.hash_logging.log_value(self.remote+":"+str(self.output),coil_current )
       self.io_control.disable_all_sprinklers()
 

   def measure_current(self):
      
       max_current = self.irrigation_hash_control.hget("SLAVE_MAX_CURRENT")
       relay_state = self.irrigation_hash_control.hget("SLAVE_RELAY_STATE")
       return_value = False
       print("max_current",max_current)
       print("relay_state",relay_state)
       ref_time = time.time()
       plc_flag = False
       if max_current == None:
          plc_flag = True
       if relay_state == None:
         plc_flag = True
       if ref_time - max_current["timestamp"] > 6: # results greater than one minute ago
           plc_flag = True
       if ref_time - relay_state["timestamp"] >  6: # results greater than one minute ago
           plc_flag = True
           
       if plc_flag == True:
         return_value =  self.io_controlmeasure_valve_current()
               
       
       elif relay_state['IRRIGATION_STATE'] == False:
         return_value =  max_current['MAX_IRRIGATION_CURRENT']
         detail = {"current":return_value,"valve":self.valve_object[1]}   
         self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"valve_short","details":detail})
       else:
         return_value =  max_current['MAX_IRRIGATION_CURRENT']
       print("valve",self.valve_object[1],return_value)
       return return_value
 
   def log_valve_check( self,*args):
        
     self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"valve_resistance_done","details":{},"level":"GREEN"})
 
       

if __name__ == "__main__":
   pass

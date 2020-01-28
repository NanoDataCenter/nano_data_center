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
                 irrigation_hash_control,
                 get_json_object,
                 current_operations,
                 generate_control_events,
                 irrigation_current_limit):
                 
                 
       self.get_json_object = get_json_object
       self.handlers = handlers
       self.sys_files    = sys_files
       self.app_files    = app_files
       self.cf           = cf
       self.cluster_control = cluster_control
       self.io_control      = io_control
       self.master_valves = master_valves
       self.cleaning_valves = cleaning_valves   
       self.current_operations = current_operations
      
       self.current_operations=current_operations
       self.generate_control_events = generate_control_events
       self.irrigation_current_limit = irrigation_current_limit
       
       self.irrigation_hash_control = irrigation_hash_control
       self.hash_logging   = Hash_Logging_Object(self.handlers, "IRRIGATION_VALVE_TEST",measurement_depths["valve_depth"] )
       

   def construct_chains( self, cf):

       cf.define_chain("resistance_check",False)        
       cf.insert.one_step(self.generate_control_events.change_master_valve_offline)
       cf.insert.one_step(self.generate_control_events.change_master_valve_offline)
       cf.insert.assert_function_terminate( "RELEASE_IRRIGATION_CONTROL" ,
                                             None, self.io_control.verify_irrigation_controllers)
       
       cf.insert.one_step( self.assemble_relevant_valves ) #  
       cf.insert.enable_chains(["test_each_valve"])
       cf.insert.wait_event_count( event = "IR_V_Valve_Check_Done" )
       cf.insert.log("event IR_V_Valve_Check_Done")
       cf.insert.one_step(self.log_valve_check)
       cf.insert.send_event("RELEASE_IRRIGATION_CONTROL" ) 
       cf.insert.one_step(self.generate_control_events.change_master_valve_online)
       cf.insert.one_step(self.generate_control_events.change_cleaning_valve_online)
       cf.insert.terminate() 

       cf.define_chain("test_each_valve",False,init_function= self.check_queue)
       cf.insert.wait_event_count( count = 1 ) #synchronize on second tick
       cf.insert.one_step(self.valve_setup)

       cf.insert.wait_event_count(count =2)
       cf.insert.one_step( self.valve_measurement)
       cf.insert.verify_function_terminate(  reset_event = "IR_V_Valve_Check_Done",
                                             reset_event_data=None,
                                             function = self.check_queue) 

       cf.insert.reset()
       
   
       return  ["resistance_check","test_each_valve"]

 



   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id, ["resistance_check"]  )


   def assemble_relevant_valves(self, *args):
       self.job_dictionary = set()
 
      
       
       
       
       self.job_queue = []
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
               self.job_queue.append(json_object)
              


   def update_entry( self,remote,pin ):
       
     
       
       
       self.add_resistance_entry( remote, pin)

          
       

   def check_queue( self,*args ):

       length = len(self.job_queue)
      
       if length > 0:
           return_value = True
       else:
           
           return_value = False
       
       return return_value

   def valve_setup(self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
          return "CONTINUE" 
       json_object = self.job_queue.pop()
       
       self.valve_object = json_object
       #print("valve object",self.valve_object)
      
          
       self.io_control.clear_max_currents()
       self.io_control.enable_irrigation_relay()
          
       self.io_control.turn_on_valves(  [{"remote": json_object[0], "bits":[int(json_object[1])]}] ) 
       self.remote = json_object[0]
       self.output = json_object[1]

 
           
   def valve_measurement(self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
          return "CONTINUE"
       # check time stamp
       #
       #
       #
       
       coil_current = self.io_control.measure_valve_current()
 
       print("coil_current",self.irrigation_current_limit,coil_current )
       if coil_current > self.irrigation_current_limit:
          details["remote"] = self.valve_object[0]
          details["bit"]    = self.valve_object[1]
          details["relay_state"] = relay_state
          details["current"] = coil_current
          details["limit"] = self.irrigation_current_limit
        
          self.current_operation= {}
          self.current_operation["state"] = "MEASURE_RESISTANCE"
          self.failure_report(self.current_operation,"MEASURE_RESISTANCE_CURRENT",None,details )
          self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"measure_resistance","details":details,"level":"RED"})
             
       
       logging_key = self.remote+":"+str(self.output)
       print(logging_key,coil_current)
       self.hash_logging.log_value(logging_key,coil_current )
       self.io_control.disable_all_sprinklers()
 


 
   def log_valve_check( self,*args):
        
     self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"valve_resistance_done","details":{},"level":"GREEN"})
 
       

if __name__ == "__main__":
   pass

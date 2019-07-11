import json

import time

from .irrigation_logging_py3 import Hash_Logging_Object
class Valve_Resistance_Check(object):

   def __init__( self, cf, cluster_control,io_control, handlers,
               app_files, sys_files,master_valves,cleaning_valves,measurement_depths):
       self.handlers = handlers
       self.sys_files    = sys_files
       self.app_files    = app_files
       self.cf           = cf
       self.cluster_control = cluster_control
       self.io_control      = io_control
       self.master_valves = master_valves
       self.cleaning_valves = cleaning_valves
       self.hash_logging   = Hash_Logging_Object(self.handlers, "IRRIGATION_VALVE_TEST",measurement_depths["valve_depth"] )
       


   def construct_chains( self, cf):

       cf.define_chain("resistance_check",False)        
       cf.insert.send_event("IRI_MASTER_VALVE_SUSPEND",None)
       cf.insert.one_step( self.assemble_relevant_valves )
       cf.insert.enable_chains(["test_each_valve"])
       cf.insert.wait_event_count( event = "IR_V_Valve_Check_Done" )
       cf.insert.log("event IR_V_Valve_Check_Done")
       cf.insert.one_step(self.log_valve_check)
       cf.insert.send_event("RELEASE_IRRIGATION_CONTROL" ) 
       cf.insert.send_event("IRI_MASTER_VALVE_RESUME",None)
       cf.insert.terminate() 

       cf.define_chain("test_each_valve",False,init_function= self.check_queue)
       cf.insert.wait_event_count( count = 1 )
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

   def valve_setup(self, *args ):
      
       json_object = self.handlers["VALVE_JOB_QUEUE_SERVER"].pop()
       if json_object[0] == True:
          json_object = json_object[1]
          
          self.io_control.load_duration_counters( 1  ) 
          self.io_control.turn_on_valve(  [{"remote": json_object[0], "bits":[int(json_object[1])]}] ) #  {"remote":xxxx,"bits":[] } 
          self.remote = json_object[0]
          self.output = json_object[1]
 

           
   def valve_measurement(self, *args ):
       
       coil_current = self.io_control.measure_valve_current()
       print( "coil current",coil_current )
       self.hash_logging.log_value(self.remote+":"+str(self.output),coil_current )
       self.io_control.disable_all_sprinklers()
               
   def log_valve_check( self,*args):
        
     self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"valve resistance","details":{},"level":"GREEN"})
 
       

if __name__ == "__main__":
   pass

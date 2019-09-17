import time
import json
from .irrigation_step_monitoring_py3 import Irrigation_Step_Monitoring

class Irrigation_Control_Basic(object):

   def __init__( self,   cf,cluster_control,io_control,handlers,
                        app_files, sys_files, manage_eto,measurement_depths,
                        irrigation_hash_control,qs,redis_site,current_limit,
                        Check_Cleaning_Valve ,Check_Excessive_Current,Check_Excessive_Flow):
                        
       self.cf = cf
       self.cluster_ctrl   = cluster_control 
       self.io_control    = io_control
       self.handlers  =  handlers
       self.measurement_depths = measurement_depths
       self.manage_eto   = manage_eto
       self.app_files     = app_files
       self.sys_files     = sys_files
       self.irrigation_hash_control = irrigation_hash_control
       self.current_limit = current_limit
       
       
       self.step_monitor = Irrigation_Step_Monitoring(handlers,manage_eto,io_control,cf,irrigation_hash_control,qs,redis_site)
     

   

   def construct_chains( self , cf ):

  
       ## startup chain ##########################################################
       cf.define_chain("IR_D_start_irrigation_step", False ) # tested

      
       cf.insert.log("start irrigation ")
       
       cf.insert.wait_event_count( count= 2 )  # wait for termination chain going
       cf.insert.assert_function_terminate(  reset_event =  "RELEASE_IRRIGATION_CONTROL",
                                             reset_event_data=None,
                                             function = self.grab_json_data)      

       cf.insert.one_step( self.start_logging )

       cf.insert.wait_event_count( count= 1 )  # wait till timer tick
            
       cf.insert.assert_function_terminate(  reset_event = "RELEASE_IRRIGATION_CONTROL",
                                             reset_event_data=None,
                                             function = self.check_required_plcs)
                                             
       cf.insert.assert_function_terminate(  reset_event = "RELEASE_IRRIGATION_CONTROL",
                                             reset_event_data=None,
                                             function = self.start)

       cf.insert.wait_event_count(event = "MINUTE_TICK")
       cf.insert.log("enabling chain ")
       cf.insert.enable_chains( ["IR_D_monitor_irrigation_step" ])
       cf.insert.terminate()      
      
      
       ## monitor chain ##########################################################
      


       cf.define_chain("IR_D_monitor_irrigation_step", False )
       cf.insert.log("monitor irrigation  step")
       cf.insert.wait_event_count(event = "MINUTE_TICK")
       

                                            

      
       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.monitor_irrigation)
       
       
       cf.insert.reset()      

       Check_Cleaning_Valve("basic_irrigation_cleaning_valve",cf,handlers,irrigation_io,irrigation_hash_control)
       Check_Excessive_Current("basic_irrigation_excessive_current",cf,handlers,irrigation_io,irrigation_hash_control)
       Check_Excessive_Flow("basic_irrigation_excessive_flow",cf,handlers,irrigation_io,irrigation_hash_control)
       

      


       return [ "IR_D_start_irrigation_step","IR_D_monitor_irrigation_step","basic_irrigation_cleaning_valve",
                 "basic_irrigation_excessive_current", "basic_irrigation_excessive_flow"      ]
                
                
   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id,
                          ["IR_D_start_irrigation_step"]  )
                          
                          
 ################################# Local Functions ################################################################


   def grab_json_data( self, *args ): #Transfer queue object to class
       try:
          self.json_object = self.handlers["IRRIGATION_CURRENT_SERVER"].show_next_job()[1]
       
          self.json_object["max_flow_time"] = 0
          self.json_object = self.convert_to_integers( self.json_object,
                                  ["run_time","step","elasped_time"])
          return True
       except:
          details = {}
          details["schedule_name"] = self.json_object["schedule_name"]
          details["step"]          = self.json_object["step"]
          details["run_time"]      = self.json_object["run_time"]
          details["io_setup"]      = self.json_object["io_setup"]
          self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"BAD_IRRIGATION_DATA","details":details,"level":"RED"})

   def convert_to_integers( self, dictionary, list_elements):
       for i in list_elements:
           dictionary[i] = int(dictionary[i] )
       return dictionary    
 


   def start_logging(self,*args):
       self.step_monitor.initialize_logging(self.json_object)  
   


   def check_required_plcs(self,cf_handle, chainObj, parameters, event):
      return_value = self.io_control.check_required_plcs(self.json_object['io_setup'])
      return return_value       
   
   def start(self,*args):
     
      self.io_control.load_duration_counters(self.json_object['run_time']+2)
      # turn on master valve
      self.io_control.turn_on_valve(self.json_object['io_setup'])
      self.update_json_object(self.json_object)
      time.sleep(5)
      if self.io_control.monitor_current(self.current_limit):
         return True
      else:
          details = {}
          details["schedule_name"] = self.json_object["schedule_name"]
          details["step"]          = self.json_object["step"]
          details["run_time"]      = self.json_object["run_time"]
          details["io_setup"]      = self.json_object["io_setup"]
          self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"IRRIGATION_EXCESSIVE_START_CURRENT","details":details,"level":"RED"})
          return False


   def monitor_irrigation( self, cf_handle, chainObj, parameters, event):
      return_value = True
      if event["name"] == "INIT":
           return True
      print("json_object",self.json_object)
      self.json_object["elasped_time"]  =      self.json_object["elasped_time"] +1
      self.io_control.turn_on_master_valves()
      self.io_control.turn_on_valve(self.json_object['io_setup'])
      self.update_json_object(self.json_object)
      self.manage_eto.update_eto_queue_minute( self.json_object['eto_list'] )
      if self.json_object["elasped_time"] <= self.json_object["run_time"]  :
           self.step_monitor.step_logging(self.json_object)       
 
      else:
           self.step_monitor.finalize_logging()
           details = {}
           details["schedule_name"] = self.json_object["schedule_name"]
           details["step"]          = self.json_object["step"]
           details["run_time"]      = self.json_object["run_time"]
           details["io_setup"]      = self.json_object["io_setup"]
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"IRRIGATION_STEP_COMPLETE","details":details,"level":"GREEN"})
           
           return_value = False
      return return_value


   def update_json_object(self,json_object):
      self.irrigation_hash_control.hset("SCHEDULE_NAME",json_object["schedule_name"])  
      self.irrigation_hash_control.hset("STEP",json_object["step"])  
      self.irrigation_hash_control.hset("RUN_TIME",json_object["run_time"])  
      self.irrigation_hash_control.hset("ELASPED_TIME",json_object["elasped_time"])  
      self.irrigation_hash_control.hset("TIME_STAMP",time.time())


  
















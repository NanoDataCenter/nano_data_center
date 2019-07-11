
import json
from .irrigation_step_monitoring_py3 import Irrigation_Step_Monitoring

class Irrigation_Control_Basic(object):

   def __init__( self,   cf,cluster_control,io_control,handlers,
                        app_files, sys_files, manage_eto,measurement_depths,irrigation_hash_control):
                        
       self.cf = cf
       self.cluster_ctrl   = cluster_control 
       self.io_control    = io_control
       self.handlers  =  handlers
       self.measurement_depths = measurement_depths
       
       self.app_files     = app_files
       self.sys_files     = sys_files
       self.irrigation_hash_control = irrigation_hash_control

       self.step_monitor = Irrigation_Step_Monitoring(handlers,manage_eto,io_control,cf)


   

   def construct_chains( self , cf ):

       ## terminate chain  ##########################################################
       cf.define_chain("IR_D_end_irrigation", True)
       cf.insert.log("termination started ")
       cf.insert.wait_event_count( event = "IR_D_END_IRRIGATION")
       #cf.insert.one_step(self.shutdown_irrigation)
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.terminate()      
  
       ## startup chain ##########################################################
       cf.define_chain("IR_D_start_irrigation_step", False ) # tested

      
       cf.insert.log("start irrigation ")
       cf.insert.enable_chains( ["IR_D_end_irrigation" ])
       cf.insert.wait_event_count( count= 2 )  # wait for termination chain going
       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.grab_json_data)      

       cf.insert.one_step( self.start_logging )

       cf.insert.wait_event_count( count= 1 )  # wait till timer tick
            

       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.start)


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
      
      
    

      
      
      


       return [ "IR_D_start_irrigation_step","IR_D_monitor_irrigation_step","IR_D_end_irrigation" ]
                
                
   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id,
                          ["IR_D_start_irrigation_step"]  )
                          
                          
 ################################# Local Functions ################################################################


   def grab_json_data( self, *args ): #Transfer queue object to class
      
       self.json_object = self.handlers["IRRIGATION_CURRENT_SERVER"].show_next_job()[1]
       
       self.json_object["max_flow_time"] = 0
       self.json_object = self.convert_to_integers( self.json_object,
                                  ["run_time","step","max_flow_time"])
       return True

   def convert_to_integers( self, dictionary, list_elements):
       for i in list_elements:
           dictionary[i] = int(dictionary[i] )
       return dictionary    
 


   def start_logging(self,*args):
       pass
   def start(self,*args):
      return True

   def monitor_irrigation( self, cf_handle, chainObj, parameters, event):
      return_value = True
      if event["name"] == "INIT":
           return True
     
      self.json_object["elasped_time"]  =      self.json_object["elasped_time"] +1
      self.json_object["max_flow_time"]       =  self.json_object["max_flow_time"]+1
      print("json_object",self.json_object)
      if self.json_object["elasped_time"] <= self.json_object["run_time"]  :
           self.step_monitor.step_monitoring(self.json_object)       
 
      else:
           return_value = False
      return return_value






















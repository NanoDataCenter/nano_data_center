
import json
class Irrigation_Control_Basic(object):

   def __init__( self,   cf,cluster_control,io_control,  
                        redis_handle, alarm_queue, 
                        app_files, sys_files,
                        hooks_15 = [], hooks_60= [],hooks_start = [], hooks_term=[],
                        logging_obj = None, user_data = None ):
       self.cf = cf
       self.cluster_ctrl   = cluster_control
       self.io_control    = io_control
       self.redis_handle  = redis_handle
       self.alarm_queue   = alarm_queue
       self.app_files     = app_files
       self.sys_files     = sys_files
       self.hooks_start   = hooks_start
       self.hooks_15      = hooks_15
       self.hooks_60      = hooks_60
       self.logging_obj   = logging_obj
       self.hooks_term    = hooks_term
       self.user_data     = user_data


   def construct_chains( self , cf ):

       #
       #  Define Chain
       #
       cf.define_chain("IR_D_monitor",False)
       cf.insert.wait_event_count(event = "MINUTE_TICK")
       cf.insert.one_step(self.check_to_clean_filter)
       cf.insert.reset()

       cf.define_chain("IR_D_start_irrigation_step", False ) # tested

       # retreive json data from redis data base
       cf.insert.one_step( self.grab_json_data )
       # user defined checks on startup
       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.start_hook_functions)
       cf.insert.one_step( self.start_logging )

       cf.insert.wait_event_count( count= 1 )  # wait till timer tick
            

       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.start)

       cf.insert.wait_event_count( count= 2 )  # wait a second
       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.measure_current)
     
       cf.insert.enable_chains( ["IR_D_monitor_current_sub","IR_D_monitor_irrigation_step" ])
       cf.insert.terminate()



       #
       # Define Chain
       #
       #

       cf.define_chain("IR_D_monitor_current_sub", False )
       cf.insert.log( "monitor_current_sub chain is working")
       cf.insert.wait_event_count( count = 15 )
       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.measure_current)
       cf.insert.one_step( self.monitor_io)
       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.hook_15_functions)

       cf.insert.reset()

       #
       # Define Chain
       #
       #

       cf.define_chain("IR_D_monitor_irrigation_step", False )
       cf.insert.wait_event_count(event = "MINUTE_TICK")
       

       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.hook_60_functions)


  
       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.check_for_excessive_flow_rate)
       cf.insert.one_step(self.update_logging)

       cf.insert.assert_function_terminate(  reset_event = "IR_D_END_IRRIGATION",
                                             reset_event_data=None,
                                             function = self.monitor_irrigation)
       
       cf.insert.reset()

       #
       # Define Chain
       #
       #

       cf.define_chain("IR_D_end_irrigation", False)
       cf.insert.wait_event_count( event = "IR_D_END_IRRIGATION")
       cf.insert.one_step( self.hook_term_functions)
       cf.insert.one_step( self.end_logging)
       cf.insert.one_step(self.clean_up_irrigation_cell)
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.terminate()

       return ["IR_D_monitor", "IR_D_start_irrigation_step","IR_D_monitor_current_sub",
                "IR_D_monitor_irrigation_step","IR_D_end_irrigation" ]



   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id,
                          ["IR_D_monitor","IR_D_start_irrigation_step","IR_D_end_irrigation"]  )


   #
   #
   # Chain flow functions
   #
   #

   def monitor_io( self,*args):
       if self.ref_current == None:
           self.ref_current = self.current
       if (self.current / self.ref_current) > .9 :
           self.ref_current = self.current
       else:
           self.json_object["io_restarts"] +=1
           self.io_control.turn_on_master_valves()
           self.io_control.turn_on_valve(self.json_object["io_setup"])

  

   def grab_json_data( self, *args ): #Transfer queue object to class
       json_string      = self.redis_handle.lindex( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE",0 )
       self.json_object                             = json.loads(json_string)
       self.json_object["max_flow_time"] = 0
       self.json_object = self.convert_to_integers( self.json_object,
                                  ["run_time","step","max_flow_time"])

       self.json_object["max_flow"]  =             float( self.check_redis_value("FLOW_CUT_OFF"))
             

   

   def start_logging( self, *args):
       self.alarm_queue.alarm_state = False
       if self.logging_obj != None:
           self.logging_obj.start( self )

   def update_logging( self, *args):
       if self.logging_obj != None:
           self.logging_obj.update( self )

   def end_logging( self, *args):
       if self.logging_obj != None:
           self.logging_obj.post( self )
            
   def start_hook_functions( self, cf_handle, chainObj, parameters, event):  #user defined checks on startup
       if event["name"] == "INIT":
          return True

       return_value = True
       for i in self.hooks_start:
           return_value = i(self)
           if return_value != True:
               break
       return return_value


   def hook_15_functions( self, cf_handle, chainObj, parameters, event):  #user defined checks on startup'
       if event["name"] == "INIT":
          return True

       return_value = True
       for i in self.hooks_15:
           return_value = i(self)
           if return_value != True:
               break
       return return_value

   def hook_60_functions( self, cf_handle, chainObj, parameters, event):  #user defined checks on startup
       if event["name"] == "INIT":
          return True

       return_value = True
       for i in self.hooks_60:
           return_value = i(self)
           if return_value != True:
               break
       return return_value


   def hook_term_functions( self, cf_handle, chainObj, parameters, event): #user defined termination steps      
       for i in self.hooks_term:
           i(self)



   def measure_current( self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
          return True
      
       else:
           
           return_value = True
           self.current =  self.io_control.measure_valve_current()
          
           if self.current > 24:
               self.alarm_queue.alarm_state = True
               self.alarm_queue.store_past_action_queue("IRRIGATION:CURRENT_ABORT",
                   "RED", { "schedule_name":self.json_object["schedule_name"],
                            "step_number":self.json_object["step"] } )
               return_value = False
       print("measure current",self.current,return_value)
       return return_value
 
   def check_for_excessive_flow_rate(self, cf_handle, chainObj, parameters, event):
       return_value = True
       
       if event["name"] == "INIT":
           return_value = True
           
           flow_value = 0
       else:       
           if self.json_object["max_flow"]  == 0:
               return True
           flow_value  =  float( self.check_redis_value( "global_flow_sensor_corrected" ) ) 
  
           if (self.json_object["max_flow_time"] >= 2) and (flow_value > self.json_object["max_flow"]):
               self.over_load_time = self.over_load_time + 1
               if self.over_load_time > 2:
                   self.alarm_queue.alarm_state = True
                   self.alarm_queue.store_past_action_queue("IRRIGATION:FLOW_ABORT","RED",
                   { "schedule_name":self.json_object["schedule_name"],
                     "step_number":self.json_object["step"],
                     "flow_value":flow_value,"max_flow":self.json_object["max_flow"] } )

                   return_value =  False
 
           else:
              self.over_load_time = 0
       
       return return_value


   def start( self, cf_handle, chainObj, parameters, event):
       return_value = True
       if event["name"] == "INIT":
           return True
    
       
  
       return_value = True
       self.over_load_time = 0 
       self.json_object["io_restarts"] = 0
       if  self.json_object["run_time"]  == 0:
           return_value = False

       self.ref_current = None

       
             
       self.io_control.load_duration_counters( self.json_object["run_time"]  )
       self.io_control.turn_on_master_valves()
       self.io_control.turn_on_valve(self.json_object["io_setup"])
       self.elasped_time = 0
       self.update_control_variables()       

       return return_value


   def monitor_irrigation( self, cf_handle, chainObj, parameters, event):
       return_value = True
       if event["name"] == "INIT":
           return True
     
       self.json_object["elasped_time"]  =      self.json_object["elasped_time"] +1
       self.json_object["max_flow_time"]       =  self.json_object["max_flow_time"]+1
       if self.json_object["elasped_time"] <= self.json_object["run_time"]  :
           
          
           self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_count", self.json_object["elasped_time"] )
           
           self.update_control_variables()
       else:
           return_value = False
       return return_value





   #
   #
   # Support Functions
   #

   def check_redis_value( self,key):
       value =  self.redis_handle.hget( "CONTROL_VARIABLES",key )
       if value == None:
           value = 0
       return value








   def update_control_variables( self ):
       #self.redis_handle.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","AUTO")
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_name", self.json_object["schedule_name"] )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_step_number", self.json_object["step"] )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_step", self.json_object["step"] )

       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_count", self.json_object["elasped_time"] )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_max",  self.json_object[ "run_time"] )  

       json_string                       = json.dumps( self.json_object )
       self.redis_handle.lset( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", 0, json_string )

   def clean_up_irrigation_cell( self ,*arg):
       
       self.redis_handle.delete("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_name","offline" )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_step_number",0 )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_step",0 )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_time_count",0 )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_max",0 ) 
       self.redis_handle.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","AUTO")
 
       self.io_control.disable_all_sprinklers()
       self.io_control.clear_duration_counters()
       self.io_control.turn_off_master_valves()

 
   def convert_to_integers( self, dictionary, list_elements):
       for i in list_elements:
           dictionary[i] = int(dictionary[i] )
       return dictionary
                                 
   def check_to_clean_filter( self, chainFlowHandle, chainObj, parameters,event ):
       if event["name"] == "INIT":
          return True
       cleaning_interval = self.redis_handle.hget("CONTROL_VARIABLES","CLEANING_INTERVAL")
       cleaning_interval = float( cleaning_interval)
       flow_value   =  float( self.check_redis_value( "global_flow_sensor_corrected" ) )
       cleaning_sum =  float( self.check_redis_value( "cleaning_sum") )
       cleaning_sum = cleaning_sum + flow_value
       self.redis_handle.hset("CONTROL_VARIABLES","cleaning_sum",cleaning_sum)
       if cleaning_interval == 0 :
           return True  # no cleaning interval active

       if cleaning_sum > cleaning_interval :
           return False
       else:
           return True

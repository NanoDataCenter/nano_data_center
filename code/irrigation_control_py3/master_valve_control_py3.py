# This class controls the Master Valve and monitors for excessive flow
# The master valve is turned of for two reasons
# 1. Commands from irrigation programs
# 2. Commands from web where the valve will stay open a for a tbd time
# 3. Problem comes during cleaning where master control must be turned off during part of test
import time
class Master_Valve(object):

   def __init__( self, cluster_id, cf,cluster_control, irrigation_io, handlers,current_operation,failure_report,irrigation_excessive_flow_limits):
       self.cf = cf
       self.cluster_ctrl  = cluster_control
       self.irrigation_io = irrigation_io
       self.current_operation = current_operation
       self.failure_report    = failure_report
       self.irrigation_excessive_flow_limits = irrigation_excessive_flow_limits
       self.handlers  = handlers
       self.cluster_id    = cluster_id
       self.chain_list    = ["MV_STARTUP",
                             "MV_OFF_EV_HANDLER","MV_OFF_MONITOR",
                             "MV_ON_EV_HANDLER","MV_ON_MONITOR",
                             "MV_OFFLINE_EV_HANDLER",
                             "MV_TIME_EV_HANDLER","MV_TIME_CYCLE_MONITOR","MV_TIME_TURN_OFF"]
       self.current_operation = current_operation
       self.construct_chains( cf)
       cluster_control.define_cluster( cluster_id, self.chain_list , "MV_STARTUP" )
       # Master valve off
       # Master valve control disabled
       # Master valve time condition
     
       cluster_control.define_state( self.cluster_id, "MV_OFF", ["MV_OFF_EV_HANDLER","MV_OFF_MONITOR"])
       cluster_control.define_state( self.cluster_id, "MV_ON",["MV_ON_EV_HANDLER","MV_ON_MONITOR"])   
       cluster_control.define_state( self.cluster_id, "MV_OFFLINE", ["MV_OFFLINE_EV_HANDLER"])
       cluster_control.define_state( self.cluster_id, "MV_TIME_CYCLE",["MV_TIME_EV_HANDLER","MV_TIME_CYCLE_MONITOR","MV_TIME_TURN_OFF"])
       self.irrigation_io.turn_off_master_valves_direct() 
      
       
       
   def construct_chains( self, cf ):

       #
       # Start up chain
       #
       cf.define_chain("MV_STARTUP",True) # this thread is always active
       cf.insert.one_step(self.initial_setup)
       cf.insert.terminate()
       #
       # ON STATE
       #
       #    
    
 
       cf.define_chain("MV_ON_EV_HANDLER",False) # this thread is always active
       #cf.insert.log("mv off ev handler")
       cf.insert.check_event_no_init("IRI_CLOSE_MASTER_VALVE",self.change_to_off_state)
       cf.insert.check_event_no_init("IRI_OPEN_MASTER_VALVE", self.turn_on_master_valves )
       cf.insert.check_event_no_init("IRI_MASTER_VALVE_SUSPEND", self.change_to_offline_state ) 
       #cf.insert.check_event_no_init("IRI_MASTER_VALVE_RESUME", self.offline_exit ) #do nothing for this event
       #cf.insert.check_event_no_init("IRI_EXTERNAL_CLOSE", self.cancel_timed_state )
       cf.insert.check_event_no_init("IRI_EXTERNAL_TIMED_OPEN",self.change_to_timed_state)   
       cf.insert.reset()

       cf.define_chain("MV_ON_MONITOR",False) # make sure that there is no flow if master valve is off
       cf.insert.wait_event_count( event = "MINUTE_TICK" ) 
       #cf.insert.log("mv on monitor")
       cf.insert.verify_function_reset( reset_event=None,reset_event_data=None, 
                                        function = self.monitor_master_valve_open )
       cf.insert.one_step(self.turn_off_master_valves)
       cf.insert.send_event(event="RELEASE_IRRIGATION_CONTROL" )
       cf.insert.one_step( self.report_excessive_flow ) #master valve has been detected to be off
       cf.insert.one_step(self.change_to_off_state)

       #
       # OFF STATE
       #
       #
       cf.define_chain("MV_OFF_EV_HANDLER",False)
       #cf.insert.log("mv off ev handler")
       cf.insert.check_event_no_init("IRI_OPEN_MASTER_VALVE",self.change_to_on_state)
       cf.insert.check_event_no_init("IRI_CLOSE_MASTER_VALVE", self.turn_off_master_valves)
       cf.insert.check_event_no_init("IRI_MASTER_VALVE_SUSPEND", self.change_to_offline_state ) 
       #cf.insert.check_event_no_init("IRI_MASTER_VALVE_RESUME", self.offline_exit ) #do nothing for this event
       #cf.insert.check_event_no_init("IRI_EXTERNAL_CLOSE", self.cancel_timed_state )
       cf.insert.check_event_no_init("IRI_EXTERNAL_TIMED_OPEN",self.change_to_timed_state)       
       cf.insert.reset()

       cf.define_chain("MV_OFF_MONITOR",False) # make sure that there is no flow if master valve is off
       cf.insert.wait_event_count( event = "MINUTE_TICK" ) 
       #cf.insert.log("mv off monitor")
       cf.insert.verify_function_reset( reset_event=None,reset_event_data=None, 
                                        function = self.monitor_master_valve_close )
       cf.insert.one_step(self.irrigation_io.turn_off_pump) # currently system doesnot have this capability
       cf.insert.one_step( self.report_master_valve_failure ) #master valve has been detected to be off
       cf.insert.terminate()

       #
       # OFFLINE State
       #
       #
       cf.define_chain("MV_OFFLINE_EV_HANDLER",False)
       #cf.insert.log("off line state")
       cf.insert.check_event_no_init("IRI_OPEN_MASTER_VALVE",self.turn_on_master_valves)
       cf.insert.check_event_no_init("IRI_CLOSE_MASTER_VALVE", self.turn_off_master_valves )
       #cf.insert.check_event_no_init("IRI_MASTER_VALVE_SUSPEND", #### ) ####
       cf.insert.check_event_no_init("IRI_MASTER_VALVE_RESUME", self.offline_state_exit ) #do nothing for this event
       cf.insert.check_event_no_init("IRI_EXTERNAL_CLOSE", self.cancel_timed_state )
       cf.insert.check_event_no_init("IRI_EXTERNAL_TIMED_OPEN",self.change_to_timed_defered)       
       cf.insert.reset()
       
       #
       #
       #
       
       
       
       
       #
       # TIMED STATE
       #
       #
       cf.define_chain("MV_TIME_EV_HANDLER",False)
       cf.insert.check_event_no_init("IRI_OPEN_MASTER_VALVE",self.turn_on_master_valves)
       #cf.insert.check_event_no_init("IRI_CLOSE_MASTER_VALVE",self.set_timed_close_flag  )####
       cf.insert.check_event_no_init("IRI_MASTER_VALVE_SUSPEND", self.change_to_offline_state ) ####
       #cf.insert.check_event_no_init("IRI_MASTER_VALVE_RESUME", #### ) ######
       cf.insert.check_event_no_init("IRI_EXTERNAL_CLOSE", self.exit_timed_state )
       cf.insert.check_event_no_init("IRI_EXTERNAL_TIMED_OPEN",self.change_to_timed_state)    
       cf.insert.reset()
       
       cf.define_chain("MV_TIME_TURN_OFF",False) # thread becomes active if web commanded it to
       #cf.insert.log("mv time turn on")
       cf.insert.one_step(self.irrigation_io.turn_on_pump)
       cf.insert.one_step( self.turn_on_master_valves_timed )
       cf.insert.wait_function( self.determine_time_out ) 
       cf.insert.one_step(self.exit_timed_state )
       cf.insert.log("mv turn exit")
       cf.insert.terminate()
       
       cf.define_chain("MV_TIME_CYCLE_MONITOR",False) # make sure that there is no flow if master valve is off
       cf.insert.wait_event_count( event = "MINUTE_TICK" ) # 5 seconds
       cf.insert.verify_function_reset( reset_event=None,reset_event_data=None, 
                                        function = self.monitor_master_valve_open )
       cf.insert.one_step(self.turn_off_master_valves)
       cf.insert.send_event(event="RELEASE_IRRIGATION_CONTROL" )
       cf.insert.one_step( self.report_excessive_flow_timed ) #master valve has been detected to be off
       cf.insert.one_step(self.change_to_off_state)
       




   #
   #
   # Local Functions
   #
   #
   #
   
 
   def initial_setup(self,*parms):
      
       self.ref_time = time.time()
       self.change_to_off_state()    
   #
   # State Change functions
   #   
   def change_to_off_state(self,*parms):
      self.master_valve_close_count = 0
      self.turn_off_master_valves()
      self.cluster_ctrl.enable_cluster_reset_rt(self.cf, self.cluster_id,"MV_OFF" )
      
   def change_to_on_state(self,*parms):
       self.monitor_excessive_flow_count = 0
       self.turn_on_master_valves()
       self.cluster_ctrl.enable_cluster_reset_rt(self.cf, self.cluster_id,"MV_ON" )

   
   def change_to_offline_state(self,*parms):
      
      self.turn_off_master_valves()
      self.current_state = self.cluster_ctrl.get_current_state(self.cluster_id)
      self.cluster_ctrl.enable_cluster_reset_rt(self.cf, self.cluster_id,"MV_OFFLINE" )
   
   
   def offline_state_exit(self,*parms):
      if self.current_state == "MV_TIME_CYCLE_DEFERED":
         self.change_to_timed_state()
      else:
         self.cluster_ctrl.enable_cluster_reset_rt(self.cf, self.cluster_id,self.current_state )
   
   def change_to_timed_defered(self,*parms):
       self.current_state = "MV_TIME_CYCLE_DEFERED"
 
 
 
   def change_to_timed_state(self,*parms):
       self.turn_off_master_valves()
       self.ref_time = time.time() + 30 #3600*8 # 8 hour time in future
       self.cluster_ctrl.enable_cluster_reset_rt(self.cf, self.cluster_id,"MV_TIME_CYCLE" )
   
   def cancel_timed_state(self,*parms):
       if event["name"] == "INIT":
         return
       self.ref_time = time.time()
   
   def exit_timed_state(self,*parms):
 
       self.ref_time = time.time()
       if self.master_valve_state == True:
         self.cluster_ctrl.enable_cluster_reset_rt(self.cf, self.cluster_id,"MV_ON" )
       else:
         self.cluster_ctrl.enable_cluster_reset_rt(self.cf, self.cluster_id,"MV_OFF" )
 
   def set_timed_close_flag(self,*params):
       self.master_valve_state = False
 
   def turn_on_master_valves(self,*parms):
       self.master_valve_state = True
       self.irrigation_io.turn_on_master_valves_direct()

   def turn_off_master_valves(self,*parms):
       self.master_valve_state = True
       self.irrigation_io.turn_off_master_valves_direct() 
 
   def turn_off_master_valves(self,*parms):
       self.master_valve_state = False
       self.irrigation_io.turn_off_master_valves_direct()
       
   def turn_on_master_valves_timed(self,*parms):
       
       self.irrigation_io.turn_on_master_valves_direct()      
       
       
   #
   # 
   # Monitor Functions
   #
   # 
   def monitor_master_valve_open(self,cf_handle, chainObj, parameters, event):
 
       if event["name"] == "MINUTE_TICK":
         
           
           self.master_flow = self.handlers["MQTT_SENSOR_STATUS"].hget("MAIN_FLOW_METER")
                             
           if self.master_flow > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_VALUE"]:
             self.monitor_excessive_flow_count += 1
           else:
             self.monitor_excessive_flow_count = 0
          
           if self.monitor_excessive_flow_count > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_TIME"]:

              return True
       return False  
      
      
   def monitor_master_valve_close(self,cf_handle, chainObj, parameters, event):
       if event["name"] == "INIT":
          pass
          
       else:
         self.master_flow = self.handlers["MQTT_SENSOR_STATUS"].hget("MAIN_FLOW_METER")
         
         if self.master_flow > 1:
            
            self.master_valve_close_count +=1
            if self.master_valve_close_count > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_TIME"]:
                return True
         else:
             self.master_valve_close_count = 0
               
       return False


   #
   # timed cycle functions
   #
   #
   def determine_time_out(self,*parms):
      if time.time() > self.ref_time:
         return True
      else:
         return False
         
       


   #
   #
   # Report functions
   #
   #failure_type,state,details
   def report_master_valve_failure(self,*parms):
     self.failure_report(self.current_operation,"MASTER_VALVE","OFF",{"flow_rate":self.master_flow}   )
     
     raise ValueError("Excessive Idle Cleaning Valve Flow  "+str(self.master_flow))
    
   
   def report_excessive_flow(self,*parms):
     self.current_operation["flow_rate"] = self.master_flow
     
     self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"EXCESSIVE_FLOW","details":self.current_operation,"level":"RED"})
     self.failure_report(self.current_operation,"MASTER_VALVE","ON",{"flow_rate":self.master_flow}   )
 
   def report_excessive_flow_timed(self,*parms):
       self.current_operation["flow_rate"] = self.master_flow
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"EXCESSIVE_FLOW","details":self.current_operation,"level":"RED"})
       self.failure_report(self.current_operation,"MASTER_VALVE","TIMED_OPERATION",{"flow_rate":self.master_flow}   )   

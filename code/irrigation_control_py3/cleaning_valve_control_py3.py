class Cleaning_Valve(object):

   def __init__( self, cluster_id, cf,cluster_control, irrigation_io, handlers,current_operations,failure_report,irrigation_excessive_flow_limits):
       self.cf = cf
       self.current_operations = current_operations
       self.cluster_ctrl  = cluster_control
       self.irrigation_io = irrigation_io
       self.failure_report = failure_report
       self.irrigation_excessive_flow_limits = irrigation_excessive_flow_limits
       self.handlers  = handlers
       self.cluster_id    = cluster_id
       self.state_list    = ["CLEANING_ONLINE_MONITOR","CLEANING_OFFLINE_MONITOR","CLEANING_EV_HANDLER"]
       self.disable_chain = False
       self.deferred_enable = False
       self.construct_chains( cf)
       cluster_control.define_cluster( cluster_id, self.state_list ,"CLEANING_INIT" )
       cluster_control.define_state( cluster_id, "ONLINE", ["CLEANING_EV_HANDLER","CLEANING_ONLINE_MONITOR"])
       cluster_control.define_state( cluster_id, "OFFLINE", ["CLEANING_EV_HANDLER","CLEANING_OFFLINE_MONITOR"])
       self.irrigation_io.turn_off_cleaning_valves() 
       self.cluster_ctrl.enable_cluster_reset_rt(  self.cf,self.cluster_id, "ONLINE" )
       
    

   def init_startup(self,*parms):
       self.cluster_ctrl.enable_cluster_reset_rt(  self.cf,self.cluster_id, "ONLINE" )
   
   
   def construct_chains( self, cf ):
 
       cf.define_chain("CLEANING_INIT",True)
       cf.insert.one_step(self.init_startup )
       cf.insert.terminate()



       cf.define_chain("CLEANING_EV_HANDLER",True) 
       
       cf.insert.check_event_no_init("IRI_OPEN_CLEANING_VALVE", self.check_open )  # checking for open cleaning valve command
       cf.insert.check_event_no_init("IRI_CLOSE_CLEANING_VALVE", self.check_close ) # checking for close cleaning valve command
       cf.insert.check_event_no_init("IRI_CLEANING_VALVE_MONITOR_OFFLINE", self.change_to_offline_state)
       cf.insert.check_event_no_init("IRI_CLEANING_VALVE_MONITOR_ONLINE",self.change_to_online_state)       
       cf.insert.reset()

 



       cf.define_chain("CLEANING_ONLINE_MONITOR",False) # make sure that there is no flow if cleaning valve is off
      
       cf.insert.wait_event_count( event = "MINUTE_TICK" ) 
       cf.insert.wait_event_count(count = 10)  # wait 10 seconds to ensure MQTT update of sensor values
       cf.insert.verify_function_reset( reset_event=None,reset_event_data=None, 
                                        function = self.monitor_cleaning_valve_close )
       cf.insert.one_step(self.irrigation_io.turn_off_pump) # currently system doesnot have this capability
       cf.insert.send_event(event="RELEASE_IRRIGATION_CONTROL" )
       cf.insert.one_step( self.report_cleaning_valve_failure ) #cleaning valve has been detected to be off
       cf.insert.terminate()

       cf.define_chain("CLEANING_OFFLINE_MONITOR",False) # make sure that there is no flow if cleaning valve is off
       cf.insert.terminate() # Monitoring done by cleaning app



   def check_open( self, cf_handle, chainObj, parameters, event ):  #event handler for web open command
       if event["name"] == "INIT":
           return
       if self.cluster_ctrl.get_current_state(self.cluster_id) ==  "OFFLINE" :       
          self.irrigation_io.turn_on_cleaning_valves_direct()
  
       else:
          self.disable_all_sprinklers()
          raise ValueError("Cannot open cleaning valve in ONLINE STATE") #  online state is only during filter cleaning
          
   def check_close( self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
           return
       
       self.irrigation_io.turn_off_cleaning_valves_direct()
        
   def change_to_offline_state( self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
           return
       self.irrigation_io.turn_off_cleaning_valves()    
       self.cluster_ctrl.enable_cluster_reset_rt(  self.cf,self.cluster_id, "OFFLINE" )
       
   def change_to_online_state( self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
           return
       self.irrigation_io.turn_off_cleaning_valves()    
       self.cluster_ctrl.enable_cluster_reset_rt(  self.cf,self.cluster_id, "ONLINE" )


       
   def monitor_cleaning_valve_close(self,cf_handle, chainObj, parameters, event):
       if event["name"] == "INIT":
          pass
          
       else:
         self.master_flow = self.handlers["MQTT_SENSOR_STATUS"].hget("CLEANING_FLOW_METER")
         
         if self.master_flow > 0:
            
            self.master_valve_close_count +=1
            if self.master_valve_close_count > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_TIME"]:
                return True
         else:
             self.master_valve_close_count = 0
               
       return False
            
       
      
       
       

   
   def report_cleaning_valve_failure(self, chainObj, parameters, event):
       self.failure_report(self.current_operation,"CLEANING_VALVE",None,{"flow_rate":self.cleaning_flow}   )   
       
       raise ValueError("Excessive Idle Cleaning Valve Flow  "+self.cleaning_flow)
       
if __name__ == "__main__":
   pass

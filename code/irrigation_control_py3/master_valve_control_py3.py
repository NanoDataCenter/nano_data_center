
class Master_Valve(object):

   def __init__( self, cluster_id, cf,cluster_control, irrigation_io, handlers ):
       self.cf = cf
       self.cluster_ctrl  = cluster_control
       self.irrigation_io = irrigation_io
       
       self.handlers  = handlers
       self.cluster_id    = cluster_id
       self.state_list    = ["MV_time_cycle","MV_monitor_valve","MV_OFF"]
       self.disable_chain = False
       self.deferred_enable = False
       self.construct_chains( cf)
       cluster_control.define_cluster( cluster_id, self.state_list , "MV_monitor_chain" )
       cluster_control.define_state( cluster_id, "ON", ["MV_time_cycle","MV_monitor_valve"])
       cluster_control.define_state( cluster_id, "OFF", ["MV_OFF"])
       self.irrigation_io.turn_off_master_valves() 
       self.cluster_ctrl.enable_cluster_reset_rt(  self.cf,self.cluster_id, "OFF" )
    


   def construct_chains( self, cf ):
 

       cf.define_chain("MV_monitor_chain",True) # this thread is always active
       #cf.insert.log("MV_monitor chain is active")
       cf.insert.check_event("IRI_OPEN_MASTER_VALVE", self.check_open )  # checking for open master valve from web
       cf.insert.check_event("IRI_CLOSE_MASTER_VALVE", self.check_close ) # checking for close master valve from web
       cf.insert.check_event("IRI_MASTER_VALVE_SUSPEND", self.check_suspend) # master valve control needs to be suspended due to valve resistance check
       cf.insert.check_event("IRI_MASTER_VALVE_RESUME", self.check_resume ) # master valve control is resumed
       cf.insert.reset()

       cf.define_chain("MV_OFF",False)
       #cf.insert.log("MV_OFF IS Active") # master valve comanded of by web
       cf.insert.halt()


       cf.define_chain("MV_time_cycle",False) # thread becomes active if web commanded it to
       #cf.insert.log("chain MV_time_cycle is on")
       cf.insert.one_step( self.irrigation_io.turn_on_master_valves )
       cf.insert.wait_event_count(count = 3600*8 ) # wait 8 hour
       cf.insert.one_step(self.cluster_ctrl.disable_cluster, self.cluster_id )
       cf.insert.terminate()
       
       
       # purpose is to turn on the master valve if some thing turned it off
       cf.define_chain("MV_monitor_valve",False) # thread becomes active if web commanded it to
       #cf.insert.log("chain MV_monitor_valve is on")
       cf.insert.wait_event_count( count = 5 ) # 5 seconds
       cf.insert.verify_function_reset( reset_event=None,reset_event_data=None, 
                                        function = self.master_valve_off )
       cf.insert.one_step( self.irrigation_io.turn_on_master_valves ) #master valve has been detected to be off
       
       cf.insert.reset()

       self.suspend_chain = False
       self.deferred_enable = False

   def check_open( self, cf_handle, chainObj, parameters, event ):  #event handler for web open command
       if event["name"] == "INIT":
           return
      
       if self.suspend_chain == True:  # chain is not under control of master valve
          self.deferred_enable = True  # valve will be turned on when control is resumed
       else:
          

          self.cluster_ctrl.enable_cluster_reset_rt(  cf_handle, self.cluster_id, "ON" )  # set the state to ON

   def check_close( self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
           return
       
       if self.suspend_chain == False:
           self.irrigation_io.turn_off_master_valves()  # turn off valve if under control

       
       self.cluster_ctrl.enable_cluster_reset_rt(cf_handle, self.cluster_id,"OFF" )
       self.suspend_chain = False
       self.deferred_enable = False

   def  check_suspend( self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
           return

       
       if self.suspend_chain == True:
           pass # chain is already suspended
       else:

           self.cluster_ctrl.suspend_cluster_rt(cf_handle, self.cluster_id ) # suspend chain
           self.suspend_chain = True

   def check_resume( self, cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
           return

       if self.suspend_chain == True:
           self.suspend_chain = False
           if self.deferred_enable == False:

               self.cluster_ctrl.resume_cluster_rt(cf_handle, self.cluster_id ) # resume cluster 
                                                                                # if master valve was previously on
                                                                                #  chain "MV_monitor_valve" will turn valve on within 5 seconds
           else:
   
               self.cluster_ctrl.enable_cluster_reset_rt(cf_handle, self.cluster_id,"ON")

           self.deferred_enable = False

   def master_valve_off(self, cf_handle, chainObj, parameters, event):
       
       if self.irrigation_io.get_master_valve_setup() == 1: # if master valve is on return False
          return_value = False
       else:
          return_value = True
       
       return return_value

if __name__ == "__main__":
   pass

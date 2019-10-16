
import time
class Clean_Filter(object):

   def __init__( self,cf,cluster_control,irrigation_io, handlers,irrigation_hash_control,
                 Check_Excessive_Current,get_json_object, failure_report,current_operations,generate_control_events):
 
       self.get_json_object = get_json_object
       self.cf = cf
       self.cluster_control = cluster_control
       self.irrigation_io = irrigation_io
       self.handlers = handlers
       self.irrigation_hash_control = irrigation_hash_control
       self.Check_Excessive_Current = Check_Excessive_Current
       self.failure_report = failure_report
       self.current_operations = current_operations
       self.generate_control_events = generate_control_events
       
   
   def load_duration_counter(self,cf_handle, chainObj, parameters, event):
         
          self.irrigation_io.load_duration_counters(parameters[1])

 
   
   def construct_chains( self , cf ):
       
       cf.define_chain("clean_filter_action_chain", False)  #tested
       cf.insert.log( "Clean Step 1" )
       cf.insert.one_step(self.generate_control_events.change_master_valve_offline)
       cf.insert.one_step(self.generate_control_events.change_cleaning_valve_offline)
       cf.insert.wait_event_count(count = 2)
       cf.insert.one_step(  self.irrigation_io.disable_all_sprinklers  )
       cf.insert.one_step(  self.irrigation_io.turn_off_cleaning_valves  )# turn off cleaning valve
       cf.insert.wait_event_count(count = 2)
       cf.insert.one_step(  self.irrigation_io.turn_on_master_valves  )# turn turn on master valve
       cf.insert.one_step(  self.load_duration_counter,3)
       cf.insert.log( "Clean Step 2")
       cf.insert.wait_event_count(event = "MINUTE_TICK",count = 3)
       cf.insert.one_step(self.clear_cleaning_sum)
       cf.insert.enable_chains(["cleaning_flow_accumulated"])
       cf.insert.log( "Clean Step 3" )
       cf.insert.one_step( self.irrigation_io.turn_off_master_valves )# turn turn off master valve
       cf.insert.one_step(  self.irrigation_io.turn_on_cleaning_valves  )# turn on cleaning valve

       cf.insert.wait_event_count( count = 30 ) 
       ######
       
       cf.insert.log( "Clean Step 4" ) 
       cf.insert.one_step(  self.irrigation_io.turn_on_master_valves  )# turn turn on master valve
       cf.insert.wait_event_count( count = 10 )
       cf.insert.log( "Clean Step 5" )
       cf.insert.one_step(  self.irrigation_io.turn_off_cleaning_valves  )# turn turn off master valve
       cf.insert.one_step( self.irrigation_io.turn_off_master_valves  )# turn turn off cleaning valve
       cf.insert.one_step(  self.irrigation_io.disable_all_sprinklers )
       cf.insert.wait_event_count(event = "MINUTE_TICK",count = 1)
       cf.insert.wait_event_count(count = 15)
       cf.insert.disable_chains(["cleaning_flow_accumulated"])
       cf.insert.one_step( self.check_cleaning_sum  )
       cf.insert.one_step( self.log_clean_filter  )
       cf.insert.one_step(self.generate_control_events.change_master_valve_online)
       cf.insert.one_step(self.generate_control_events.change_cleaning_valve_online)
       cf.insert.wait_event_count(count = 2)
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.log( "clean filter is terminated is terminated" )

       cf.insert.terminate()
       
       cf.define_chain("cleaning_flow_accumulated",False)
       cf.insert.wait_event_count(count = 10)
       cf.insert.one_step(self.accumulate_cleaning_flow)
       cf.insert.wait_event_count(event = "MINUTE_TICK")
       cf.insert.reset()
       
       
       
       self.Check_Excessive_Current("clean_filter_excessive_current",cf,self.handlers,
                                     self.irrigation_io,self.irrigation_hash_control,self.get_json_object)
       return  ["clean_filter_action_chain","clean_filter_excessive_current","cleaning_flow_accumulated"]


   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id,["clean_filter_action_chain","cleaning_flow_accumulated","clean_filter_excessive_current"]  )

   def clear_cleaning_sum(self, *args):
       self.irrigation_hash_control.hset("CLEANING_ACCUMULATION",0)
       
       
       
   def check_cleaning_sum(self, cf_handle, chainObj, parameters, event ):
      pass  # put this in when program has control
      #self.handlers["MQTT_SENSOR_STATUS"].hget(self.mqtt_cleaning_name)
   
   def accumulate_cleaning_flow(self, cf_handle, chainObj, parameters, event ):
      pass  # put this in when program has control
      #self.handlers["MQTT_SENSOR_STATUS"].hget(self.mqtt_cleaning_name)   
   
   def log_clean_filter( self,*args):
        
     self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"clean filter","details":{},"level":"GREEN"})

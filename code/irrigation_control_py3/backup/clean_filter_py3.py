
import time
class Clean_Filter(object):

   def __init__( self,cf,cluster_control,irrigation_io, redis_handle, alarm_queue):

       self.cf = cf
       self.cluster_control = cluster_control
       self.irrigation_io = irrigation_io
       self.redis_handle = redis_handle
       self.alarm_queue = alarm_queue
       
   
   def load_duration_counter(self,cf_handle, chainObj, parameters, event):
          print(parameters,len(parameters))
          self.irrigation_io.load_duration_counters(parameters[1])

 
   
   def construct_chains( self , cf ):
       cf.define_chain("clean_filter_action_chain", False)  #tested
       cf.insert.log( "Clean Step 1" )
       cf.insert.send_event("IRI_MASTER_VALVE_SUSPEND",None)
       cf.insert.one_step(  self.irrigation_io.disable_all_sprinklers  )
       cf.insert.one_step(  self.irrigation_io.turn_off_cleaning_valves  )# turn off cleaning valve
       cf.insert.one_step(  self.irrigation_io.turn_on_main_valves  )# turn turn on main valve
       cf.insert.one_step(  self.load_duration_counter,3)
       cf.insert.log( "Clean Step 2")
       cf.insert.wait_event_count( count = 120 )
       cf.insert.log( "Clean Step 3" )
       cf.insert.one_step( self.irrigation_io.turn_off_main_valves )# turn turn off main valve
       cf.insert.one_step(  self.irrigation_io.turn_on_cleaning_valves  )# turn on cleaning valve

       cf.insert.wait_event_count( count = 30 ) 
       cf.insert.log( "Clean Step 4" ) 
       cf.insert.one_step(  self.irrigation_io.turn_on_main_valves  )# turn turn on main valve
       cf.insert.wait_event_count( count = 10 )
       cf.insert.log( "Clean Step 5" )
       cf.insert.one_step(  self.irrigation_io.turn_off_cleaning_valves  )# turn turn off main valve
       cf.insert.one_step( self.irrigation_io.turn_off_main_valves  )# turn turn off cleaning valve
       cf.insert.one_step(  self.irrigation_io.disable_all_sprinklers )
       cf.insert.one_step( self.clear_cleaning_sum  )
       cf.insert.one_step( self.log_clean_filter  )
       cf.insert.send_event("IRI_MASTER_VALVE_RESUME",None)
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.log( "clean filter is terminated is terminated" )

       cf.insert.terminate()

       return  ["clean_filter_action_chain"]


   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id,["clean_filter_action_chain"]  )

   def clear_cleaning_sum(self, *args):
       self.redis_handle.hset("CONTROL_VARIABLES","cleaning_sum",0)

   def log_clean_filter( self,*args):
        
        self.alarm_queue.store_past_action_queue("CLEAN_FILTER","GREEN"  )
        self.redis_handle.hset("CONTROLLER_STATUS","clean_filter",time.time() )

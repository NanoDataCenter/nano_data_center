
import time
class Clean_Filter(object):

   def __init__( self,cf,cluster_control,irrigation_io, handlers,irrigation_hash_control ):

       self.cf = cf
       self.cluster_control = cluster_control
       self.irrigation_io = irrigation_io
       self.handlers = handlers
       self.irrigation_hash_control = irrigation_hash_control
       
       
   
   def load_duration_counter(self,cf_handle, chainObj, parameters, event):
         
          self.irrigation_io.load_duration_counters(parameters[1])

 
   
   def construct_chains( self , cf ):
       cf.define_chain("clean_filter_action_chain", False)  #tested
       cf.insert.log( "Clean Step 1" )
       cf.insert.send_event("IRI_MASTER_VALVE_SUSPEND",None)
       cf.insert.one_step(  self.irrigation_io.disable_all_sprinklers  )
       cf.insert.one_step(  self.irrigation_io.turn_off_cleaning_valves  )# turn off cleaning valve
       cf.insert.one_step(  self.irrigation_io.turn_on_master_valves  )# turn turn on master valve
       cf.insert.one_step(  self.load_duration_counter,3)
       cf.insert.log( "Clean Step 2")
       cf.insert.wait_event_count( count = 120 )
       cf.insert.log( "Clean Step 3" )
       cf.insert.one_step( self.irrigation_io.turn_off_master_valves )# turn turn off master valve
       cf.insert.one_step(  self.irrigation_io.turn_on_cleaning_valves  )# turn on cleaning valve

       cf.insert.wait_event_count( count = 30 ) 
       cf.insert.log( "Clean Step 4" ) 
       cf.insert.one_step(  self.irrigation_io.turn_on_master_valves  )# turn turn on master valve
       cf.insert.wait_event_count( count = 10 )
       cf.insert.log( "Clean Step 5" )
       cf.insert.one_step(  self.irrigation_io.turn_off_cleaning_valves  )# turn turn off master valve
       cf.insert.one_step( self.irrigation_io.turn_off_master_valves  )# turn turn off cleaning valve
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
       self.irrigation_hash_control.hset("CLEANING_ACCUMULATION",0)

   def log_clean_filter( self,*args):
        
     self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"clean filter","details":{},"level":"GREEN"})

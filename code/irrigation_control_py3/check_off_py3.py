
class Check_Off(object):

   def __init__( self,cf,cluster_control,irrigation_hash_control,  io_control, handlers,Check_Cleaning_Valve,Check_Excessive_Current,get_json_object):
       self.cf = cf
       self.cluster_control = cluster_control
       self.io_control = io_control
       self.handlers = handlers
       self.Check_Cleaning_Valve = Check_Cleaning_Valve
       self.Check_Excessive_Current = Check_Excessive_Current
       self.irrigation_hash_control = irrigation_hash_control
       self.get_json_object = get_json_object

   def check_off (self, cf_handle, chainObj, parameters, event ):
        if event["name"] == "INIT":
           return

        temp = float(self.io_control.get_corrected_flow_rate())
        
        if temp   > 1.:
           

           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"check_off","details":{"flow_rate":temp },"level":"RED"})           
           return_value = "DISABLE"
        else:
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"check_off","details":{"flow_rate":temp },"level":"GREEN"})   
           return_value = "DISABLE"
        return return_value
 
   
   def construct_chains( self , cf ):
       cf.define_chain("check_off_chain", False ) #tested
       
       
       cf.insert.log( "check off is active" )
       cf.insert.send_event("IRI_MASTER_VALVE_SUSPEND",None) # taking over control of master valve
       
       cf.insert.one_step( self.io_control.disable_all_sprinklers  )
       cf.insert.one_step(  self.io_control.turn_off_master_valves  )# turn turn off master valve
       
       cf.insert.log( "wait to charge well tank" )
       cf.insert.wait_event_count(  count = 30 )
       
       cf.insert.log("turn on master valve and see if any leaks")
       cf.insert.one_step( self.io_control.turn_on_master_valves  )# turn turn on master valve
       cf.insert.one_step(  self.io_control.turn_off_cleaning_valves  )# turn turn off cleaning valve
       
       cf.insert.log( "wait 5 minutes to charge sprinkler lines" )
       cf.insert.wait_event_count( count = 300 ) 
       cf.insert.one_step(  self.check_off  ) # make check # in future include pressure gauge
       
       cf.insert.one_step(  self.io_control.turn_off_master_valves  )# turn turn off master valve
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.log( "check off is terminated" )
       cf.insert.send_event("IRI_MASTER_VALVE_RESUME",None) # return control of master valve
       cf.insert.terminate(  )
       
       self.Check_Cleaning_Valve("check_off_cleaning_valve",
                                 cf,
                                 self.handlers,
                                 self.io_control,
                                 self.irrigation_hash_control,
                                 self.get_json_object)
       self.Check_Excessive_Current("check_off_excessive_current",
                                    cf,
                                    self.handlers,
                                    self.io_control,
                                    self.irrigation_hash_control,
                                    self.get_json_object)
       
       return  ["check_off_chain","check_off_cleaning_valve","check_off_excessive_current"]


   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id,  state_id,["check_off_chain","check_off_cleaning_valve","check_off_excessive_current"]  )

 
if __name__ == "__main__":
   pass

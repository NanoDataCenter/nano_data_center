
class Check_Off(object):

   def __init__( self,cf,cluster_control,irrigation_hash_control,  io_control, handlers,
                Check_Excessive_Current,get_json_object,failure_report,current_operations):
       self.cf = cf
       self.cluster_control = cluster_control
       self.io_control = io_control
       self.handlers = handlers
       
       self.Check_Excessive_Current = Check_Excessive_Current
       self.irrigation_hash_control = irrigation_hash_control
       self.get_json_object = get_json_object
       self.failure_report     = failure_report
       self.current_operations = current_operations

   def check_off (self, cf_handle, chainObj, parameters, event ):
        if event["name"] == "INIT":
           return
        self.io_control.turn_off_master_valves()
        temp = float(self.handlers["MQTT_SENSOR_STATUS"].hget("MAIN_FLOW_METER"))
        
        if temp   > 1.:
           
           self.current_operation= {}
           self.current_operation["state"] = "CHECK_OFF"
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"check_off","details":{"flow_rate":temp },"level":"RED"}) 
           self.failure_report(self.current_operation,"CHECK_OFF",None,{"flow_rate":temp} )
           self.handlers["IRRIGATION_PAST_ACTIONS"].save()
           raise ValueError("CHECK OFF FAILURE OFF FLOW RATE: "+str(temp))
           
           return_value = "DISABLE"
        else:
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"check_off","details":{"flow_rate":temp },"level":"GREEN"})   
           return_value = "DISABLE"
        return return_value
 
   
   def construct_chains( self , cf ):
       cf.define_chain("check_off_chain", False ) #tested
       
       
       cf.insert.log( "check off is active" )
       
       
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
       
       
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.log( "check off is terminated" )
     
       cf.insert.terminate(  )
       

       self.Check_Excessive_Current("check_off_excessive_current",
                                    cf,
                                    self.handlers,
                                    self.io_control,
                                    self.irrigation_hash_control,
                                    self.get_json_object)
       
       return  ["check_off_chain","check_off_excessive_current"]


   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id,  state_id,["check_off_chain","check_off_excessive_current"]  )

 
if __name__ == "__main__":
   pass

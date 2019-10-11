


class Check_Cleaning_Valve(object):

   def __init__(self,chain_name,cf,handlers,irrigation_io,irrigation_hash_control,get_json_object):
       self.get_json_object = get_json_object
       cf.define_chain(chain_name, False )
       #cf.insert.log("check_cleaning_flow_meter")  
       cf.insert.verify_not_event_count_reset( event="RELEASE_IRRIGATION_CONTROL", count = 1, reset_event = None, reset_data = None ) 
        
       cf.insert.wait_event_count( count = 15 )      
       cf.insert.assert_function_reset(self.check_cleaning_valve)
       cf.insert.log("excessive_cleaning_flow_found")
       cf.insert.send_event("IRI_CLOSE_MASTER_VALVE",None)
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.one_step(irrigation_io.disable_all_sprinklers )
       cf.insert.wait_event_count( count = 1 )
       cf.insert.reset() 
       self.handlers = handlers
       self.irrigation_hash_control = irrigation_hash_control       
      
   def check_cleaning_valve(self,cf_handle, chainObj, parameters, event):
       if event["name"] == "INIT":  
         pass
       else:
            
            gpm = self.irrigation_hash_control.hget("CLEANING_FLOW_METER") # use 15 second interval to speed transistion
            #print("cleaning gpm",gpm)
            if gpm != 0:
              cf_handle.send_event("RELEASE_IRRIGATION_CONTROL",None) 
              json_object = self.get_json_object()
              details = "Schedule "+ json_object["schedule_name"] +" step "+str(json_object["step"] )+ \
                         "Flow:"+str(gpm)+" Excessive Cleaning Current"
              self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"Excessive Cleaning Valve Flow","details":details,"level":"RED"})
              return True
       return False       


class Check_Excessive_Current(object):

   def __init__(self,chain_name,cf,handlers,irrigation_io,irrigation_hash_control,get_json_object):
       self.get_json_object = get_json_object
       cf.define_chain(chain_name, False )
       #cf.insert.log("check_excessive_current")      
       cf.insert.assert_function_reset(self.check_excessive_current)
       cf.insert.log("excessive_current_found")
       cf.insert.send_event("IRI_CLOSE_MASTER_VALVE",False)
       cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
       cf.insert.one_step(irrigation_io.disable_all_sprinklers )
       cf.insert.wait_event_count( count = 15 )
       cf.insert.reset()
       self.handlers = handlers
       self.irrigation_hash_control = irrigation_hash_control

   def check_excessive_current(self,cf_handle, chainObj, parameters, event):
       print("check excessive current")
       return False #TBD
      

             
       

class Check_Excessive_Flow(object):

   def __init__(self,chain_name,cf,handlers,irrigation_io,irrigation_hash_control,get_json_object):
      self.get_json_object = get_json_object
      cf.define_chain(chain_name, False )
      #cf.insert.log("check_excessive_flow")
      cf.insert.verify_not_event_count_reset( event="RELEASE_IRRIGATION_CONTROL", count = 1, reset_event = None, reset_data = None )
      cf.insert.wait_function(self.monitor_excessive_flow)
      cf.insert.log("excessive_flow_found")
      cf.insert.send_event("IRI_CLOSE_MASTER_VALVE",None)
      cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
      cf.insert.one_step(irrigation_io.disable_all_sprinklers )
      cf.insert.wait_event_count( count = 1 )
      cf.insert.reset()
      self.handlers = handlers
      self.irrigation_hash_control = irrigation_hash_control          
      
   def monitor_excessive_flow(self,cf_handle, chainObj, parameters, event):
       if event["name"] == "INIT":
         
          self.monitor_excessive_flow_count = 0
       if event["name"] == "MINUTE_TICK":
         
           
           gpm = self.handlers["MQTT_SENSOR_STATUS"].hget(self.mqtt_flow_name)
                     
           if gpm > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_VALUE"]:
             self.monitor_excessive_flow_count += 1
           else:
             self.monitor_excessive_flow_count = 0
          
           if self.monitor_excessive_flow_count > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_TIME"]:
              json_object = self.get_json_object()
              cf_handle.send_event("RELEASE_IRRIGATION_CONTROL",None) 
              details = "Schedule "+ json_object["schedule_name"] +" step "+str(json_object["step"] )+ \
                         "Flow:"+str(gpm)+" Excessive Irrigation Current"

              self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"Excessive Flow","details":details,"level":"RED"})
              return True
       return False      
       
class Check_Excessive_Flow_Idle(object):

   def __init__(self,cf,handlers,irrigation_io,irrigation_hash_control,get_json_object):
      self.get_json_object = get_json_object
      cf.define_chain("check_excessive_flow_idle", False )
      #cf.insert.log("check_excessive_flow")
      cf.insert.verify_not_event_count_reset( event="RELEASE_IRRIGATION_CONTROL", count = 1, reset_event = None, reset_data = None )
      cf.insert.wait_function(self.monitor_excessive_flow)
      cf.insert.log("excessive_flow_found")
      cf.insert.send_event("IRI_CLOSE_MASTER_VALVE",None)
      cf.insert.send_event( "RELEASE_IRRIGATION_CONTROL")
      cf.insert.one_step(irrigation_io.disable_all_sprinklers )
      cf.insert.wait_event_count( count = 1 )
      cf.insert.reset()
      self.handlers = handlers
      self.irrigation_hash_control = irrigation_hash_control          
      
   def monitor_excessive_flow(self,cf_handle, chainObj, parameters, event):
       if event["name"] == "INIT":
         
          self.monitor_excessive_flow_count = 0
       if event["name"] == "MINUTE_TICK":
         
           
           gpm = self.handlers["MQTT_SENSOR_STATUS"].hget(self.mqtt_flow_name)
                     
           if gpm > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_VALUE"]:
             self.monitor_excessive_flow_count += 1
           else:
             self.monitor_excessive_flow_count = 0
          
           if self.monitor_excessive_flow_count > self.irrigation_excessive_flow_limits["EXCESSIVE_FLOW_TIME"]:
              json_object = self.get_json_object()
              cf_handle.send_event("RELEASE_IRRIGATION_CONTROL",None) 
              details = "Schedule "+ json_object["schedule_name"] +" step "+str(json_object["step"] )+ \
                         "Flow:"+str(gpm)+" Excessive Irrigation Current"

              self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"Excessive Flow","details":details,"level":"RED"})
              return True
       return False      
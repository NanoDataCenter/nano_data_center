




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
       #print("check excessive current")
       return False #TBD
      

             
       

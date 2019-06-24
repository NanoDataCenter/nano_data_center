


class SprinklerQueueControl():
   def __init__(self,alarm_queue,redis):
       self.alarm_queue = alarm_queue
       self.redis       = redis

   #
   # This function takes data from the IRRIGATION QUEUE And Transferrs it to the IRRIGATION_CELL_QUEUE
   # IRRIGATION_CELL_QUEUE only has one element in it
   #
   def load_irrigation_cell(self,chainFlowHandle, chainObj, parameters,event ): 
       if length > 0:
           return "RESET" 

       length = self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE")
       if length == 0:
           return "RESET"
       if self.redis.hget("CONTROL_VARIABLES","SUSPEND") == "ON":
           return "RESET"

 

       compact_data = self.redis.rpop(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       json_string = base64.b64decode(compact_data)
       json_object = json.loads(json_string)

      
       
       if json_object["type"] == "RESISTANCE_CHECK":
           chainFlowHandle.enable_chain_base( ["resistance_check"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"
       
       
       if json_object["type"] == "CHECK_OFF":
           chainFlowHandle.enable_chain_base( ["check_off_chain"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"

       if json_object["type"] == "CLEAN_FILTER":
           chainFlowHandle.enable_chain_base( ["clean_filter_action_chain"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"
 
       if json_object["type"] == "IRRIGATION_STEP":
           #print "irrigation step"
           self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", compact_data )
       '''    
       if json_object["type"] == "START_SCHEDULE" :
           self.redis.set( "schedule_step_number", json_object["step_number"] ) 
           self.store_event_queue( "irrigation_schedule_start", json_object )
  
       if json_object["type"] == "END_SCHEDULE" :
           self.store_event_queue( "irrigation_schedule_stop", json_object )
       '''
       #print "load irrigation cell   CONTINUE"
       return "DISABLE"




if __name__ == "__main__":

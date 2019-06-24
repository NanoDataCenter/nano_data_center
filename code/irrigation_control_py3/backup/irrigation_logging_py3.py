import time
import base64
import json

from .logging_object_py3 import Logging_Object




class Irrigation_Logging(object):

   def __init__( self, redis_handle, redis_new_handle,gm,alarm_queue ):
       self.redis_handle     = redis_handle
       self.redis_new_handle = redis_new_handle
       self.alarm_queue      = alarm_queue
       if isinstance( gm, str ):  # put in for testing
          self.unified_key = gm  #test path
       else:
          # production path
          unified_data_object = gm.match_terminal_relationship("MINUTE_ACQUISITION")[0]
          self.unified_key = unified_data_object["measurement"]
       self.log_obj     = Logging_Object()


   def start( self, sprinkler_object):
       self.json_object   = sprinkler_object.json_object
       schedule_name = self.json_object["schedule_name"] 
       step =          self.json_object["step"]
        
       if "logging" not in self.json_object:
           self.json_object["logging"] = {}
       self.log = self.json_object["logging"]
       if "current_log" not in self.log:
           self.log["current_log"] =  self.log_obj.initialize_object( "current_log",schedule_name,step)
       if "flow_log" not in self.log:
           self.log["flow_log"] =  self.log_obj.initialize_object( "flow_log",schedule_name,step ) 
       if "unified_log_object" not in self.log:
           self.log["unified_log"] =  self.log_obj.initialize_object( "unified_log",schedule_name,step ) 

   def update( self,sprinkler_object ):
       coil_current = float( self.redis_handle.hget( "CONTROL_VARIABLES","coil_current" ))
       self.log_coil_current ( coil_current )
       flow_value = self.redis_handle.lindex("QUEUES:SPRINKLER:FLOW:"+"main_sensor",0)
       self.log_flow_rate("main_sensor", flow_value )
      
       unified_string = self.redis_new_handle.lindex( self.unified_key,0 )
       unified_object = json.loads(unified_string)
       self.log_unified_object(unified_object)  
    


   def post( self, sprinkler_object):
       if (hasattr( self, 'log') == True) and (self.alarm_queue.alarm_state == False ):
         
           obj = self.log["flow_log"]       
           self.alarm_queue.store_past_action_queue("IRRIGATION:END","GREEN", { "schedule_name":obj["schedule_name"],"step_name":obj["step"] } )
           self.store_object( self.log["current_log"],   "coil"    )
           self.store_object( self.log["flow_log"],      "flow"    )
           self.store_object( self.log["unified_log"],   "unified"    )
           obj                        = {}
           obj["coil"]                = self.log["current_log"]
           obj["flow"]                = self.log["flow_log"]
           obj["unified"]             = self.log["unified_log"]
           # pass data to cloud server
      
       self.current_log_object    = None
       self.flow_log_object       = None
       self.unified_log_object    = None

   #
   # Internal Functions
   #
   #

    

           
      

   def log_flow_rate( self, sensor_name, flow_value ):
       if sensor_name not in self.log["flow_log"]:
           self.log_obj.initialize_field( self.log["flow_log"], sensor_name)
       self.log_obj.log_element( self.log["flow_log"],sensor_name, flow_value)

   def log_coil_current ( self,coil_current ):
       if "coil_current" not in self.log["current_log"]:
           self.log_obj.initialize_field( self.log["current_log"], "coil_current")
       self.log_obj.log_element( self.log["current_log"],"coil_current", coil_current)

   def log_unified_object( self, unified_object ):
       for i,item in unified_object.items():

           if (i != "namespace") and (i !="time_stamp"):
               if i not in self.log["unified_log"]:
                   self.log_obj.initialize_field( self.log["unified_log"], i)
               self.log_obj.log_element( self.log["unified_log"], i, item )

     



      

   def log_step_stop( self ):

       temp = self.log["flow_log"]
       
       self.alarm_queue.store_past_action_queue("IRRIGATION:END","GREEN", 
                    { "schedule_name":temp["schedule_name"],"step_name":temp["step"] } )
       self.store_object( self.log["current_log"],   "coil"    )
       self.store_object( self.log["flow_log"],      "flow"    )
       self.store_object( self.log["unified_log"],   "unified" )
       obj                        = {}
       obj["coil"]                = self.log["current_log"]
       obj["flow"]                = self.log["flow_log"]
       obj["unified"]             = self.log["unified"]
       
       self.log = None # reclaim object

   def store_object( self, obj ,queue_type ):
       if obj == None:
           return
       
       self.log_obj.compute_object_statistics( obj )
       queue = "log_data:"+queue_type+":"+obj["schedule_name"]+":"+str(obj["step"])
       json_string = json.dumps(obj)
       compact_data = base64.b64encode(json_string.encode())
       self.redis_handle.lpush( queue, json_string )
       self.redis_handle.ltrim( queue,0,100)

 
if __name__ == "__main__":
   from .alarm_queue_py3 import AlarmQueue
   import redis
   redis_new_handle  = redis.StrictRedis( host = "localhost", port=6379, db = 12 , decode_responses=True)
   
   redis_old_handle  = redis.StrictRedis( host = "localhost", port=6379, db = 0 , decode_responses=True)
 
   alarm_queue = AlarmQueue(redis_old_handle)
   ir = Irrigation_Logging(redis_old_handle,redis_new_handle,
                        "MINUTE_ACQUISITION",alarm_queue)

   #
   # kind of a hack 
   # need a class object for testing
   ir.json_object = {}       
   ir.json_object["schedule_name"] = "xxxx" 
   ir.json_object["step"]          = 1

   
   ir.start( ir)
   for i in range(0,50):
       ir.update( ir )
   ir.post( ir)
     

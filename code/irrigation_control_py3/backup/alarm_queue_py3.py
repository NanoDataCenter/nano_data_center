
import redis
import json
import base64
import time

class AlarmQueue(object):
    def __init__(self,redis_handle, time_history_queue = "QUEUES:IRRIGATION:TIME_HISTORY", 
                       event_hash = "QUEUES:IRRIGAITION:EVENTS", history = 120,
                       bypass_queue = "QUEUES:IRRIGATION:BYPASS_EVENTS"):
   
       self.redis_handle = redis_handle
       self.time_history_queue = time_history_queue 
       self.event_hash = event_hash
       self.history = history
       self.bypass_queue = bypass_queue
       

    def store_by_pass_event( self, event, bypass_queue ):
        self.redis_handle.hset(self.bypass_queue,event,bypass_queue)
        
    def get_by_pass_events( self):
        return self.redis_handle.hgetall(self.bypass_queue)
 
 
 
    def jsonize_data( self, event,status,data = None ):
       log_data = {}
       log_data["event"]   = event
       log_data["data"]     = data
       log_data["time" ]    = time.time()
       log_data["status"]   = status
       return  json.dumps(log_data)

 
    def store_past_action_queue_direct( self, event, status ,data = None):
       json_data            = self.jsonize_data(event,status,data)

       self.redis_handle.lpush( self.time_history_queue , json_data)
       self.redis_handle.ltrim( self.time_history_queue ,0, self.history )
       self.redis_handle.hset(self.event_hash,event, time.time() )
      

    def store_past_action_queue( self, event, status ,data = None):
       self.redis_handle.hset(self.event_hash,event,time.time())
       if self.redis_handle.hexists(self.bypass_queue, event ) == True:
           json_data            = self.jsonize_data(event,status,data)
           queue = self.redis_handle.hget(self.bypass_queue,event) 
           self.redis_handle.publish(queue,json_data)
       else:

         self.store_past_action_queue_direct(event,status,data)
           
       


    def store_alarm_queue( self, event,status, data =None):
        self.store_past_action_queue( self, event, status ,data)
   
   
    def get_time_data( self ):
       temp_data = self.redis_handle.lrange(self.time_history_queue,0,-1)
       return_data = []
       for i in temp_data:
          
          return_data.append(json.loads(i))     
       return return_data
       
       
    def get_events( self ):
       return self.redis_handle.hgetall(self.event_hash)
       
       
    def store_event_queue( self, event, data=None ):
       self.store_past_action_queue(  event, status="GREEN" ,data=data )
  
    def update_time_stamp( self,*args ):
         self.redis_handle.hset( "CONTROL_VARIABLES", "sprinkler_time_stamp", time.time() )
         
       

if __name__ == "__main__":
   import redis
   redis_handle                        = redis.StrictRedis( host = "192.168.1.84", port=6379, db = 0 , decode_responses=True)
   
  
   alarm_queue = AlarmQueue(redis_handle)
   '''
   redis_handle.publish("__test__", 4)
   pubsub = redis_handle.pubsub()
   pubsub.subscribe(["__test__"])
   for item in pubsub.listen():
       time.sleep(2)
       print("iterm",item)

   iterm {'pattern': None, 'channel': '__test__', 'type': 'subscribe', 'data': 1}  # initial message
   iterm {'pattern': None, 'channel': '__test__', 'type': 'message', 'data': '55'}
   '''
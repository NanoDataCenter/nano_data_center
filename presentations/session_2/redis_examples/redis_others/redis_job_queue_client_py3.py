import redis
import json
import time


redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,0,decode_responses = True )


while True:

   data = {"a":1,"b":2 }
   data_json = json.dumps(data)
   redis_handle.lpush("work_queue",data_json)
   redis_handle.ltrim("work_queue",0, 100)
   print("pushing data")
   time.sleep(2)

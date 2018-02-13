import redis
import json
import time
from  redis_utilities.redis_rpc_client_py3 import Redis_Rpc_Client

redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,0,decode_responses = True )

data = "message from pub"
while True:
   redis_handle.publish("redis_pub",data)
   time.sleep(5)
  
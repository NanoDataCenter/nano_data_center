import redis
import json
import time
from  redis_utilities.redis_rpc_client_py3 import Redis_Rpc_Client

redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,0,decode_responses = True )
rpc_client = Redis_Rpc_Client(redis_handle,"rpc_queue")


parameters = { "a":1, "b":2 }
while True:
  print( rpc_client.send_rpc_message( "echo",parameters,timeout=1 ))
  print( rpc_client.send_rpc_message("double",parameters,timeout=1))
  time.sleep(5) 
  

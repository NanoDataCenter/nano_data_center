import redis
import json
import time
from  redis_utilities.redis_rpc_server_py3 import Redis_Rpc_Server



redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,0,decode_responses = True )


ref_time = time.time()
accumulated_time = 0


def idle_time():
   pass
   #print("time_out_function")
       
def echo_handler(  parameters ):
   idle_time()
   
   return parameters
   
def double_handler( parameters ):
   print("double")
   return_value = {}
   for key,data in parameters.items():
      return_value[key] = data*2
   return return_value


rpc_server = Redis_Rpc_Server(redis_handle,"rpc_queue",timeout_function=idle_time,timeout_value = 1)
rpc_server.register_call_back( "echo",echo_handler )
rpc_server.register_call_back( "double",double_handler )
rpc_server.start()
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
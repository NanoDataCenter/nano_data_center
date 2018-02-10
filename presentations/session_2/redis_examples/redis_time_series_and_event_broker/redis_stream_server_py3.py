#
#
#
#  This python scrip implements a stream log capped 10
#
#
import redis
import json
import time
from  redis_utilities.redis_stream_utilities_py3 import Redis_Stream_Client

#
#
# Step #1
# open connection to redis server
# Important things
# handle  is only good for one redis data base
# decode_responses=True prevents binary string conflicts in python3
#
redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =0, decode_responses=True)
print(redis_handle)
redis_stream = Redis_Stream_Client(redis_handle)



while True:
  data = {}
  
  data["seconds"]  =  int(time.time()) % 60
  key = "stream_1"
  redis_stream.xadd(key,10,"*",data )
  time.sleep(1)
  
  
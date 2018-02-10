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
  current_time = time.time()
  current_time = int(current_time*1000)
  print("\n\n\n\n")
  print(redis_stream.xrange("stream_1", str(current_time-5000), str(current_time) , count=10))
  print("\n\n\n\n")
  print(redis_stream.xrevrange("stream_1", str(current_time), str(current_time-5000),  count=10))

  time.sleep(10)
  
  
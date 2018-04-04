#
#
#
#  This python scrip implements a log generator
#
#
import redis
import json
import time


#
#
# Step #1
# open connection to redis server
# Important things
# handle  is only good for one redis data base
# decode_responses=True prevents binary string conflicts in python3
#
redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =20, decode_responses=True)
print(redis_handle)
queue_key ="key_queue"
fetch_depth = 10




while True:
  data_json  = redis_handle.lrange(queue_key,0,fetch_depth)
  data = []
  for i in data_json:
     temp = json.loads(i)
     data.append(temp)
  #display data
  print("\n\n\n")
  print("data for time period ",time.time())
  print("\n\n")
  for i in data:
     print(i)
  time.sleep(10)
  
  
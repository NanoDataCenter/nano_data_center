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
redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =0, decode_responses=True)
print(redis_handle)
queue_key ="key_queue"
queue_depth = 100

# note log takes three lines
def queue_data( key, depth, data ):
  json_data = json.dumps(data)
  redis_handle.lpush(key,json_data)
  redis_handle.ltrim(key,0,depth)


while True:
  data = {}
  data["time_stamp"] = time.time()
  data["seconds"]  =  data["time_stamp"] % 60
  queue_data(queue_key,queue_depth, data)
  time.sleep(1)
  print("queue_depth",redis_handle.llen(queue_key))
  
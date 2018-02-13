import redis
import json
import time


redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,0,decode_responses = True )


while True:

  data_json = redis_handle.brpop("work_queue")  #  could pass a list of work queues [x,y,z]
  print(data_json)
  data = json.loads(data_json[1])
  #process data
  print(data)
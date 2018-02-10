import redis
import json
import time


redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,0,decode_responses = True )

subscribe_object = redis_handle.pubsub()
subscribe_object.subscribe("redis_pub")
#
# Can add many keys or channels
#

while True:
    for item in subscribe_object.listen(): ## iterate over the channes
       print( item )
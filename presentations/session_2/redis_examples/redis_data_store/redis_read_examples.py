#
#
#  This python script demonstrates read-write examples
#  using redis
#
#
import redis
import json

#
#
# Step #1
# open connection to redis server
# Important things
# handle  is only good for one redis data base
# decode_responses=True prevents binary string conflicts in python3
#
redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =20, decode_responses=True)
#print(redis_handle)

print("purpose of this test is to show that another process can read data from another process")

print("reading key_1")
print(redis_handle.get("key_1"))
print("reading key_2")
print(redis_handle.lrange("key_2",0,-1))

print("reading key_3")
print(redis_handle.hgetall("key_3"))

#
#
#  This python script demonstrates set examples
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
print(redis_handle)
redis_handle.delete("key_set_1")
redis_handle.delete("key_set_2")
redis_handle.delete("key_set_3")
redis_handle.delete("key_set_4")

#
#
# Normal Set operations
#
#
#
#

#create two sets
redis_handle.sadd("key_set_1","a","b","c","d","e") 
redis_handle.sadd("key_set_2","c","d","e","f","g")
print("number and members of key_set_1 ", redis_handle.scard("key_set_1"),redis_handle.smembers("key_set_1"))
print("number and members of key_set_2 ", redis_handle.scard("key_set_2"),redis_handle.smembers("key_set_2"))
redis_handle.sunionstore("key_set_3","key_set_1","key_set_2")
print("union of two sets", redis_handle.smembers("key_set_3"))
redis_handle.sinterstore("key_set_3","key_set_1","key_set_2")
print("intersection of two sets", redis_handle.smembers("key_set_3"))
print("subtraction of key_set_2 from key_set_1", redis_handle.sdiff("key_set_1","key_set_2"))
#
#
# Sorted Set Operation
# Sorted Sets were added at the request of online gaming servers
# Sorted sets are sets where each member has a score
#
#
#
print("\n\n")
print("sorted sets")
print("\n\n\n")
members = {"a":2.0,"b":3.0,"c":4.0,"d":5.0,"e":6.0}  
redis_handle.delete("key_set_1","key_set_2","key_set_3")
redis_handle.zadd("key_set_1",**members) 
redis_handle.zadd("key_set_2",c=4,d=5,e=6,f=7,g=8)
print("number and members of key_set_1 in assending order", redis_handle.zcard("key_set_1"),redis_handle.zrange("key_set_1",0,2,desc=False))
print("number and members of key_set_1 in decending order", redis_handle.zcard("key_set_1"),redis_handle.zrange("key_set_1",0,2,desc=True))
print("number and members of key_set_2 in assending order", redis_handle.zcard("key_set_1"),redis_handle.zrange("key_set_2",0,2,desc=False))
print("number and members of key_set_2 in decending order", redis_handle.zcard("key_set_1"),redis_handle.zrange("key_set_2",0,2,desc=True))
print("changing score of key_set_1 'e' element by -10")
redis_handle.zincrby("key_set_1","e",-10)
print("number and members of key_set_1 in assending order", redis_handle.zcard("key_set_1"),redis_handle.zrange("key_set_1",0,2,desc=False))
print("changing score of key_set_1 'a' element by 10")
redis_handle.zincrby("key_set_1","a",10)
print("number and members of key_set_1 in decending order", redis_handle.zcard("key_set_1"),redis_handle.zrange("key_set_1",0,2,desc=True))

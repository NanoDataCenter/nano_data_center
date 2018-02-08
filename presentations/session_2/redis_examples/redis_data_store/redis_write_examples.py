#
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
redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =0, decode_responses=True)
print(redis_handle)
redis_handle.delete("key_1")
redis_handle.delete("key_2")
redis_handle.delete("key_3")

#
#  Simple Store
#
#
a = "Simple_Store"
redis_handle.set("key_1", a )
b = redis_handle.get("key_1")
print("wrote ",a,"  read ",b)

a=1
redis_handle.set("key_1", a )
b = redis_handle.get("key_1")
print("wrote ",a,"  read ",b)
print(type(a),type(b))
print("notice redis converts values to string internall")

#
# Lists
# use left side push to populate list
#
for i in range(0,10):
   redis_handle.lpush("key_2",i)

print("fetching all values of the list")   
print(redis_handle.lrange("key_2",0,-1))

#
#
# use right side pop to extract list
#
#
print("right poping items off the list")
for i in range(0,redis_handle.llen("key_2")):
   print(redis_handle.rpop("key_2"))
   
#
#
# repopulate the list for further use
#
#
#
# Lists
# use left side push to populate list
#
for i in range(0,10):
   redis_handle.lpush("key_2",i)
  
#
#  to delete an item in a list is a two step process
#
#  Step #1 put a special value in list element
redis_handle.lset("key_2",5,"__DELETE__")
redis_handle.lrem("key_2",0,"__DELETE__")
print("verify 5 element, which has value of 4,  has been removed from list")
print(redis_handle.lrange("key_2",0,-1))
print("\n\n\n")
#
#
#  Hash keys
#
#
#
redis_handle.hset("key_3","field_1",1)
redis_handle.hset("key_3","field_2",2)
redis_handle.hset("key_3","field_3",3)
print("number of keys",redis_handle.hlen("key_3"),"  keys  ",redis_handle.hkeys("key_3"))
print("field_1 status ",redis_handle.hexists("key_3","field_1")," field_4 status ", redis_handle.hexists("key_3","field_4"))
print("deleting field_3")
redis_handle.hdel("key_3","field_3")
print("verify field_3 hash is gone")
print("number of keys",redis_handle.hlen("key_3"),"  keys  ",redis_handle.hkeys("key_3"))
#
# Redis only stores a simple hash.  It does not store a dictionary within a dictionary
# json can be used to store a nested structure
#
#
#
print("nested structure test")
a = {"a":[0,1,2,3,4],"b":"test"}
a_json = json.dumps(a)

redis_handle.hset("key_3","field_3",a_json)
b_json = redis_handle.hget("key_3","field_3")

b = json.loads(b_json)
print("comparison a and b",a,b)



print("\n\n\n\n")
print("keys in redis data base")
print(redis_handle.keys())


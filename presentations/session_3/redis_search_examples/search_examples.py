 
import redis
import json
from redis_utitilites.search_extensions_py3 import Search_Extensions, Text_Field, Numeric_Field 
redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =21, decode_responses=True)
redis_handle.flushdb()
search = Search_Extensions(redis_handle)
   
t_field = Text_Field()
t_field.add(["name","company"])
n_field = Numeric_Field()
n_field.add("age")
print( search.create("test",text_fields = t_field, numeric_fields= n_field) )
 
   
   
dict_values = {"name":"joe","company":"xerox","age":40}
print( search.add("test","doc_id", dict_values ))
   
   
redis_handle.hset("hash_1","name","frank")
redis_handle.hset("hash_1","company","google")
redis_handle.hset("hash_1","age",25)
print(search.add_hash( "test", "hash_1" ))
   

print(search.get("test","doc_id"))
print(search.get("test","hash_1"))
print(search.get("test","hash_2")) # should return none
print("starting search")
  
print(search.text_search("test","google"))
print(search.text_search("test","joe"))

print("doing filter test")
 

print(search.text_search("test","@name:joe")) 
print(search.text_search("test","@age:[0,100] "))
print(search.text_search("test","@age:[30,100] "))
print(search.delete("test","doc_id"))
print(search.text_search("test","@age:[0,100] "))
 
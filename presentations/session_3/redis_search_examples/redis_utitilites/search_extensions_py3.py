import redis
import json
import time





class Search_Extensions( object ):

   def __init__(self,redis_handle):
       self.redis_handle = redis_handle
      
   def create(self,index, field_types):
       fields = []
       fields.append("FT.CREATE")
       fields.append(index)
       fields.append("SCHEMA")
       
       for i in field_types:
           
           fields.append(i[0])
           fields.append(i[1] )
       command_string = " ".join(fields)
       
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       return results
       
   def drop( self, index): 
       results = self.redis_handle.execute_command("FT.DROP "+index)
       return results       

       
   def add(self, index,doc_id,field_values,payload=None, replace = False , score = 1) :
       fields = []
       fields.append("FT.ADD")
       fields.append(str(index))
       fields.append(str(doc_id))
       fields.append(str(score))
       if replace == True:
           fields.append("REPLACE")
       if payload!=None:
           payload = json.dumps(payload )
           fields.append("PAYLOAD")
           fields.append(payload)
       
       fields.append("FIELDS")
       for key,data in field_values.items():
           
           fields.append(str(key))
           fields.append(str(data) )
           
       command_string = " ".join(fields)
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       return results
  
   
   def add_hash(self, index, hash_key, replace = False,score = 1):
       fields = []
       fields.append("FT.ADDHASH")
       fields.append(index)
       fields.append(hash_key)
       fields.append(str(score))
       if replace == True:
         fields.append("REPLACE")
 
       command_string = " ".join(fields)
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       return results
        
   

   def delete( self, index, doc_id ):
       fields = []
       fields.append("FT.DEL")
       fields.append(str(index))
       fields.append(str(doc_id))
  
       command_string = " ".join(fields)
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       return results
    
   
   def get( self, index,doc_id):
       fields = []
       fields.append("FT.GET")
       fields.append(str(index))
       fields.append(str(doc_id))
  
       command_string = " ".join(fields)
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       
       return_value = {}
       for i in range(0,len(results),2):
          
          key = results[i]
          return_value[key] = results[i+1]
       return return_value

   # not sure what this does
   def tagvals( self, index, field_name ):
     return self.redis_handle.execute_command("FT.TAGVALS "+str(index)+" "+str(field_name))
     
   def text_search( self, index, text_query, FILTER_FLAG = None, FILTER_MIN=None, FILTER_MAX = None):
       fields = []
       fields.append("FT.SEARCH")
       fields.append(str(index))
       fields.append(str(text_query))
       if FILTER_FLAG == True:
          fields.append("FILTER")
          fields.append(str(FILTER_MIN))
          fields.append(str(FILTER_MAX))
  
       command_string = " ".join(fields)
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       return results
          




   

 
if __name__ == "__main__":
   print("made it here")
   redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =21, decode_responses=True)
   redis_handle.flushdb()
   search = Search_Extensions(redis_handle)
   print( search.create("test",[["field_1","TEXT"],["field_2","NUMERIC"]]) ) 
   dict_values = {"field_1":"alphabet","field_2":40}
   print( search.add("test","doc_id", dict_values ))
   redis_handle.hset("hash_1","field_1","ford")
   redis_handle.hset("hash_1","field_2",19)
   redis_handle.hset("hash_1","field_3",19)
   print(search.add_hash( "test", "hash_1" ))
   
   redis_handle.hset("hash_2","field_1","ford")
   redis_handle.hset("hash_2","field_2",19)
   redis_handle.hset("hash_2","field_3",19)
   print(search.add_hash( "test", "hash_2" ))
  
   print(search.get("test","doc_id"))
   print(search.get("test","hash_2"))
   print(search.get("test","hash_1"))
   #print(search.delete("test", "hash_1" ))
   print(search.get("test","hash_1"))
   print(search.text_search("test","ford"))
   print(search.text_search("test",19))
   
   
   print( search.drop("test"))   
   
   
'''
from http://redisearch.io/Commands/   




FT.ADD {index} {docId} {score} 
  [NOSAVE]
  [REPLACE [PARTIAL]]
  [LANGUAGE {language}] 
  [PAYLOAD {payload}]
  FIELDS {field} {value} [{field} {value}...]

FT.ADDHASH {index} {docId} {score} [LANGUAGE language] [REPLACE]


FT.SEARCH {index} {query} [NOCONTENT] [VERBATIM] [NOSTOPWORDS] [WITHSCORES] [WITHPAYLOADS] [WITHSORTKEYS]
  [FILTER {numeric_field} {min} {max}] ...
  [GEOFILTER {geo_field} {lon} {lat} {raius} m|km|mi|ft]
  [INKEYS {num} {key} ... ]
  [INFIELDS {num} {field} ... ]
  [RETURN {num} {field} ... ]
  [SUMMARIZE [FIELDS {num} {field} ... ] [FRAGS {num}] [LEN {fragsize}] [SEPARATOR {separator}]]
  [HIGHLIGHT [FIELDS {num} {field} ... ] [TAGS {open} {close}]]
  [SLOP {slop}] [INORDER]
  [LANGUAGE {language}]
  [EXPANDER {expander}]
  [SCORER {scorer}]
  [PAYLOAD {payload}]
  [SORTBY {field} [ASC|DESC]]
  [LIMIT offset num]


FT.DEL {index} {doc_id}


FT.GET {index} {doc id}


FT.DROP {index}

FT.TAGVALS {index} {field_name}

'''
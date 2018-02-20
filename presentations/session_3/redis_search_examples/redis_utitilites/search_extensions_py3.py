import redis
import json
import time

class Basic_Field(object):
  
   def __init__(self):
      self.field_list = []

   def dump(self):
      return self.field_list

   def add_fields(self,fields,field_type):
       if isinstance(fields,list) == False:
           fields = [fields]
       for i in fields:
           self.field_list.extend([i,field_type])


class Tag_Field(Basic_Field):
   
   def __init__(self):
       super().__init__()

   def add(self,fields):
      self.add_fields(fields,"TAG")
     
      
class Text_Field(Basic_Field):
   
   def __init__(self):
       super().__init__()

   def add(self,fields):
      self.add_fields(fields,"TEXT")
      

class Numeric_Field(Basic_Field):

   def __init__(self):
       super().__init__()

   def add(self,fields):
      self.add_fields(fields,"NUMERIC")
      
       


class Search_Extensions( object ):

   def __init__(self,redis_handle):
       self.redis_handle = redis_handle

      
   def create(self,index, text_fields = None, numeric_fields = None, tag_fields = None):
       fields = []
       fields.append("FT.CREATE")
       fields.append(index)
       fields.append("SCHEMA")
       
       if text_fields != None:
         fields.extend(text_fields.dump())
         
       if numeric_fields != None:
          fields.extend(numeric_fields.dump())
          
       if tag_fields != None:
          fields.extend(tag_fields.dump())

       command_string = " ".join(fields)
       
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       return results
       
   def drop( self, index): 
       results = self.redis_handle.execute_command("FT.DROP "+index)
       return results       

       
   def add(self, index,doc_id,field_values, replace = False , score = 1) :
       fields = []
       fields.append("FT.ADD")
       fields.append(str(index))
       fields.append(str(doc_id))
       fields.append(str(score))
       if replace == True:
           fields.append("REPLACE")
       
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
       self.redis_handle.delete(doc_id)
       return results
    
   
   def get( self, index,doc_id):
       fields = []
       fields.append("FT.GET")
       fields.append(str(index))
       fields.append(str(doc_id))
  
       command_string = " ".join(fields)
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       if results == None:
          return None       
       return self.__list_to_dictionary__(results)

   # not sure what this does
   def tagvals( self, index, field_name ):
     return self.redis_handle.execute_command("FT.TAGVALS "+str(index)+" "+str(field_name))
     
   def text_search( self, index, text_query, filters = None):
       fields = []
       fields.append("FT.SEARCH")
       fields.append(str(index))
       fields.append(str(text_query))
       if filters != None:
          for i in Filters:
             fields.extend(i.expand)

  
       command_string = " ".join(fields)
       print("command_string",command_string)
       results =self.redis_handle.execute_command(command_string)
       
       number = int(results[0])

       return_value = []
       
       for i in range(0,number):
          
          index = 2*i+1
          dict_name = results[index]
          dict = self.__list_to_dictionary__(results[index+1])
          dict["__doc_id__"] = dict_name
          return_value.append( dict) 
       return return_value
          
   def __list_to_dictionary__(self,list_entry):
       return_value = {}

       for i in range(0,len(list_entry),2):
          
          key = list_entry[i]
          return_value[key] = list_entry[i+1]
       return return_value
  



   

 
if __name__ == "__main__":
   
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
   
   print("tag file example")
   tag_entry = Tag_Field()
   tag_entry.add(["cities"])
   print( search.create("travel",tag_fields = tag_entry ))
   dict_values ={}
   dict_values["cities"] = '"Boston, New York"'
   #dict_values["airports"] = '"Logan, Kennedy, PHL"'
   dict_values_a = {"name":"joe","company":"xerox","age":40}
   print( search.add("test","doc_id", dict_values_a ))
  
   print( search.add("travel","doc_id_ag_6", dict_values ))
   print(search.delete("travel","doc_id_ag_6"))
   print(search.drop("travel"))
   print( search.drop("test"))   
   redis_handle.flushdb()
   exit()
   



import redis

import copy
import json


def basic_init(self):
      self.sep       = "["
      self.rel_sep   = ":"
      self.label_sep = "]"
      self.namespace     = []
  



class Build_Configuration(object):
   def __init__( self, redis_handle):  
       self.redis_handle = redis_handle
       self.delete_all()
       self.keys = set()
       basic_init(self)
 
   def build_namespace( self,name ):
       return_value = copy.deepcopy(self.namespace) 
       return_value.append(name)
       return return_value


   def pop_namespace( self ):
       del self.namespace[-1]    

   def add_header_node( self, relation,label=None, properties = {}, json_flag= True ):
     if label== None:
        label = relation
     properties["name"] = label
     self.construct_node( True, relation, label, properties, json_flag )

   def end_header_node( self, assert_namespace ):
       assert (assert_namespace == self.namespace[-1][0]) ,"miss match namespace  got  "+assert_namespace+" expected "+self.namespace[-1][0]
       del self.namespace[-1]    


   def check_namespace( self ):
       assert len(self.namespace) == 0, "unbalanced name space, current namespace: "+ json.dumps(self.namespace)
       #print ("name space is in balance")
      
   def add_info_node( self, relation,label, properties = {}, json_flag= True ):
     
     
     self.construct_node( False, relation,  label, properties, json_flag )

   # concept of namespace name is a string which ensures unique name
   # the name is essentially the directory structure of the tree
   def construct_node(self, push_namespace,relationship, label,  properties, json_flag = True ):
 

       redis_key, new_name_space = self.construct_basic_node( self.namespace, relationship,label ) 
       if redis_key in self.keys:
            raise ValueError("Duplicate Key")
       self.keys.add(redis_key)
       for i in properties.keys():
           temp = json.dumps(properties[i] )
           self.redis_handle.hset(redis_key, i, temp )
       
       
       if push_namespace == True:
          self.namespace = new_name_space

   def _convert_namespace( self, namespace):
     
       temp_value = []

       for i in namespace:
          temp_value.append(self.make_string_key( i[0],i[1] ))
       key_string = self.sep+self.sep.join(temp_value)
 
       return  key_string
  
   def construct_basic_node( self, namespace, relationship,label ): #tested 
       
       new_name_space = copy.copy(namespace)
       new_name_space.append( [ relationship,label ] )
       
       redis_string =  self._convert_namespace(new_name_space)

       self.redis_handle.hset(redis_string,"namespace",json.dumps(redis_string))
       self.redis_handle.hset(redis_string,"name",json.dumps(label))
       self.update_terminals( relationship, label, redis_string)
       self.update_relationship( new_name_space, redis_string )
       return redis_string, new_name_space


   def make_string_key( self, relationship,label):
       return relationship+self.rel_sep+label+self.label_sep
 
   def update_relationship( self, new_name_space, redis_string ):
       for relationship,label in new_name_space:
           #print( relationship,label,redis_string)
           self.redis_handle.sadd("@RELATIONSHIPS",relationship)
           self.redis_handle.sadd("%"+relationship,redis_string)
           self.redis_handle.sadd("#"+relationship+self.rel_sep+label,redis_string)

   def update_terminals( self, relationship,label, redis_string ):
       self.redis_handle.sadd("@TERMINALS",relationship)
       self.redis_handle.sadd("&"+relationship,redis_string)
       self.redis_handle.sadd("$"+relationship+self.rel_sep+label,redis_string)


 
   def store_keys( self ):
       for i in self.keys:
            self.redis_handle.sadd("@GRAPH_KEYS", i )



   def delete_all(self): #tested
       self.redis_handle.flushdb()

class Query_Configuration(object):

   def __init__( self, redis_handle):
      
        self.redis_handle = redis_handle
        basic_init(self)  

   def to_dictionary( self, list, key, json_flag = False ):
       return_value = {}
       for i in list:
           if json_flag == True:
               i = json.loads(i)
           return_value[i[key]] = i
       return return_value


   def match_terminal_relationship( self, relationship, label= None , starting_set = None,property_values = None, data_flag = True ):
       return_value = None
       #print("initial starting set",starting_set)
       if starting_set == None:
          starting_set = self.redis_handle.smembers("@GRAPH_KEYS")
       #print("starting set",starting_set)#
       if label == None:
          #print("made it here")
          if self.redis_handle.sismember( "@TERMINALS", relationship) == True:
              #print("made it here #2") 
              return_value = set(self.redis_handle.smembers("&"+relationship))
              #print("return_value 1",return_value)
              #print( starting_set)
              return_value = return_value.intersection(starting_set)
              #print("return_value",return_value)
       
       else:
          if self.redis_handle.sismember( "@TERMINALS", relationship) == True:
               if self.redis_handle.exists("$"+relationship+self.rel_sep+label) == True:
                   return_value = self.redis_handle.smembers("$"+relationship+self.rel_sep+label)
                   return_value = return_value.intersection(starting_set)

       if (property_values != None) and (return_value != None):
          return_value = self.match_properties( return_value , property_values )

       if data_flag == True:
           return_value = self.return_data( return_value)
       return return_value


   def match_relationship( self, relationship, label= None , starting_set = None ):
       return_value = None
       if starting_set == None:
          starting_set = self.redis_handle.smembers("@GRAPH_KEYS")
       #print("starting set",starting_set)#
       if label == None:
          #print("made it here")
          if self.redis_handle.sismember( "@RELATIONSHIPS", relationship) == True:
              #print("made it here #2") 
              return_value = set(self.redis_handle.smembers("%"+relationship))
              #print("return_value 1",return_value)
              #print( starting_set)
              return_value = return_value.intersection(starting_set)
       
       else:
          if self.redis_handle.sismember( "@RELATIONSHIPS", relationship) == True:
               if self.redis_handle.exists("#"+relationship+self.rel_sep+label) == True:
                   return_value = self.redis_handle.smembers("#"+relationship+self.rel_sep+label)
                   return_value = return_value.intersection(starting_set)
   
       return return_value

   def match_properties( self, starting_set , property_values ):
       return_value = []
       for i in list(starting_set):
           flag = True
           for j , value in property_values.items(): 
               data = self.redis_handle.hget(i,j)
               if data == None:
                   flag = False
                   break
               
               if json.loads(data) != value:
                   flag = False
                   break
 
           if flag == True:
               return_value.append( i)
       return return_value

   def match_relationship_list ( self, relationship_list, starting_set = None, property_values = None, fetch_values = True ):
      for relationship ,label in relationship_list:  
          starting_set = self.match_relationship( relationship, label, starting_set )
      if property_values != None:
         starting_set = self.match_properties( starting_set, property_values )
      
      if fetch_values == True:
           return_value = self.return_data( starting_set)
      else:
           return_value = starting_set
 
      return return_value

   def return_data( self, key_set ):
       return_value = []
       for i in key_set:
           data = self.redis_handle.hgetall(i)
           
           temp = {}
           for j in data.keys():

               try:
                   temp[j] = json.loads(data[j] )
               except:
                   #print("exception")
                   temp[j] = data[j]
           return_value.append(temp)
       return return_value



   def modify_properties( self, redis_key, new_properties):
       for i , value in new_properties.items():
         self.redis_handle.hset(redis_key,i, value )

   def form_dict_from_list( self, list_set, dict_property ):
       return_value = {}
       for i in list_set:
           return_value[i[dict_property]] = i
       return return_value

   def form_key_list( self,key, property_array ):
       return_value = []
       for i in property_array:
          return_value.append(i[key])
       return return_value   



      
if __name__ == "__main__":
   redis_handle  = redis.StrictRedis( host = "127.0.0.1", port=6379, db = 11 , decode_responses=True)
   

   bc = Build_Configuration( redis_handle)  
   qc = Query_Configuration(redis_handle)
 
   bc.construct_node( True, "HEAD","HEAD",{})
   bc.construct_node( True, "Level_1","level11",{})
   bc.construct_node( True, "Level_2","level21",{} )
   bc.pop_namespace()
   bc.construct_node( True, "Level_2","level12",{})
   bc.construct_node( True, "Level_3","level33",{} )
   bc.store_keys()
   #print ("nodes ",redis_handle.keys("*]"))
   #print ("system",redis_handle.keys("@*"))
   #print ("relations",redis_handle.keys("%*"))
   #print ("labels",redis_handle.keys("#*"))

  
   #print ("all redis keys", redis_handle.keys("*"))
   print("single relationship", qc.match_relationship("Level_1"))
   print("single relationship-label", qc.match_relationship("Level_3","level33"))
   x =  qc.match_relationship_list( [["Level_1","level11"],["Level_2","level12"]],fetch_values= True)
   print ("multiple relationship")
   for i in x:
     print( i )
   x = qc.match_relationship_list( [["Level_1","level11"]],property_values={"name":"level21"},fetch_values= True)
   print ("multiple relationship")
   for i in x:
     print( i )
   new_properties = {"speed":10,"acc":32.2 }
   qc.modify_properties( '[HEAD:HEAD][Level_1:level11][Level_2:level21]', new_properties)
   print( redis_handle.hgetall('[HEAD:HEAD][Level_1:level11][Level_2:level21]'))
   print (qc.match_terminal_relationship( "Level_2", label= None , starting_set = None ))
   print (qc.match_terminal_relationship( "Level_2", label= "level21" , starting_set = None ))
   print (qc.match_terminal_relationship( "Level_2", label= None , starting_set = None ,data_flag = False))
   print (qc.match_terminal_relationship( "Level_2", label= "level21" , starting_set = None,data_flag = False ))
   pv = {"speed":10,"acc":32.2}
   print (qc.match_terminal_relationship( "Level_2", label= "level21" ,property_values = pv, starting_set = None ))
   
   

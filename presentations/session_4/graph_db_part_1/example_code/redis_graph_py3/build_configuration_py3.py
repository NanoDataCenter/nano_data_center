import redis
import copy
import json


class Build_Configuration(object):
   def __init__( self, redis_handle):  
       self.redis_handle = redis_handle
       self.delete_all()
       self.keys = set()
       self.sep       = "["
       self.rel_sep   = ":"
       self.label_sep = "]"
       self.namespace     = []
 
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
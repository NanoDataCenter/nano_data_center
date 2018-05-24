

import redis
import time
import copy
import pickle
import redis
import gzip
import json
import sys

from .redis_stream_utilities_py3 import Redis_Stream
from .graph_query_support_py3 import Query_Support

class Construct_Namespace(object):
   def __init__(self):
       
       self.sep       = "["
       self.rel_sep   = ":"
       self.label_sep = "]"



   def construct_name_space(self,topic):
       name_space_list = []
       namespace = ""
       topic_list = topic.split("/")
       if topic_list[0].strip() == "":
           topic_list.pop(0)
       if topic_list[-1].strip() == "":
           topic_list.pop(-1)
       for i in topic_list:
           i_list = i.split(self.rel_sep)
           if len(i_list) < 2:
               i_list.append("")

           i_list[0] = i_list[0].replace(" ","_")
           i_list[1] = i_list[1].replace(" ","_")
            
           name_space_list.append(i_list)   
           
           namespace = namespace+self.sep+i_list[0]+self.rel_sep+i_list[1]+self.label_sep    
       return namespace, name_space_list           
           
        
        
        

class MQTT_TO_REDIS_BRIDGE_STORE(Redis_Stream,Construct_Namespace):

   def __init__(self,redis_site,depth=100):

       self.depth = depth
       self.redis_handle = redis.StrictRedis( host = redis_site["host"] , 
                                             port=redis_site["port"], 
                                             db=redis_site["mqtt_db"] , 
                                             decode_responses=True)
                                                          
       Redis_Stream.__init__(self,self.redis_handle,exact_flag = False)
       Construct_Namespace.__init__(self)
       
     

   def clear_db(self):
       self.redis_handle.flushdb()   
                                             
   def store_mqtt_data(self,topic,data):
        
       namespace,namespace_list = self.construct_name_space(topic)
     
       

       self.construct_relations(namespace,namespace_list)
       try:
          self.xadd(key = namespace , max_len=self.depth,id="*",data_dict={"data":data} )
       except: 
         pass
         #raise
         
       

   def construct_relations(self,namespace, namespace_list):
       for relationship,label in namespace_list:
           #print( relationship,label,redis_string)
           self.redis_handle.sadd("@RELATIONSHIPS",relationship)
           self.redis_handle.sadd("%"+relationship,namespace)
           self.redis_handle.sadd("#"+relationship+self.rel_sep+label,namespace)
       
       relationship = namespace_list[-1][0]
       label        = namespace_list[-1][1]
       self.redis_handle.sadd("@TERMINALS",relationship)
       self.redis_handle.sadd("&"+relationship,namespace)
       self.redis_handle.sadd("$"+relationship+self.rel_sep+label,namespace)
       
       
       

class MQTT_TO_REDIS_BRIDGE_RETRIEVE(Redis_Stream,Construct_Namespace,Query_Support):

   def __init__(self,redis_site_data,depth):
       self.redis_handle = redis.StrictRedis( host = redis_site["host"] , 
                                             port=redis_site["port"], 
                                             db=redis_site["mqtt_db"] , 
                                             decode_responses=True)
       self.depth = depth               
       self.sep       = "["
       self.rel_sep   = ":"
       self.label_sep = "]"
                                            
    
   def list_all_topics(self):
       return self.redis_handle.smembers("@TOPICS") 


   def add_mqtt_match_terminal( self, query_list, relationship, label=None , property_mask = None ):
       temp = {}
       temp["relationship"] = relationship
       temp["label"]        = label
       temp["property_mask"] = property_mask
       temp["type"] = "MATCH_TERMINAL"
       query_list.append(temp)
       return query_list

   def add_mqtt_match_relationship( self, query_list, relationship, label=None , property_mask=None ):
       temp = {}
       temp["relationship"] = relationship
       temp["label"]        = label
       temp["property_mask"] = property_mask
       temp["type"] = "MATCH_RELATIONSHIP"
       query_list.append(temp)
       return query_list


       

   def match_mqtt_list( self,  match_list, starting_set = None , return_data_flag = True ):
       if starting_set == None:
           starting_set = self.redis_handle.smembers("@GRAPH_KEYS")
       
       for i in match_list:
           if i["type"] == "MATCH_TERMINAL":
               starting_set = self.match_terminal_relationship( i["relationship"], i["label"] , starting_set, i["property_mask"])
               if starting_set == None:
                   return set([]), []

           elif i["type"] == "MATCH_RELATIONSHIP":
               starting_set = self.match_relationship( i["relationship"], i["label"] , starting_set )
               if starting_set == None:
                   return set([]), []
          
         
       return starting_set
          
       
   def mqtt_xrange_topic(self, topic, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@TOPICS",topic) == True:
           namespace = self.construct_name_space(topic)
           return xrevrange_namespace(namespace, start_timestamp, end_timestamp , count)
       else:
           return None

   def xrevrange_namespace_list(self,namespace, start_timestamp, end_timestamp , count=100):
       return_list = []
       for i in namespace_list:
           return_list.append(self.xrevrange_namespace( i, start_timestamp, end_timestamp , count ))
       return return_list
      
   def xrevrange_namespace(self,namespace, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@TOPICS",topic) == True:
           namespace = self.construct_name_space(topic)
           return xrevrange_namespace(namespace, start_timestamp, end_timestamp , count)
       else:
           return None

   def xrange_topic(self, namespace, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@NAMESPACE",namespace) == True:
           return self.xrange(namespace,start_timestamp,end_timestamp, count)
       else:
          return None      
          
   def xrange_namespace_list(self,namespace, start_timestamp, end_timestamp , count=100):
      return_list = []
      for i in namespace_list:
         return_list.append(self.xrange_namespace( i, start_timestamp, end_timestamp , count ))
      return return_list

   def xrange_namespace(self,namespace, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@NAMESPACE",namespace) == True:
          return self.xrange(namespace,start_timestamp,end_timestamp, count)
       else:
          return None 
   

'''

def basic_init(self):
      self.sep       = "["
      self.rel_sep   = ":"
      self.label_sep = "]"
      self.namespace     = []
  

   
   
class Build_Configuration(object):
   def __init__( self, redis_site ):  
       self.redis_handle = redis.StrictRedis( host = redis_site["host"] , port=redis_site["port"], db=redis_site["graph_db"] , decode_responses=True)
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
       
   def extract_db(self):
       keys = self.redis_handle.keys("*")
       self.extract = {}
       print("len",len(keys))
       for i in keys:
           self.extract[i] = self.redis_handle.dump(i)
           
   def save_extraction(self,filename):
        file = gzip.GzipFile(filename, 'wb')
        file.write(pickle.dumps(self.extract, pickle.DEFAULT_PROTOCOL))
        file.close()

   def restore_extraction(self,filename):
        file = gzip.GzipFile(filename, 'rb')
        buffer = b""
        while True:
                data = file.read()
                if data == b"":
                        break
                buffer += data
        extract = pickle.loads(buffer)
        file.close()
        keys = extract.keys()
        print("len",len(keys))
        for i,item in extract.items():
           self.redis_handle.restore(name = i,ttl=0, value = item, replace = True)
        

'''
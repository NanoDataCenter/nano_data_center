

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
       
   def get_topics(self):
       return self.redis_handle.smembers("@TOPICS")
                                             
   def store_mqtt_data(self,topic,data):
        
       namespace,namespace_list = self.construct_name_space(topic)
       self.redis_handle.sadd("@GRAPH_KEYS",namespace)
       self.redis_handle.sadd("@NAMESPACE",namespace)
       self.redis_handle.sadd("@TOPICS",topic)
     
       

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

   def __init__(self,redis_site_data):
       self.redis_handle = redis.StrictRedis( host = redis_site_data["host"] , 
                                             port=redis_site_data["port"], 
                                             db=redis_site_data["mqtt_db"] , 
                                             decode_responses=True)
                    
       self.sep       = "["
       self.rel_sep   = ":"
       self.label_sep = "]"
                                            
    


   def add_mqtt_match_terminal( self, query_list, relationship, label=None ):
       temp = {}
       temp["relationship"] = relationship
       temp["label"]        = label
       temp["property_mask"] = None
       temp["type"] = "MATCH_TERMINAL"
       query_list.append(temp)
       return query_list

   def add_mqtt_match_relationship( self, query_list, relationship, label=None ):
       temp = {}
       temp["relationship"] = relationship
       temp["label"]        = label
       temp["property_mask"] =None
       temp["type"] = "MATCH_RELATIONSHIP"
       query_list.append(temp)
       return query_list


       

   def match_mqtt_list( self,  match_list, starting_set = None  ):
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
          
       
   def mqtt_xrevrange_topic(self, topic, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@TOPICS",topic) == True:
           namespace,name_space_list = self.construct_name_space(topic)
           return self.xrevrange_namespace(namespace, start_timestamp, end_timestamp , count)
       else:
           return None

   def xrevrange_namespace_list(self,namespace_list, start_timestamp, end_timestamp , count=100):
       return_list = []
       for i in namespace_list:
           
           return_list.append(self.xrevrange_namespace( i, start_timestamp, end_timestamp , count ))
       return return_list
      
   def xrevrange_namespace(self,namespace, start_timestamp, end_timestamp , count=100):
       print("made it here 1")
       if self.redis_handle.sismember("@NAMESPACE",namespace) == True:
           print("made it here 2")
           return self.xrevrange(namespace, start_timestamp, end_timestamp , count)
       else:
           return None

   def xrange_topic(self, topic, start_timestamp, end_timestamp , count=100):
        if self.redis_handle.sismember("@TOPICS",topic) == True:
           namespace,namespace_list = self.construct_name_space(topic)
           
           return self.xrange_namespace(namespace, start_timestamp, end_timestamp , count)
        else:
           return None
          
   def xrange_namespace_list(self,namespace_list, start_timestamp, end_timestamp , count=100):
      return_list = []
      for i in namespace_list:
         return_list.append(self.xrange_namespace( i, start_timestamp, end_timestamp , count ))
      return return_list

   def xrange_namespace(self,namespace, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@NAMESPACE",namespace) == True:
          return self.xrange(namespace,start_timestamp,end_timestamp, count)
       else:
          return None 
   


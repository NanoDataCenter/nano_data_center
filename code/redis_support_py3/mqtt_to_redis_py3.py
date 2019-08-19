

import redis
import time
import copy
import pickle
import redis
import gzip
import json
import sys
import msgpack


from .graph_query_support_py3 import Query_Support
from .redis_stream_utilities_py3 import Redis_Stream
from .mqtt_message_processing_py3 import MQTT_Message_Processing

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
           
        
        
        

class MQTT_TO_REDIS_BRIDGE_STORE(Construct_Namespace,Redis_Stream):

   def __init__(self,redis_site,
                     mqtt_devices,
                     package,
                     generate_handlers,
                     irrigation_table_entries,
                     irrigation_table,
                     depth=1000):

   
       self.depth = depth
       self.irrigation_table_entries = irrigation_table_entries
       self.irrigation_table  = irrigation_table
      
       self.mqtt_devices = mqtt_devices
       self.redis_handle = redis.StrictRedis( host = redis_site["host"] , 
                                             port=redis_site["port"], 
                                             db=redis_site["mqtt_db"] )
                                             
                                                          
       self.mqtt_messaging = MQTT_Message_Processing()
       Construct_Namespace.__init__(self)
       data_structures = package["data_structures"]
       
       self.ds_handlers = {}
       self.ds_handlers["MQTT_UNKNOWN_DEVICES"] = generate_handlers.construct_hash(data_structures["MQTT_UNKNOWN_DEVICES"])   
       self.ds_handlers["MQTT_UNKNOWN_SUBSCRIPTIONS"] = generate_handlers.construct_hash(data_structures["MQTT_UNKNOWN_SUBSCRIPTIONS"])
       
       
   def clear_db(self):
       self.redis_handle.flushdb()   
       
   def get_topics(self):
       return self.redis_handle.smembers("@TOPICS")

   def validate_device(self,topic,namespace_list):
       device_id = namespace_list[1][0]
      
       if device_id in self.mqtt_devices:
          self.device_id = device_id
          return True
       else:
            print("no_match",topic)
            data = {}
            data["topic"] = topic
            data["timestamp"] = time.time()
            self.ds_handlers["MQTT_UNKNOWN_DEVICES"].hset(device_id,data)
            return False

 
   def check_for_null_command(self,topic,namespace_list):
       null_commands = self.mqtt_devices[self.device_id]["null_commands"]
       topic_list = topic.split("/")
       topic_list = topic_list[3:]
       topic_search = "/".join(topic_list)
       if topic_search in null_commands:
          #print("null_commands found")
          return True
       else:
          
           return False

   def check_for_valid_subscriptions(self,topic,namespace_list):
       valid_commands = self.mqtt_devices[self.device_id]["subscriptions"]
       topic_list = topic.split("/")
       topic_list = topic_list[3:]
       topic_search = "/".join(topic_list)
       if topic_search in valid_commands:
          #print("valid command",topic)
          return True
       else:
            print("no_match",topic)
            data = {}
            data["topic"] = topic
            data["timestamp"] = time.time()
            self.ds_handlers["MQTT_UNKNOWN_SUBSCRIPTIONS"].hset(topic,data)
            return False
  
 
   def store_mqtt_data(self,topic,mqtt_data):
       print("*******************************topic",topic)
       namespace,namespace_list = self.construct_name_space(topic)
       if self.validate_device(topic,namespace_list) != True:
           return # unknown device
       if self.check_for_null_command(topic,namespace_list) == True :
           return #null command 
       if self.check_for_valid_subscriptions(topic,namespace_list) != True:
            return #bad subscription       
       self.redis_handle.sadd("@GRAPH_KEYS",namespace)
       self.redis_handle.sadd("@NAMESPACE",namespace)
       self.redis_handle.sadd("@TOPICS",topic)
     
       

       self.construct_relations(namespace,namespace_list)
       
       try:

          data = msgpack.unpackb(mqtt_data)
         
          data["device_path"] = topic
         
          self.stream_write(namespace,data)
          self.update_irrigation_table(topic,data)   
  
       except: 
          print("*******************************exception")
          data = {}
          data["topic"] = topic
          data["timestamp"] = time.time()
          self.stream_write(namespace,data)
         
         
       
   def stream_write(self,key, data):
       store_dictionary = {}
       packed_data  =msgpack.packb(data,use_bin_type = True )
       out_data = {}
       out_data["data"] = packed_data
       self.xadd(key = key, max_len=self.depth,id="*",data_dict=out_data )
   
   
   
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
       
       
   def update_irrigation_table(self,topic,data):
       
       topic_list = topic.split("/")
       device = topic_list[2]
       device_topic = "/".join(topic_list[3:])
       for key,item in self.irrigation_table_entries.items():
           
           if (device == item[0]) and (device_topic == item[1]):
              
               if isinstance(self.mqtt_devices[device]["subscriptions"][device_topic],dict): 
                  processed_data = self.mqtt_messaging.process_mqtt_message(self.mqtt_devices[device]["subscriptions"][device_topic],item[2],data)
                  print(key,processed_data)
                  self.irrigation_table.hset(key,processed_data)
                  
       #print("xxxxxxxx",topic,device,device_topic)








   

class MQTT_TO_REDIS_BRIDGE_RETRIEVE(Construct_Namespace,Redis_Stream):

   def __init__(self,redis_site_data):
       self.site_data = redis_site_data 
                                    
                    
       self.sep       = "["
       self.rel_sep   = ":"
       self.label_sep = "]"
       Construct_Namespace.__init__(self) 
       self.redis_handle   = redis.StrictRedis( host = redis_site_data["host"], port = redis_site_data["port"],db=redis_site_data["mqtt_db"])       
       

   def stream_exists(self,key):
       
       if self.redis_handle.exists(key):
          if self.redis_handle.type(key) == b'stream':
             return True
       return False
          
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
 
   def match_terminal_relationship( self, relationship, label= None , starting_set = None,property_values = None ):
       return_value = None
      
       if label == None:
         
          if self.redis_handle.sismember( "@TERMINALS", relationship) == True:
             
              return_value = set(self.redis_handle.smembers("&"+relationship))
             
              return_value = return_value.intersection(starting_set)
              
              
       
       else:
          if self.redis_handle.sismember( "@TERMINALS", relationship) == True:
               if self.redis_handle.exists("$"+relationship+self.rel_sep+label) == True:
                   return_value = self.redis_handle.smembers("$"+relationship+self.rel_sep+label)
                   return_value = return_value.intersection(starting_set)

       if (property_values != None) and (return_value != None):
          return_value = self.match_properties( return_value , property_values )
       return return_value

   def match_relationship( self, relationship, label= None , starting_set = None ):
       return_value = None
       
       if label == None:
          
          if self.redis_handle.sismember(  "@RELATIONSHIPS", relationship) == True:
             
              return_value = set(self.redis_handle.smembers("%"+relationship))
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



 
       
   def xrange_topic(self, topic, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@TOPICS",topic) == True:
           namespace,name_space_list = self.construct_name_space(topic)
           return self.xrange_namespace(namespace, start_timestamp, end_timestamp , count)
       else:
           return None

    

          
   def xrange_namespace_list(self,namespace_list, start_timestamp, end_timestamp , count=100):
      return_list = []
      for i in namespace_list:
         return_list.append(self.xrange_namespace( i, start_timestamp, end_timestamp , count ))
      return return_list

   def xrange_namespace(self,namespace, start_timestamp, end_timestamp , count=100):
       if isinstance(start_timestamp,str) == False:
           start_timestamp = int(start_timestamp*1000)
       if isinstance(end_timestamp,str) == False:
           end_timestamp = int(end_timestamp*1000)


       data_list = self.xrange(namespace,start_timestamp,end_timestamp, count)

       return data_list
       
   def xrevrange_topic(self, topic, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@TOPICS",topic) == True:
           namespace,name_space_list = self.construct_name_space(topic)
           return self.xrevrange_namespace(namespace, start_timestamp, end_timestamp , count)
       else:
           return None

    

          
   def xrevrange_namespace_list(self,namespace_list, start_timestamp, end_timestamp , count=100):
      return_list = []
      for i in namespace_list:
         return_list.append(self.xrange_namespace( i, start_timestamp, end_timestamp , count ))
      return return_list

   def xrevrange_namespace(self,namespace, start_timestamp, end_timestamp , count=100):
       if self.redis_handle.sismember("@NAMESPACE",namespace) == False:
          return None
       if isinstance(start_timestamp,str) == False:
           start_timestamp = int(start_timestamp*1000)
       if isinstance(end_timestamp,str) == False:
           end_timestamp = int(end_timestamp*1000)

       data_list = self.xrevrange(namespace,start_timestamp,end_timestamp, count)

       return data_list

 


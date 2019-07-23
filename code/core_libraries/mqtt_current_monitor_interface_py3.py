import paho.mqtt.client as mqtt
import ssl
from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
import time
import msgpack
class MQTT_Current_Monitor_Publish(object):

   def __init__(self,redis_site,topic_prefix) :
       self.topic_prefix = topic_prefix
       qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"MQTT_DEVICES_DATA"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)
       package = package_sources[0] 
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,redis_site)
       self.job_queue_client = generate_handlers.construct_job_queue_client(data_structures["MQTT_PUBLISH_QUEUE"])
       
 
     

  

   def  read_current_limit(self):
      request = {}
      request["topic"] = "INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS"
      self.send_request(request)   
 
   def read_max_currents(self):
      request = {}
      request["topic"] = "INPUT/MQTT_CURRENT/GET_MAX_CURRENTS"
      self.send_request(request)   
      

   def clear_max_currents(self):
      request = {}
      request["topic"] = "OUTPUT/MQTT_CURRENT/CLEAR_MAX_CURRENTS"
      self.send_request(request)   
      

   def read_current(self):
      request = {}
      request["topic"] = "INPUT/MQTT_CURRENT/READ_CURRENT"
      self.send_request(request)   

   def enable_equipment_relay(self):
      request = {}
      request["topic"] = "OUTPUT/MQTT_CURRENT/ENABLE_EQUIPMENT_RELAY"
      self.send_request(request)   

   def enable_irrigation_relay(self):
      request = {}
      request["topic"] = "OUTPUT/MQTT_CURRENT/ENABLE_IRRIGATION_RELAY"
      self.send_request(request)   

   def disable_equipment_relay(self):
      request = {}
      request["topic"] = "OUTPUT/MQTT_CURRENT/DISABLE_EQUIPMENT_RELAY"
      self.send_request(request)   

   def disable_irrigation_irrigation(self):
      request = {}
      request["topic"] = "OUTPUT/MQTT_CURRENT/DISABLE_IRRIGATION_RELAY"
      self.send_request(request)   

   def read_relay_states(self):
      request = {}
      request["topic"] = "OUTPUT/MQTT_CURRENT/READ_RELAY_STATES"
      self.send_request(request)   
  

 


   def send_request(self,msg_dict):
     
     msg_dict["tx_topic"] =self.topic_prefix +msg_dict["topic"]
     #print("msg_dict",msg_dict)
     self.job_queue_client.push(msg_dict)
     
      
 
 
 
if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json

    import os
    import copy
    #import load_files_py3
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    import datetime
    

    from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter

    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
    x = MQTT_Current_Monitor_Publish(redis_site,"/REMOTES/CURRENT_MONITOR_1/")
    while(1):
      time.sleep(5)
      x.read_max_currents()
      time.sleep(5)
      x.clear_max_currents()
      time.sleep(5)
      x.read_relay_states()
    
    
    
    

  
    

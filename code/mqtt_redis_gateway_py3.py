#
#  MQTT To Redis Bridge
#
#
#
import json
import msgpack
import base64
import redis
import time
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from redis_support_py3.mqtt_to_redis_py3 import MQTT_TO_REDIS_BRIDGE_STORE
import paho.mqtt.client as mqtt
import ssl

class MQTT_Redis_Bridge(object):
   
   def __init__(self,
                mqtt_server_data,
                mqtt_devices,
                site_data,
                package,
                qs ):
                
       self.mqtt_server_data = mqtt_server_data
       self.site_data = site_data
       generate_handlers = Generate_Handlers(package,qs)
       self.mqtt_bridge = MQTT_TO_REDIS_BRIDGE_STORE(site_data,mqtt_devices,package,generate_handlers)
       
       self.client = mqtt.Client(client_id="", clean_session=True, userdata=None,  transport="tcp")
       self.client.tls_set( cert_reqs=ssl.CERT_NONE )
       
       redis_handle_pw = redis.StrictRedis(site_data["host"], 
                                           site_data["port"], 
                                           db=site_data["redis_password_db"], 
                                           decode_responses=True)
                                        
       self.client.username_pw_set("pi", redis_handle_pw.hget("mosquitto_local","pi"))
       
       self.client.on_connect = self.on_connect
       self.client.on_message = self.on_message
       self.connection_flag = False
       while self.connection_flag == False:
           try:
              
              print(self.mqtt_server_data["HOST"],self.mqtt_server_data["PORT"])
              self.client.connect(self.mqtt_server_data["HOST"],self.mqtt_server_data["PORT"], 60)
           except:
              
              time.sleep(5)
           else:
              self.connection_flag = True
           
       self.client.loop_forever()

   def on_connect(self,client, userdata, flags, rc):
      
     
        self.client.subscribe(self.mqtt_server_data["BASE_TOPIC"]+"/#")

# The callback for when a PUBLISH message is received from the server.
   def on_message(self, client, userdata, msg):
       self.mqtt_bridge.store_mqtt_data(msg.topic,msg.payload)


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
     
    qs = Query_Support( redis_site )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_terminal( query_list, 
                                        relationship =  "MQTT_DEVICE" )
                                        
    mqtt_sets, mqtt_sources = qs.match_list(query_list) 
    mqtt_devices = {}
    for i in mqtt_sources:
       mqtt_devices[i["name"]] = i

    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_terminal( query_list, 
                             relationship = "MQTT_SERVER" )
                                           
    host_sets, host_sources = qs.match_list(query_list)
    host_data = host_sources[0]
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"MQTT_DEVICES_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)
    package = package_sources[0]  
    
                                           

    MQTT_Redis_Bridge(mqtt_server_data = host_data,
                      mqtt_devices = mqtt_devices,
                      site_data = redis_site,
                      package = package,
                      qs= qs)

   
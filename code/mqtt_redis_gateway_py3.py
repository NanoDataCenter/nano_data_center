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

from redis_support_py3.mqtt_to_redis_py3 import MQTT_TO_REDIS_BRIDGE_STORE
import paho.mqtt.client as mqtt
import ssl

class MQTT_Redis_Bridge(object):
   
   def __init__(self,redis_site_data):
       self.redis_site_data = redis_site_data
       self.mqtt_bridge = MQTT_TO_REDIS_BRIDGE_STORE(redis_site_data,100)
       
       self.client = mqtt.Client(client_id="", clean_session=True, userdata=None,  transport="tcp")
       self.client.tls_set(ca_certs= "/etc/mosquitto/certs/ca.crt", cert_reqs=ssl.CERT_NONE )
       
       redis_handle_pw = redis.StrictRedis(redis_site_data["host"], 
                                           redis_site_data["port"], 
                                           db=redis_site_data["redis_password_db"], 
                                           decode_responses=True)
                                          
       self.client.username_pw_set("pi", redis_handle_pw.hget("mosquitto_local","pi"))
       
       self.client.on_connect = self.on_connect
       self.client.on_message = self.on_message
       self.connection_flag = False
       while self.connection_flag == False:
           try:
              self.client.connect(redis_site_data["mqtt_server"],redis_site_data["mqtt_port"], 60)
           except:
              print("exception")
              time.sleep(5)
           else:
              self.connection_flag = True
           
       self.client.loop_forever()

   def on_connect(self,client, userdata, flags, rc):
      
       print("Connected with result code "+str(rc),self.redis_site_data["mqtt_topic"])
       self.client.subscribe(self.redis_site_data["mqtt_topic"])

# The callback for when a PUBLISH message is received from the server.
   def on_message(self, client, userdata, msg):
       print(msg.topic+" "+str(msg.payload))
       self.mqtt_bridge.store_mqtt_data(msg.topic,msg.payload)

__test__ = False
if __name__ == "__main__":
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
  
   redis_site_data = json.loads(data)
   if __test__== False:
      MQTT_Redis_Bridge(redis_site_data)

   
   else:
       #test code
       import time
       from threading import Thread
       from redis_support_py3.mqtt_client_py3 import MQTT_CLIENT
       from redis_support_py3.mqtt_to_redis_py3 import MQTT_TO_REDIS_BRIDGE_RETRIEVE
       def test_driver(redis_site_data):
       
           MQTT_Redis_Bridge(redis_site_data)
   
       file_handle = open("system_data_files/redis_server.json",'r')
       data = file_handle.read()
       file_handle.close()
      
       redis_site_data = json.loads(data)
   
       server = Thread(target=test_driver,args=(redis_site_data,))
       server.start()
   
       mqtt_client = MQTT_CLIENT(redis_site_data,redis_site_data["mqtt_server"],redis_site_data["mqtt_port"],"pi","mosquitto_local")
       print("client connected",mqtt_client.connect())
       print("starting to publish")
       print("message published",mqtt_client.publish("REMOTES/SLAVE:Node_1/TEMPERATURE:Case",msgpack.packb(72,use_bin_type = True )))
       print("made it here")
       mqtt_retreive = MQTT_TO_REDIS_BRIDGE_RETRIEVE(redis_site_data)
       print("instantiated class")
       time.sleep(1) # let message be published
       query_list = []
       mqtt_retreive.add_mqtt_match_relationship(  query_list,"SLAVE" )
       print("Match on SLAVE",mqtt_retreive.match_mqtt_list( query_list ))
 
   query_list = []
   mqtt_retreive.add_mqtt_match_relationship(  query_list,"SLAVE",label= "Node_1" )
   print("Match on SLAVE:Node_1",mqtt_retreive.match_mqtt_list( query_list ))

   query_list = []
   mqtt_retreive.add_mqtt_match_relationship(  query_list,"TEMPERATURE",label= "Case" )
   print("Match on TEMPERATURE:Case",mqtt_retreive.match_mqtt_list( query_list ))

   query_list = []
   mqtt_retreive.add_mqtt_match_terminal(  query_list,"TEMPERATURE" )
   print("Match on TEMPERATURE",mqtt_retreive.match_mqtt_list( query_list ))
 
   query_list = []
   mqtt_retreive.add_mqtt_match_terminal(  query_list,"TEMPERATURE",label= "Case" )
   nodes = mqtt_retreive.match_mqtt_list( query_list) 
   print("Match on TEMPERATURE:Case",nodes)
   
   nodes = list(nodes)
   print(mqtt_retreive.xrange_namespace_list( nodes, "+", "-" , count=100))
   
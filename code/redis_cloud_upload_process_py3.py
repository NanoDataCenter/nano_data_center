
#
#
import json
import msgpack
import base64
import redis
import time


import paho.mqtt.client as mqtt
import ssl

from redis_support_py3.cloud_handlers_py3 import Cloud_TX_Handler
from redis_support_py3.mqtt_client_py3 import MQTT_CLIENT

   

class Redis_Cloud_Upload(object):

   def __init__(self,redis_site_data):
       self.mqtt_client = MQTT_CLIENT(redis_site_data)
       self.redis_handle = redis.StrictRedis(redis_site_data["host"], 
                                            redis_site_data["port"], 
                                            db=redis_site_data["redis_io_db"], 
                                            decode_responses=True)
       self.state = "CONNECT"
       self.cloud_tx_handler = Cloud_TX_Handler(self.redis_handle)
       self.packet_list = None
       self.topic = redis_site_data["mqtt_cloud_topic"]
       self.do_start()
       
   def do_connect(self):
      print("connect state")
      status = self.mqtt_client.connect()
      if status == True:
         self.state = "MONITOR"
      else:
         self.state == "CONNECT"
      
   def do_monitor(self):
       print("monitor_state")
       if self.packet_list == None:
           length = self.cloud_tx_handler.length()
           print("length",length)
           if length > 0:
               self.packet_data = self.cloud_tx_handler.extract()
           else:
               return
       return_value = self.mqtt_client.publish(self.topic,payload=self.packet_list,qos=2)
       if return_value[0] == True:
           self.packet_data = None
           return
       else:
         self.mqtt_client.disconnect()
         self.state = "CONNECT"         
       
      
   def do_start(self):
      while True:
        if self.state == "CONNECT":
           self.do_connect()
        else:
           self.do_monitor()
        time.sleep(1)
        
if __name__ == "__main__":
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
      
   redis_site_data = json.loads(data)
   Redis_Cloud_Upload(redis_site_data)
        


#
#
import json
import msgpack
import base64
import redis
import time
import copy
import zlib
#import hashlib



import paho.mqtt.client as mqtt
import ssl

from redis_support_py3.cloud_handlers_py3 import Cloud_TX_Handler
from redis_support_py3.mqtt_client_py3 import MQTT_CLIENT



class Redis_Cloud_Upload(object):

   def __init__(self,redis_site_data):
       self.redis_site_data = redis_site_data
       self.mqtt_client = MQTT_CLIENT(redis_site_data,redis_site_data["mqtt_cloud_server"],redis_site_data["mqtt_cloud_port"],"remote","mosquitto_cloud")
       self.redis_handle = redis.StrictRedis(redis_site_data["host"], 
                                            redis_site_data["port"], 
                                            db=redis_site_data["redis_io_db"] )
       self.state = "CONNECT"
       self.cloud_tx_handler = Cloud_TX_Handler(self.redis_handle)
       self.packet_data = None
       self.topic = redis_site_data["mqtt_upload_topic"]
       print("topic",self.topic)
       self.do_start()
       
   def do_connect(self):
      #print("***************************connect state******************************************************")
      try:
          status = self.mqtt_client.connect()
      except:
          status = False
      if status == True:
         self.state = "MONITOR"
      else:
         self.state == "CONNECT"
      
   def do_monitor(self):
       #print("*******************************monitor state*************")
       if self.packet_data == None:
           length = self.cloud_tx_handler.length()
          
           if length > 0:
               self.packet_data = self.cloud_tx_handler.extract()
               self.packet_data = zlib.compress(self.packet_data)
           else:
              self.packet_data = None
              return
         
      
       payload = copy.deepcopy(self.packet_data)
       
       return_value = self.mqtt_client.publish(self.topic,payload=payload,qos=2)
      
       print("sending packet len ",len(self.packet_data),zlib.crc32(self.packet_data))
       if return_value[0] == True:
           self.packet_data = None
           return
       else:
         print("*********************************** bad publish **************")
         self.mqtt_client.disconnect()
         time.sleep(5)
         self.mqtt_client = MQTT_CLIENT(self.redis_site_data,redis_site_data["mqtt_cloud_server"],redis_site_data["mqtt_cloud_port"],"remote","mosquitto_cloud")
         self.state = "CONNECT"  

         return # error lets try to reconnect         
       
      
   def do_start(self):
      while True:
        if self.state == "CONNECT":
           self.do_connect()
        else:
           self.do_monitor()
        time.sleep(2)
        
if __name__ == "__main__":
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
      
   redis_site_data = json.loads(data)
   Redis_Cloud_Upload(redis_site_data)
        

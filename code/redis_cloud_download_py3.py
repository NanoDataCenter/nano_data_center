import json
import msgpack
import base64
import redis

from redis_support_py3.cloud_handlers_py3 import Cloud_RX_Handler
import paho.mqtt.client as mqtt
import ssl

class REDIS_CLOUD_SYNC(object):
   
   def __init__(self,redis_site_data):
   
       
       self.redis_site_data = redis_site_data
       
       self.redis_handle = redis.StrictRedis(redis_site_data["host"], 
                                           redis_site_data["port"], 
                                           db=redis_site_data["redis_io_db"], 
                                           decode_responses=True)
                                           
       self.cloud_rx_handler =  Cloud_RX_Handler(self.redis_handle,redis_site_data)

  
       self.client = mqtt.Client(client_id="", clean_session=True, userdata=None,  transport="tcp")
       self.client.tls_set(certfile= "/home/pi/mosquitto/certs/client.crt", keyfile= "/home/pi/mosquitto/certs/client.key", cert_reqs=ssl.CERT_NONE )
       
       redis_handle_pw = redis.StrictRedis(redis_site_data["host"], 
                                           redis_site_data["port"], 
                                           db=redis_site_data["redis_password_db"], 
                                           decode_responses=True)
                                        
       self.client.username_pw_set("remote", redis_handle_pw.hget("mosquitto_cloud","remote"))
       
       self.client.on_connect = self.on_connect
       self.client.on_message = self.on_message
       self.client.connect(redis_site_data["mqtt_cloud_server"],redis_site_data["mqtt_cloud_port"], 60)
       self.client.loop_forever()

   def on_connect(self,client, userdata, flags, rc):
       print("Connected with result code "+str(rc),self.redis_site_data["mqtt_topic"])
       self.client.subscribe(self.redis_site_data["mqtt_cloud_topic"])


   def on_message(self, client, userdata, msg):
       print(msg.topic+" "+str(msg.payload))
       cloud_rx_handler.unpack_remote_data(msg.payload)
       
     

 
       
  
  
if __name__ == "__main__":
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
      
   redis_site_data = json.loads(data)
   REDIS_CLOUD_SYNC(redis_site_data)
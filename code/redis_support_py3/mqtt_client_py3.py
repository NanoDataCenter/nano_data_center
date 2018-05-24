
import paho.mqtt.client as mqtt
import ssl
import redis
import time
class MQTT_CLIENT(object):

   def __init__(self,redis_site_data):
       self.redis_site_data = redis_site_data
       self.client = mqtt.Client(client_id="", clean_session=True, userdata=None,  transport="tcp")
       self.client.tls_set(certfile= "/home/pi/mosquitto/certs/client.crt", keyfile= "/home/pi/mosquitto/certs/client.key", cert_reqs=ssl.CERT_NONE )
       
       redis_handle_pw = redis.StrictRedis(redis_site_data["host"], 
                                           redis_site_data["port"], 
                                           db=redis_site_data["redis_password_db"], 
                                           decode_responses=True)
                                          
       self.client.username_pw_set("pi", redis_handle_pw.hget("mosquitto_local","pi"))
       
       self.client.on_connect = self.on_connect
       self.client.on_publish = self.on_publish
       
   def connect(self):
       self.rc = -1 
       self.client.connect(self.redis_site_data["mqtt_server"],self.redis_site_data["mqtt_port"], 60)
       self.client.loop_start()
       for i in range(0,50):
           time.sleep(.1)
           if self.rc == 0:
              return True
       return False
           
          


          
   def loop(self,time):
       self.client.loop(time)   
       
   def on_connect(self,client, userdata, flags, rc):
       
       
       self.rc = rc
       print("on connect rc",self.rc)
       #self.client.loop_stop()
       
   def on_publish(self, client, userdata, mid):
       self.mid_server = mid
       

   def publish(self,topic,payload=None,qos=0,retain=False):
       
       self.mid_server = -1
       self.client_result ,self.mid_client = self.client.publish(topic, payload, qos, retain)
       self.client.loop(5)
       for i in range(0,50):
           if (self.client_result == 0 ) and (self.mid_server == self.mid_client):
              return True
       return False
        
       
       
if __name__ == "__main__":
   import json
   import time
   file_handle = open("../system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
      
   redis_site_data = json.loads(data)
   mqtt_client = MQTT_CLIENT(redis_site_data)
   print(mqtt_client.connect())
   print("starting to publish")
   print(mqtt_client.publish("REMOTES/SLAVE:1/TEMPERATURE:Case",72))
   while True:
      pass
   
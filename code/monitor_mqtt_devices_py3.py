import ssl
import msgpack
import time

import paho.mqtt.client as mqtt
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
'''
msg_dict_pack_string(&msg_pack[0],"TOPIC","INPUT/GPIO/CHANGE");      
   msg_dict_pack_unsigned_integer(&msg_pack[1],"PIN",pin );
   msg_dict_pack_unsigned_integer(&msg_pack[2],"INPUT",value);
   pack_buffer = msg_dict_stream( &pack_buffer_size,3,msg_pack);
   mqtt_clt_publish("INPUT/GPIO/CHANGE", pack_buffer,pack_buffer_size );
   
     mqtt_ctrl_register_subscription("OUTPUTS/GPIO/SET", app_ouput_set_pin_data );
   return CF_DISABLE;      
} 
   


current monitor
       msg_dict_pack_string(&msg_pack[0],"TOPIC","OUTPUT/MQTT_CURRENT/EQUIPMENT_RELAY_TRIP");      
        msg_dict_pack_float(&msg_pack[1],"CURRENT_VALUE",average_currents[EQUIPMENT_CHANNEL] );
        msg_dict_pack_float(&msg_pack[2],"LIMIT_VALUE",mqtt_current_get_equipment_level());
        pack_buffer = msg_dict_stream( &pack_buffer_size,3,msg_pack);
        mqtt_clt_publish("OUTPUT/MQTT_CURRENT/EQUIPMENT_RELAY_TRIP/RESPONSE", pack_buffer,pack_buffer_size );
 mqtt_relay_set_irrigation_inactive();
        msg_dict_pack_string(&msg_pack[0],"TOPIC","OUTPUT/MQTT_CURRENT/IRRIGATION_RELAY_TRIP");      
        msg_dict_pack_float(&msg_pack[1],"CURRENT_VALUE",average_currents[IRRIGATION_CHANNEL] );
        msg_dict_pack_float(&msg_pack[2],"LIMIT_VALUE",mqtt_current_get_irrigation_level());
        pack_buffer = msg_dict_stream( &pack_buffer_size,3,msg_pack);
        mqtt_clt_publish("OUTPUT/MQTT_CURRENT/IRRIGATION_RELAY_TRIP/RESPONSE", pack_buffer,pack_buffer_size );        
  msg_dict_pack_string(&msg_pack[0],"TOPIC","INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS");      
   msg_dict_pack_float(&msg_pack[1],"EQUIPMENT_CURRENT_LIMIT", mqtt_current_get_equipment_level() );
   msg_dict_pack_float(&msg_pack[2],"IRRIGATION_CURRENT_LIMIT", mqtt_current_get_irrigation_level());
   pack_buffer = msg_dict_stream( &pack_buffer_size,3,msg_pack);
   mqtt_clt_publish("INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS/REPONSE", pack_buffer,pack_buffer_size );
   free(pack_buffer);
    
}
 msg_dict_pack_string(&msg_pack[0],"TOPIC","INPUT/MQTT_CURRENT/MAX_CURRENTS");      
   msg_dict_pack_float(&msg_pack[1],"MAX_EQUIPMENT_CURRENT", max_equipment_current );
   msg_dict_pack_float(&msg_pack[2],"MAX_IRRIGATION_CURRENT", max_irrigation_current);
   pack_buffer = msg_dict_stream( &pack_buffer_size,3,msg_pack);
   mqtt_clt_publish("INPUT/MQTT_CURRENT/MAX_CURRENTS/RESPONSE", pack_buffer,pack_buffer_size );
   free(pack_buffer);

 msg_dict_pack_string(&msg_pack[0],"TOPIC","INPUT/MQTT_CURRENT/CURRENTS");      
   msg_dict_pack_float(&msg_pack[1],"EQUIPMENT_CURRENT", average_currents[EQUIPMENT_CHANNEL] );
   msg_dict_pack_float(&msg_pack[2],"IRRIGATION_CURRENT", average_currents[IRRIGATION_CHANNEL]);
   pack_buffer = msg_dict_stream( &pack_buffer_size,3,msg_pack);
   mqtt_clt_publish("INPUT/MQTT_CURRENT/CURRENTS/RESPONSE", pack_buffer,pack_buffer_size );
   free(pack_buffer);
    
   mqtt_current_get_relay_states( &equipment_state_value, &irrigation_state_value);
   msg_dict_pack_string(&msg_pack[0],"TOPIC","OUTPUT/MQTT_CURRENT/RELAY_STATE");      
   msg_dict_pack_boolean(&msg_pack[1],"EQUIPMENT_STATE", equipment_state_value );
   msg_dict_pack_boolean(&msg_pack[2],"IRRIGATION_STATE",irrigation_state_value);
   pack_buffer = msg_dict_stream( &pack_buffer_size,3,msg_pack);
   mqtt_clt_publish("OUTPUT/MQTT_CURRENT/RELAY_STATE/RESPONSE", pack_buffer,pack_buffer_size );
   free(pack_buffer);
}
    
  

18 5
/REMOTES/GARAGE_MONITOR_1/b'INPUT/GPIO/CHANGE'
'''
class Base_Manager(object):
   def __init__(self):
       self.topic_dispatch_table[b"REBOOT"] = self.handle_reboot
       self.topic_dispatch_table[b"HEART_BEAT"] = self.handle_presence
 
   def handle_presence(self,data):     
      #print("presence",data)
      self.ds_handlers["MQTT_CONTACT_LOG"].hset(data["device_id"],data) 
       
   def handle_reboot(self,data):
      #print("reboot",data)
      if self.ds_handlers["MQTT_REBOOT_LOG"].hexists(data["device_id"]):
         temp = self.ds_handlers["MQTT_REBOOT_LOG"].hget(data["device_id"])
         delta_t = time.time() - temp["timestamp"]
         data["delta_t"] = delta_t
      else:
         data["delta_t"] = 0.
         
      self.ds_handlers["MQTT_REBOOT_LOG"].hset(data["device_id"],data)

   def process_message(self,data):
       if data[b"TOPIC"] in self.topic_dispatch_table:
          self.topic_dispatch_table[data[b"TOPIC"]](data)
       else:
         key = data["device_id"] +"/"+str(data[b"TOPIC"])
         print("unrecognized command",key)
         print(self.topic_dispatch_table.keys())
         #self.ds_handlers["MQTT_UNRECOGNIZEvD_COMMANDS"].hset(key,data)
         
         
         
class Security_Monitor(Base_Manager):
   def __init__(self,ds_handlers):
      self.topic_dispatch_table = {}
      self.ds_handlers = ds_handlers
      Base_Manager.__init__(self)
      self.topic_dispatch_table[b'INPUT/GPIO/CHANGE'] = self.gpio_change
      
   def gpio_change(self,data):
        results = {}
        if data[b"PIN"] == 5:
            results["topic"] = "SECURITY_INPUT"
            results["device"] = "RADAR_SENSOR"        
            results["level"] = data[b"INPUT"]
        if data[b"PIN"] == 17:
            results["topic"] = "SECURITY_INPUT"
            results["device"] = "PIR_SENSOR"        
            results["level"] = data[b"INPUT"]
        if data[b"PIN"] == 23:
            results["topic"] = "SIGNALING_INPUT"
            results["device"] = "BUTTON_1"        
            results["level"] = data[b"INPUT"]
        if data[b"PIN"] == 23:
            results["topic"] = "SIGNALING_INPUT"
            results["device"] = "BUTTON_2"        
            results["level"] = data[b"INPUT"]
        results["timestamp"] = time.time()
        results["device_id"] = data["device_id"]
        print(results)
        #self.ds_handlers["MQTT_INPUT_QUEUE"].push(results)              
   
   
class Current_Monitor(Base_Manager):
   def __init__(self,ds_handlers):
      self.topic_dispatch_table = {}
      self.ds_handlers = ds_handlers
      Base_Manager.__init__(self)
      self.topic_dispatch_table[b'INPUT/AD1/VALUE'] = self.manage_device_currents
      self.topic_dispatch_table[b"OUTPUT/MQTT_CURRENT/EQUIPMENT_RELAY_TRIP/RESPONSE"]  = self.equipment_relay_trip
      self.topic_dispatch_table[b"OUTPUT/MQTT_CURRENT/IRRIGATION_RELAY_TRIP/RESPONSE"] = self.irrigation_current_trip
      self.topic_dispatch_table[b"INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS/REPONSE"] = self.get_limit_current
      self.topic_dispatch_table[b"INPUT/MQTT_CURRENT/MAX_CURRENTS/RESPONSE"]   = self.get_max_currents
      self.topic_dispatch_table[b"INPUT/MQTT_CURRENT/CURRENTS/RESPONSE"]      = self.get_currents
      self.topic_dispatch_table[b"OUTPUT/MQTT_CURRENT/RELAY_STATE/RESPONSE"]  = self.relay_state
      
   def equipment_relay_trip(self,data):
          print("data",data)
          
          
   def irrigation_current_trip(self,data):
          print("data",data)
          
          
   def get_limit_current(self,data):
          print("data",data)
          
   def get_max_currents(self,data):
          print("data",data)
          
   def get_currents(self,data):
          print("data",data)
          
   def relay_state(self,data):
          print("data",data)
      
      
   def manage_device_currents(self,data):
              
       temp = data[b'MEASUREMENTS']
       results = {}
       for i in temp: 
          if i[b'CHANNEL'] == 0:       
             results["EQUIPMENT"] ={"DC":i[ b'DC'],"SD":i[ b'SD']}
          if i[b'CHANNEL'] == 3:       
             results["IRRIGATION_VALVES"] ={"DC":i[ b'DC'],"SD":i[ b'SD']}
       results["timestamp"] = time.time()
       results["topic"] = "SLAVE_CURRENTS"
       results["device_id"] = data["device_id"]
       #print(results)
       #self.ds_handlers["MQTT_INPUT_QUEUE"].push(results)              
      
class Well_Monitor(Base_Manager):
   def __init__(self,ds_handlers):
      self.topic_dispatch_table = {}
      self.ds_handlers = ds_handlers
      Base_Manager.__init__(self)
      self.topic_dispatch_table[b'INPUT/AD1/VALUE'] = self.manage_well_data
      self.topic_dispatch_table[b'INPUT/PULSE_COUNT/VALUE'] = self.manage_well_flow_meters
      print(self.topic_dispatch_table.keys())
      
   def manage_well_data(self,data):
       
       temp = data[b'MEASUREMENTS']
       results = {}
       for i in temp: 
          if i[b'CHANNEL'] == 6:
             dc = i[ b'DC']
             sd = i[ b'SD']
             dc = dc-.004*150
             if dc < 0:
               dc = 0
             dc_amps = dc/(.016*150)*50
             sd_amps = sd/(.016*150)*50
             results["INPUT"] ={"DC":dc_amps,"SD":sd_amps}             
          
          if i[b'CHANNEL'] == 7:
             dc = i[ b'DC']
             sd = i[ b'SD']
             dc = dc-.004*150
             if dc < 0:
               dc = 0
             dc_amps = dc/(.016*150)*20
             sd_amps = sd/(.016*150)*20
             results["OUTPUT"] ={"DC":dc_amps,"SD":sd_amps}
             
       results["timestamp"] = time.time()
       results["topic"] = "PUMP_CURRENTS"
       results["device_id"] = data["device_id"]
       #print(results)
       #self.ds_handlers["MQTT_INPUT_QUEUE"].push(results)         

   def manage_well_flow_meters(self,data): 
       temp = data[b"DATA"]
       results = {}
       for i in temp:
          if i[b"GPIO_PIN"] == 5:
            results["MAIN_FLOW_METER"] = i[b"COUNTS"]*4./2./60./2.0  # 2HZ per GPM
          if i[b"GPIO_PIN"] == 18:
            results["CLEANING_OUTLET"] =  i[b"COUNTS"]*4./300./3.78541  # 330 ticks equal 1 liter           
       
       results["timestamp"] = time.time()
       results["topic"] = "FLOW_METERS"
       results["device_id"] = data["device_id"]
       #print(results)
       #self.ds_handlers["MQTT_INPUT_QUEUE"].push(results)
       
       
class MQTT_Monitor(object):

   def __init__(self,mqtt_server_data, mqtt_devices, package,site_data):
        
        self.mqtt_server_data  = mqtt_server_data
        self.mqtt_devices = mqtt_devices
        self.package  = package
        self.site_data = site_data
       
        self.generate_data_handlers()
        self.mqtt_handlers = {}
        self.mqtt_handlers["SECURITY_MONITOR"] = Security_Monitor(self.ds_handlers)
        self.mqtt_handlers["CURRENT_MONITOR"]     = Current_Monitor(self.ds_handlers)
        self.mqtt_handlers["WELL_MONITOR"]  = Well_Monitor(self.ds_handlers)

        self.build_device_table()
        self.validate_handlers()
        self.register_subscriptions()
        self.process_messages()


      
   def generate_data_handlers(self):
        self.handlers = {}
        data_structures = self.package["data_structures"]
        generate_handlers = Generate_Handlers(self.package,self.site_data)
        self.ds_handlers = {}
        self.ds_handlers["MQTT_INPUT_QUEUE"] = generate_handlers.construct_redis_stream_writer(data_structures["MQTT_INPUT_QUEUE"])
        self.ds_handlers["MQTT_DEVICES"] = generate_handlers.construct_hash(data_structures["MQTT_DEVICES"])
        self.ds_handlers["MQTT_CONTACT_LOG"] = generate_handlers.construct_hash(data_structures["MQTT_CONTACT_LOG"])
        self.ds_handlers["MQTT_UNKNOWN_CONTACTS"] = generate_handlers.construct_hash(data_structures["MQTT_UNKNOWN_CONTACTS"])
        self.ds_handlers["MQTT_REBOOT_LOG"]       = generate_handlers.construct_hash(data_structures["MQTT_REBOOT_LOG"])
        self.ds_handlers["PRESENCE_LOG"] = generate_handlers.construct_hash(data_structures["PRESENCE_LOG"])
        self.ds_handlers["MQTT_UNRECOGNIZED_COMMANDS"] = generate_handlers.construct_hash(data_structures["MQTT_UNRECOGNIZED_COMMANDS"])

   def build_device_table(self):
       self.ds_handlers["MQTT_DEVICES"].delete_all()
       self.ds_handlers["PRESENCE_LOG"].delete_all()
       base_topic = self.mqtt_server_data["BASE_TOPIC"]
       for i,item in self.mqtt_devices.items():   
          
          item["device_topic"] = base_topic+"/"+item["topic"]
         
          self.ds_handlers["MQTT_DEVICES"].hset(item["device_topic"],item)
          self.ds_handlers["PRESENCE_LOG"].hset(item["device_topic"],time.time())
          if self.ds_handlers["MQTT_UNKNOWN_CONTACTS"].hexists(item["device_topic"]) == True:
              print("deleteing contact",item["device_topic"])
              self.ds_handlers["MQTT_UNKNOWN_CONTACTS"].hdelete(item["device_topic"])
 
   def validate_handlers(self):
      for i,item in self.mqtt_devices.items():
        if item["type"] not in self.mqtt_handlers:
           raise ValueError("unknown type",item["type"])

   
   def register_subscriptions(self):
       pass
       
   def process_messages(self):
       self.client = mqtt.Client(client_id="", clean_session=True, userdata=None,  transport="tcp")
       print(self.mqtt_server_data["HOST"],self.mqtt_server_data["PORT"])
       redis_handle_pw = redis.StrictRedis(self.site_data["host"], 
                                           self.site_data["port"], 
                                           db=self.site_data["redis_password_db"], 
                                           decode_responses=True)      
       self.client.username_pw_set("pi", redis_handle_pw.hget("mosquitto_local","pi"))
       self.client.tls_set( cert_reqs=ssl.CERT_NONE )
       self.client.on_connect = self.on_connect
       self.client.on_message = self.on_message
       self.connection_flag = False
       print("connection attempting")
       while self.connection_flag == False:
           try:
                self.client.connect(self.mqtt_server_data["HOST"],self.mqtt_server_data["PORT"], 60)
           except:
                
                time.sleep(5)
           else:
              self.connection_flag = True
       print("connection achieved")
       self.client.loop_forever()
       
   def on_connect(self,client, userdata, flags, rc):
      
       print("Connected with result code "+str(rc),)
       self.client.subscribe(self.mqtt_server_data["BASE_TOPIC"]+"/#")


   def on_message(self, client, userdata, msg):
       try:
          topic = msg.topic
          data = msgpack.unpackb(msg.payload)
          process_topic = topic.split("/")
          search_key = "/".join(process_topic[:3])
          if self.ds_handlers["MQTT_DEVICES" ].hexists(search_key) == True:
             temp = self.ds_handlers["MQTT_DEVICES"].hget(search_key)
             data["timestamp"] = time.time()
             data["device_id"] = search_key
             self.mqtt_handlers[temp["type"] ].process_message(data)
          else:
            print(search_key_no_match)
            data["timestamp"] = time.time()
            self.ds_handlers["MQTT_UNKNOWN_CONTACTS"].hset(search_key,data)
       except:
         print("data",type(data),data)
         print("topic",topic)         

      
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
     
    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_terminal( query_list, 
                                        relationship =  "MQTT_DEVICE" )
                                        
    mqtt_sets, mqtt_sources = qs.match_list(query_list) 
    mqtt_devices = {}
    for i in mqtt_sources:
       mqtt_devices[i["name"]] = {"name":i["name"], "type":i["type"],"topic":i["topic"] }

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
    MQTT_Monitor(mqtt_server_data = host_data,
                 mqtt_devices = mqtt_devices,
                 package = package,
                 site_data = redis_site)

   

else:
  pass
  


import msgpack
import base64
import redis
import time
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from redis_support_py3.mqtt_to_redis_py3 import MQTT_TO_REDIS_BRIDGE_RETRIEVE
from core_libraries.irrigation_hash_control_py3 import generate_irrigation_control

class MQTT_Log(object):

   def __init__(self,mqtt_server_data, mqtt_devices, package,site_data,irrigation_control,qs):
        
        self.mqtt_server_data  = mqtt_server_data
        self.mqtt_devices = mqtt_devices
        self.site_data = site_data
        self.irrigation_control = irrigation_control
        

        self.mqtt_bridge = MQTT_TO_REDIS_BRIDGE_RETRIEVE(site_data)
        self.construct_presence_key_name()
        self.construct_reboot_key_name()
        self.generate_data_handlers(package,qs)
        

        self.log_data()
        
        
   def construct_presence_key_name(self):
       for i,item in self.mqtt_devices.items():
          self.mqtt_devices[i]["presence_name_space"] = self.mqtt_bridge.construct_name_space(item["heart_beat"])[0]       
       
   def construct_reboot_key_name(self):
       for i,item in self.mqtt_devices.items():
         if "reboot_flag" in item:
          self.mqtt_devices[i]["reboot_name_space"] = self.mqtt_bridge.construct_name_space(item["reboot_key"])[0]   
       print(self.mqtt_devices)
        
   def generate_data_handlers(self,package,qs):
        self.handlers = {}
        data_structures = package["data_structures"]
        generate_handlers = Generate_Handlers(package,qs)
        self.ds_handlers = {}
        self.ds_handlers["MQTT_INPUT_QUEUE"] = generate_handlers.construct_redis_stream_reader(data_structures["MQTT_INPUT_QUEUE"])
        self.ds_handlers["MQTT_PAST_ACTION_QUEUE"] = generate_handlers.construct_redis_stream_writer(data_structures["MQTT_PAST_ACTION_QUEUE"])
        self.ds_handlers["MQTT_SENSOR_QUEUE"] = generate_handlers.construct_redis_stream_writer(data_structures["MQTT_SENSOR_QUEUE"])
        self.ds_handlers["MQTT_CONTACT_LOG"] = generate_handlers.construct_hash(data_structures["MQTT_CONTACT_LOG"])
        self.ds_handlers["MQTT_REBOOT_LOG"] = generate_handlers.construct_hash(data_structures["MQTT_REBOOT_LOG"])
        self.ds_handlers["MQTT_SENSOR_STATUS"] = generate_handlers.construct_hash(data_structures["MQTT_SENSOR_STATUS"])
        
       


   def log_data(self):
       
       self.base_time = time.time()
       self.check_heartbeat()
       self.check_reboot()
       
       while 1:
           self.interval_time = time.time()
           while (time.time() -self.base_time)< 60:
               time.sleep(15)
               self.update_mqtt_ad_packets()
               self.update_pulse_count_packets()
               self.update_irrigation_relay_trip()
               
               
              
           self.check_heartbeat()
           self.check_reboot()
           self.average_irrigation_data()
           self.base_time = time.time() 


   def self.update_mqtt_ad_packets(self):
[INPUT:][AD1:][VALUE:][RESPONSE:]       
   
       
   def update_pulse_count_packets(self):
       "[REMOTES:][WELL_MONITOR_1:][INPUT:][PULSE_COUNT:][VALUE:]" 
        key = self.device_id+"/"+data["topic"]
       key_1 = key+":MAIN_FLOW_METER"
       if key_1 not in composite_record:
          composite_record[key_1] = []
       composite_record[key_1].append(data["MAIN_FLOW_METER"])
       self.irrigation_control.hset("MAIN_FLOW_METER",data["MAIN_FLOW_METER"])
       key_1 = key+":CLEANING_OUTLET"
       if key_1 not in composite_record:
          composite_record[key_1] = []
       composite_record[key_1].append(data["CLEANING_OUTLET"])
       self.irrigation_control.hset("CLEANING_FLOW_METER",data["CLEANING_OUTLET"])      
   def update_irrigation_relay_trip(self):
       pass



   def update_contact(self,name,key,status):
       old_data = self.ds_handlers["MQTT_CONTACT_LOG"].hget(name)
       data = {}
       data["time"] = time.time()
       data["status"] = status
       data["name"] = name
       data["device_id"] = name # redundant with name
       
       update_flag = False
       if old_data == None:
          update_flag = False # already made update
          self.ds_handlers["MQTT_PAST_ACTION_QUEUE"].push({"action":"Device_Change","device_id":name,"status":status})
          self.ds_handlers["MQTT_CONTACT_LOG"].hset(name,data)  
          return
       if old_data["status"] != status:
           update_flag = True
           print("device change")
           self.ds_handlers["MQTT_PAST_ACTION_QUEUE"].push({"action":"Device_Change","device_id":name,"status":status})   
       if status == True:
          update_flag = True
       if update_flag == True:
          self.ds_handlers["MQTT_CONTACT_LOG"].hset(name,data)  

   def check_heartbeat(self):
      
      for i,items in self.mqtt_devices.items():
          name = items["name"]
          key = items["presence_name_space"]
          if self.mqtt_bridge.stream_exists(key) == False:
            print("stream does not exist")
            self.update_contact(name,key,False)
          else:
            data = self.mqtt_bridge.xrevrange_namespace(key, "+", "-" , count=1)
            print(type(data[0]),data)
            timestamp = data[0]["timestamp"]
            print(i,time.time()-timestamp)
            if items["HEART_BEAT_TIME_OUT"] < time.time()-timestamp:
              print("device not responding")
              self.update_contact(name,key,False)
            else:
              print("device responding")
              self.update_contact(name,key,True)

   def update_reboot(self,name,key,timestamp):
       old_data = self.ds_handlers["MQTT_REBOOT_LOG"].hget(name)
       data = {}
       data["timestamp"] = timestamp
       data["name"] = name
       data["device_id"] = name # redundant with name
       update_flag = False
       if (old_data == None) or (old_data["timestamp"] < timestamp):
           self.ds_handlers["MQTT_REBOOT_LOG"].hset(name,data)  
           self.ds_handlers["MQTT_PAST_ACTION_QUEUE"].push({"action":"Device_Reboot","device_id":name,"status":True})   




      
   def check_reboot(self):
      print("check reboot",self.mqtt_devices)
      for i,items in self.mqtt_devices.items():
          name = items["name"]
          if "reboot_flag" in items:
             key = items["reboot_name_space"] 
             if self.mqtt_bridge.stream_exists(key) == False:
                print("stream does not exist")
                
             else:
                 data = self.mqtt_bridge.xrevrange_namespace(key, "+", "-" , count=1)
                 data = data[0]
                 self.update_reboot(name,key,data["timestamp"])
      

   def average_irrigation_data(self):
       print(time.time()-self.base_time )
       
   
       
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
                             relationship = "MQTT_SERVER" )
                                           
    host_sets, host_sources = qs.match_list(query_list)
    host_data = host_sources[0]
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_terminal( query_list, 
                                        relationship =  "MQTT_DEVICE" )
                                        
    mqtt_sets, mqtt_sources = qs.match_list(query_list) 
    mqtt_devices = {}
    for i in mqtt_sources:
       mqtt_devices[i["name"]] = {"name":i["name"], "type":i["type"],"topic":i["topic"],"HEART_BEAT_TIME_OUT":i["HEART_BEAT_TIME_OUT"],
                                      "reboot_flag":i["REBOOT_FLAG"],"reboot_key":host_data["BASE_TOPIC"]+"/"+i["name"]+"/"+i["REBOOT_KEY"],
                                      "heart_beat":host_data["BASE_TOPIC"]+"/"+i["name"]+"/"+i["HEART_BEAT"] }
   
   

    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"MQTT_DEVICES_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)
    package = package_sources[0]
    redis_handle =  redis.StrictRedis( host = redis_site["host"] , port=redis_site["port"], db=redis_site["redis_io_db"] )
    irrigation_control = generate_irrigation_control(redis_site,qs)
    MQTT_Log(mqtt_server_data = host_data,
                 mqtt_devices = mqtt_devices,
                 package = package,
                 site_data = redis_site,
                 irrigation_control = irrigation_control,
                 qs = qs)

   

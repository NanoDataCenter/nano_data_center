import ssl
import msgpack
import time

import paho.mqtt.client as mqtt
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from core_libraries.irrigation_hash_control_py3 import generate_irrigation_control


class Base_Monitor(object):
   def __init__(self,device_id):
      self.reset_composite_record()
      self.device_id = device_id
      self.check_device_id = "/REMOTES/"+device_id
      self.handlers = {}
      

   def add_handler(self,topic,handler):
      entry = {}
      entry["topic"] = topic
      entry["device_id"] = self.device_id
      entry["msg_handler"] = handler
      self.handlers[topic] = entry
 
            
      
   def reset_composite_record(self):
      self.composite_record = {}


   def log_data(self,data):
      
      
       if data["device_id"] != self.check_device_id:
         
          return
       for key, item in self.handlers.items():
         
         if key == data["topic"]:
          
            item["msg_handler"](self.composite_record,data)


   def summarize_data(self,summarized_values):
      
      for key,item in self.composite_record.items():
        avg = 0
        count = 0
        for i in item:
          avg = avg +float(i)
          count = count +1
        avg = avg/float(count)
        
        summarized_values[key] = avg
     
      
 

class Well_Monitor(Base_Monitor):
   def __init__(self,device_id,irrigation_control):
       self.irrigation_control = irrigation_control
       Base_Monitor.__init__(self,device_id)
       self.add_handler("PUMP_CURRENTS",self.pump_currents)
       self.add_handler("FLOW_METERS",self.flow_meters)
       
   def flow_meters(self, composite_record,data):
       
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

       
   def pump_currents(self,composite_record,data):
       
       key = self.device_id+"/"+data["topic"]
       key_1 = key+":OUTPUT"
       if key_1 not in composite_record:
          composite_record[key_1] = []
       composite_record[key_1].append(data["OUTPUT"]["DC"])
       self.irrigation_control.hset("OUTPUT_PUMP_CURRENT",data["OUTPUT"]["DC"]) 
       key_1 = key+":INPUT"
       if key_1 not in composite_record:
          composite_record[key_1] = []
       composite_record[key_1].append(data["INPUT"]["DC"])
       self.irrigation_control.hset("INPUT_PUMP_CURRENT",data["INPUT"]["DC"]) 
       key_1 = key+":WELL_PRESSURE"
       if key_1 not in composite_record:
          composite_record[key_1] = []
       composite_record[key_1].append(data['WELL_PRESSURE']["DC"])
       
       self.irrigation_control.hset("WELL_PRESSURE",data['WELL_PRESSURE']["DC"]) 
 


class Current_Monitor(Base_Monitor):

   def __init__(self,device_id,irrigation_control):
       self.irrigation_control = irrigation_control
       Base_Monitor.__init__(self,device_id)
       self.add_handler("SLAVE_CURRENTS",self.slave_currents)
       self.add_handler("SLAVE_EQUIPMENT_RELAY_TRIP",self.slave_irrigation_relay_trip)
       self.add_handler("SLAVE_IRRIGATION_RELAY_TRIP",self.slave_equipment_relay_trip)
       self.add_handler("SLAVE_MAX_CURRENT",self.slave_max_current)
       self.add_handler("SLAVE_RELAY_STATE",self.slave_relay_state)
       
   def slave_currents(self,composite_record,data):
       
       key = self.device_id+"/"+data["topic"]
       key_1 = key+":IRRIGATION_VALVES"
       if key_1 not in composite_record :
          composite_record[key_1] =[]
       composite_record[key_1].append(data["IRRIGATION_VALVES"]["DC"])
       self.irrigation_control.hset("IRRIGATION_CURRENT",data["IRRIGATION_VALVES"]["DC"])
       
       key_1 = key+":EQUIPMENT"
       if key_1 not in composite_record:
          composite_record[key_1] = []
       composite_record[key_1].append(data["EQUIPMENT"]["DC"])
       self.irrigation_control.hset("EQUIPMENT_CURRENT",data["EQUIPMENT"]["DC"])
 
   def slave_irrigation_relay_trip(self,composite_record,data):
       results = {}
       results["timestamp"] = time.time()
       
       results["device_id"] = data["device_id"]
       results["status"] = False
       
       results["CURRENT_VALUE"] = data[b"CURRENT_VALUE"]
       results["LIMIT_VALUE"] = data[b"LIMIT_VALUE"]
       self.irrigation_control.hset("SLAVE_IRRIGATION_RELAY_TRIP",results)   

       
   def slave_equipment_relay_trip(self,composite_record,data):
       results = {}
       results["timestamp"] = time.time()
       
       results["device_id"] = data["device_id"]
       results["status"] = False
       results["CURRENT_VALUE"] = data[b"CURRENT_VALUE"]
       results["LIMIT_VALUE"] = data[b"LIMIT_VALUE"]
       self.irrigation_control.hset("SLAVE_EQUIPMENT_RELAY_TRIP",results)  

       
   def slave_max_current(self,composite_record,data):
        results = {}
        #print(data)
        results["timestamp"] = time.time()
        results["topic"] = "SLAVE_MAX_CURRENT"
        results["device_id"] = data["device_id"]       
        results['MAX_EQUIPMENT_CURRENT'] = data["currents"]['MAX_EQUIPMENT_CURRENT']
        results['MAX_IRRIGATION_CURRENT'] = data["currents"]['MAX_IRRIGATION_CURRENT'] 
        #print("results",results)
        self.irrigation_control.hset("SLAVE_MAX_CURRENT",results)     
      
   def slave_relay_state(self,composite_record,data):
          results = {}
          #print(data)
          results["timestamp"] = time.time()
          results["topic"] = "SLAVE_RELAY_STATE"
          results["device_id"] = data["device_id"]        
          results['EQUIPMENT_STATE'] = data["relay_state"]['EQUIPMENT_STATE']
          if results["EQUIPMENT_STATE"] != 0:
             results["EQUIPMENT_STATE"] = True
          else:
             results["EQUIPMENT_STATE"] = False
          results['IRRIGATION_STATE'] = data["relay_state"]['IRRIGATION_STATE']
          if results['IRRIGATION_STATE'] != 0:
             results['IRRIGATION_STATE'] = True
          else:
             results['IRRIGATION_STATE'] = False
          self.irrigation_control.hset("SLAVE_RELAY_STATE",results)
          #print("results",results)          
 


class MQTT_Log(object):

   def __init__(self,mqtt_server_data, mqtt_devices, package,site_data,irrigation_control,qs):
        
        self.mqtt_server_data  = mqtt_server_data
        self.mqtt_devices = mqtt_devices
        self.package  = package
        self.site_data = site_data
        self.irrigation_control = irrigation_control
        self.redis_handle = redis_handle
        self.generate_data_handlers(qs)
        self.mqtt_handlers = {}
        self.mqtt_handlers["WELL_MONITOR_1"] = Well_Monitor("WELL_MONITOR_1",irrigation_control)
        self.mqtt_handlers['CURRENT_MONITOR_1'] = Current_Monitor('CURRENT_MONITOR_1',irrigation_control)
        #self.test()
     
        self.log_data()

   def test(self):  # test non periodic functions
       data = {}
       data["device_id"] = "test"
       data["status"]  = True
       data[b"CURRENT_VALUE"] = 0
       data[b"LIMIT_VALUE"] = 0
       self.mqtt_handlers['CURRENT_MONITOR_1'].slave_irrigation_relay_trip([],data)
       print(self.irrigation_control.hget("SLAVE_IRRIGATION_RELAY_TRIP"))   
       
       data = {}
       data["device_id"] = "test"
       data["status"]  = True
       data[b"CURRENT_VALUE"] = 0
       data[b"LIMIT_VALUE"] = 0
       self.mqtt_handlers['CURRENT_MONITOR_1'].slave_equipment_relay_trip([],data)
       print(self.irrigation_control.hget("SLAVE_EQUIPMENT_RELAY_TRIP"))   

       results = {}
       results["timestamp"] = time.time()
       results["topic"] = "SLAVE_MAX_CURRENT"
       results["device_id"] = ""       
       results[b'MAX_EQUIPMENT_CURRENT'] = 0
       results[b'MAX_IRRIGATION_CURRENT'] = 0 
       self.mqtt_handlers['CURRENT_MONITOR_1'].slave_max_current([],results)
       print(self.irrigation_control.hget("SLAVE_MAX_CURRENT"))     

       results = {}
       results["timestamp"] = time.time()
       results["topic"] = "SLAVE_RELAY_STATE"
       results["device_id"] = ""        
       results[b'EQUIPMENT_STATE'] = 1
       results[b'IRRIGATION_STATE'] = True
       self.mqtt_handlers['CURRENT_MONITOR_1'].slave_relay_state([],results)
       print(self.irrigation_control.hget("SLAVE_RELAY_STATE")) 

   
   def process_messages(self,data):
        data = data["data"]
        for key,class_inst in self.mqtt_handlers.items():
            class_inst.log_data(data)
        
 
   def summarize_data(self):   
       summarized_values = {}
       for key,class_inst in self.mqtt_handlers.items():
           class_inst.summarize_data(summarized_values)  
          
       return summarized_values
   

   def reset_composite_record(self):
       for key,class_inst in self.mqtt_handlers.items():
           class_inst.reset_composite_record()
     


   def log_data(self):
       ref_time = time.time()
       base_time = ref_time
       while 1:
           while (time.time() -base_time)< 60:
               time.sleep(5)  # sleep 1 minute
               
               start_time = time.time()
               results = self.ds_handlers["MQTT_INPUT_QUEUE"].revrange(start_time, ref_time , count=1000) 
          
               for i in results:
                  self.process_messages(i)
                  
               ref_time = start_time
           base_time = ref_time   
           summarized_data = self.summarize_data()
           self.reset_composite_record()
           
           self.ds_handlers["MQTT_SENSOR_QUEUE"].push({"timestamp":time.time(),"data":summarized_data })
           for key,data in summarized_data.items():
              self.ds_handlers["MQTT_SENSOR_STATUS"].hset(key,data)
           self.check_slave_devices()  
             
             
   def check_slave_devices(self):
        keys = self.ds_handlers["MQTT_CONTACT_LOG"].hkeys()
        reference_time = time.time()
        for i in keys:
            
           x = self.ds_handlers["MQTT_CONTACT_LOG"].hget(i)
           
           old_status = x["status"]
           diff = reference_time - float(x["time"])
          
           if diff > 60*2:
              x["status"] = False
           else:
              x["status"] = True
         
           self.ds_handlers["MQTT_CONTACT_LOG"].hset(i,x)
           if old_status != x["status"] :
              
              self.ds_handlers["MQTT_PAST_ACTION_QUEUE"].push({"action":"Device_Change","device_id":x[ 'device_id'],"status":x["status"]})          
             
   def generate_data_handlers(self,qs):
        self.handlers = {}
        data_structures = self.package["data_structures"]
        generate_handlers = Generate_Handlers(self.package,qs)
        self.ds_handlers = {}
        self.ds_handlers["MQTT_INPUT_QUEUE"] = generate_handlers.construct_redis_stream_reader(data_structures["MQTT_INPUT_QUEUE"])
        self.ds_handlers["MQTT_PAST_ACTION_QUEUE"] = generate_handlers.construct_redis_stream_writer(data_structures["MQTT_PAST_ACTION_QUEUE"])
        self.ds_handlers["MQTT_SENSOR_QUEUE"] = generate_handlers.construct_redis_stream_writer(data_structures["MQTT_SENSOR_QUEUE"])
        self.ds_handlers["MQTT_CONTACT_LOG"] = generate_handlers.construct_hash(data_structures["MQTT_CONTACT_LOG"])
        self.ds_handlers["MQTT_SENSOR_STATUS"] = generate_handlers.construct_hash(data_structures["MQTT_SENSOR_STATUS"])
        

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
    redis_handle =  redis.StrictRedis( host = redis_site["host"] , port=redis_site["port"], db=redis_site["redis_io_db"] )
    irrigation_control = generate_irrigation_control(redis_site,qs)
    MQTT_Log(mqtt_server_data = host_data,
                 mqtt_devices = mqtt_devices,
                 package = package,
                 site_data = redis_site,
                 irrigation_control = irrigation_control,
                 qs = qs)

   

else:
  pass
  

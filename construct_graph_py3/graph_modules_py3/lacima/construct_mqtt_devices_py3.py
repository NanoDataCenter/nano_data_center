import json


class Construct_Lacima_MQTT_Devices(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      
      bc.add_header_node("MQTT_DEVICES")
      
      cd.construct_package("MQTT_DEVICES_DATA")
      cd.add_redis_stream("MQTT_INPUT_QUEUE",50000)
      cd.add_redis_stream("MQTT_SENSOR_QUEUE",10000)
      cd.add_redis_stream("MQTT_PAST_ACTION_QUEUE",300)
      cd.add_hash("MQTT_SENSOR_STATUS")
      cd.add_hash("MQTT_DEVICES")
      cd.add_hash("MQTT_SUBSCRIPTIONS")
      cd.add_hash("MQTT_CONTACT_LOG")
      cd.add_hash("MQTT_UNKNOWN_DEVICES")
      cd.add_hash("MQTT_UNKNOWN_SUBSCRIPTIONS")
      cd.add_hash("MQTT_REBOOT_LOG")
      
      cd.add_job_queue("MQTT_PUBLISH_QUEUE",depth= 50,forward = False)
      cd.close_package_contruction()
      properties = {}
      properties["HOST"] = "farm_control.fios-router.home"
      properties["PORT"] = 8883
      properties["BASE_TOPIC"] = "/REMOTES"
      self.bc.add_info_node( "MQTT_SERVER","MQTT_SERVER",properties=properties )
      #self.add_security_monitor("GARAGE_MONITOR_1")
      #self.add_current_monitor("CURRENT_MONITOR_1")
      self.add_well_monitor("WELL_MONITOR_1")
      self.irrigation_hash_fields()
      self.add_minute_average_fields()
      bc.end_header_node("MQTT_DEVICES")

   def add_minute_average_fields(self):
       properties = {}
       properties["data"] = {}
       properties["data"]["WELL_PRESSURE"] = ["WELL_MONITOR_1",'INPUT/AD1/VALUE/RESPONSE', "WELL_PRESSURE"    ]
       #properties["data"]["EQUIPMENT_CURRENT"] =["CURRENT_MONITOR_1",'INPUT/AD1/VALUE/RESPONSE',"EQUIPMENT_CURRENT"]
       #properties["data"]["IRRIGATION_CURRENT"] = [ "CURRENT_MONITOR_1", 'INPUT/AD1/VALUE/RESPONSE', "IRRIGATION_CURRENT"]
       properties["data"]["MAIN_FLOW_METER"] = ["WELL_MONITOR_1",  'INPUT/PULSE_COUNT/VALUE',  "MAIN_FLOW_METER" ]
       properties["data"]["CLEANING_FLOW_METER"] = ["WELL_MONITOR_1",'INPUT/PULSE_COUNT/VALUE' , "CLEANING_OUTLET"   ]
       properties["data"]["INPUT_PUMP_CURRENT"] = ["WELL_MONITOR_1",'INPUT/AD1/VALUE/RESPONSE' ,"INPUT_PUMP_CURRENT"    ]
       properties["data"]["OUTPUT_PUMP_CURRENT"] = ["WELL_MONITOR_1", 'INPUT/AD1/VALUE/RESPONSE', "OUTPUT_PUMP_CURRENT"   ]

       self.bc.add_info_node( "SENSOR_MINUTE_FIELDS","SENSOR_MINUTE_FIELDS",properties=properties )


   def irrigation_hash_fields(self):
       properties = {}
       properties["data"] = {}
       properties["data"]["WELL_PRESSURE"] = ["WELL_MONITOR_1",'INPUT/AD1/VALUE/RESPONSE', "WELL_PRESSURE"    ]
       #properties["data"]["EQUIPMENT_CURRENT"] =["CURRENT_MONITOR_1" ,'INPUT/AD1/VALUE/RESPONSE',"EQUIPMENT_CURRENT"]
       #properties["data"]["IRRIGATION_CURRENT"] = [ "CURRENT_MONITOR_1", 'INPUT/AD1/VALUE/RESPONSE', "IRRIGATION_CURRENT"]
       properties["data"]["MAIN_FLOW_METER"] = ["WELL_MONITOR_1",  'INPUT/PULSE_COUNT/VALUE',  "MAIN_FLOW_METER" ]
       properties["data"]["CLEANING_FLOW_METER"] = ["WELL_MONITOR_1",'INPUT/PULSE_COUNT/VALUE' , "CLEANING_OUTLET"   ]
       properties["data"]["INPUT_PUMP_CURRENT"] = ["WELL_MONITOR_1",'INPUT/AD1/VALUE/RESPONSE' ,"INPUT_PUMP_CURRENT"    ]
       properties["data"]["OUTPUT_PUMP_CURRENT"] = ["WELL_MONITOR_1", 'INPUT/AD1/VALUE/RESPONSE', "OUTPUT_PUMP_CURRENT"   ]
       
       properties["data"]["SLAVE_RELAY_STATE"] = ["CURRENT_MONITOR_1" ,"OUTPUT/MQTT_CURRENT/RELAY_STATE/RESPONSE",None]
       properties["data"]["SLAVE_MAX_CURRENT"] = ["CURRENT_MONITOR_1" ,"INPUT/MQTT_CURRENT/MAX_CURRENTS/RESPONSE",None]
       properties["data"]["INSTANT_CURRENT"]  = ["CURRENT_MONITOR_1" ,"INPUT/MQTT_CURRENT/CURRENTS/RESPONSE",None]
       self.bc.add_info_node( "IRRIGATION_HASH_FIELDS","IRRIGATION_HASH_FIELDS",properties=properties )       
     

 


     

       
   def add_well_monitor(self,mqtt_tag):
       properties = {}
       properties["type"] = "WELL_MONITOR"
       properties["HEART_BEAT"] = "HEART_BEAT"
       properties["HEART_BEAT_TIME_OUT"] = 120
       properties["REBOOT_FLAG"] = True
       properties["REBOOT_KEY"] = "REBOOT"
       properties["topic"] = mqtt_tag
       properties["null_commands"] = {}
       properties["subscriptions"] = {}
       properties["subscriptions"]["REBOOT"] = True
       properties["subscriptions"]["HEART_BEAT"] = True
 
       properties["subscriptions"]['INPUT/AD1/VALUE/RESPONSE'] = {"type":"analog_input","main_field":'MEASUREMENTS' ,"fields":
          [  {  "name":"WELL_PRESSURE","type":"pressure_gauge","reduction":2,"range":100,"channel_field":'CHANNEL',"channel_value":0},
             { "name":"INPUT_PUMP_CURRENT","type":"rms_current_transformer","range":50,"channel_field":'CHANNEL',"channel_value":6,"resistor":150},
             { "name":"OUTPUT_PUMP_CURRENT","type":"rms_current_transformer","range":20,"channel_field":'CHANNEL',"channel_value":7,"resistor":150} ]}
             
       properties["subscriptions"]['INPUT/PULSE_COUNT/VALUE'] = {"type":"pulse_flow","main_field":"DATA",  "fields": [
          {"name":"MAIN_FLOW_METER", "GPIO_PIN":5,"data_field":"COUNTS","conversion":4./2./60./2.0 },
          {"name":"CLEANING_OUTLET", "GPIO_PIN":18,"data_field":"COUNTS","conversion":4./300./3.78541 }
          ]}

       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
   '''    
   def add_current_monitor(self,mqtt_tag):
       properties = {}
       properties["type"] = "CURRENT_MONITOR"
       properties["topic"] = mqtt_tag
       properties["HEART_BEAT"] = "HEART_BEAT"
       properties["HEART_BEAT_TIME_OUT"] = 120
       properties["REBOOT_FLAG"] = True
       properties["REBOOT_KEY"] = "REBOOT"
       properties["null_commands"] = {}
             
       properties["null_commands"]["INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS"] = True
       properties["null_commands"]["INPUT/MQTT_CURRENT/GET_MAX_CURRENTS"] = True
       properties["null_commands"]["INPUT/MQTT_CURRENT/READ_CURRENT"] = True
       properties["null_commands"]["OUTPUT/MQTT_CURRENT/READ_RELAY_STATES"] = True
       properties["null_commands"]["OUTPUT/MQTT_CURRENT/CLEAR_MAX_CURRENTS"] = True
       properties["null_commands"]["OUTPUT/MQTT_CURRENT/ENABLE_EQUIPMENT_RELAY"] = True
       properties["null_commands"]["OUTPUT/MQTT_CURRENT/ENABLE_IRRIGATION_RELAY"] = True
       properties["null_commands"]["OUTPUT/MQTT_CURRENT/DISABLE_EQUIPMENT_RELAY"] = True
       properties["null_commands"]["OUTPUT/MQTT_CURRENT/DISABLE_IRRIGATION_RELAY"] = True

       properties["subscriptions"] = {}
       properties["subscriptions"]["REBOOT"] = True
       properties["subscriptions"]["HEART_BEAT"] = True
       properties["subscriptions"]['INPUT/AD1/VALUE/RESPONSE'] = {"type":"analog_input","main_field":'MEASUREMENTS' ,"fields":[
         {"name":"EQUIPMENT_CURRENT","type":"analog","channel_field":'CHANNEL',"channel_value":0},
         {"name":"IRRIGATION_CURRENT","type":"analog","channel_field":'CHANNEL',"channel_value":3}]}
          

 
       properties["subscriptions"]["OUTPUT/MQTT_CURRENT/EQUIPMENT_RELAY_TRIP/RESPONSE"] = True

       properties["subscriptions"]["OUTPUT/MQTT_CURRENT/IRRIGATION_RELAY_TRIP/RESPONSE"] = True
 
       properties["subscriptions"]["INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS/REPONSE"] = True
          
       properties["subscriptions"]["INPUT/MQTT_CURRENT/MAX_CURRENTS/RESPONSE"] = {"type":"flat","main_field":None ,"fields":[
          {"name":'MAX_EQUIPMENT_CURRENT',"field":'MAX_EQUIPMENT_CURRENT'},
          {"name":'MAX_IRRIGATION_CURRENT',"field":'MAX_IRRIGATION_CURRENT'}]}
          
 
    
       properties["subscriptions"]["INPUT/MQTT_CURRENT/CURRENTS/RESPONSE"] = {"type":"flat","main_field":None ,"fields":[
          {"name":'EQUIPMENT_CURRENT',"field":'EQUIPMENT_CURRENT'},
          {"name":'IRRIGATION_CURRENT',"field":'IRRIGATION_CURRENT'}]}
         

       properties["subscriptions"]["OUTPUT/MQTT_CURRENT/RELAY_STATE/RESPONSE"] = {"type":"flat","main_field":None ,"fields":[
          {"name":'EQUIPMENT_STATE',"field":'EQUIPMENT_STATE'},
          {"name":'IRRIGATION_STATE',"field":'IRRIGATION_STATE'}]}
          
 
       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
       
   def add_security_monitor(self,mqtt_tag):
       properties = {}
       properties["REBOOT_FLAG"] = True
       properties["REBOOT_KEY"] = "REBOOT"
       properties["type"] = "SECURITY_MONITOR"
       properties["HEART_BEAT"] = "HEART_BEAT"
       properties["HEART_BEAT_TIME_OUT"] = 120
       properties["topic"] = mqtt_tag
       properties["null_commands"] = {}
       properties["subscriptions"] = {}
       properties["subscriptions"]["REBOOT"] = True
       properties["subscriptions"]["HEART_BEAT"] = True
       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
   '''
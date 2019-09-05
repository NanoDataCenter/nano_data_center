import json
import time

class Construct_Irrigation_Scheduling_Control(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      bc.add_header_node("IRRIGIGATION_SCHEDULING_CONTROL")
      
      cd.construct_package("IRRIGIGATION_SCHEDULING_CONTROL_DATA")
      cd.add_hash("IRRIGATION_COMPLETION_DICTIONARY") 
      cd.add_hash("SYSTEM_COMPLETION_DICTIONARY")
      cd.add_hash("IRRIGATION_VALVE_TEST")
      cd.add_hash("IRRIGATION_TIME_HISTORY")
      cd.add_job_queue("IRRIGATION_VALVE_JOB_QUEUE",250)
      cd.add_job_queue("IRRIGATION_JOB_SCHEDULING",100,forward=False)
      cd.add_job_queue("IRRIGATION_PENDING",100)
      cd.add_job_queue("IRRIGATION_CURRENT",1)    
      cd.add_redis_stream("IRRIGATION_PAST_ACTIONS",2000)
      cd.close_package_contruction()
      bc.add_info_node("MQTT_CURRENT_LIMITS","MQTT_CURRENT_LIMITS",properties = {"EQUIPMENT":1.0 ,"IRRIGATION": 1.75} )
      bc.add_info_node("EXCESSIVE_FLOW_LIMITS","EXCESSIVE_FLOW_LIMITS",properties={ "EXCESSIVE_FLOW_VALUE":30,"EXCESSIVE_FLOW_TIME":5 } )
      bc.add_info_node("CLEANING_LIMITS","CLEANING_LIMITS",properties={ "limit":25000 } )
      bc.add_info_node("MASTER_VALVES","MASTER_VALVES",properties={"MASTER_VALVES":[ {"remote":"satellite_1","pins":[43] } ]} )
      bc.add_info_node("CLEANING_VALVES","CLEANING_VALVES",properties= {"CLEANING_VALVES":[ {"remote":"satellite_1","pins":[44] } ]} )
      bc.add_info_node("LOGGING_DEPTH","LOGGING_DEPTH",properties = {"valve_depth":20} )   
      bc.add_info_node("IRRIGATION_LOGGING","IRRIGATION_LOGGING",properties={"log_length": 50,"settling_time":5})
      

      
   
      bc.add_header_node("IRRIGATION_CONTROL_MANAGEMENT")
      cd.construct_package("IRRIGATION_CONTROL_MANAGEMENT")
      fields = {}
      fields["RAIN_FLAG"]   = { "type":"binary","init_value":False }
      fields["ETO_MANAGEMENT"]   = { "type":"binary","init_value":True}
      fields["FLOW_CUT_OFF"]   = { "type":"float","init_value":30 }
      fields["CLEANING_INTERVAL"]   =   { "type":"float","init_value":25000 }
      fields["MASTER_VALVE"]   =  { "type":"binary","init_value":False }
      fields["CLEANING_ACCUMULATION"]   = { "type":"float","init_value":0 }
      fields["MASTER_VALVE_SETUP"]   = { "type":"binary","init_value":False }
      fields["SCHEDULE_NAME"]   = { "type":"string","init_value":"" }
      fields["STEP"]   =        { "type":"float","init_value":0 }
      fields["RUN_TIME"]   =   { "type":"float","init_value":0 }
      fields["ELASPED_TIME"]  = { "type":"float","init_value":0 }
      fields["TIME_STAMP"]  = { "type":"float" ,"init_value":time.time()}
      fields["SUSPEND"]    = { "type":"binary","init_value":False }
      fields["WELL_PRESSURE"] = { "type":"float","init_value":0 }
      fields["EQUIPMENT_CURRENT"] = { "type":"float","init_value":0 }
      fields["IRRIGATION_CURRENT"] = { "type":"float","init_value":0 }
      fields["MAIN_FLOW_METER"] =    { "type":"float","init_value":0 }
      fields["CLEANING_FLOW_METER"] ={ "type": "float","init_value":0 }
      fields["INPUT_PUMP_CURRENT"] = { "type":"float","init_value":0 }
      fields["OUTPUT_PUMP_CURRENT"] = { "type":"float","init_value":0 }

      fields["SLAVE_MAX_CURRENT"] = { "type":"dictionary", "fields":{'MAX_EQUIPMENT_CURRENT':0,'MAX_IRRIGATION_CURRENT':0,"timestamp":time.time()} }
      fields["SLAVE_RELAY_STATE"] = { "type":"dictionary", "fields":{'EQUIPMENT_STATE':True,'IRRIGATION_STATE':True,"timestamp":time.time()} }
      fields["INSTANT_CURRENT"] = { "type":"dictionary","fields":{'EQUIPMENT_CURRENT':0,'IRRIGATION_CURRENT':0,"timestamp":time.time()} }
      cd.add_managed_hash(name = "IRRIGATION_CONTROL",fields= fields)
      cd.close_package_contruction()
    

      bc.end_header_node("IRRIGATION_CONTROL_MANAGEMENT")
      
      bc.add_header_node("IRRIGATION_OBJECTS") 
      # basic startup operations
      self.construct_irrigation_object(bc,"VERIFY_MODBUS_OPERATION")
      self.construct_irrigation_object(bc,"VERIFY_CURRENT_CONTROLLER",  )
      self.construct_irrigation_object(bc,"VERIFY_REQUIRE_MQTT_DEVICES",dependency=["VERIFY_CURRENT_CONTROLLER"],)
           
      # normal irrigation
      self.construct_irrigation_object(bc,"VERIFY_PLC_DEVICES",dependency=["VERIFY_MODBUS_OPERATION"])
       

      self.construct_irrigation_object(bc,"VERIFY_INITIAL_TURN_ON",dependency=["VERIFY_PLC_DEVICES","VERIFY_REQUIRE_MQTT_DEVICES"])
    
      self.construct_irrigation_object(bc,"MONITOR_EXCESSIVE_CURRENT",dependency=["VERIFY_INITIAL_TURN_ON"])
      self.construct_irrigation_object(bc,"MONITOR_EXCESSIVE_FLOW",dependency=["MONITOR_EXCESSIVE_CURRENT"])
      self.construct_irrigation_object(bc,"MONITOR_CLEANING_VALVE",dependency=["MONITOR_EXCESSIVE_FLOW"])
      self.construct_irrigation_object(bc,"MONITOR_IRRIGATION_VALVE",dependency=["MONITOR_CLEANING_VALVE"])
      self.construct_irrigation_object(bc,"MONITOR_IRRIGATION_STATISTICS",dependency=["MONITOR_IRRIGATION_VALVE"])
      self.construct_irrigation_object(bc,"MONITOR_IRRIGATION_OPERATION",dependency=["MONITOR_IRRIGATION_STATISTICS"],)
      # check off
      self.construct_irrigation_object(bc,"MONITOR_CHECK_OFF",dependency=["VERIFY_REQUIRE_MQTT_DEVICES","VERIFY_MODBUS_OPERATION"])
      # clean filter
      self.construct_irrigation_object(bc,"MONITOR_CLEAN_FILTER",dependency=["VERIFY_REQUIRE_MQTT_DEVICES","VERIFY_MODBUS_OPERATION"])
      # valve resistance
      self.construct_irrigation_object(bc,"VERIFY_ALL_PLC_DEVICES",dependency=["VERIFY_MODBUS_OPERATION"])
      self.construct_irrigation_object(bc,"MONITOR_VALVE_RESISTANCE",dependency=["VERIFY_REQUIRE_MQTT_DEVICES","VERIFY_ALL_PLC_DEVICES"])
      bc.end_header_node("IRRIGATION_OBJECTS")
      
      
      bc.add_header_node("IRRIGATION_MODES") 
      self.contruct_mode(bc,"IRRIGATION",objects = ["MONITOR_IRRIGATION_OPERATION"])
      self.contruct_mode(bc,"CLEANING",objects = ["MONITOR_CLEAN_FILTER"])
      self.contruct_mode(bc,"CHECK_OFF",objects = ["MONITOR_CHECK_OFF"])
      self.contruct_mode(bc,"VALVE_RESISTANCE",objects = ["MONITOR_VALVE_RESISTANCE"])
      bc.end_header_node("IRRIGATION_MODES")

 
      bc.end_header_node("IRRIGIGATION_SCHEDULING_CONTROL")
     



   def construct_irrigation_object(self,bc,name,dependency=[]):
      properties = {}
      properties["name"] = name
     
      properties["dependency"] = dependency
      bc.add_info_node("IRRIGATION_OBJECT_ELEMENTS",name,properties=properties)   
   
   def contruct_mode(self,bc,name,objects):
      properties = {}
      properties["name"] = name
      properties["objects"] = objects

      bc.add_info_node("IRRIGATION_MODE_ELEMENT",name,properties=properties)   
      

       
       

      
      

      

      
      

      

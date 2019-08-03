import json


class Construct_MQTT_Devices(object):

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
      self.add_security_monitor("GARAGE_MONITOR_1")
      self.add_current_monitor("CURRENT_MONITOR_1")
      self.add_well_monitor("WELL_MONITOR_1")

      bc.end_header_node("MQTT_DEVICES")

   def add_security_monitor(self,mqtt_tag):
       properties = {}
       properties["type"] = "SECURITY_MONITOR"
       properties["topic"] = mqtt_tag
       properties["null_commands"] = {}
       properties["subscriptions"] = {}
       properties["subscriptions"]["REBOOT"] = True
       properties["subscriptions"]["HEART_BEAT"] = True
       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
       
   def add_current_monitor(self,mqtt_tag):
       properties = {}
       properties["type"] = "CURRENT_MONITOR"
       properties["topic"] = mqtt_tag
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
       properties["subscriptions"]['INPUT/AD1/VALUE/RESPONSE'] = True
       properties["subscriptions"]["OUTPUT/MQTT_CURRENT/EQUIPMENT_RELAY_TRIP/RESPONSE"] = True
       properties["subscriptions"]["OUTPUT/MQTT_CURRENT/IRRIGATION_RELAY_TRIP/RESPONSE"] = True
       properties["subscriptions"]["INPUT/MQTT_CURRENT/GET_LIMIT_CURRENTS/REPONSE"] = True
       properties["subscriptions"]["INPUT/MQTT_CURRENT/MAX_CURRENTS/RESPONSE"] = True
       properties["subscriptions"]["INPUT/MQTT_CURRENT/CURRENTS/RESPONSE"] = True
       properties["subscriptions"]["OUTPUT/MQTT_CURRENT/RELAY_STATE/RESPONSE"] = True

       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
       
   def add_well_monitor(self,mqtt_tag):
       properties = {}
       properties["type"] = "WELL_MONITOR"
       properties["topic"] = mqtt_tag
       properties["null_commands"] = {}
       properties["subscriptions"] = {}
       properties["subscriptions"]["REBOOT"] = True
       properties["subscriptions"]["HEART_BEAT"] = True
 
       properties["subscriptions"]['INPUT/AD1/VALUE/RESPONSE'] = True
       properties["subscriptions"]['INPUT/PULSE_COUNT/VALUE'] = True

       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
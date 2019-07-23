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
       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
       
   def add_current_monitor(self,mqtt_tag):
       properties = {}
       properties["type"] = "CURRENT_MONITOR"
       properties["topic"] = mqtt_tag
       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
       
   def add_well_monitor(self,mqtt_tag):
       properties = {}
       properties["type"] = "WELL_MONITOR"
       properties["topic"] = mqtt_tag
       self.bc.add_info_node( "MQTT_DEVICE",mqtt_tag,properties=properties )
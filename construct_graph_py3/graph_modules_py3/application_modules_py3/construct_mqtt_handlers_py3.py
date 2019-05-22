class Construct_MQTT_HANDLERS(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      bc.add_header_node("MQTT_HANDLERS")
      cd.construct_package("MQTT_HANDLERS")
      cd.add_hash("PRESENCE_STATUS")
      cd.add_hash("POWER_SUPPLY_STATUS")
      cd.add_hash("WELL_MONITOR")
      cd.add_hash("GARAGE_MONITOR")
      cd.add_stream("PRESENCE_STATUS")
      cd.add_stream("POWER_SUPPLY_STATUS")
      cd.add_stream("WELL_MONITOR")
      cd.add_stream("GARAGE_MONITOR")
      cd.close_package_contruction()
      
      self.add_status_panel("/REMOTES/GARAGE_MONITOR_1")
      self.add_well_monitor("/REMOTES/WELL_MONITOR_1")
      self.add_power_supply_monitor("/REMOTES/CURRENT_MONITOR_1")
      
      bc.end_header_node("MQTT_HANDLERS")


   def add_status_panel(self,base_topic):
       properties = {"base_topic":base_topic,"type":"STATION_PANEL"}
       self.bc.add_info_node( "STATION_PANNEL",base_topic,properties=properties) 
       
   def add_well_monitor(self,base_topic):
       properties = {"base_topic":base_topic,"type":"WELL_MONITOR"}
       self.bc.add_info_node( "WELL_MONITOR",base_topic,properties=properties) 
        
   def add_power_supply_monitor(self,base_topic):
       properties = {"base_topic":base_topic,"type":"POWER_SUPPLY"}
       self.bc.add_info_node( "POWER_SUPPLY",base_topic,properties=properties) 
        
     

       

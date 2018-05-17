
import json

class Construct_Irrigation_Data_Acquisiton(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      bc.add_header_note("IRRIGATION_DATA_ACQUISTION")
      cd.construct_package("IRRIGATION_DATA")
      cd.add_stream("ETO_HISTORY",360)
      cd.add_stream("RAIN_HISTORY",360)
      cd.close_package_contruction()
      self.add_master_valves()
      self.add_current_measurement()
      bc.end_header_node("IRRIGATION_SUPPORT")

 


  cf.add_header_node("DATA_STORE",properties={"ip":"192.168.1.84","port":6379},json_flag = True)

  

   cf.add_header_node( "DATA_ACQUISITION")


 
   cf.add_header_node( "MINUTE_ACQUISITION",properties= {"measurement":"MINUTE_ACQUISITION","length":5760, "routing_key":"MINUTE_ACQUISITION" }  )



   properties = {}
   properties["units"] = "mAmps"
   properties["modbus_remote"] = "satellite_1"
   properties["m_tag"]          = "measure_analog"
   properties["parameters"]     = [ "DF1",1.0]
   properties["exec_tag"  ]     = ["transfer_controller_current"]
   
   cf.add_info_node( "MINUTE_ELEMENT","CONTROLLER_CURRENT",properties=properties, json_flag=True)


   properties = {}
   properties["units"] = "mAmps"
   properties["modbus_remote"] = "satellite_1"
   properties["m_tag"]          = "measure_analog"
   properties["parameters"]     = ["DF2",1.0]
   properties["exec_tag"]       = ["transfer_irrigation_current"]
   cf.add_info_node( "MINUTE_ELEMENT","IRRIGATION_VALVE_CURRENT",properties=properties, json_flag=True)

   properties = {}
   properties["units"]         = "GPM"
   properties["modbus_remote"] = "satellite_1"
   properties["parameters"]   =  {"latch_bit":"C201",
                                   "read_register":"DS301",  "conversion_factor":0.0224145939 }   
   properties["m_tag"]        = "measure_counter"
 
   properties["exec_tag"]     = ["measure_flow",0.0224145939,"main_sensor"]
   cf.add_info_node( "MINUTE_ELEMENT","MAIN_FLOW_METER",properties=properties, json_flag=True)

   
   properties = {}
   properties["units"]         = "AMPS"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["well_controller_output"]
  
   cf.add_info_node( "MINUTE_ELEMENT","WELL_CONTROLLER_OUTPUT",properties=properties, json_flag = True )

   properties = {}
   properties["units"]         = "AMPS"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["well_controller_input"]
   cf.add_info_node( "MINUTE_ELEMENT","WELL_CONTROLLER_INPUT", properties=properties, json_flag = True)

   properties = {}
   properties["units"]         = "PSI"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["filter_pressure"]
   cf.add_info_node( "MINUTE_ELEMENT","FILTER_PRESSURE", properties=properties, json_flag = True )

   properties = {}
   properties["units"]         = "PSI"
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["parameters"]   = [.0224145939]
   properties["exec_tag"]     = ["well_pressure"]
   cf.add_info_node( "MINUTE_ELEMENT", "WELL_PRESSURE", properties=properties, json_flag = True )
   
   cf.end_header_node("MINUTE_ACQUISITION") #"MINUTE_ACQUISITION"





   cf.end_header_node("DATA_ACQUISITION") #DATA_ACQUISITION
   
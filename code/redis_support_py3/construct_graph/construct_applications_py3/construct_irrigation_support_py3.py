
import json


class Construct_Irrigation_Support(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      bc.add_header_note("IRRIGATION_SUPPORT")
      cd.construct_package("IRRIGATION_DATA")
      cd.add_stream("ETO_HISTORY",360)
      cd.add_stream("RAIN_HISTORY",360)
      cd.close_package_contruction()
      self.add_master_valves()
      self.add_current_measurement()
      bc.end_header_node("IRRIGATION_SUPPORT")

      
      
      
      
   cf.add_header_node("MASTER_VALVES")
   cf.add_info_node("MASTER_VALVE_CONTROLLER","satellite_1",json_flag = True,
        properties = { "remote":"satellite_1","master_valve":43, "cleaning_valve":44 })

   cf.end_header_node("MASTER_VALVES")
       
   cf.add_header_node("CURRENT_MEASUREMENT")

   cf.add_info_node("CURRENT_DEVICE" ,"satellite_1",properties={ "remote":"satellite_1","register":"DF2", "conversion":1.0 },
        json_flag = True)

   cf.end_header_node("CURRENT_MEASUREMENT")

   cf.add_header_node("FLOW_METERS")

   cf.add_info_node( "FLOW_METER_CONTROL","main_flow_meter",json_flag = True,
                       properties={ "main_flow_meter" : "True",  "type":"CLICK", "remote":"satellite_1", 
                       "io_setup" : {"latch_bit":"C201",
                        "read_register":"DS301",  "conversion_factor":0.0224145939 } }  )



   cf.end_header_node("FLOW_METERS")


   cf.add_header_node("IRRIGATION_DATA" )

   cf.add_info_node( "IRRIGATION_DATA_ELEMENT","MASTER_VALVE",json_flag = True,
                       properties={ "dict":"CONTROL_VARIABLES", "key":"MASTER_VALVE_SETUP"  }  )
   cf.add_info_node( "IRRIGATION_DATA_ELEMENT","CURRENT",json_flag = True,
                       properties={ "dict":"CONTROL_VARIABLES", "key":"coil_current"  }  )


   cf.end_header_node("IRRIGATION_DATA")

   cf.end_header_node("IRRIGATION_SUPPORT")

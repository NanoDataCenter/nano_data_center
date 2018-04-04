
import json


class Construct_Irrigation(object):

   def __init__(self,bc,cd):
       self.bc = bc
       self.cd = cd
       bc.add_header_node("IRRIGATION")
       cd.construct_package("IRRIGATION_DATA")
       
       cd.add_hash("IRRIGATION_CONTROL")
       cd.add_job_queue("IRRIGATION_ACTIONS",16)
       cd.add_job_queue("IRRIGATION_PENDING",64)
       cd.add_job_queue("IRRIGATION_CURRENT",1)
       cd.add_hash("IRRIGATION_STATUS")
       cd.add_stream("IRRIGATION_STREAM",2800)  # 2 days worth of minute stream
       cd.close_package_contruction()
       
       bc.add_header_node("IRRIGATION_CONTROL")
       bc.add_info_node("NOTE","RAIN_FLAG",properties={"description":"controls rain disable 1 == disable"} )
       bc.end_header_node("IRRIGATION_CONTROL")
       
       bc.add_header_node("IRRIGATION_STATUS")
       bc.end_header_node("IRRIGATION_STATUS")
       
       bc.add_header_node("MASTER_VALVES")
       bc.add_info_node("MASTER_VALVE_CONTROLLER","satellite_1",
        properties = { "remote":"satellite_1","master_valve":43, "cleaning_valve":44 })
       bc.end_header_node("MASTER_VALVES")
       bc.add_header_node("CURRENT_MEASUREMENT")

       bc.add_info_node("CURRENT_DEVICE" ,"satellite_1",properties= { "remote":"satellite_1","register":"DF2", "conversion":1.0 } )
          

       bc.end_header_node("CURRENT_MEASUREMENT")

       bc.add_header_node("FLOW_METERS")

       bc.add_info_node( "FLOW_METER_CONTROL","main_flow_meter",json_flag = True,
                       properties={ "main_flow_meter" : "True",  "type":"CLICK", "remote":"satellite_1", 
                       "io_setup" : {"latch_bit":"C201",
                        "read_register":"DS301",  "conversion_factor":0.0224145939 } }  )



       bc.end_header_node("FLOW_METERS")
       bc.end_header_node("IRRIGATION")

      
      
      


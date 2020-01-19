class Construct_PLC_Measurements(object):

   def __init__(self,bc,cd):
       self.bc = bc
       self.cd = cd

       bc.add_header_node("PLC_MEASUREMENTS")
       bc.add_header_node("PLC_FLOW_METERS")
       properties={ "main" : "True",  "type":"CLICK", "remote":"satellite_1", 
                    "io_setup" : {"latch_bit":"C201",
                                  "read_register":"DS301",  
                                  "conversion_factor":0.0224145939 }
                   }
       bc.add_info_node( "FLOW_METER","main_flow_meter", properties = properties )
       
       bc.end_header_node("PLC_FLOW_METERS")
       
       
       bc.add_header_node("PLC_SLAVE_CURRENTS")
       bc.add_info_node("CURRENT_DEVICE" ,"satellite_1",properties={ "main" : "True","remote":"satellite_1","register":"DF2", "conversion":1.0 })

       bc.end_header_node("PLC_SLAVE_CURRENTS")
       
       bc.add_header_node("PLC_IRRIGATION_CURRENTS")
       bc.add_info_node("CURRENT_DEVICE" ,"satellite_1",properties={ "main" : "True","remote":"satellite_1","register":"DF1", "conversion":1.0 })
       bc.end_header_node("PLC_IRRIGATION_CURRENTS")

       cd.construct_package("PLC_MEASUREMENTS_PACKAGE")      
       cd.add_redis_stream("PLC_MEASUREMENTS_STREAM")       
       cd.close_package_contruction()
          
       
       
       bc.end_header_node("PLC_MEASUREMENTS")



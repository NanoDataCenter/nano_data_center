class Construct_PLC_Devices(object):

   def __init__(self,bc,cd):
       self.bc = bc
       self.cd = cd

       bc.add_header_node("PLC_SYSTEM")
       bc.add_header_node("PLC_SERVERS") # mulitple plc servers are allowed
      
       bc.add_header_node( "PLC_SERVER","MAIN_SERVER",properties={} )
       cd.construct_package("PLC_SERVER_DATA")
       cd.add_rpc_client("PLC_RPC_CLIENT")
       cd.close_package_contruction()
       properties                           = {}
       properties["type"]                  = "rs485_modbus",
       properties["interface_parameters"]  =  { "interface":None, "timeout":.05, "baud_rate":38400 }
       properties["search_device"]         =  "satellite_1" 
       bc.add_header_node( "SERIAL_LINK","rtu_2", properties = properties, json_flag= True )
       
       properties                   = {}
       properties["modbus_address"] = 100
       properties["type"]           = "click_44"
       properties["function"]       = ["irrigation","flow_meter","plc_current","valve_current","switches"]
       properties["parameters"]     = { "address":100 , "search_register":0, "register_number":1 }
       bc.add_info_node( "REMOTE_UNIT","satellite_1", properties = properties, json_flag= True )
  
  

       properties                   = {}
       properties["modbus_address"] = 125
       properties["type"]           = "click_22"
       properties["function"]       = ["irrigation"]
       properties["parameters"]     = { "address":125 , "search_register":0 ,"register_number":1  }
       bc.add_info_node( "REMOTE_UNIT","satellite_2", properties = properties, json_flag= True )

  
   
       properties                   = {}
       properties["modbus_address"] = 170
       properties["type"]           = "click_22"
       properties["function"]       = ["irrigation"]
       properties["parameters"]     = { "address":170 , "search_register":0, "register_number":1 }
       bc.add_info_node( "REMOTE_UNIT","satellite_3", properties =properties,  json_flag= True )


       properties                   = {}
       properties["modbus_address"] = 40
       properties["type"]           = "PSOC_4_Moisture"
       properties["function"]       = ["moisture"]
       properties["parameters"]     =  { "address":40 , "search_register":1,"register_number":10 }
       bc.add_info_node( "REMOTE_UNIT","moisture_1", properties =properties,  json_flag= True )

       properties                   = {}
       properties["modbus_address"] = 121
       properties["type"]           = "esp32_relay"
       properties["function"]       = ["irrigation"]
       properties["parameters"]     =  { "address":121 , "search_register":1,"register_number":1 }
       bc.add_info_node( "REMOTE_UNIT","satellite_4", properties =properties,  json_flag= True )   
   
       bc.end_header_node("SERIAL_LINK") 
       bc.end_header_node("PLC_SERVER")
       bc.end_header_node("PLC_SERVERS") # mulitple plc servers are allowed  
       bc.end_header_node("PLC_SYSTEM")



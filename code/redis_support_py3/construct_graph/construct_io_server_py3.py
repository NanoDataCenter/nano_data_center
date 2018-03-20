  cf.add_header_node("MODBUS_STATISTICS")

   cf.add_header_node( "HOUR_ACQUISTION",properties= {"measurement":"HOUR_LIST_STORE","length":300 , "routing_key":"HOUR_ACQUISTION"} , json_flag=True )
   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["init_tag"]     = ["clear_daily_modbus_statistics"]
   properties["exec_tag"]     = ["accumulate_daily_modbus_statistics"]
   cf.add_info_node( "HOUR_ELEMENT","MODBUS_STATISTICS",properties=properties,json_flag=True ) 
   cf.end_header_node("HOUR_ACQUISTION") # HOUR_ACQUISTION


   cf.add_header_node( "DAILY_ACQUISTION", properties= {"measurement":"DAILY_LIST_STORE","length":300, "routing_key":"DAILY_ACQUISTION"}, json_flag=True  )

   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]    = []
   properties["m_tag"]         =  "no_controller"
   properties["exec_tag"]      =  ["log_daily_modbus_statistics"]
   cf.add_info_node( "DAILY_ELEMENT","daily_modbus_statistics", properties=properties,json_flag=True ) 
   cf.end_header_node("DAILY_ACQUISTION")  # Daily Acquistion

   cf.end_header_node("MODBUS_STATISTICS") #MODBUS_STATISTICS

   properties = {}
   properties["ip"] = "192.168.1.84"   
   properties["remote_type"] = "UDP"
   properties["port"] = 5005   
   properties["redis_host"] = "192.168.1.84"
   properties["redis_db"]   = 0
   properties["redis_rpc_db"] = 5
   properties["redis_rpc_key"] = "#_RPC_QUEUE_"
   properties["logging_key"]  = "QUEUES:MODBUS_LOGGING"
   cf.add_header_node( "UDP_IO_SERVER","main_remote", properties = properties, json_flag= True )
 
   properties                           = {}
   properties["type"]                  = "rs485_modbus",
   properties["interface_parameters"]  =  { "interface":None, "timeout":.05, "baud_rate":38400 }
   properties["search_device"]         =  "satellite_1" 
   cf.add_header_node( "SERIAL_LINK","rtu_2", properties = properties, json_flag= True )


   
   
   properties                   = {}
   properties["modbus_address"] = 100
   properties["type"]           = "click_44"
   properties["function"]       = ["irrigation","flow_meter","plc_current","valve_current","switches"]
   properties["parameters"]     = { "address":100 , "search_register":0, "register_number":1 }
   cf.add_info_node( "REMOTE_UNIT","satellite_1", properties = properties, json_flag= True )
  
  

   properties                   = {}
   properties["modbus_address"] = 125
   properties["type"]           = "click_22"
   properties["function"]       = ["irrigation"]
   properties["parameters"]     = { "address":125 , "search_register":0 ,"register_number":1  }
   cf.add_info_node( "REMOTE_UNIT","satellite_2", properties = properties, json_flag= True )

  
   
   properties                   = {}
   properties["modbus_address"] = 170
   properties["type"]           = "click_22"
   properties["function"]       = ["irrigation"]
   properties["parameters"]     = { "address":170 , "search_register":0, "register_number":1 }
   cf.add_info_node( "REMOTE_UNIT","satellite_3", properties =properties,  json_flag= True )


   properties                   = {}
   properties["modbus_address"] = 40
   properties["type"]           = "PSOC_4_Moisture"
   properties["function"]       = ["moisture"]
   properties["parameters"]     =  { "address":40 , "search_register":1,"register_number":10 }
   cf.add_info_node( "REMOTE_UNIT","moisture_1", properties =properties,  json_flag= True )

   cf.end_header_node("SERIAL_LINK")
   cf.end_header_node("UDP_IO_SERVER")
cf.add_header_node( "LINUX_DATA_ACQUISITION")

   cf.add_header_node( "LINUX_HOUR_ACQUISTION",properties= {"measurement":"LINUX_HOUR_LIST_STORE","length":300 , "routing_key":"linux_hour_measurement"
} , json_flag=True )
  
   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["exec_tag"]     = ["python_processes"]
   cf.add_info_node( "LINUX_HOUR_ELEMENT","python_processes",properties=properties,json_flag=True )
 


   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]   = []
   properties["m_tag"]        = "no_controller"
   properties["exec_tag"]     = ["pi_temperature"]
   cf.add_info_node( "LINUX_HOUR_ELEMENT","pi_temperature_hourly",properties=properties,json_flag=True )
   
   
   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]    = []
   properties["m_tag"]         =  "no_controller"
   properties["exec_tag"]      =  ["linux_disk"]
   cf.add_info_node( "LINUX_HOUR_ELEMENT","linux_disk", properties=properties,json_flag=True ) 

   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]    = []
   properties["m_tag"]         =  "no_controller"
   properties["exec_tag"]      =  ["linux_redis"]
   cf.add_info_node( "LINUX_HOUR_ELEMENT","linux_redis", properties=properties,json_flag=True ) 

   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]    = []
   properties["m_tag"]         =  "no_controller"
   properties["exec_tag"]      =  ["linux_memory"]
   cf.add_info_node( "LINUX_HOUR_ELEMENT","linux_memory", properties=properties,json_flag=True )

   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]    = []
   properties["m_tag"]         =  "no_controller"
   properties["exec_tag"]      =  ["free_cpu"]
   cf.add_info_node( "LINUX_HOUR_ELEMENT","free_cpu", properties=properties,json_flag=True )


   properties = {}
   properties["modbus_remote"] = "skip_controller"
   properties["parameters"]    = []
   properties["m_tag"]         =  "no_controller"
   properties["exec_tag"]      =  ["proc_mem"]
   cf.add_info_node( "LINUX_HOUR_ELEMENT","proc_mem", properties=properties,json_flag=True )

   cf.end_header_node( "LINUX_HOUR_ACQUISTION") # HOUR_ACQUISTION


   cf.end_header_node("LINUX_DATA_ACQUISITION") 
      properties["error_queue_key"] = "PROCESS:ERROR_QUEUE"
   properties["web_command_key"] = "PROCESS:WEB_COMMAND_KEY"
   properties["web_process_data"] = "PROCESS:WEB_PROCESS_DATA"
   properties["web_display_list"]  = "PROCESS:WEB_DISPLAY_LIST"
   properties["command_string_list"] = []
   properties["command_string_list"].append( "linux_acquisition_py3.py")
   properties["command_string_list"].append( "eto_py3.py")
   properties["command_string_list"].append( "modbus_server_py3.py  main_remote")
   properties["command_string_list"].append( "rabbit_web_access_py3.py")
   properties["command_string_list"].append("rabbit_cloud_status_publish_py3.py")
   properties["command_string_list"].append("utilities_py3.py")
   #properties["command_string_list"].append("flask_web_py3.py")
   properties["command_string_list"].append("irrigation_monitoring_py3.py")
   properties["command_string_list"].append("irrigation_ctrl_startup_py3.py")

   cf.add_info_node("PROCESS_CONTROL","main_processor",properties=properties,json_flag = True )
   
# file build system
#
#  The purpose of this file is to load a system configuration
#  in the graphic data base
#

import json

import redis
from .build_configuration_py3 import Build_Configuration
from .construct_data_structures_py3 import Construct_Data_Structures
from .graph_modules_py3.construct_applications_py3 import Construct_Applications
from .graph_modules_py3.construct_controller_py3 import Construct_Processes

if __name__ == "__main__" :

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   redis_site = json.loads(data)


   bc = Build_Configuration(redis_site)
   cd = Construct_Data_Structures(redis_site["site"],bc)
   
   #
   #
   # Construct Systems
   #
   #
   bc.add_header_node( "SYSTEM","main_operations" )
                                                  

   #
   #
   # Construction Sites for LaCima
   #
   #
 
   bc.add_header_node( "SITE","LaCima",  properties = {"address":"21005 Paseo Montana Murrieta, Ca 92562" } )
                                                  

   Construct_Applications(bc,cd)
   Construct_Processes(bc,cd)


   bc.end_header_node("SITE")
   bc.end_header_node("SYSTEM")
   bc.check_namespace()
   bc.store_keys()


   '''

   
   #altitude = 2400
   #cf.add_eto_setup_code(access_codes = access_codes, altitude = altitude)
   #cf.start_info_store()
   #cf.add_eto_store()
   
   cf.add_header_node( "ETO_SITES", properties = {"status_dictionary":"eto_status",
                                                  "eto_stream":{"name":"eto_stream","depth":360} }
                                                  
                                                  
                                  

   properties = {"key":"WUNDERGROUND","pws":'KCAMURRI101','lat':33.2,"alt":2400, "priority":3}  
   cf.add_info_node( "ETO_ENTRY","WUNDERGROUND_SITE_NORMAL",properties=properties, json_flag=True)

   properties = {"key":"WUNDERGROUND","pws":'KCAMURRI101','lat':33.2,"alt":2400,"priority":4}  
   cf.add_info_node( "ETO_ENTRY","WUNDERGROUND_SITE_GUST",properties=properties, json_flag=True)

   properties = {"key":"WUNDERGROUND","pws":'KCAMURRI101','lat':33.2,"alt":2400"priority":1}  
   cf.add_info_node( "ETO_ENTRY","WUNDERGROUND_SITE_MAX",properties=properties, json_flag=True)

   properties = { "api-key":"ETO_CIMIS_SATELLITE"  , 
                  "url":"http://et.water.ca.gov/api/data", 
                  "longitude":  -117.299459  ,
                  "latitude":33.578156 ,
                  "priority":5 } 
   cf.add_info_node( "ETO_ENTRY","ETO_CIMIS_SATELLITE",properties=properties, json_flag=True)

   properties = { "api-key":"ETO_CIMIS"  , "url":"http://et.water.ca.gov/api/data"     , "station":62 }
   properties["altitude"]        = 2400
   properties["priority"]        = 4
   cf.add_info_node( "ETO_ENTRY","ETO_CIMIS",properties=properties, json_flag=True)

                                                    
                                                  
   properties = {"api-key":"MESSOWEST"  ,"url":"http://api.mesowest.net/v2/stations/timeseries?" ,  "station":"SRUC1" }
   properties["altitude"] = 2400
   properties["priority"] = 2
   cf.add_info_node( "ETO_ENTRY","Santa_Rosa_RAWS",properties=properties, json_flag=True)

 
   cf.end_header_node("ETO_SITES")

   cf.add_header_node("RAIN_SOURCES",properties = {"measurement":"LACIMA_RAIN_MEASUREMENTS" } )

   properties = { "api-key":"ETO_CIMIS"  , "url":"http://et.water.ca.gov/api/data"     , "station":62 }
   properties["measurement_tag"] = "CIMIS_RAIN"
   properties["list_length"]     = 100
   properties["measurement"]     = "CIMIS_RAIN_STORE"

   cf.add_info_node( "RAIN_ENTRY","CIMIS_RAIN",properties=properties, json_flag=True)

   properties = {"api-key":"MESSOWEST"  ,"url":"http://api.mesowest.net/v2/stations/precip?" ,  "station":"SRUC1" }
   properties["measurement_tag"] ="SRUC1_RAIN"
   properties["list_length"]     = 100
   properties["measurement"]     = "SRCU1_RAIN_STORE"
   cf.add_info_node( "RAIN_ENTRY","SRUC1_RAIN",properties=properties, json_flag=True)
   cf.end_header_node("RAIN_SOURCES")

   cf.add_header_node("IRRIGATION_SUPPORT")


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


   cf.end_header_node("APPLICATION_SUPPORT")

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
   
  
   
   #cf.add_info_node( "MINUTE_LIST_STORE", "MINUTE_LIST_STORE",properties =  { "LIST_LENGTH" :10000} , json_flag = True) # about 1 week of data 
   #cf.add_info_node( "HOUR_LIST_STORE", "HOUR_LIST_STORE",properties =  { "LIST_LENGTH" :10000} , json_flag = True) # about 1 week of data 

   cf.add_header_node("RAIN_MEASUREMENTS")
   
   cf.add_info_node("RAIN_STORE","CIMIS_RAIN_STORE",properties={"list_length":300},json_flag = True)
   cf.add_info_node("RAIN_STORE","SRCU1_RAIN_STORE",properties={"list_length":300},json_flag = True)
   cf.end_header_node("RAIN_MEASUREMENTS")
   cf.add_info_node("INTEGRATED_RAIN_ESTIMATE","LACIMA_INTEGRATED_RAIN_ESTIMATE",properties={},json_flag = True )

   cf.add_info_node("RAIN_QUEUE","QUEUES:ETO:RAIN",properties={"list_length":300},json_flag = True )  
   cf.add_info_node("ETO_QUEUE","QUEUES:ETO:ETO",properties={"list_length":300},json_flag = True )
   cf.add_info_node("INTEGRATED_ETO_ESTIMATE","LACIMA_INTEGRATED_ETO_ESTIMATE",properties={"list_length":300},json_flag = True )

   cf.add_header_node("ETO_MEASUREMENTS")
   cf.add_info_node("ETO_STORE","CIMIS_SATELLITE_ETO_STORE",properties={"list_length":300},json_flag = True)
   cf.add_info_node("ETO_STORE","CIMIS_ETO_STORE",properties={"list_length":300},json_flag = True)
   cf.add_info_node("ETO_STORE","SRUC1_ETO_STORE",properties={"list_length":300},json_flag = True)
   cf.add_info_node("ETO_STORE","HYBRID_SITE_STORE",properties={"list_length":300},json_flag = True)

   cf.end_header_node("ETO_MEASUREMENTS") 

   cf.add_header_node("MOISTURE_SENSOR_DATA")
   cf.add_header_node("moisture_1")
   cf.add_info_node("MOISTURE_DATA",          "moisture_1",properties={"queue_name":"moisture_1_data","list_length":300},json_flag = True)
   cf.add_info_node("MOISTURE_AIR_TEMP_LIST", "moisture_1",properties={"queue_name":"moisture_1_list","list_length":24},json_flag = True)
   cf.add_info_node("MOISTURE_ROLLOVER",      "moisture_1",properties={"queue_name":"moisture_1_rollover","list_length":24},json_flag = True)

 
   
   cf.end_header_node("moisture_1") #moisture_1
   cf.end_header_node("MOISTURE_SENSOR_DATA") #MOISTURE_DATA


   cf.end_header_node("DATA_STORE")

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
  

   cf.add_header_node("RABBITMQ_CLIENTS")
   #cf.add_rabbitmq_status_queue( "LaCima",vhost="LaCima",queue="status_queue",port=5671,server = 'lacimaRanch.cloudapp.net' )
   cf.end_header_node("RABBITMQ_CLIENTS")
   properties = {}
   properties["redis"] = {"ip":"127.0.0.1","port": 6379, "db":0 }
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
   #cf.construct_controller(  name="PI_1", ip = "192.168.1.82",type="PI")
   #cf.end_controller()

   #cf.construct_web_server( name="main_web_server",url="https://192.168.1.84" )
  
   #cf.add_rabbitmq_command_rpc_queue("LaCima" )
   #cf.add_rabbitmq_web_rpc_queue("LaCima")
   #cf.add_rabbitmq_event_queue("LaCima")


   #cf.add_rabbitmq_status_queue( "LaCima",vhost="LaCima",queue="status_queue",port=5671,server = 'lacimaRanch.cloudapp.net' )



   #cf.add_info_node( "CIMIS_EMAIL","CIMIS_EMAIL",properties =  { "imap_username" :'lacima.ranch@gmail.com',"imap_password" : 'Gr1234gfd'} , json_flag = True)


   #cf.add_ntpd_server("LaCima")   #cf.add_moisture_monitoring("LaCima")
   #cf.irrigation_monitoring("LaCima")
   #cf.add_device_monitoring("LaCima")
   #cf.add_watch_dog_monitoring("LaCima")
'''
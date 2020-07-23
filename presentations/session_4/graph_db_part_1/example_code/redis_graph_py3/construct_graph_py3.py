
import redis
import copy
import json
import redis_graph_py3
from .site_configuration_py3 import Retrieve_Site_ID
from .build_configuration_py3 import Build_Configuration
from .data_configuration import config_dictionary

if __name__ == "__main__":

    # read configuration file    
    retrieve = Retrieve_Site_ID("redis_graph_py3")
    site_data = retrieve.read_configuration()
    redis_handle  = redis.StrictRedis( host = site_data["redis_ip"], 
                                       port=site_data["redis_port"],
                                       db= site_data["graph_db"] , 
                                       decode_responses=True)
    bc = Build_Configuration(redis_handle) 
    
    bc.add_header_node( "SYSTEM","Creator Space",properties = config_dictionary["SYSTEM"]["properties"] )
    
    bc.add_header_node("SITE","Murrieta",properties = config_dictionary["SITE"] ) 
    
    bc.add_header_node( "CONTROLLERS","Murrieta")
    for key,data in config_data["CONTROLLER"].items()
       bc.add_info_node("CONTROLLER",key,properties=data["properties"] )
    bc.end_header_node( "CONTROLLERS" )

    bc.add_header_node( "APPLICATIONS","MURRIETA")
    for key,data in config_data["APPLICATION"].items()
       bc.add_info_node("APPLICATION",key,properties=data["properties"] )
    bc.end_header_node( "APPLICATIONS"" )

    bc.add_header_node( "IO_CONTROLLERS","MURRIETA")
    for key,data in config_data["IO_CONTROLLER"].items()
       bc.add_header_node("IO_CONTROLLER",key,properties=data["properties"] )
       for key1, data1 in  data["LINKS"]:
          bc.add_info_node("LINKS",key1,properties= data_1["properties"] )
          for key_2,data2 in data_1["SLAVES"].items()
              bc.add_info_node("SLAVES",key2,data_2["properties"] )
          bc.end_header_node("LINKS")
       bc.add_header_node("IO_CONTROLLER")
    bc.end_header_node( "IO_CONTROLLERS")
    
    
        


'''

"redis_ip":"127.0.0.1",
"redis_port":6379 ,
"graph_db":25,
"site_id":"xxxx"
import redis
from . import farm_template_py3

if __name__ == "__main__" :
   print( "constructing graph")
   cf = farm_template_py3.Construct_Farm()
   
   #
   #
   # Construct Systems
   #
   #
   cf.construct_system("LaCima Operations")

   #
   #
   # Construction Sites for LaCima
   #
   #

   cf.construct_site( name="LaCima",address="21005 Paseo Montana Murrieta, Ca 92562")

   # we are going to construct the data store here
   cf.add_header_node("APPLICATION_SUPPORT")

   cf.add_header_node( "UTILITY_MODULE", properties = {}, json_flag= True )
   cf.add_info_node( "CIMIS_EMAIL","CIMIS_EMAIL",properties =  { "imap_username" :'lacima.ranch@gmail.com',"imap_password" : 'Gr1234gfd'} , json_flag = True)
   cf.end_header_node("UTILITY_MODULE")

   cf.add_header_node( "MOISTURE_CONTROLLERS", properties = {}, json_flag= True )
   
   cf.add_info_node("MOISTURE_MANUAL_UPDATE_FLAG","MANUAL_UPDATE_FLAG",properties = {},json_flag = True)

   description_map = ["Bank 10A Watermark 8 inch","Bank 10A Resistive 8 inch", "Bank 10A Resistive 18 inch", "empty",
                      "Bank 10B Watermark 8 inch", "Bank 10B Resistive 8 inch","Bank 10B Resistive 18 inch","empty",
                      "Bank 10C Watermark 8 inch","Bank 10C Resistive 8 inch", "Bank 10C Resistive 18 inch", "empty",
                      "Bank 10D Watermark 8 inch", "Bank 10D Resistive 8 inch","Bank 10D Resistive 18 inch","empty" ]

   depth_map = [8,8,18,0,8,8,18,0,8,8,18,0,8,8,18,0]
   properties = {}
   properties["description"]        =  "Moisture Sensor for Irrigation Bank10"   
   properties["description_map"]    =   description_map
   properties["update_time"]        =   15
   properties["depth_map"]          =   depth_map
   properties["moisture_list_store"]         =   "MOISTURE_1_DATA_STORE"
   properties["air_temp_list_store"]         =   "MOISTURE_1_AIR_TEMP_LIST_STORE"
   properties["roll_over_list_store"]        =   "MOISTURE_1_ROLL_OVER_LIST_STORE"
   properties["subordinate_controller_address"]    =    40
   cf.add_info_node( "MOISTURE_CTR","moisture_1", properties = properties, json_flag= True )
 
   cf.end_header_node("MOISTURE_CONTROLLERS")
 
   cf.add_info_node( "CLOUD_STATUS_STORE","status_store", properties = {"queue_name":"status_store"} )
   
   #altitude = 2400
   #cf.add_eto_setup_code(access_codes = access_codes, altitude = altitude)
   #cf.start_info_store()
   #cf.add_eto_store()
   
   cf.add_header_node( "ETO_SITES", properties = {"integrated_measurement":"LACIMA_INTEGRATED_ETO_ESTIMATE",
                                                  "measurement":"LACIMA_ETO_MEASUREMENTS",
                                                  "mv_threshold_number":1 } )

   properties = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "longitude":  -117.299459  ,"latitude":33.578156  }
   properties["altitude"] = 2400
   properties["measurement_tag"] = "CIMIS_SATELLITE_ETO"
   properties["list_length"]     = 100
   properties["measurement"]     = "CIMIS_SATELLITE_ETO_STORE"
   properties["majority_vote_flag"] = True

   cf.add_info_node( "ETO_ENTRY","ETO_CIMIS_SATELLITE",properties=properties, json_flag=True)

   properties = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "station":62 }
   properties["altitude"]        = 2400
   properties["measurement_tag"] = "CIMIS_ETO"
   properties["list_length"]     = 100
   properties["measurement"]     = "CIMIS_ETO_STORE"
   properties["majority_vote_flag"] = True

   cf.add_info_node( "ETO_ENTRY","ETO_CIMIS",properties=properties, json_flag=True)

   properties = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/timeseries?" ,  "station":"SRUC1" }
   properties["altitude"] = 2400
   properties["measurement_tag"] = "SRUC1_ETO"  
   properties["list_length"]     = 100
   properties["measurement"]    = "SRUC1_ETO_STORE"

   properties["majority_vote_flag"] = True
   cf.add_info_node( "ETO_ENTRY","Santa_Rosa_RAWS",properties=properties, json_flag=True)
   

   properties = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/timeseries?" ,  "station":"SRUC1" }
   properties["altitude"] = 2400
   properties["measurement_tag"] = "HYBRID_SITE"
   properties["list_length"]     = 100
   properties["measurement"]    = "HYBRID_SITE_STORE"
   properties["rollover"]       = "moisture_1_rollover"
   properties["majority_vote_flag"] = False
   cf.add_info_node( "ETO_ENTRY","LaCima_Ranch",properties=properties, json_flag=True)
   cf.end_header_node("ETO_SITES")

   cf.add_header_node("RAIN_SOURCES",properties = {"measurement":"LACIMA_RAIN_MEASUREMENTS" } )

   properties = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "station":62 }
   properties["measurement_tag"] = "CIMIS_RAIN"
   properties["list_length"]     = 100
   properties["measurement"]     = "CIMIS_RAIN_STORE"

   cf.add_info_node( "RAIN_ENTRY","CIMIS_RAIN",properties=properties, json_flag=True)

   properties = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/precip?" ,  "station":"SRUC1" }
   properties["measurement_tag"] ="SRUC1_RAIN"
   properties["list_length"]     = 100
   properties["measurement"]     = "SRCU1_RAIN_STORE"
   cf.add_info_node( "RAIN_ENTRY","SRUC1_RAIN",properties=properties, json_flag=True)
   cf.end_header_node("RAIN_SOURCES")

   cf.add_header_node("IRRIGATION_SUPPORT")


   cf.add_header_node("MASTER_VALVES")
   cf.add_info_node("MASTER_VALVE_CONTROLLER","satellite_1",json_flag = True,
        properties = { "remote":"satellite_1","main_valve":43, "cleaning_valve":44 })

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
   cf.add_rabbitmq_status_queue( "LaCima",vhost="LaCima",queue="status_queue",port=5671,server = 'lacimaRanch.cloudapp.net' )
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
   cf.end_site()
   cf.end_system()
   cf.check_namespace()
   cf.store_keys()
'''


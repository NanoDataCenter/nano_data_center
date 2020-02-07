
import json


ONE_WEEK = 24*7

class Construct_Controllers(object):

   def __init__(self,bc,cd):
       properties = {}
       properties["command_list"] = []
      
       properties["command_list"].append( { "file":"eto_py3.py","restart":True })
       properties["command_list"].append( { "file":"utilities_py3.py","restart":True })
       properties["command_list"].append( { "file":"redis_monitoring_py3.py","restart":True })
       properties["command_list"].append( { "file":"pi_monitoring_py3.py","restart":True })
       properties["command_list"].append( { "file":"mqtt_scan_data_py3.py","restart":True })
       properties["command_list"].append( { "file":"mqtt_redis_gateway_py3.py","restart":True })
       
       properties["command_list"].append( { "file":" -m  mqtt_clients.mqtt_local_publish_server_py3","restart":True })
       properties["command_list"].append( { "file":"modbus_server_py3.py  MAIN_SERVER","restart":True })
       properties["command_list"].append( { "file":"irrigation_ctrl_startup_py3.py","restart":True })
       properties["command_list"].append( { "file":"plc_io_cntrl_py3.py","restart":True })
       properties["command_list"].append( { "file":"cloud_interface_py3.py","restart":True })
       #properties["command_list"].append( { "file":"redis_cloud_download_py3.py","restart":True })
       bc.add_header_node("PROCESSOR","nano_data_center",properties=properties) # name is identified in site_data["local_node"]

       properties["command_list"] =[]
           
       #properties["command_list"].append( { "file":"eto_init_py3.py"})
      
       #properties["command_list"].append( { "file":"irrigation_int_py3.py"} )
       bc.add_info_node("PROCESS_INITIALIZATION","nano_data_center",properties=properties)
              

       cd.construct_package("DATA_STRUCTURES")      
       cd.add_redis_stream("ERROR_STREAM",forward=True)
       cd.add_hash("ERROR_HASH")
       cd.add_job_queue("WEB_COMMAND_QUEUE",1)
       cd.add_hash("WEB_DISPLAY_DICTIONARY")
       cd.close_package_contruction()


       cd.construct_package("SYSTEM_MONITORING")
       cd.add_redis_stream("FREE_CPU",forward = True) # one month of data
       cd.add_redis_stream("RAM",forward = True)
       cd.add_redis_stream("DISK_SPACE",forward = True) # one month of data
       cd.add_redis_stream("TEMPERATURE",forward = True)
       cd.add_redis_stream("PROCESS_VSZ")
       cd.add_redis_stream("PROCESS_RSS")
       cd.add_redis_stream("PROCESS_CPU")
       
       cd.add_redis_stream("CPU_CORE")
       cd.add_redis_stream("SWAP_SPACE")
       cd.add_redis_stream("IO_SPACE")
       cd.add_redis_stream("BLOCK_DEV")
       cd.add_redis_stream("CONTEXT_SWITCHES")
       cd.add_redis_stream("RUN_QUEUE")       
       cd.add_redis_stream("DEV") 
       cd.add_redis_stream("SOCK") 
       cd.add_redis_stream("TCP") 
       cd.add_redis_stream("UDP") 
       cd.close_package_contruction()
          
       bc.end_header_node("PROCESSOR")
       
       #
       #
       #  Add other processes if desired
       #
       
       properties = {}
       properties["command_list"] = []
      

       properties["command_list"].append( { "file":"redis_monitoring_py3.py","restart":True })
       properties["command_list"].append( { "file":"pi_monitoring_py3.py","restart":True })

       bc.add_header_node("PROCESSOR","block_chain_server",properties=properties) # name is identified in site_data["local_node"]

       properties["command_list"] =[]

       bc.add_info_node("PROCESS_INITIALIZATION","block_chain_server",properties=properties)
              

       cd.construct_package("DATA_STRUCTURES")      
       cd.add_redis_stream("ERROR_STREAM",forward=True)
       cd.add_hash("ERROR_HASH")
       cd.add_job_queue("WEB_COMMAND_QUEUE",1)
       cd.add_hash("WEB_DISPLAY_DICTIONARY")
       cd.close_package_contruction()


       cd.construct_package("SYSTEM_MONITORING")
       cd.add_redis_stream("FREE_CPU",forward = True) # one month of data
       cd.add_redis_stream("RAM",forward = True)
       cd.add_redis_stream("DISK_SPACE",forward = True) # one month of data
       cd.add_redis_stream("TEMPERATURE",forward = True)
       cd.add_redis_stream("PROCESS_VSZ")
       cd.add_redis_stream("PROCESS_RSS")
       cd.add_redis_stream("PROCESS_CPU")
       
       cd.add_redis_stream("CPU_CORE")
       cd.add_redis_stream("SWAP_SPACE")
       cd.add_redis_stream("IO_SPACE")
       cd.add_redis_stream("BLOCK_DEV")
       cd.add_redis_stream("CONTEXT_SWITCHES")
       cd.add_redis_stream("RUN_QUEUE")       
       cd.add_redis_stream("DEV") 
       cd.add_redis_stream("SOCK") 
       cd.add_redis_stream("TCP") 
       cd.add_redis_stream("UDP") 
       cd.close_package_contruction()
          
       bc.end_header_node("PROCESSOR")
       
       #
       #
       #  Add other processes if desired
       #

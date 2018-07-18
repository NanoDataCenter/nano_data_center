
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
       properties["command_list"].append( { "file":"redis_cloud_upload_py3.py","restart":True })
       properties["command_list"].append( { "file":"mqtt_redis_gateway_py3.py","restart":True })
       properties["command_list"].append( { "file":"redis_cloud_download_py3.py","restart":True })
       bc.add_header_node("PROCESSOR","nano_data_center",properties=properties)

       properties["command_list"] =[]
           
       properties["command_list"].append( { "file":"eto_init_py3.py"})
      
       properties["command_list"].append( { "file":"irrigation_int_py3.py"} )
       bc.add_info_node("PROCESS_INITIALIZATION","nano_data_center",properties=properties)
              

       cd.construct_package("DATA_STRUCTURES")      
       cd.add_stream("ERROR_STREAM",depth=256)
       cd.add_hash("ERROR_HASH")
       cd.add_job_queue("WEB_COMMAND_QUEUE",1)
       cd.add_hash("WEB_DISPLAY_DICTIONARY")
       cd.close_package_contruction()


       cd.construct_package("SYSTEM_MONITORING")
       cd.add_stream("FREE_CPU",depth=ONE_WEEK) # one month of data
       cd.add_stream("RAM",depth=ONE_WEEK)
       cd.add_stream("DISK_SPACE",depth=ONE_WEEK) # one month of data
       cd.add_stream("TEMPERATURE",depth=ONE_WEEK)
       cd.add_stream("PROCESS_VSZ",depth=ONE_WEEK)
       cd.add_stream("PROCESS_RSS",depth=ONE_WEEK)
       cd.add_stream("PROCESS_CPU",depth=ONE_WEEK)
       
       cd.add_stream("CPU_CORE",depth=ONE_WEEK)
       cd.add_stream("SWAP_SPACE",depth=ONE_WEEK)
       cd.add_stream("IO_SPACE",depth=ONE_WEEK)
       cd.add_stream("BLOCK_DEV",depth=ONE_WEEK)
       cd.add_stream("CONTEXT_SWITCHES",depth=ONE_WEEK)
       cd.add_stream("RUN_QUEUE",depth=ONE_WEEK)       
       cd.add_stream("DEV",depth=ONE_WEEK) # one month of data
       cd.add_stream("SOCK",depth=ONE_WEEK) # one month of data
       cd.add_stream("TCP",depth=ONE_WEEK) # one month of data
       cd.add_stream("UDP",depth=ONE_WEEK) # one month of data
       cd.close_package_contruction()
          
       bc.end_header_node("PROCESSOR")
       
       #
       #
       #  Add other processes if desired
       #
       
 


import json


ONE_MONTH = 24*30

class Construct_Controllers(object):

   def __init__(self,bc,cd):
       properties = {}
       properties["command_list"] = []
      
       properties["command_list"].append( { "file":"eto_py3.py","restart":True })
       properties["command_list"].append( { "file":"utilities_py3.py","restart":True })
       properties["command_list"].append( { "file":"redis_monitoring_py3.py","restart":True })
       properties["command_list"].append( { "file":"pi_monitoring_py3.py","restart":True })
       bc.add_header_node("PROCESSOR","nano_data_center",properties=properties)
       

       
       cd.construct_package("DATA_STRUCTURES")      
       cd.add_stream("ERROR_STREAM",depth=256)
       cd.add_job_queue("WEB_COMMAND_QUEUE",1)
       cd.add_hash("WEB_DISPLAY_DICTIONARY")
       cd.close_package_contruction()


       cd.construct_package("SYSTEM_MONITORING")
       cd.add_stream("FREE_CPU",depth=ONE_MONTH) # one month of data
       cd.add_stream("RAM",depth=ONE_MONTH)
       cd.add_stream("DISK_SPACE",depth=ONE_MONTH) # one month of data
       cd.add_stream("TEMPERATURE",depth=ONE_MONTH)
       cd.add_stream("PROCESS_VSZ",depth=ONE_MONTH)
       cd.add_stream("PROCESS_RSS",depth=ONE_MONTH)
       cd.add_stream("PROCESS_STATE",depth=ONE_MONTH)
       cd.close_package_contruction()
       
       cd.construct_package("NETWORK_MONITORING")
       cd.add_stream("SYSTEM_STATE",depth=ONE_MONTH) # one month of data

       cd.close_package_contruction()
          
       bc.end_header_node("PROCESSOR")
       
       #
       #
       #  Add other processes if desired
       #
       
 

import json


ONE_MONTH = 24*30

class Construct_Controllers(object):

   def __init__(self,bc,cd):
       properties = {}
       properties["command_string_list"] = []
       properties["command_string_list"].append( "eto_py3.py")
       properties["command_string_list"].append("utilities_py3.py")
       properties["command_string_list"].append("controller_monitoring_py3.py")
       properties["command_string_list"].append("network_monitoring_py3.py")
       properties["command_string_list"].append("redis_monitoring_py3.py")   
       bc.add_header_node("PROCESSOR","nano_data_center",properties=properties)
       

       
       cd.construct_package("ATTACHED_PROCESSES")      
       cd.add_stream("ERROR_QUEUE",depth=32)
       cd.add_job_queue("WEB_COMMAND_QUEUE",1)
       cd.add_hash("PROCESS_DATA")
       cd.add_hash("WEB_DISPLAY_LIST",1)
       cd.close_package_contruction()

       cd.construct_package("SYSTEM_MONITORING")
       cd.add_stream("SYSTEM_STATE",depth=ONE_MONTH) # one month of data
       cd.add_stream("PROCESS_VSS",depth=ONE_MONTH)
       cd.close_package_contruction()
       
       cd.construct_package("NETWORK_MONITORING")
       cd.add_stream("SYSTEM_STATE",depth=ONE_MONTH) # one month of data

       cd.close_package_contruction()
          
       bc.end_header_node("PROCESSOR")
       
       #
       #
       #  Add other processes if desired
       #
       
 
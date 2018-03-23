
import json

class Construct_Processes(object):

   def __init__(self,bc,cd):
       properties = {}
       properties["error_queue_key"] = "PROCESS:ERROR_QUEUE"   #### Not sure what this is
       properties["web_command_key"] = "PROCESS:WEB_COMMAND_KEY"
       properties["web_process_data"] = "PROCESS:WEB_PROCESS_DATA"
       properties["web_display_list"]  = "PROCESS:WEB_DISPLAY_LIST"
       
       properties["command_string_list"] = []
       properties["command_string_list"].append( "eto_py3.py")
       properties["command_string_list"].append("utilities_py3.py")
       properties["command_string_list"].append("flask_web_py3.py")
       bc.add_info_node("ATTACHED_PROCESSES","nano_data_center",properties=properties)
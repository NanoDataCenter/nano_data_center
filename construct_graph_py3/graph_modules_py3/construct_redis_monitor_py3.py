
import json


ONE_MONTH = 24*30

class Construct_Redis_Monitoring(object):

   def __init__(self,bc,cd):
   
       bc.add_header_node("REDIS_MONITORING","nano_data_center",properties={})
       

       
       cd.construct_package("REDIS_MONITORING")      
       cd.add_stream("REDIS_MONITOR_KEY_STREAM",depth=ONE_MONTH)
       cd.add_stream("REDIS_MONITOR_CLIENT_STREAM",depth=ONE_MONTH)
       cd.add_stream("REDIS_MONITOR_MEMORY_STREAM",depth=ONE_MONTH)
       cd.add_stream("REDIS_MONITOR_CALL_STREAM",depth=ONE_MONTH)
       cd.add_stream("REDIS_MONITOR_CMD_TIME_STREAM",depth=ONE_MONTH)
       cd.add_stream("REDIS_MONITOR_SERVER_TIME",depth = ONE_MONTH)
       
       cd.close_package_contruction()
          
       bc.end_header_node("REDIS_MONITORING")
       
       #
       #
       #  Add other processes if desired
       #
       
 
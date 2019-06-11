
import json


ONE_MONTH = 24*30

class Construct_Redis_Monitoring(object):

   def __init__(self,bc,cd):
   
       bc.add_header_node("REDIS_MONITORING","nano_data_center",properties={})
       

       
       cd.construct_package("REDIS_MONITORING")      
       cd.add_redis_stream("REDIS_MONITOR_KEY_STREAM")
       cd.add_redis_stream("REDIS_MONITOR_CLIENT_STREAM")
       cd.add_redis_stream("REDIS_MONITOR_MEMORY_STREAM")
       cd.add_redis_stream("REDIS_MONITOR_CALL_STREAM")
       cd.add_redis_stream("REDIS_MONITOR_CMD_TIME_STREAM")
       cd.add_redis_stream("REDIS_MONITOR_SERVER_TIME")
       
       cd.close_package_contruction()
          
       bc.end_header_node("REDIS_MONITORING")
       
       #
       #
       #  Add other processes if desired
       #
       
 
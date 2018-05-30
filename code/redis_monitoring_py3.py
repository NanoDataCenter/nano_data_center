
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers


class Redis_Monitor(object):

   def __init__(self,redis_handle, redis_monitoring_streams ):
       self.redis_handle = redis_handle
       self.redis_monitoring_streams = redis_monitoring_streams
       
       
   def log_data(self,*parameters):
       
       redis_data = self.redis_handle.info("Keyspace")     

       self.redis_monitoring_streams["KEYS"].push(data=redis_data)      
       redis_data = self.redis_handle.info("Clients") 
             
       self.redis_monitoring_streams["CLIENTS"].push(data=redis_data)      
       redis_data = self.redis_handle.info("Memory")      
      
       self.redis_monitoring_streams["MEMORY"].push(data=redis_data)      
       #print(self.redis_monitoring_streams["KEYS_READER"].xrange_compress("-","+"))
       #print(self.redis_monitoring_streams["KEYS_READER"].xrevrange_compress("+","-"))



def construct_redis_instance( qs, site_data ):

                   
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"REDIS_MONITORING"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)  
 
    package = package_sources[0]
    
    #
    #  do verifications of data package
    #
    #
    #
    data_structures = package["data_structures"]
    generate_handlers = Generate_Handlers( package, site_data )
    
    redis_monitoring_streams = {}
    redis_monitoring_streams["KEYS"] = generate_handlers.construct_stream_writer(data_structures["REDIS_MONITOR_KEY_STREAM"] )
    redis_monitoring_streams["CLIENTS"] = generate_handlers.construct_stream_writer(data_structures["REDIS_MONITOR_CLIENT_STREAM"] )
    redis_monitoring_streams["MEMORY"] = generate_handlers.construct_stream_writer(data_structures["REDIS_MONITOR_MEMORY_STREAM"] )
    redis_monitoring_streams["KEYS_READER"] = generate_handlers.construct_stream_reader(data_structures["REDIS_MONITOR_KEY_STREAM"] )

 
   
    redis_handle = generate_handlers.get_redis_handle()  # reusing handle from package
    redis_monitor = Redis_Monitor(redis_handle , redis_monitoring_streams )
    
    
    
  

    return redis_monitor




def add_chains(redis_monitor, cf):
 
    cf.define_chain("make_measurements", True)
    cf.insert.log("logging_redis_data")
    cf.insert.one_step(redis_monitor.log_data)
    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 1)
    cf.insert.reset()

 

if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json

    import os
    import copy
    #import load_files_py3
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    import datetime
    from redis_support_py3.user_data_tables_py3 import User_Data_Tables

    from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter

    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
 
    #
    # Setup handle
    # open data stores instance
   
    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
    
    redis_monitor = construct_redis_instance(qs, redis_site )
    #
    # Adding chains
    #
    cf = CF_Base_Interpreter()
    add_chains(redis_monitor, cf)
    #
    # Executing chains
    #
    
    cf.execute()
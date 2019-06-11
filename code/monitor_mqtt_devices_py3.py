

from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers

class MQTT_Monitor(object):

   def __init__(self,mqtt_devices, package,site_data):
        self.mqtt_devices = mqtt_devices
        self.package  = package
        self.site_data = site_data
        
       
        self.generate_data_handlers()
        self.generate_mqtt_handlers()
        self.start_mqtt_client()
        self.register_subscriptions()


   def generate_data_handlers(self):
        self.handlers = {}
        data_structures = self.package["data_structures"]
        generate_handlers = Generate_Handlers(self.package,self.site_data)
        self.ds_handlers = {}
        self.ds_handlers["EXCEPTION_VALUES"] = generate_handlers.construct_hash(data_structures["EXCEPTION_VALUES"])
        self.ds_handlers["ETO_VALUES"] = generate_handlers.construct_hash(data_structures["ETO_VALUES"])
        self.ds_handlers["RAIN_VALUES"] = generate_handlers.construct_hash(data_structures["RAIN_VALUES"])
        self.ds_handlers["ETO_CONTROL"] = generate_handlers.construct_hash(data_structures["ETO_CONTROL"])
        self.ds_handlers["ETO_HISTORY"] = generate_handlers.construct_stream_writer(data_structures["ETO_HISTORY"])
        self.ds_handlers["RAIN_HISTORY"] = generate_handlers.construct_stream_writer(data_structures["RAIN_HISTORY"] )
        self.ds_handlers["EXCEPTION_LOG"] = generate_handlers.construct_stream_writer(data_structures["EXCEPTION_LOG"] )
       
       
def construct_mqtt_devices(qs, redis_site,user_table ):
    pass


      
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
    from eto_init_py3 import User_Data_Tables

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
    user_table = User_Data_Tables(redis_site)
    
    user_table.initialize()  
    
    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
    
    mqtt_devices = construct_mqtt_devices(qs, redis_site,user_table )
    #
    # Adding chains
    #

    cf = CF_Base_Interpreter()
    add_eto_chains(mqtt_devices, cf)
    #
    # Executing chains
    #
    
    cf.execute()

else:
  pass
  

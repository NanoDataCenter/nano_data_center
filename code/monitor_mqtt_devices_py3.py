

from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers

class Eto_Management(object):

   def __init__(self):
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
    
    eto = construct_eto_instance(qs, redis_site,user_table )
    #
    # Adding chains
    #

    cf = CF_Base_Interpreter()
    add_eto_chains(eto, cf)
    #
    # Executing chains
    #
    
    cf.execute()

else:
  pass
  

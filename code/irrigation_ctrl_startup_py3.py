

if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json
    import datetime
    import os
    import copy
   
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
    from redis_support_py3.load_files_py3 import APP_FILES
    from redis_support_py3.load_files_py3 import SYS_FILES
    from   py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
    from   py_cf_new_py3.cluster_control_py3 import Cluster_Control
    from   irrigation_control_py3.Incomming_Queue_Management_py3 import Incomming_Queue_Management
   
    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
                            
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGIGATION_SCHEDULING_CONTROL_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)
    package = package_sources[0]    
    data_structures = package["data_structures"]
    generate_handlers = Generate_Handlers(package,redis_site)
    redis_handle = generate_handlers.get_redis_handle()    
    app_files        =  APP_FILES(redis_handle,redis_site)     
    sys_files        =  SYS_FILES(redis_handle,redis_site)
    ds_handlers = {}
    ds_handlers["IRRIGATION_PAST_ACTIONS"] = generate_handlers.construct_redis_stream_writer(data_structures["IRRIGATION_PAST_ACTIONS"] )
    ds_handlers["IRRIGATION_CURRENT"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_CURRENT"] )
    ds_handlers["IRRIGATION_JOB_SCHEDULING"] = generate_handlers. construct_job_queue_server(data_structures["IRRIGATION_JOB_SCHEDULING"] )
    ds_handlers["IRRIGATION_PENDING"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_PENDING"] )
    ds_handlers["IRRIGATION_CONTROL"] = generate_handlers.construct_hash(data_structures["IRRIGATION_CONTROL"])
    ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"REBOOT","level":"RED"})
   
    query_list = []
    query_list = qs.add_match_terminal( query_list,relationship="IRRIGATION_ETO_CONTROL",label="IRRIGATION_ETO_CONTROL" )
    control_field, control_field_nodes = qs.match_list(query_list)
    eto_control_field = control_field_nodes[0] 

   
    remote_classes = None #construct_classes_py3.Construct_Access_Classes(io_server_ip,io_server_port)
    io_control  = None #  IO_Control(gm,remote_classes, redis_old_handle,redis_new_handle,eto_control_field)
     
    cf = CF_Base_Interpreter()
    cluster_control = Cluster_Control(cf)   
    Incomming_Queue_Management( cf = cf,
                                    handlers = ds_handlers,
                                    app_files = app_files,
                                    sys_files = sys_files,
                                    eto_control_field = eto_control_field)
    #
    #  Instanciate Sub modules
    #  
    #  Instanciate sub modules
    #     Incomming job queue
    #     Job Dispacther
    #     Job Workers
    #         
    
    try:
       
       cf.execute()
    except Exception as tst:
      #
      #Deleting current irrigation job to prevent circular reboots
      #
      ds_handlers["IRRIGATION_CURRENT"].delete_all()
      ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"IRRIGATION_CONTROLLER_EXCEPTION","details":tst,"level":"RED"})
      print("tst",tst)
      raise
     



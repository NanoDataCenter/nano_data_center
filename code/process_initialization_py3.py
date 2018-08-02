import time
import json
import redis
import subprocess
from subprocess import Popen, check_output
import shlex
import os
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
import msgpack
import pickle
import zlib
import sys

def run_process_to_completion_no_log(command_string ):

       try:
          command_string = "python3  " + command_string
          command_parameters = shlex.split(command_string)
          temp_name = command_parameters[-1]
          
          temp_name = temp_name.replace(".","_")
          temp_name = temp_name.split("/")[-1]
          
         
          error_file = "/tmp/"+temp_name+".err"
          
               
          print("error_file",error_file)
          print("command_parameters",command_parameters)
          process_handle = Popen(command_parameters, stderr=open(error_file,'w' ))
          process_handle.wait()        
          return_value = True
       except :
           return_value = False
           raise
           
       with open(error_file, 'r') as myfile:
           data=myfile.read()
       if data != None:
           
           data = data.encode()
           crc = zlib.crc32(data)
           data = zlib.compress(data)
       else:
            crc = 0
            data = ""
 
       return return_value,crc, data
 



  

if __name__ == "__main__":
   
 
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   site_data = json.loads(data)
   results = []
   for i in range(1,len(sys.argv)):
      results.append( [run_process_to_completion_no_log(sys.argv[i]), sys.argv[i]])
      
      
   print("results",results)
   
   
   qs = Query_Support( redis_server_ip = site_data["host"], redis_server_port=site_data["port"], db = site_data["graph_db"] )
   
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_terminal(query_list,relationship="PROCESS_INITIALIZATION")
   initialization_sets, initialization_nodes = qs.match_list(query_list)
   
   initialization_list = initialization_nodes[0]["command_list"] 
   
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "DATA_STRUCTURES" )
  
   package_sets, package_nodes = qs.match_list(query_list)  
   
   data_structures = package_nodes[0]["data_structures"]
   generate_handlers = Generate_Handlers(package_nodes[0],site_data)
   ds_handlers = {}
   ds_handlers["ERROR_STREAM"]        = generate_handlers.construct_stream_writer(data_structures["ERROR_STREAM"])
   
   ds_handlers["ERROR_STREAM"].push( data = { "script":"Reboot","crc":0, "error_output" : "Process Manager is Rebooting" } )

   for i in results:
      print(i)
      ds_handlers["ERROR_STREAM"].push( data = { "script":i[1],"crc":i[0][1], "error_output" : i[0][2] } )
      
   
   
   for j in  initialization_list:
        i = j["file"]
        results.append( [run_process_to_completion_no_log(i), i])

   for i in results:
      print(i)
      ds_handlers["ERROR_STREAM"].push( data = { "script":i[1],"crc":i[0][1], "error_output" : i[0][2] } )
       
       
       
 
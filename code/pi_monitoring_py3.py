# 
#
# File: utilities.py
#
#
#
#


import datetime
import time
import string
import math
import redis
import base64
import json
import msgpack
import os
import copy

from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers



#import rabbit_cloud_status_publish_py3

#
#
# File: linux_acquisition.py
# Monitors status of raspberry pi
#
#


class PI_MONITOR( object ):

   def __init__( self, package_node,generate_handlers ):
       data_structures = package_node["data_structures"]
       self.ds_handlers = {}
       self.ds_handlers["FREE_CPU"]           = generate_handlers.construct_stream_writer(data_structures["FREE_CPU"])
       self.ds_handlers["RAM"]                = generate_handlers.construct_stream_writer(data_structures["RAM"])
       self.ds_handlers["DISK_SPACE"]         = generate_handlers.construct_stream_writer(data_structures["DISK_SPACE"])
       self.ds_handlers["TEMPERATURE"]        = generate_handlers.construct_stream_writer(data_structures["TEMPERATURE"])
       self.ds_handlers["PROCESS_VSZ"]        = generate_handlers.construct_stream_writer(data_structures["PROCESS_VSZ"])
       self.ds_handlers["PROCESS_RSS"]        = generate_handlers.construct_stream_writer(data_structures["PROCESS_RSS"])
       self.ds_handlers["PROCESS_STATE"]        = generate_handlers.construct_stream_writer(data_structures["PROCESS_STATE"])       
       self.construct_chains()

   def measure_temperature( self, *args ):
      temp = os.popen("vcgencmd measure_temp").readline()
      temp = temp.replace("temp=","").replace("'C\n","")
      temp = float(temp)
      temp = (9.0/5.0*temp)+32.

      return temp


   def measure_disk_space( self, *args ):
       f = os.popen("df")
       data = f.read()
       f.close()
       lines = data.split("\n")
       
       return_value = {}
       for i in range(0,len(lines)):
           if i == 0:
               continue
           fields = lines[i].split()
          
           if len(fields) > 3:
              percent = float( fields[2] )/float( fields[1] )
              temp_value =  "disk "+str(fields[0])+ "   used % : "+str(percent)   
              return_value[str(fields[0])] = percent
       return return_value

   def measure_processor_ram( self , *args ):
       f = os.popen("free -l")
       data = f.readlines()
       f.close()
       return data

   def measure_processor_load( self , *args  ):
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("ps -aux | grep python")
       data = f.read()
       f.close()
       lines = data.split("\n")
       
       for i in range(0,len(lines)):

           fields = lines[i].split()
           temp_value = {}
           if len(fields) <= len(headers):
               for i in range(0,len(fields)):
                   temp_value[headers[i]] = fields[i]
               
               if "PARAMETER1" in temp_value:
                 if temp_value["COMMAND"] == "python3":
                    temp_dict = {}
                    temp_dict["python_process"] = temp_value["PARAMETER1"]
                    temp_dict["pid"]            = temp_value["PID"]
                    temp_dict["RSS"]            = temp_value["RSS"]
                    temp_dict["VSZ"]            = temp_value["VSZ"]
                    temp_dict["%CPU"]           = temp_value["%CPU"]
                   
                    self.ds_handlers["PROCESS_STATE"].add_compress(data = temp_dict)

       

   def vsz_handler( self , *args  ):
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("ps -aux | grep python")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = {}
       for i in range(0,len(lines)):

           fields = lines[i].split()
           temp_value = {}
           if len(fields) <= len(headers):
               for i in range(0,len(fields)):
                   temp_value[headers[i]] = fields[i]
               
               if "PARAMETER1" in temp_value:
                   if temp_value["COMMAND"] == "python3":
                       key = temp_value["PARAMETER1"]
                       return_value[key] = temp_value["VSZ"]

       return return_value
       
   def rss_handler( self , *args  ):
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("ps -aux | grep python3")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = {}
       for i in range(0,len(lines)):
     
           
           fields = lines[i].split()
           temp_value = {}
           if len(fields) <= len(headers):
               for i in range(0,len(fields)):
                   temp_value[headers[i]] = fields[i]
               
               if "PARAMETER1" in temp_value:
                   if temp_value["COMMAND"] == "python3":
                       key = temp_value["PARAMETER1"]
                       return_value[key] = temp_value["RSS"]

       return return_value

   def measure_free_cpu( self,*args):
       headers = [ "Time","cpu","%user" , "%nice", "%system", "%iowait" ,"%steal" ,"%idle" ]
       return_value = {}
       f = os.popen("sar -u 60 1 ")
       data = f.readlines()
       fields = data[-1].split()
       for i in range(2,len(fields)):
           return_value[headers[i]] = float(fields[i])
       return return_value

   def proc_memory( self, *args ):
       f = os.popen("cat /proc/meminfo ")
       
       data_list = f.readlines()
       return_value = {}
       for i in data_list:
          items = i.split(":")
          key = items[0].strip()
          values = items[1].split("kB")
          return_value[key] = values[0].strip()
       return return_value
       
  
   def assemble_free_cpu( self, *args ):
       data = self.measure_free_cpu()
       self.ds_handlers["FREE_CPU"].add_compress(data = data)
       return "DISABLE"
 
   def assemble_ram( self, *args ):
       memory_dict = self.proc_memory()
       self.ds_handlers["RAM"].add_compress( data = memory_dict)
       return "DISABLE"
       
       
   def assemble_temperature( self, *args):
       temp_f = self.measure_temperature()
       self.ds_handlers["TEMPERATURE"].add_compress(data = {"TEMP_F":temp_f})
       return "DISABLE"

       
   def assemble_vsz(self,*args):
       data = self.vsz_handler()
       self.ds_handlers["PROCESS_VSZ"].add_compress( data =  data )
       return "DISABLE"
       
   def assemble_rss(self,*args):
       data = self.rss_handler()
       self.ds_handlers["PROCESS_RSS"].add_compress( data = data )
       return "DISABLE"
       
   def assemble_process_state(self,*args):
       self.measure_processor_load()
       return "DISABLE"
      
   def assemble_disk_space(self,*args):
      data = self.measure_disk_space()     
      self.ds_handlers["DISK_SPACE"].add_compress(data = data)
      return "DISABLE" 
      
   def construct_chains(self,*args):

       cf = CF_Base_Interpreter()
       cf.define_chain("pi_monitor", True)
       cf.insert.log("starting processor measurements")
       cf.insert.one_step(self.assemble_free_cpu)
       cf.insert.one_step(self.assemble_ram)
       cf.insert.one_step(self.assemble_temperature)
       cf.insert.one_step(self.assemble_vsz)
       cf.insert.one_step(self.assemble_rss)
       cf.insert.one_step(self.assemble_process_state)
       cf.insert.one_step(self.assemble_disk_space)
       cf.insert.log("ending processor measurements")
       cf.insert.wait_event_count( event = "MINUTE_TICK",count = 15)
       cf.insert.reset()
       cf.execute()
        
    
if __name__ == "__main__":
   
   
    #
    #
    # Read Boot File
    # expand json file
    # 
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   site_data = json.loads(data)

  
   qs = Query_Support( redis_server_ip = site_data["host"], redis_server_port=site_data["port"], db = site_data["graph_db"] ) 
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "SYSTEM_MONITORING" )
                                        
                                        
                                           
   package_sets, package_nodes = qs.match_list(query_list)  
  

   generate_handlers = Generate_Handlers(package_nodes[0],site_data)
   pi_monitor = PI_MONITOR(package_nodes[0],generate_handlers)
   
   
else:
   pass



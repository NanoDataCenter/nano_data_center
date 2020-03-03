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
import re

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

   def __init__( self, package_node,generate_handlers,site_node ):
       data_structures = package_node["data_structures"]
       self.ds_handlers = {}
       self.ds_handlers["FREE_CPU"]           = generate_handlers.construct_stream_writer(data_structures["FREE_CPU"])
       self.ds_handlers["RAM"]                = generate_handlers.construct_stream_writer(data_structures["RAM"])
       self.ds_handlers["DISK_SPACE"]         = generate_handlers.construct_stream_writer(data_structures["DISK_SPACE"])
       self.ds_handlers["TEMPERATURE"]        = generate_handlers.construct_stream_writer(data_structures["TEMPERATURE"])
       self.ds_handlers["PROCESS_VSZ"]        = generate_handlers.construct_stream_writer(data_structures["PROCESS_VSZ"])
       self.ds_handlers["PROCESS_RSS"]        = generate_handlers.construct_stream_writer(data_structures["PROCESS_RSS"])
       self.ds_handlers["PROCESS_CPU"]        = generate_handlers.construct_stream_writer(data_structures["PROCESS_CPU"])  
       self.ds_handlers["CPU_CORE"]        = generate_handlers.construct_stream_writer(data_structures["CPU_CORE"])  
       self.ds_handlers["SWAP_SPACE"]        = generate_handlers.construct_stream_writer(data_structures["SWAP_SPACE"])  
       self.ds_handlers["IO_SPACE"]        = generate_handlers.construct_stream_writer(data_structures["IO_SPACE"])  
       self.ds_handlers["BLOCK_DEV"]        = generate_handlers.construct_stream_writer(data_structures["BLOCK_DEV"])  
       self.ds_handlers["CONTEXT_SWITCHES"]        = generate_handlers.construct_stream_writer(data_structures["CONTEXT_SWITCHES"])  
       self.ds_handlers["RUN_QUEUE"]        = generate_handlers.construct_stream_writer(data_structures["RUN_QUEUE"])  
       self.ds_handlers["DEV"]        = generate_handlers.construct_stream_writer(data_structures["DEV"])  
       self.ds_handlers["SOCK"]        = generate_handlers.construct_stream_writer(data_structures["SOCK"])  
       self.ds_handlers["TCP"]        = generate_handlers.construct_stream_writer(data_structures["TCP"])  
       self.ds_handlers["UDP"]        = generate_handlers.construct_stream_writer(data_structures["UDP"])  
       self.site_node = site_node

       
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
                    
                    self.ds_handlers["PROCESS_STATE"].push(data = temp_dict,local_node = self.site_node)

       

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
       
   def cpu_handler( self , *args  ):
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
                       return_value[key] = temp_value["%CPU"]
       
       return return_value

   def measure_free_cpu( self,*args):
       headers = [ "Time","cpu","%user" , "%nice", "%system", "%iowait" ,"%steal" ,"%idle" ]
       return_value = {}
       f = os.popen("sar -u 60 1 ")
       data = f.readlines()
       f.close()
       print("data",data)
       fields = data[-1].split()
       for i in range(2,len(fields)):
           return_value[headers[i]] = float(fields[i])
       
       return return_value

   def proc_memory( self, *args ):
       f = os.popen("cat /proc/meminfo ")
       
       data_list = f.readlines()
       f.close()
       return_value = {}
       for i in data_list:
          items = i.split(":")
          key = items[0].strip()
          values = items[1].split("kB")
          return_value[key] = values[0].strip()
       
       return return_value
       
  
   def assemble_free_cpu( self, *args ):
       data = self.measure_free_cpu()
       self.ds_handlers["FREE_CPU"].push(data = data,local_node = self.site_node)
       
       return "DISABLE"
 
   def assemble_ram( self, *args ):
       memory_dict = self.proc_memory()
       self.ds_handlers["RAM"].push( data = memory_dict,local_node = self.site_node)
       
       return "DISABLE"
       
       
   def assemble_temperature( self, *args):
       temp_f = self.measure_temperature()
       self.ds_handlers["TEMPERATURE"].push(data = {"TEMP_F":temp_f},local_node = self.site_node)
       
       return "DISABLE"

       
   def assemble_vsz(self,*args):
       data = self.vsz_handler()
       self.ds_handlers["PROCESS_VSZ"].push( data =  data,local_node = self.site_node )
       return "DISABLE"
       
   def assemble_rss(self,*args):
       data = self.rss_handler()
       self.ds_handlers["PROCESS_RSS"].push( data = data,local_node = self.site_node )
       return "DISABLE"
       
   def assemble_cpu_handler(self,*args):
       data = self.cpu_handler()
       self.ds_handlers["PROCESS_CPU"].push( data = data,local_node = self.site_node )
       return "DISABLE"
      
   def assemble_disk_space(self,*args):
      data = self.measure_disk_space()     
      self.ds_handlers["DISK_SPACE"].push(data = data,local_node = self.site_node)
      return "DISABLE" 
 
   def assemble_cpu_core(self,*args):
       self.parse_multi_line("sar -P ALL 10 1","CPU_CORE",-1)
       return "DISABLE" 
      
   def assemble_swap_space(self,*args):
       self.parse_one_line("sar -S 1 1","SWAP_SPACE")     
       return "DISABLE" 
      
   def assemble_io_space(self,*args):
        self.parse_one_line("sar -w 1 1","IO_SPACE")        
        return "DISABLE" 
      
   def assemble_block_io(self,*args):
        self.parse_multi_line("sar -d  3 1","BLOCK_DEV",-1)
        return "DISABLE"       

   def assemble_context_switches(self,*args):
        self.parse_one_line("sar -w 1 1","CONTEXT_SWITCHES")   
        return "DISABLE" 

   def assemble_run_queue(self,*args):
        self.parse_one_line("sar -q 3 1","RUN_QUEUE")   
        return "DISABLE" 
 
   def assemble_net_dev(self,*args):
       self.parse_multi_line("sar -n DEV  3 1","DEV",-1)
       return "DISABLE" 

   def assemble_net_socket(self,*args):
        self.parse_one_line("sar -n SOCK 3 1","SOCK")
        return "DISABLE" 

   def assemble_net_tcp(self,*args):
        self.parse_one_line("sar -n TCP 3 1","TCP")
        return "DISABLE" 
        
   def assemble_net_udp(self,*args):
        self.parse_one_line("sar -n UDP 3 1","UDP")
        return "DISABLE" 


   def parse_multi_line(self,sar_command,stream_key,ref_index = -1):
   

       f = os.popen(sar_command)
       data = f.read()
       f.close()
       lines = data.split("\n")
       i = 3
       data = {}
       while True:
          line = lines[i]
          if line == "":
             break
          line = re.sub(' +',' ',line)
          fields = line.split(" ")
          
          key = fields[1]
          value = fields[ref_index]
          data[key] = float(float(value))
          i = i+1

       print("data",data)   
       self.ds_handlers[stream_key].push(data = data,local_node = self.site_node)

   def parse_one_line(self, sar_command, stream_field ):
        f = os.popen(sar_command)
        data = f.read()
        f.close()

        lines = data.split("\n")
        line = lines[2]
        line = re.sub(' +',' ',line)
        fields_keys = line.split(" ")
        line = lines[3]
        line = re.sub(' +',' ',line)
        fields_data = line.split(" ")
        fields_data.pop(0)
        fields_keys.pop(0)
        data = {}
        for i in range(0,len(fields_keys)):
           data[fields_keys[i]] = float(fields_data[i])
       
        print("data",data)
          
        self.ds_handlers[stream_field].push(data = data,local_node = self.site_node)
 
   def construct_chains(self,*args):

       cf = CF_Base_Interpreter()
       cf.define_chain("pi_monitor", True)
       cf.insert.log("starting processor measurements")

       cf.insert.one_step(self.assemble_free_cpu)
       cf.insert.one_step(self.assemble_ram)
       cf.insert.one_step(self.assemble_temperature)
       cf.insert.one_step(self.assemble_vsz)
       cf.insert.one_step(self.assemble_rss)
       cf.insert.one_step(self.assemble_cpu_handler)
       cf.insert.one_step(self.assemble_disk_space)
       cf.insert.one_step(self.assemble_cpu_core)
       cf.insert.one_step(self.assemble_swap_space)
       cf.insert.one_step(self.assemble_io_space)
       cf.insert.one_step(self.assemble_block_io)

       cf.insert.one_step(self.assemble_context_switches)
       cf.insert.one_step(self.assemble_run_queue)
       cf.insert.one_step(self.assemble_net_dev)
       cf.insert.one_step(self.assemble_net_socket)
       cf.insert.one_step(self.assemble_net_tcp)
       cf.insert.one_step(self.assemble_net_udp)
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

  
   qs = Query_Support( site_data ) 
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "SYSTEM_MONITORING" )
                                        
                                        
                                           
   package_sets, package_nodes = qs.match_list(query_list)  
  
   
   generate_handlers = Generate_Handlers(package_nodes[0],qs)
   pi_monitor = PI_MONITOR(package_nodes[0],generate_handlers,site_data["local_node"])
   
   
else:
   pass



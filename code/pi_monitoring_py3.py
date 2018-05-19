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
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter

import os
import copy
import load_files_py3
#import rabbit_cloud_status_publish_py3
from   io_control_py3 import io_controller_py3
from   io_control_py3 import construct_classes_py3
from   io_control_py3 import new_instrument_py3

#
#
# File: linux_acquisition.py
# Monitors status of raspberry pi
#
#
#add cat /proc/meminfo

from data_acquisition_py3 import data_scheduling_py3
from data_acquisition_py3.data_scheduling_py3 import Data_Acquisition
from data_acquisition_py3.data_scheduling_py3 import add_chains
from data_acquisition_py3.data_scheduling_py3 import construct_class

import os
class PI_Status( object ):

   def __init__( self, redis_handle ):
       self.redis_handle = redis_handle

   def measure_temperature( self, tag, value, parameters ):
      temp = os.popen("vcgencmd measure_temp").readline()
      temp = temp.replace("temp=","").replace("'C\n","")
      temp = float(temp)
      temp = (9.0/5.0*temp)+32.

      return temp


   def measure_disk_space( self, tag, value, parameters  ):
       f = os.popen("df")
       data = f.read()
       f.close()
       lines = data.split("\n")
       
       return_value = []
       for i in range(0,len(lines)):
           if i == 0:
               continue
           fields = lines[i].split()
          
           if len(fields) > 3:
              percent = float( fields[2] )/float( fields[1] )
              temp_value =  "disk "+str(fields[0])+ "   used % : "+str(percent)   
              return_value.append( temp_value )
       return return_value

   def measure_processor_ram( self ,tag, value, parameters ):
       f = os.popen("free -l")
       data = f.readlines()
       f.close()
       return data

   def measure_processor_load( self ,tag, value, parameters  ):
       headers = [ "USER","PID","%CPU","%MEM","VSZ","RSS","TTY","STAT","START","TIME","COMMAND", "PARAMETER1", "PARAMETER2" ]
       f = os.popen("ps -aux | grep python")
       data = f.read()
       f.close()
       lines = data.split("\n")
       return_value = []
       for i in range(0,len(lines)):

           if i == 0:
               continue
           fields = lines[i].split()
           temp_value = {}
           if len(fields) <= len(headers):
               for i in range(0,len(fields)):
                   temp_value[headers[i]] = fields[i]
               
               if "PARAMETER1" in temp_value:
                 
                 temp_dict = {}
                 temp_dict["python_process"] = temp_value["PARAMETER1"]
                 temp_dict["pid"]            = temp_value["PID"]
                 temp_dict["RSS"]            = temp_value["RSS"]
                 temp_dict["VSZ"]            = temp_value["VSZ"]
                 temp_dict["%CPU"]           = temp_value["%CPU"]
                 return_value.append( json.dumps(temp_dict, sort_keys = True, indent = 5) )

       return return_value

   def log_redis_info( self, tag,value,parameters):
        data = self.redis_handle.info()
        print("data",data)
        return_value= []
        try:
           return_value.append("used_memory_human "+ str(data["used_memory_human"]))
           return_value.append("uptime_in_seconds "+ str(data["uptime_in_seconds"]))
           return_value.append("total_connections_received "+ str(data["total_connections_received"]))
           return_value.append("config_file "+ str(data["config_file"]))
           return_value.append("aof_last_write_status "+ str(data["aof_last_write_status"]))
           return_value.append("total_commands_processed "+ str(data["total_commands_processed"]))
           return_value.append("used_memory_rss_human "+ str(data["used_memory_rss_human"]))
           return_value.append("db0:keys "+ json.dumps(data["db0"]))
           return_value.append("db1:keys "+ json.dumps(data["db1"]))
           return_value.append("db2:keys "+ json.dumps(data["db2"]))
           return_value.append("db3:keys "+ json.dumps(data["db3"]))
           return_value.append("db11:keys "+ json.dumps(data["db11"]))
           return_value.append("db12:keys "+ json.dumps(data["db12"]))
           return_value.append("db14:keys "+ json.dumps(data["db14"]))
           return_value.append("db15:keys "+ json.dumps(data["db15"]))
        except:
            pass
        return return_value

   def measure_free_cpu( self, tag, value, parameters):
       headers = [ "Time","cpu","%user" , "%nice", "%system", "%iowait" ,"%steal" ,"%idle" ]
       return_value = []
       f = os.popen("sar -u 360 1 ")
       data = f.readlines()
       fields = data[-1].split()
       print(data)
       print(fields)
       for i in range(0,len(fields)):
           return_value.append(headers[i]+"    "+str(fields[i]))
       return return_value

   def proc_memory( self, tag, value, parameters):
       f = os.popen("cat /proc/meminfo ")
       data = f.readlines()
       return data

def construct_linux_acquisition_class( redis_handle, gm, io_server,io_server_port ):
   pi_stat = PI_Status( redis_handle )
   gm.add_cb_handler("pi_temperature",       pi_stat.measure_temperature )  
   gm.add_cb_handler("python_processes",    pi_stat.measure_processor_load )
   gm.add_cb_handler("linux_disk",     pi_stat.measure_disk_space )
   gm.add_cb_handler("linux_redis",    pi_stat.log_redis_info )
   gm.add_cb_handler("linux_memory",   pi_stat.measure_processor_ram)
   gm.add_cb_handler("free_cpu",   pi_stat.measure_free_cpu)
   gm.add_cb_handler("proc_mem",   pi_stat.proc_memory)
   instrument = new_instrument_py3.Modbus_Instrument()

   
   remote_classes = construct_classes_py3.Construct_Access_Classes(io_server,io_server_port)
   fifteen_store   =  []
   minute_store    =  []
   hour_store      =  list(gm.match_terminal_relationship(  "LINUX_HOUR_ACQUISTION"))[0]
   daily_store     =  []
   fifteen_list   =  []
   minute_list     =  []     
   hour_list       =  list(gm.match_terminal_relationship( "LINUX_HOUR_ELEMENT" ))
   daily_list      =  []

   return  construct_class( redis_handle,
                     gm,instrument,
                     remote_classes,
                     fifteen_store,
                     minute_store,
                     hour_store,
                     daily_store,
                     fifteen_list,
                     minute_list,
                     hour_list,
                     daily_list )
                     
    
if __name__ == "__main__":

   import time
   from redis_graph_py3.farm_template_py3 import Graph_Management 



   gm =Graph_Management("PI_1","main_remote","LaCima_DataStore")
  
   data_store_nodes = gm.find_data_stores()
   io_server_nodes  = gm.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12 , decode_responses=True)



   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]
   # find ip and port for ip server
   status_server =  gm.match_terminal_relationship("RABBITMQ_STATUS_QUEUE")[0]
   queue_name     = status_server[ "queue"]

   #status_queue_class = rabbit_cloud_status_publish_py3.Status_Queue(redis_handle, queue_name ) 
   
   construct_linux_acquisition_class= construct_linux_acquisition_class( redis_handle, gm, io_server_ip, io_server_port )

   

   #
   # Adding chains
   #
   cf = CF_Base_Interpreter()
   cf.define_chain("test",False)
   cf.insert.log( "test chain start")
   cf.insert.send_event("MINUTE_TICK",1 )
   cf.insert.wait_event_count( event = "TIME_TICK", count = 1 )
   cf.insert.send_event( "HOUR_TICK",1  )
   cf.insert.wait_event_count( event = "TIME_TICK", count = 1 )
   cf.insert.send_event("DAY_TICK", 1 )
   cf.insert.terminate()

   add_chains(cf, construct_linux_acquisition_class)

   print( "starting chain flow" )

   cf.execute()


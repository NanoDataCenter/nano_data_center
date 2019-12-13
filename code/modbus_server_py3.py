
import time
import base64
from datetime import datetime
import sys
import json
from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from    modbus_redis_server_py3.modbus_serial_ctrl_py3  import ModbusSerialCtrl
from   modbus_redis_server_py3.msg_manager_py3 import MessageManager
from     modbus_redis_server_py3.rs485_mgr_py3  import RS485_Mgr  
from    modbus_redis_server_py3.modbus_serial_ctrl_py3  import ModbusSerialCtrl
from   modbus_redis_server_py3.msg_manager_py3 import MessageManager
from   redis_support_py3.redis_rpc_server_py3 import Redis_Rpc_Server
        
class Modbus_Server( object ):
    
   def __init__( self, redis_rpc_server,interfaces, device_dictionary,msg_handler):  # fill in proceedures
       self.msg_handler = msg_handler
  

       self.statistic_handler = Statistic_Handler(redis_handle, redis_rpc_handle,master_remote_dictionary,logging_start, redis_rpc_queue)
       self.redis_rpc_server = redis_rpc_server
       self.redis_rpc_server.register_call_back( modbus_key, self.process_modbus_message)
       self.redis_rpc_server.register_call_back( ping_key, self.process_ping_message)
       self.redis_rpc_server.start()
 
 
   def process_ping_message(self, address):    
        temp = self.msg_handler.ping_devices([address])
        return temp[0]["result"]        
        
   def process_modbus_message( self,input_msg ):

       address = input_msg[0]
       
       self.statistic_handler.process_start_message( address )
      
       
       
      
       failure, retries, output_message = self.msg_handler.process_msg( input_msg )
       
       if failure != 0:
           output_msg = "@"
           self.statistic_handler.log_bad_message( address, retries )
       else:
            self.statistic_handler.log_good_message( address, retries )
       self.statistic_handler.process_end_message()
       return output_message
        

   def process_null_msg( self ):
       self.statistic_handler.process_null_message()



def contruct_device_map(interfaces):
   return_value = {}
   for i,item in interfaces.items():
      for j in item["remote_dict"].keys():
        return_value[j]=i
   return return_value

def find_remotes(qs,link_name):
   return_value = {}
   query_list = []      
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=plc_server_name )
   query_list = qs.add_match_relationship( query_list, relationship = "IO_LINK",label=link_name) 
   query_list = qs.add_match_terminal( query_list,  relationship = "REMOTE_UNIT")
                                                                               
   remote_sets, remote_sources = qs.match_list(query_list)
   for i in remote_sources:

      return_value[i["modbus_address"]] = i["parameters"]
 
   return return_value

if __name__ == "__main__":
   plc_server_name =  sys.argv[1]
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   redis_site = json.loads(data)
   qs = Query_Support( redis_site )
   query_list = []   
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=plc_server_name )
   query_list = qs.add_match_terminal( query_list, 
                                           relationship = "PACKAGE", 
                                           property_mask={"name":"PLC_SERVER_DATA"} )
                                           
   package_sets, package_sources = qs.match_list(query_list)
       
   package = package_sources[0] 
   generate_handlers = Generate_Handlers(package,qs)   
   data_structures = package["data_structures"]
   rpc_server_handle = generate_handlers.construct_rpc_sever(data_structures["PLC_RPC_SERVER"] )
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=plc_server_name )
   query_list = qs.add_match_terminal( query_list, relationship = "IO_LINK") 
                                     
   serial_sets, serial_sources = qs.match_list(query_list)
   
   interfaces = {}
   
   for item in serial_sources:
       
       item["remote_dict"] = find_remotes(qs,item["name"])
       interfaces[item["name"]]= item
     
   device_map = contruct_device_map(interfaces)
   rs485_interface =   RS485_Mgr() 
   msg_mgr = MessageManager()
 for i,item in serial_links.items():
       remote_dict = setup.find_and_register_remotes( item , rs485_interface, msg_mgr )
       temp_dict = {}
       temp_dict[i] = item
       modbus_serial_ctrl  = ModbusSerialCtrl( temp_dict, remote_dict, msg_mgr)
       for j,k in remote_dict.items():
           msg_mgr.add_device( k["modbus_address"], modbus_serial_ctrl )  
           master_remote_dictionary.append(k["modbus_address"])           
       msg_mgr.add_device( 255,    redis_handle) 
   
   print(msg_mgr.ping_devices([100]))
  
   Modbus_Server( redis_handle, redis_rpc_handle,msg_mgr, server_dict, master_remote_dictionary,"modbus_relay","ping_message"  )    
   
   
   
  
'''   
   
   for i,item in serial_links.items():
       remote_dict = setup.find_and_register_remotes( item , rs485_interface, msg_mgr )
       temp_dict = {}
       temp_dict[i] = item
       modbus_serial_ctrl  = ModbusSerialCtrl( temp_dict, remote_dict, msg_mgr)
       for j,k in remote_dict.items():
           msg_mgr.add_device( k["modbus_address"], modbus_serial_ctrl )  
           master_remote_dictionary.append(k["modbus_address"])           
       msg_mgr.add_device( 255,    redis_handle) 
   
   print(msg_mgr.ping_devices([100]))
  
   Modbus_Server( redis_handle, redis_rpc_handle,msg_mgr, server_dict, master_remote_dictionary,"modbus_relay","ping_message"  )       
'''       
'''   
   from redis_graph_py3.farm_template_py3 import Graph_Management

   
   
   server_index = 0
   
   server_name =  sys.argv[1]
   
   gm = Graph_Management("PI_1","main_remote","LaCima_DataStore")
   setup  = Setup_Remote_Devices(gm)
   server_dict = setup.find_server( server_name )
   serial_links      = setup.find_serial_links( server_name )
   
  
   rs485_interface =   RS485_Mgr() 
   msg_mgr = MessageManager()
   redis_rpc_handle   =  redis.StrictRedis(  server_dict["ip"] , 6379, server_dict["redis_rpc_db"],decode_responses=True )
   redis_handle       =  redis.StrictRedis(  server_dict["ip"] , 6379, 0,decode_responses=True )
   master_remote_dictionary = []
   for i,item in serial_links.items():
       remote_dict = setup.find_and_register_remotes( item , rs485_interface, msg_mgr )
       temp_dict = {}
       temp_dict[i] = item
       modbus_serial_ctrl  = ModbusSerialCtrl( temp_dict, remote_dict, msg_mgr)
       for j,k in remote_dict.items():
           msg_mgr.add_device( k["modbus_address"], modbus_serial_ctrl )  
           master_remote_dictionary.append(k["modbus_address"])           
       msg_mgr.add_device( 255,    redis_handle) 
   
   print(msg_mgr.ping_devices([100]))
  
   Modbus_Server( redis_handle, redis_rpc_handle,msg_mgr, server_dict, master_remote_dictionary,"modbus_relay","ping_message"  )
    
'''
'''
class No_Server_In_Graph(Exception):
    """Base class for exceptions in this module."""
    pass

class Statistic_Handler( object ):
    
    def __init__(self,redis_handle,redis_rpc_queue, remote_units,graph_key, rpc_queue ):

        # copy instantiation parameters
        self.redis_handle = redis_handle
        self.remote_units = remote_units

        self.time_base = time.time()
        self.rpc_queue = rpc_queue
        self.graph_key = graph_key
        
        
        
        
        self.queue_history_length =  1500
        self.redis_current_key = self.graph_key+":RECENT_DATA"
        self.redis_hour_key    = self.graph_key+":HOUR_DATA"
        self.redis_server_queue = self.redis_hour_key+":SERVER_QUEUE"
        self.redis_basic_queue = self.redis_hour_key+":BASIC_STATS"
        self.redis_remote_queue_header = self.redis_hour_key+":REMOTES"        
        self.redis_remote_queues = {}
        for i in remote_units:
            self.redis_remote_queues[i] = self.redis_remote_queue_header+":"+str(i)
            
            
        for i in [  self.redis_current_key,self.redis_hour_key,self.redis_basic_queue]: 
            self.verify_list(i)
        for i, item in self.redis_remote_queues.items():
            self.verify_list(i)
            
        self.initialize_logging_data()
 
    def update_current_state(self):
        data = self.update_current_state_a()
 
        data["remotes"] = {}
        for i in self.remote_units:           
            data["remotes"][i] = self.remote_data[i]
        self.redis_handle.set(self.redis_current_key, json.dumps(data ) )       
        return data
        
    def update_current_state_a(self):
        total_time = self.busy_time + self.idle_time
        if total_time == 0 :
            time_ratio = 0   
        else:
            time_ratio = ( self.busy_time *100)/total_time
        data = {}
        data["time_ratio"] = time_ratio
        data["counts"] = self.message_count
        data["losses"] = self.message_loss 
        data["retries"] = self.retries
        data["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
       
        
        return data
 


       
    def update_list( self, key, data ):
        self.redis_handle.lpush(key,data)
        self.redis_handle.ltrim(key,0,self.queue_history_length  )
       
    def verify_list( self, item ):
            if self.redis_handle.exists(item):
                if self.redis_handle.type(item) == "list":
                    pass                   
                else:
                    self.redis_handle.delete(item)              

        
    def initialize_logging_data( self ):
        self.hour = datetime.now().hour
        self.minute = datetime.now().minute
        #initial basic stuff
        self.time_stamp = datetime.now()
        self.busy_time = 0
        self.idle_time = 0
        self.message_count = 0
        self.message_loss = 0
        self.retries  = 0
        
        #initialize server queue stuff
        self.queue = {}
       
        #initialize remotes
        
        self.remote_data = {}
        for i in self.remote_units:
           item = {}
           item["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
           item["message_count"] = 0
           item["message_loss"] = 0
           item["retries"] = 0
           self.remote_data[i] = item
                
        
    def hour_rollover( self ):
        print("hour rollover")
        self.hour_basic_stuff()
        self.hour_remote_stuff()
        self.initialize_logging_data()
        
    def hour_basic_stuff( self ):
        data = self.update_current_state_a()
        self.update_list(self.redis_basic_queue, json.dumps(data ) )
 
    def hour_remote_stuff( self ):
        for i, item in self.remote_data.items():
           self.update_list(self.redis_remote_queues[i], json.dumps(item))
        

    def process_null_message( self ):

        temp = time.time()
        delta_t = temp - self.time_base
        self.time_base = temp
        self.idle_time = self.idle_time + delta_t
        if self.hour != datetime.now().hour:
        #if self.minute != datetime.now().minute:    
             self.hour_rollover()

        self.update_current_state()
        
        
        
    def process_start_message( self , modbus_address ):
       
        self.start_base = time.time()
      
        
         
    def process_end_message( self ):
        self.time_base = time.time()
        delta_t = self.time_base - self.start_base
        self.busy_time += delta_t
        if self.hour != datetime.now().hour:
             self.hour_rollover()
        self.update_current_state()
        
 
    def log_bad_message( self, modbus_address,retries ):
        self.message_count +=1
        self.message_loss += 1
        self.retries +=retries
        if modbus_address in self.remote_units:
            self.remote_data[modbus_address]["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
            self.remote_data[modbus_address]["message_count"] += 1
            self.remote_data[modbus_address]["message_loss"] += 1
            self.remote_data[modbus_address]["retries"] += retries

        
    def log_good_message( self, modbus_address,retries ):
        self.message_count +=1
        self.retries +=retries
        if modbus_address in self.remote_units:
            self.remote_data[modbus_address]["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
            self.remote_data[modbus_address]["message_count"] += 1
            self.remote_data[modbus_address]["retries"] += retries

        
class Modbus_Server( object ):
    
   def __init__( self, redis_handle, redis_rpc_handle,msg_handler, server_dict, master_remote_dictionary, modbus_key,ping_key ):  # fill in proceedures
       self.msg_handler = msg_handler
       redis_rpc_queue = server_dict["redis_rpc_key"]
       logging_start   = server_dict["logging_key"]

       self.statistic_handler = Statistic_Handler(redis_handle, redis_rpc_handle,master_remote_dictionary,logging_start, redis_rpc_queue)
       self.redis_rpc_server = Redis_Rpc_Server(redis_rpc_handle,redis_rpc_queue, self.process_null_msg, timeout_value = 5 )
       self.redis_rpc_server.register_call_back( modbus_key, self.process_modbus_message)
       self.redis_rpc_server.register_call_back( ping_key, self.process_ping_message)
       self.redis_rpc_server.start()
 
 
   def process_ping_message(self, address):    
        temp = self.msg_handler.ping_devices([address])
        return temp[0]["result"]        
        
   def process_modbus_message( self,input_msg ):
       input_msg = base64.b64decode(input_msg)
       #if input_msg[0] == 100:
       #   print(":".join("{:02x}".format(c) for c in input_msg))
       address = input_msg[0]
       
       self.statistic_handler.process_start_message( address )
      
       
       
      
       failure, retries, output_message = self.msg_handler.process_msg( input_msg )
       
       if failure != 0:
           output_msg = "@"
           self.statistic_handler.log_bad_message( address, retries )
       else:
            self.statistic_handler.log_good_message( address, retries )
       self.statistic_handler.process_end_message()
       return base64.b64encode(output_message).decode()
        

   def process_null_msg( self ):
       self.statistic_handler.process_null_message()
        
class Setup_Remote_Devices(object):
       def __init__( self, gm ):
           self.gm = gm
            
       def find_server( self, server_name ):
           server_list  = (self.gm.match_terminal_relationship( "UDP_IO_SERVER" ,property_values = {"name":server_name} ))           
           if len(server_list) == 0:
               raise No_Server_In_Graph
       
           self.server = server_list[0]
           return server_list[0]



       def find_serial_links( self, server_name ):
            self.search_nodes =    gm.match_relationship_list ( [["UDP_IO_SERVER",server_name]], starting_set = None, property_values = None, fetch_values = False )
            serial_set = gm.match_terminal_relationship("SERIAL_LINK",starting_set = self.search_nodes)
            return gm.to_dictionary( serial_set, "name", json_flag = False )
   
 
           
       def find_and_register_remotes( self, serial_link ,interface_handler, msg_mgr ):
        
            serial_link["handler"] = interface_handler
            
            name = serial_link["name"]
            serial_search_nodes =    gm.match_relationship_list ( [["SERIAL_LINK",name ]], starting_set = self.search_nodes, property_values = None, fetch_values = False )
            remote_lists = gm.match_terminal_relationship("REMOTE_UNIT",starting_set = serial_search_nodes)
            remote_dict = gm.to_dictionary( remote_lists, "name", json_flag = False)
            for j,k in remote_dict.items():
                 k["interface"] = name
            self.remotes = remote_dict
            return remote_dict
            
          

if __name__ == "__main__":
   import   redis
   import   sys 
   import   json
   from   modbus_redis_server_py3.modbus_redis_mgr_py3  import  ModbusRedisServer
   from     modbus_redis_server_py3.rs485_mgr_py3  import RS485_Mgr  
   from    modbus_redis_server_py3.modbus_serial_ctrl_py3  import ModbusSerialCtrl
   from   modbus_redis_server_py3.msg_manager_py3 import MessageManager
   from   redis_support_py3.redis_rpc_server_py3 import Redis_Rpc_Server

   
   from redis_graph_py3.farm_template_py3 import Graph_Management

   
   
   server_index = 0
   
   server_name =  sys.argv[1]
   
   gm = Graph_Management("PI_1","main_remote","LaCima_DataStore")
   setup  = Setup_Remote_Devices(gm)
   server_dict = setup.find_server( server_name )
   serial_links      = setup.find_serial_links( server_name )
   
  
   rs485_interface =   RS485_Mgr() 
   msg_mgr = MessageManager()
   redis_rpc_handle   =  redis.StrictRedis(  server_dict["ip"] , 6379, server_dict["redis_rpc_db"],decode_responses=True )
   redis_handle       =  redis.StrictRedis(  server_dict["ip"] , 6379, 0,decode_responses=True )
   master_remote_dictionary = []
   for i,item in serial_links.items():
       remote_dict = setup.find_and_register_remotes( item , rs485_interface, msg_mgr )
       temp_dict = {}
       temp_dict[i] = item
       modbus_serial_ctrl  = ModbusSerialCtrl( temp_dict, remote_dict, msg_mgr)
       for j,k in remote_dict.items():
           msg_mgr.add_device( k["modbus_address"], modbus_serial_ctrl )  
           master_remote_dictionary.append(k["modbus_address"])           
       msg_mgr.add_device( 255,    redis_handle) 
   
   print(msg_mgr.ping_devices([100]))
  
   Modbus_Server( redis_handle, redis_rpc_handle,msg_mgr, server_dict, master_remote_dictionary,"modbus_relay","ping_message"  )
    

'''
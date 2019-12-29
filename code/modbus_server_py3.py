




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
    
   def __init__( self,  msg_handler,generate_handlers,data_structures):  # fill in proceedures
       self.msg_handler = msg_handler
  

       #self.statistic_handler = Statistic_Handler(data_structures)
       self.rpc_server_handle = generate_handlers.construct_rpc_sever(data_structures["PLC_RPC_SERVER"] )
      
       self.rpc_server_handle.register_call_back( "modbus_relay", self.process_modbus_message)
       self.rpc_server_handle.register_call_back( "ping_message", self.process_ping_message)
       self.rpc_server_handle.add_time_out_function(self.process_null_msg)
       self.rpc_server_handle.start()
 
 
   def process_ping_message(self, address):    
        temp = self.msg_handler.ping_devices([address])
        return temp[0]["result"]        
        
   def process_modbus_message( self,input_msg ):

       address = input_msg[0]
       
       #self.statistic_handler.process_start_message( address )
      
       
       
      
       failure, retries, output_message = self.msg_handler.process_msg( input_msg )
       
       if failure != 0:
           output_msg = "@"
           #self.statistic_handler.log_bad_message( address, retries )
       else:
            pass
            #self.statistic_handler.log_good_message( address, retries )
       #self.statistic_handler.process_end_message()
       return output_message
        

   def process_null_msg( self ):
      print("null message")
      return
       #self.statistic_handler.process_null_message()





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
   
   #  find data structures
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
   
   
   # 
   # finding IO_LINKS
   #
   #
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=plc_server_name )
   query_list = qs.add_match_terminal( query_list, relationship = "IO_LINK") 
                                     
   serial_sets, serial_sources = qs.match_list(query_list)
   
   rs485_interface =   RS485_Mgr()
   interfaces = {}
   for i in serial_sources:
     i["handler"] = rs485_interface
     interfaces[i["name"]] = i
     
   
   
   
   msg_mgr = MessageManager()
  
   for i,item in interfaces.items():
       
       remote_dict = find_remotes(qs,item["name"])
       modbus_serial_ctrl  = ModbusSerialCtrl( item, remote_dict)
      
       for j,k in remote_dict.items():
          
           msg_mgr.add_device( k["address"], modbus_serial_ctrl )  
   
   #print(msg_mgr.ping_devices([100]))
 
   
   Modbus_Server( msg_mgr,generate_handlers,data_structures  )    
 
   
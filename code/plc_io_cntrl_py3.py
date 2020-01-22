


class PLC_IO_Control(object):

   def __init__(self,
                redis_site,
                qs,
                generate_irrigation_control ):
                
       self.generate_irrigation_control = generate_irrigation_control
       self.redis_site = redis_site
       self.qs         = qs
       self.hash_update = self.generate_irrigation_control(redis_site,qs)
       self.construct_plc_elements(redis_site,qs)
       self.construct_plc_flow_measurements(redis_site,qs) 
       self.construct_plc_slave_current_measurements(redis_site,qs) 
       self.construct_plc_irrigation_measurements(redis_site,qs) 
       self.generate_data_handlers(redis_site,qs)

       self.log_data()        

   def log_data(self):
    
       while 1:
           self.minute_measurement = {}
           return_value = {}
           self.measure_flow_meters(return_value)
           self.measure_irrigation_current(return_value)
           self.measure_slave_current(return_value)
           print("return_value",return_value)
           self.ds_handlers["PLC_MEASUREMENTS_STREAM"].push(return_value)
           time.sleep(60)
               
              

   def measure_flow_meters(self,return_value):
       
       for i in self.plc_flow_meas:
           return_value[i["name"]] = self.make_flow_measurement(i,"PLC_FLOW_METER")
       

   def measure_irrigation_current(self,return_value):
       for i in self.plc_irrigation_current_meas:
           
          return_value[i["name"]] = self.make_current_measurement(i,"PLC_EQUIPMENT_CURRENT")

   def measure_slave_current(self,return_value):
       for i in self.plc_slave_current_meas:
           return_value[i["name"]] = self.make_current_measurement(i,"PLC_SLAVE_CURRENT")

           
   def make_current_measurement(self,i,status_key): 
       controller     = i["remote"]
       rpc_queue   =    self.plc_table[controller]["rpc_queue"]
       type   =    self.plc_table[controller]["type"]
       action_class   = self.construct_access_class.find_class( type,rpc_queue )
       
       conversion = i["conversion"]
       register        = i["register"]
       current_value =  action_class.measure_analog(  self.plc_table[controller]["modbus_address"], [register, conversion ] )
       if i["main"] == True:
           self.generate_irrigation_control.hset(status_key,current_value) 
       return current_value
       
       
   def make_flow_measurement(self,i,status_key):    
       controller     = i["remote"]
       rpc_queue   =    self.plc_table[controller]["rpc_queue"]
       type   =    self.plc_table[controller]["type"]
       action_class   = self.construct_access_class.find_class( type,rpc_queue )
      
       conversion_rate = i["io_setup"]["conversion_factor"]
       flow_value = action_class.measure_counter( self.plc_table[controller]["modbus_address"], i["io_setup"] )*conversion_rate
       if i["main"] == True:
           self.generate_irrigation_control.hset(status_key,flow_value) 
       return flow_value
       
       
       

   def construct_plc_flow_measurements(self,redis_site,qs): 
       self.plc_flow_meas = []
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS" )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_FLOW_METERS")
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "FLOW_METER")
                                                 
       sensor_sets, sensor_nodes = qs.match_list(query_list)

       for i in sensor_nodes:
          self.plc_flow_meas.append(i)
          
       
   def construct_plc_slave_current_measurements(self,redis_site,qs):
       self.plc_slave_current_meas = []
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS" )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_SLAVE_CURRENTS" )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "CURRENT_DEVICE")
                                                 
       sensor_sets, sensor_nodes = qs.match_list(query_list)
       
       for i in sensor_nodes:
          self.plc_slave_current_meas.append(i)
          
       
   def construct_plc_irrigation_measurements(self,redis_site,qs):
       self.plc_irrigation_current_meas = []
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS" )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_IRRIGATION_CURRENTS" )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "CURRENT_DEVICE")
                                                 
       sensor_sets, sensor_nodes = qs.match_list(query_list)
       
       for i in sensor_nodes:
          self.plc_irrigation_current_meas.append(i)
   
                
                
   def generate_data_handlers(self,redis_site,qs):
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS" )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "PACKAGE", 
                                           property_mask={"name":"PLC_MEASUREMENTS_PACKAGE"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)
       
       package = package_sources[0]       
   
        
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,qs)
       self.ds_handlers = {}
       self.ds_handlers["PLC_MEASUREMENTS_STREAM"] = generate_handlers.construct_redis_stream_writer(data_structures["PLC_MEASUREMENTS_STREAM"])                
       self.construct_access_class =   Construct_Access_Classes(generate_handlers)


   def construct_plc_elements(self,redis_site,qs):
       self.plc_table = {}  # indexed by logical name
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_terminal( query_list,relationship="PLC_SERVER" )
       plc_server_field, plc_server_nodes = qs.match_list(query_list)
       for i in plc_server_nodes:
           rpc_queue = self.generate_rpc_client_queue(qs,redis_site,i["name"])
           query_list = []
           query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
           query_list = qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=i["name"] )
           query_list = qs.add_match_terminal( query_list,relationship="REMOTE_UNIT" )
           plc_field, plc_nodes = qs.match_list(query_list)
           for j in plc_nodes:
               j["rpc_queue"]         = rpc_queue
               self.plc_table[j["name"]] = j
       
               
    
       
   def generate_rpc_client_queue(self,qs,redis_site,name): 
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=name )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "PACKAGE", 
                                           property_mask={"name":"PLC_SERVER_DATA"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)
       
       package = package_sources[0]    
       data_structures = package["data_structures"]
       
       queue = data_structures["PLC_RPC_SERVER"]["queue"]
       return queue
       



           

        




                   
if __name__ == "__main__":


    
    import os
    import copy
    import msgpack
    import base64
    import redis
    import time
    import datetime
    import json
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
    from   plc_control_py3.construct_classes_py3 import Construct_Access_Classes
    from core_libraries.irrigation_hash_control_py3 import generate_irrigation_control    

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
     
    qs = Query_Support( redis_site )
    PLC_IO_Control(redis_site,qs,generate_irrigation_control)

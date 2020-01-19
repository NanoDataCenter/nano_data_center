import msgpack
import base64
import redis
import time
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from   plc_control_py3.construct_classes_py3 import Construct_Access_Classes
from core_libraries.irrigation_hash_control_py3 import generate_irrigation_control


class PLC_IO_Control(object):

   def __init__(self,
                redis_site,
                qs):
                
       self.generate_irrigation_control
       self.redis_site = redis_site
       self.qs         = qs
       self.hash_update = self.generate_irrigation_control(redis_site,qs)
       self.construct_plc_elements(redis_site,qs)
       self.construct_plc_flow_measurements(redis_site,qs) 
       self.construct_plc_slave_current_measurements(redis_site,qs) 
       self.construct_plc_irrigation_measurements(redis_site,qs) 
       self.generate_data_structures(redis_site,qs)
       self.log_data()        

   def log_data(self):
    
       while 1:
           self.minute_measurement = {}
           self.measure_flow_meters()
           self.measure_irrigation_current()
           self.measure_slave_current()
           self.ds_handlers["PLC_MEASUREMENTS_STREAM"].push(return_value)
           time.sleep(60)
               
              

   def measure_flow_meters(self):
       for i in self.plc_flow_meas:
           self.make_flow_measurement(i,"PLC_FLOW_METER")


   def measure_irrigation_currents(self):
       for i in self.plc_irrigation_current_meas:
           self.make_current_measurement(i,"PLC_EQUIPMENT_CURRENT")

   def measure_slave_current(self):
       for i in self.plc_slave_current_meas:
           self.make_current_measurement(i,"PLC_SLAVE_CURRENT")

           
   def make_current_measurement(self,input,status_key):
       pass
       
       
   def make_flow_measurement(self,input,status_key):
       pass
       
       
       
   '''
   def measure_valve_current( self,*args):

       controller = self.irrigation_controllers[self.current_device["remote"]]
       action_class = self.find_class( controller["type"] )
       register     = self.current_device["register"]
       conversion   = self.current_device["conversion"]
       current      = action_class.measure_analog(  controller["modbus_address"], [register, conversion ] )
 
       redis_dict = self.ir_data["CURRENT"]["dict"]
       redis_key = self.ir_data["CURRENT"]["key"]
       self.redis_old_handle.hset(redis_dict,redis_key,current)
       
       return current      
       
   def measure_flow_rates ( self, *args ):
       for i in  self.fc_list:
           remote = i["remote"]
           print("flow rate remote",remote)
           controller     = self.irrigation_controllers[i["remote"]]
           action_class   = self.find_class( controller["type"] )
           print("i",i["io_setup"])
           conversion_rate = i["io_setup"]["conversion_factor"]
           flow_value = action_class.measure_counter( controller["modbus_address"], i["io_setup"] )
           print("flow_value",flow_value)
           self.redis_old_handle.lpush("QUEUES:SPRINKLER:FLOW:"+str(i),flow_value )
           self.redis_old_handle.ltrim("QUEUES:SPRINKLER:FLOW:"+str(i),0,800)
           if i["main_flow_meter"] == "True":
               self.redis_old_handle.hset("CONTROL_VARIABLES","global_flow_sensor",flow_value )         
               self.redis_old_handle.hset("CONTROL_VARIABLES","global_flow_sensor_corrected",flow_value*conversion_rate )    
  
   '''
   def construct_plc_flow_measurements(redis_site,qs): 
       self.plc_flow_meas = []
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS",label=name )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_FLOW_METERS",label=name )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "PLC_FLOW_METER")
                                                 
       sensor_sets, sensors_nodes = qs.match_list(query_list)
       
       for i in sensor_nodes:
          self.plc_flow_meas.append(i)
          
       
   def construct_plc_slave_current_measurements(redis_site,qs):
       self.plc_slave_current_meas = []
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS",label=name )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_SLAVE_CURRENTS",label=name )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "CURRENT_DEVICE")
                                                 
       sensor_sets, sensors_nodes = qs.match_list(query_list)
       
       for i in sensor_nodes:
          self.self.plc_slave_current_meas.append(i)
          
       
   def construct_plc_irrigation_measurements(redis_site,qs):
       self.plc_irrigation_current_meas = []
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS",label=name )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_IRRIGATION_CURRENTS",label=name )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "CURRENT_DEVICE")
                                                 
       sensor_sets, sensors_nodes = qs.match_list(query_list)
       
       for i in sensor_nodes:
          self.self.plc_irrigation_current_meas.append(i)
   
                
                
   def generate_data_handlers(self,redis_site,qs):
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS",label=name )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "PACKAGE", 
                                           property_mask={"name":"PLC_MEASUREMENTS_PACKAGE"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)
       
       package = package_sources[0]       
   
        
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,qs)
       self.ds_handlers = {}
       self.ds_handlers["PLC_MEASUREMENTS_STREAM"] = generate_handlers.construct_redis_stream_reader(data_structures["PLC_MEASUREMENTS_STREAM"])                
                
                

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
       


   def generate_data_handlers(self,redis_site,qs):
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_SERVER",label=name )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "PACKAGE", 
                                           property_mask={"name":"PLC_SERVER_DATA"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)
       
       package = package_sources[0]       
   
        
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,qs)
       self.ds_handlers = {}
       self.ds_handlers["MQTT_INPUT_QUEUE"] = generate_handlers.construct_redis_stream_reader(data_structures["MQTT_INPUT_QUEUE"])
           

        




                   
if __name__ == "__main__":


    
    import os
    import copy
    #import load_files_py3
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    import datetime
    

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
    PLC_IO_Control(redis_site,qs)

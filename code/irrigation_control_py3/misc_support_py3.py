
from plc_control_py3.construct_classes_py3 import Construct_Access_Classes
from core_libraries.irrigation_hash_control_py3 import get_main_valves
from core_libraries.irrigation_hash_control_py3 import get_cleaning_valves
class IO_Control(object):

   def __init__(self,irrigation_hash_control,event_handlers,qs,redis_site,generate_handlers ):
      self.irrigation_hash_control = irrigation_hash_control
      self.event_handlers = event_handlers
      self.generate_handlers = generate_handlers
      self.plc_classes = Construct_Access_Classes(generate_handlers)
      self.construct_plc_elements(qs,redis_site)
      self.main_valves = get_main_valves(redis_site,qs)
      self.cleaning_valves = get_cleaning_valves(redis_site,qs)
      self.ir_ctrl = self.find_irrigation_controllers() 
      self.find_class = self.plc_classes.find_class
      self.construct_plc_irrigation_measurements(redis_site,qs)
      
      #
      # Build device tables
      #
      self.disable_all_sprinklers()
      
   def construct_plc_subordinate_current_measurements(self,redis_site,qs):
       self.plc_subordinate_current_meas = []
       query_list = []   
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_MEASUREMENTS" )
       query_list = qs.add_match_relationship( query_list,relationship="PLC_SLAVE_CURRENTS" )
       query_list = qs.add_match_terminal( query_list, 
                                           relationship = "CURRENT_DEVICE")
                                                 
       sensor_sets, sensor_nodes = qs.match_list(query_list)
       
       for i in sensor_nodes:
          self.plc_subordinate_current_meas.append(i)
   
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
      
      
 
 
   def read_wd_flag(self,io_list ):
       for item in self.io_list: 
           remote = item[0]       
           control_block = self.plc_table[remote]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]       
           action_class = self.find_class( type,rpc_queue)
           action_class.read_wd_flag( item["modbus_address"] )

   def write_wd_flag(self,io_list ):
       for item in self.io_list: 
           remote = item[0]       
           control_block = self.plc_table[remote]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]       
           action_class = self.find_class( type,rpc_queue)
           action_class.write_wd_flag( item["modbus_address"] )


 

   def turn_on_pump(self,*args):
       print("turn_on_pump")
       print("function not currently supported")
       
   def turn_off_pump(self,*args):
       print("turn_off_pump")
       print("function not currently supported")      
   
   
   def monitor_current(self,current_limit):
       temp = self.measure_valve_current()
       return True
       if temp > current_limit:
         return False
       else:
         return True
         
   def check_equipment_relay(self,*args):
       return True # return true or false depending upon state of relay
       
       
       
   def check_equipment_current(self,*args):
       return .30 #      

   def measure_valve_current( self,*args):
       i = self.plc_irrigation_current_meas[0]
       controller     =  i["remote"]
       rpc_queue      =  self.plc_table[controller]["rpc_queue"]
       type           =  self.plc_table[controller]["type"]
       action_class   =  self.plc_classes.find_class( type,rpc_queue )
       
       conversion = i["conversion"]
       register        = i["register"]
       current_value =  action_class.measure_analog(  self.plc_table[controller]["modbus_address"], [register, conversion ] )
       print("current_value",current_value)
       return current_value
       
     
   def get_main_valve_setup(self):
       return self.irrigation_hash_control.hget("MASTER_VALVE_SETUP")

   def disable_all_sprinklers( self,*arg ):
       print("disable all sprinklers")
       self.irrigation_hash_control.hset("MASTER_VALVE",False)       
       self.turn_off_cleaning_valves()
       self.turn_off_main_valves()
 
       for item in self.ir_ctrl:
           control_block = self.plc_table[item]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]

           action_class = self.find_class( type,rpc_queue)
           action_class.disable_all_sprinklers( modbus_address, [] )
       
   def turn_on_main_valves( self,*arg ):
       self.event_handlers.change_main_valve_on()
       
   def turn_off_main_valves( self,*arg ):
       #print("turn off main valve") 
       self.event_handlers.change_main_valve_off()

   def turn_on_main_valves_direct( self,*arg ):
       print("turn on main valve direct")
       self.irrigation_hash_control.hset("MASTER_VALVE",True)
      
       for io_setup in self.main_valves:
            temp = {}
            temp["remote"] = io_setup["remote"]
            temp["bits"] = io_setup["pins"]
            self.turn_on_valve( temp )

       
   def turn_off_main_valves_direct( self,*arg ):
       print("turn off main valve direct")
       self.irrigation_hash_control.hset("MASTER_VALVE",False)
      
       for io_setup in self.main_valves:
            temp = {}
            temp["remote"] = io_setup["remote"]
            temp["bits"] = io_setup["pins"]
            self.turn_off_valve( temp )


   def turn_on_cleaning_valves( self,*arg ):
       
       self.event_handlers.open_cleaning_valve()
            
   def turn_off_cleaning_valves( self,*arg ):
      #print("turn off cleaning valve") 
      self.turn_off_cleaning_valves_direct()  ## added safety
     
      self.event_handlers.close_cleaning_valve()
 
   def turn_on_cleaning_valves_direct( self,*arg ):
        print("turn on cleaning valve")
        for io_setup in self.cleaning_valves:
            temp = {}
            temp["remote"] = io_setup["remote"]
            temp["bits"] = io_setup["pins"]
            self.turn_on_valve( temp )
       
            
   def turn_off_cleaning_valves_direct( self,*arg ):
        print("turn off cleaning valve direct")
        for io_setup in self.cleaning_valves:
            temp = {}
            temp["remote"] = io_setup["remote"]
            temp["bits"] = io_setup["pins"]
            self.turn_off_valve( temp )
      


   def check_required_plcs(self,setup):
       for i in setup:
          remote = i["remote"]
 
          control_block = self.plc_table[remote]
          modbus_address = control_block["modbus_address"]
          rpc_queue      = control_block["rpc_queue"]
          type           = control_block["type"]       
          action_class = self.find_class( type,rpc_queue)
          action_class.write_wd_flag( modbus_address )
      
 
   def verify_all_devices(self,*args):
       for i,control_block in self.plc_table.items():
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]
           action_class = self.find_class( type,rpc_queue)
           #print("turn_off_cleaning_valves_direct")
           action_class.write_wd_flag(  modbus_address )           
       return True    
           
   def verify_irrigation_controllers(self,*args):
      #print("verify irrigation controllers",self.ir_ctrl)
      for item in self.ir_ctrl:
           control_block = self.plc_table[item]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]
           action_class = self.find_class( type,rpc_queue)       
           action_class.write_wd_flag(  modbus_address ) 
      return True           
           
   def verify_selected_devices(self,device_list):
       for remote in device_list:
           control_block = self.plc_table[remote]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]
           action_class = self.find_class( type,rpc_queue)
           action_class.write_wd_flag(  modbus_address )    
 

          
   def load_duration_counters(self,json_object):
           print("json_object",json_object)
           run_time  = json_object["run_time"]
           io_setup_list  =  json_object["io_setup"]
           for io_setup in io_setup_list:
                remote = io_setup["remote"]           
                control_block = self.plc_table[remote]
                modbus_address = control_block["modbus_address"]
                rpc_queue      = control_block["rpc_queue"]
                type           = control_block["type"]
                action_class = self.find_class( type,rpc_queue)
           
                #duration counter ticks in 100 ms refresh for 10 minutes
                action_class.load_duration_counters( modbus_address,10*60*10 ) # refresh duration counter

   def turn_on_valves(self,io_setup):
       for i in io_setup:
          self.turn_on_valve(i)

   def turn_on_valve( self ,io_setup ):
           # io_setup is a list of dict { "remote":xx , "bits":[1,2,3,4] }
           print("turn_on_valve",io_setup)
        
           pins = io_setup["bits"]
           remote = io_setup["remote"]           
           control_block = self.plc_table[remote]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]
           action_class = self.find_class( type,rpc_queue)
           action_class.turn_on_valves(  modbus_address, pins)
           #duration counter ticks in 100 ms refresh for 10 minutes
           
           action_class.write_wd_flag( modbus_address )
       

   def turn_off_valves(self,io_setup):
       for i in io_setup:
          self.turn_off_valve(i)
       
   def turn_off_valve( self ,io_setup ):
           print("turn off valve",io_setup)   
           pins = io_setup["bits"]
           remote = io_setup["remote"]           
           control_block = self.plc_table[remote]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]
           action_class = self.find_class( type,rpc_queue)
           action_class.turn_off_valves(  modbus_address, pins)
           action_class.write_wd_flag( modbus_address )
 

  
       
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
       
   def turn_on_equipment_relay(self,*args):
       pass
   
   def check_equipment_relay(self,*args):
       return True # return true or false depending upon state of relay
       
       
       
   def check_equipment_current(self,*args):
       return .30 #
    
       
   def clear_max_currents(self,*args):
       pass
       
   def enable_irrigation_relay(self,*args):
       pass   
       
       
   def get_irrigation_relay_state(self,*args):
       return True
       
   def get_max_current(self,*args):
       return .333
       
       
   def construct_plc_elements(self,qs,redis_site):
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
       
   def find_irrigation_controllers(self):
       return_value = []
       for key ,item in self.plc_table.items():
          if "irrigation" in item["function"]:
              return_value.append(key)
       
       return return_value       


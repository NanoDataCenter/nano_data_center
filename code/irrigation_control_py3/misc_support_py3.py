
from plc_control_py3.construct_classes_py3 import Construct_Access_Classes
from core_libraries.irrigation_hash_control_py3 import get_master_valves
from core_libraries.irrigation_hash_control_py3 import get_cleaning_valves
class IO_Control(object):

   def __init__(self,irrigation_hash_control,event_handlers,qs,redis_site,generate_handlers ):
      self.irrigation_hash_control = irrigation_hash_control
      self.event_handlers = event_handlers
      self.generate_handlers = generate_handlers
      self.plc_classes = Construct_Access_Classes()
      self.construct_plc_elements(qs,redis_site)
      self.master_valves = get_master_valves(redis_site,qs)
      self.cleaning_valves = get_cleaning_valves(redis_site,qs)
      self.ir_ctrl = self.find_irrigation_controllers() 
      self.find_class = self.plc_classes.find_class
      
      #
      # Build device tables
      #
      self.disable_all_sprinklers()
      
      
      
 
 
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
       

   def measure_valve_current( self,*args):
       return 1
       
     
   def get_master_valve_setup(self):
       return self.irrigation_hash_control.hget("MASTER_VALVE_SETUP")

   def disable_all_sprinklers( self,*arg ):
       
       self.irrigation_hash_control.hset("MASTER_VALVE",False)       
       self.turn_off_cleaning_valves()
       self.turn_off_master_valves()
 
       for item in self.ir_ctrl:
           control_block = self.plc_table[item]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]

           action_class = self.find_class( type,rpc_queue)
           action_class.disable_all_sprinklers( modbus_address, [] )
       
   def turn_on_master_valves( self,*arg ):
       self.event_handlers.change_master_valve_on()
       
   def turn_off_master_valves( self,*arg ):
       #print("turn off master valve") 
       self.event_handlers.change_master_valve_off()

   def turn_on_master_valves_direct( self,*arg ):
    
       self.irrigation_hash_control.hset("MASTER_VALVE",False)
      
       for io_setup in self.master_valves:
            temp = {}
            temp["remote"] = io_setup["remote"]
            temp["bits"] = io_setup["pins"]
            self.turn_on_valve( temp )

       
   def turn_off_master_valves_direct( self,*arg ):
       #print("turn off master valve direct")
       self.irrigation_hash_control.hset("MASTER_VALVE",False)
      
       for io_setup in self.master_valves:
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
        #print("turn on cleaning valve")
        for io_setup in self.cleaning_valves:
            temp = {}
            temp["remote"] = io_setup["remote"]
            temp["bits"] = io_setup["pins"]
            self.turn_on_valve( temp )
       
            
   def turn_off_cleaning_valves_direct( self,*arg ):
        #print("turn off cleaning valve direct")
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
           action_class.load_duration_counters( modbus_address,10 ) # refresh duration counter
           action_class.write_wd_flag( modbus_address )
       

   def turn_off_valves(self,io_setup):
       for i in io_setup:
          self.turn_off_valve(i)
       
   def turn_off_valve( self ,io_setup ):
           #print(io_setup)   
           pins = io_setup["bits"]
           remote = io_setup["remote"]           
           control_block = self.plc_table[remote]
           modbus_address = control_block["modbus_address"]
           rpc_queue      = control_block["rpc_queue"]
           type           = control_block["type"]
           action_class = self.find_class( type,rpc_queue)
           action_class.turn_off_valves(  modbus_address, pins)
           action_class.write_wd_flag( modbus_address )
 

       
       
       
       
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
       handler = self.generate_handlers.construct_rpc_client(data_structures["PLC_RPC_CLIENT"] )
       return handler
       
   def find_irrigation_controllers(self):
       return_value = []
       for key ,item in self.plc_table.items():
          if "irrigation" in item["function"]:
              return_value.append(key)
       
       return return_value       

   def monitor_current(self,current_limit):
       return True

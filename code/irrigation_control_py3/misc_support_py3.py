
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
           #print("turn_on_valve",io_setup)
        
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
           print(io_setup)   
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

   
'''
           if "irrigation" in element["function"]:
              self.ir_ctrl.append(element)  # finding irrigation controllers.
class IO_Control(object):

   def __init__(self,  graph_management, construct_class, redis_old_handle, redis_new_handle ):
       
       self.gm              = graph_management
       self.construct_class = construct_class
       self.find_class      = construct_class.find_class
       self.redis_old_handle = redis_old_handle
       self.redis_new_handle = redis_new_handle
       temp_controllers     = self.gm.match_terminal_relationship(  "REMOTE_UNIT")  #find remote controllers
       
       #print("temp_controllers",temp_controllers)
       self.irrigation_controllers = self.gm.to_dictionary(temp_controllers,"name")
       #print("irrigation_controllers",irrigation_controllers)
       for element in temp_controllers:
           
           
           if "irrigation" in element["function"]:
              self.ir_ctrl.append(element)  # finding irrigation controllers.

       self.mv_list = self.gm.match_terminal_relationship(  "MASTER_VALVE_CONTROLLER")  #finding all master valves
       for i in self.mv_list:
           remote = i["remote"]
           if remote in self.irrigation_controllers:
               pass
           else:   
               raise ValueError("Remote does not support MASTER VALVE ")

       self.fc_list = self.gm.match_terminal_relationship(  "FLOW_METER_CONTROL" )  #finding all master valves
       for i in self.fc_list:
           remote = i["remote"]
           if remote in self.irrigation_controllers:
               pass
           else:   
               raise ValueError("Remote does not support MASTER VALVE ")
           if "flow_meter"  in self.irrigation_controllers[remote]["function"]:         
                pass
           else:
               raise ValueError("Remote does not support MASTER VALVE ")


       self.current_device = self.gm.match_terminal_relationship( "CURRENT_DEVICE" )[0]
       remote = self.current_device["remote"]
       if "valve_current"  in self.irrigation_controllers[remote]["function"]:
           pass
       else:
           raise ValueError("Remote does not support MASTER VALVE ")

       temp_data = self.gm.match_terminal_relationship("IRRIGATION_DATA_ELEMENT" )
       self.ir_data = self.gm.to_dictionary(temp_data,"name")
       print(self.ir_data.keys())

   def read_wd_flag(self,*args ):
       for item in self.ir_ctrl:           
           action_class = self.find_class(item["type"])
           action_class.read_wd_flag( item["modbus_address"] )

   def write_wd_flag(self,*args):
       for item in self.ir_ctrl:          
           action_class = self.find_class(item["type"])
           action_class.write_wd_flag( item["modbus_address"] )

   def read_mode_switch( self,*args ):
       for item in self.ir_ctrl:           
           action_class = self.find_class(item["type"])
           action_class.read_mode( item["modbus_address"] )

   def read_mode( self,*args ):
       for item in self.ir_ctrl:          
           action_class = self.find_class(item["type"])
           action_class.read_mode_switch( item["modbus_address"])
 

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
       
     

   def disable_all_sprinklers( self,*arg ):
       print("disable_all_sprinklers")
       self.redis_old_handle.hset("CONTROL_VARIABLES","MASTER_VALVE_SETUP","OFF")

       for item in self.ir_ctrl:
           
           action_class = self.find_class(item["type"])
           action_class.disable_all_sprinklers( item["modbus_address"], [] )

              
 
   def turn_on_master_valves( self,*arg ):
       print("turn on master valve")
       self.redis_old_handle.hset("CONTROL_VARIABLES","MASTER_VALVE_SETUP","ON")

       redis_dict = self.ir_data["MASTER_VALVE"]["dict"]
       redis_key = self.ir_data["MASTER_VALVE"]["key"]
       self.redis_old_handle.hset(redis_dict,"redis_key","ON")
       for item in self.mv_list:
           controller = self.irrigation_controllers[item["remote"]]
           action_class = self.find_class(controller["type"])
           action_class.turn_on_valves( controller["modbus_address"], [item["master_valve"]] )
            
   def turn_off_master_valves( self,*arg ):
       print("turn off master valve")
       self.redis_old_handle.hset("CONTROL_VARIABLES", "MASTER_VALVE_SETUP","OFF")
       redis_dict = self.ir_data["MASTER_VALVE"]["dict"]
       redis_key = self.ir_data["MASTER_VALVE"]["key"]
       self.redis_old_handle.hset(redis_dict,"redis_key","OFF")

       for item in self.mv_list:
            controller = self.irrigation_controllers[item["remote"]]
            action_class = self.find_class( controller["type"] )
            action_class.disable_all_sprinklers( controller["modbus_address"], [] )
            action_class.turn_off_valves(  controller["modbus_address"], [item["master_valve"]] )


   def turn_on_cleaning_valves( self,*arg ):
       print("turn on cleaning values")
       for item in self.mv_list:
            controller = self.irrigation_controllers[item["remote"]]
            action_class = self.find_class( controller["type"] )
            action_class.turn_on_valves(  controller["modbus_address"], [item["cleaning_valve"]] )
            
   def turn_off_cleaning_valves( self,*arg ):
       print("turn off cleaning valves")
       for item in self.mv_list:
            
            controller = self.irrigation_controllers[item["remote"]]
            action_class = self.find_class( controller["type"] )
            action_class.turn_off_valves( controller["modbus_address"], [item["cleaning_valve"]] )
    

 
 
   #
   #  Clearing Duration counter is done through a falling edge
   #  going from 1 to 0 generates the edge
   def clear_duration_counters( self,remote ):
           item = 
           action_class = self.find_class(item["type"])
           action_class.clear_duration_counters( item["modbus_address"] )


   def load_duration_counters( self, time_duration ,*arg):
       print("################################time_duration",time_duration)
       time_duration = 10*(time_duration*60)+15  # convert minutes to seconds
       time_duration = int(time_duration+.5)
       for item in self.ir_ctrl:
           
           action_class = self.find_class(item["type"])
           action_class.load_duration_counters( item["modbus_address"], [time_duration] )

               

   def turn_on_valve( self ,io_setup ):
       # io_setup is a list of dict { "remote":xx , "bits":[1,2,3,4] }
       print("turn_on_valve",io_setup)
       for i in io_setup:      
           remote        = i["remote"]
           bits          = i["bits"]  # list of outputs on remote to turn off
           controller     = self.irrigation_controllers[remote]
           action_class   = self.find_class( controller["type"] )
           action_class.turn_on_valves(  controller["modbus_address"], bits)

 
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

   def measure_flow_rate( self, remote, io_setup ):           
       controller     = self.irrigation_controllers[remote]
       action_class   = self.find_class( controller["type"] )
       flow_value     = action_class.measure_counter( remote, io_setup )


'''
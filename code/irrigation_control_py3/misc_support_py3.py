class IO_Control(object):

   def __init__(self,irrigation_hash_control ):
      self.irrigation_hash_control = irrigation_hash_control
      self.disable_all_sprinklers()


   def read_wd_flag(self,*args ):
       return 1

   def write_wd_flag(self,*args):
       pass

   def read_mode_switch( self,*args ):
       pass

   def read_mode( self,*args ):
       pass
 

   def measure_valve_current( self,*args):
       return 1
       
     
   def get_master_valve_setup(self):
       return self.irrigation_hash_control.get_master_valve_setup()
       
       
   def disable_all_sprinklers( self,*arg ):
       print("disable all sprinklers")
       self.irrigation_hash_control.set_master_valve(0)
       self.irrigation_hash_control.set_cleaning_valve(0)       
       self.irrigation_hash_control.set_master_valve_setup(0)
       
       
   def turn_on_master_valves( self,*arg ):
       self.irrigation_hash_control.set_master_valve(1)
       self.irrigation_hash_control.set_master_valve_setup(1)
       print("turn on master valve")
       
   def turn_off_master_valves( self,*arg ):
       self.irrigation_hash_control.set_master_valve(0)
       print("turn off master valve")


   def turn_on_cleaning_valves( self,*arg ):
       self.irrigation_hash_control.set_cleaning_valve(1)
       print("turn on cleaning valve")
            
   def turn_off_cleaning_valves( self,*arg ):
      self.irrigation_hash_control.set_cleaning_valve(0)
      print("turn off cleaning valve")
    

 
 
   #
   #  Clearing Duration counter is done through a falling edge
   #  going from 1 to 0 generates the edge
   def clear_duration_counters( self,*arg ):
       print("clear duration counters")


   def load_duration_counters( self, time_duration ,*arg):
      print("load_duration_counters",time_duration)
               

   def turn_on_valve( self ,io_setup ):
       print("turn_on_valve",io_setup)
 
   def measure_flow_rates ( self, *args ):
         return [4]

   def get_corrected_flow_rate(self):
       return 0
       
   def measure_flow_rate( self, remote, io_setup ):           
       return   0


'''

class IO_Control(object):

   def __init__(self,  graph_management, construct_class, redis_old_handle, redis_new_handle ):
       
       self.gm              = graph_management
       self.construct_class = construct_class
       self.find_class      = construct_class.find_class
       self.redis_old_handle = redis_old_handle
       self.redis_new_handle = redis_new_handle
       temp_controllers     = self.gm.match_terminal_relationship(  "REMOTE_UNIT")  #find remote controllers
       self.ir_ctrl         = [] #irrigation controllers
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
   def clear_duration_counters( self,*arg ):
       for item in self.ir_ctrl:
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
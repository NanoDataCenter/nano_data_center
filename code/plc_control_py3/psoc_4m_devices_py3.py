
"""
File: psoc_rtu_base.py
This file is the base class that all modbus 4m modules use


Variables which can be read as modbus type 3 measages

 

    
#define MOD_UNIT_ID                     0
#define MOD_UNIT_TEMP                   1
#define MOD_RTU_WATCH_DOG_FLAG          2
#define MOD_CONTROLLER_WATCH_DOG_FLAG   3
#define MOD_COMMISSIONING_FLAG          4
#define MOD_POWER_UP_EVENT             5
#define MOD_MINUTE_ROLLOVER             6
#define MOD_DISCRETE_IO_CHANGE          7
#define MOD_YEAR                        8
#define MOD_MONTH                       9
#define MOD_DAY                        10
#define MOD_HOUR                       11
#define MOD_MINUTE                     12
#define MOD_SECOND                     13

       


Registers which can be changes are through type 16 messages



The only functions which can be changed are the following registers

System level changes
    change_time        
    change_modbus_address                    
    clear_watch_dog_flags          
    clear_power_up_event           
    clear_minute_rollover          

Python Functions are provided for all common accesses

Register MOD_RESET_REASON has the following bit field definitions
CY_SYS_RESET_WDT       - WDT caused a reset
CY_SYS_RESET_PROTFAULT - Occured protection violation that requires reset
CY_SYS_RESET_SW        - Cortex-M0 requested a system reset.

/* CySysGetResetReason() */
#define CY_SYS_RESET_WDT_SHIFT          (0u)
#define CY_SYS_RESET_PROTFAULT_SHIFT    (3u)
#define CY_SYS_RESET_SW_SHIFT           (4u)

#define CY_SYS_RESET_WDT                ((uint32)1u << CY_SYS_RESET_WDT_SHIFT      )
#define CY_SYS_RESET_PROTFAULT          ((uint32)1u << CY_SYS_RESET_PROTFAULT_SHIFT)
#define CY_SYS_RESET_SW                 ((uint32)1u << CY_SYS_RESET_SW_SHIFT       )


"""
import datetime
import time
class PSOC_BASE_4M(object):
    
   def __init__(self,instrument, system_id):
       self.instrument = instrument
       self.system_id = system_id  
       self.commission_address = 0xc0       
       # write address definitions definitions
       self.change_time_addr                       = 20       
       self.change_modbus_addr                     = 21            
       self.clear_watch_dog_flags_addr             = 22
       self.clear_power_up_event_addr              = 23
       self.clear_discrete_io_change_addr          = 24
       self.clear_minute_rollover_addr             = 25
       self.clear_controller_watch_dog_flags_addr  = 26     
     
 
   

       #System  Variables
       self.system_var_start = 0
 
       self.system_var_list = [
                                "MOD_UNIT_ID" ,   #0
                                "MOD_RTU_WATCH_DOG_FLAG",#1
                                "MOD_CONTROLLER_WATCH_DOG_FLAG" ,#2
                                "MOD_COMMISSIONING_FLAG " ,#3
                                "MOD_POWER_UP_EVENT", #4
                                "MOD_RESET_REASON",#5
                                "MOD_MINUTE_ROLLOVER" #6
                              ]
     
       
       
        
   def set_instrument( self, instrument ):
       self.instrument = instrument


   # 
   #
   #  Read Variables
   #
   #
 
 
   def read_system_variables( self, modbus_address ):
       return_value = {}
 
       data =  self.instrument.read_registers( modbus_address,   self.system_var_start ,len(self.system_var_list) , 3 ,False)
       for i in range(0,len(self.system_var_list)):
          return_value[self.system_var_list[i]] = data[i]
       return return_value

   def read_time( self, modbus_address):
      return_value = {}
      data = self.instrument.read_longs( modbus_address, 8, 2, 3, False)
      return data[0]

       
   #
   #
   #  Write routines
   #
   #
       
   def update_current_time(self, address):
        now = int(time.time())
        print( "now",now)
        self.instrument.write_longs(address, self.change_time_addr, [int(now),0],functioncode=16, signed=False) 
        
   def commission_modbus_address( self, new_address , new_commissioning_address =  None ):
        if new_commissioning_address == None:
            new_commissioning_address = self.commission_address
        print( new_commissioning_address)
        self.instrument.write_registers(  new_commissioning_address,  self.change_modbus_addr , [new_address, new_commissioning_address ] )   


   def clear_watch_dog_flag(self,address):
        self.instrument.write_registers(address, self.clear_watch_dog_flags_addr, [0] )

   def set_controller_watch_dog_flag(self,address):
        self.instrument.write_registers(address, self.clear_controller_watch_dog_flags_addr, [1] )

        
   def clear_power_on_reset(self, address):

       self.instrument.write_registers(address, self.clear_power_up_event_addr, [0] )
      
       
   def clear_minute_rollover(self, address):

        self.instrument.write_registers(address, self.clear_minute_rollover_addr, [0] )
       
   def verify_unit(self, address ):
        data = self.instrument.read_registers( address,self.system_var_list.index(  "MOD_UNIT_ID"),1)
        if data[0] == self.system_id:
           return_value = True
        else:
           return_value = False
        return return_value

   def process_event_queue( self, address, fifo_index ):
        #returns a list of a list [ event, event_data]
        #event id's are system depenedent but 0 is POWER_UP
        return self.instrument.read_fifo( address,fifo_index)
        
   def update_flash( self,address ):
       self.instrument.write_registers( address, self.update_flash_addr, [0])

       
 
       
class PSOC_4M_MOISTURE_UNIT(PSOC_BASE_4M):
    
   def __init__(self,instrument):
       self.system_id = 0x201
       super().__init__( instrument, self.system_id )
 
       # additional write address definitions definitions
       self.check_one_wire_presence_addr                     = 27
       self.make_soil_temperature_addr                       = 28
       self.make_air_temp_humidity_addr                      = 29
       self.force_moisture_reading_addr                      = 30  
       self.update_moisture_sensor_configuration_addr        = 31
  
       self.update_flash_addr                                = 33
       self.clear_moisture_flag_addr                         = 34
       
       self.sensor_length                                    = 16
       
       self.new_measurement_flag_start = 20
       self.new_measurement_flag_list = [ "NEW_MOISTURE_DATA_FLAG"]
       
       # status
       self.status_start   =    13
       self.status_list    =  [
                                          
                                          "ONE_WIRE_DEVICE_FOUND",
                                          "NEW_MOISTURE_DATA_FLAG"
                               ]
       self.moisture_control_start = 15   
       self.moisture_control_list  = [
                             
                           
                           
                           "AIR_HUMIDITY_FLOAT" ,       
                           "AIR_TEMP_FLOAT",
                           "MOISTURE_SOIL_TEMP_FLOAT",
                           "RESISTOR_FLOAT",
                           


                        ]
       self.capacitance_mask_start = 23
       self.capacitance_mask_list  = [ "CAPACITANCE_MASK"]
       
       # Moisture Data
       self.moisture_data_start  =    30   
       self.moisture_data_number =    16      
       
       self.moisture_data_resistive_start              = 70                
       self.moisture_resistive_configuration_number    = 16                      
    
     
       # Moisture Configuration Data
       self.moisture_configuration_start  =    110
       self.moisture_configuration_number =     16
 
                          
 


   # 
   #
   #  Read Variables
   #
   #
 
 
   def check_status( self, address):
       return_value = {}
       data =  self.instrument.read_registers( address,  self.status_start, len(self.status_list) )

       for i in range(0,len(self.status_list)):
          
           return_value[  self.status_list[i]  ] = data[i]
           
       return return_value
       

   
        
   def read_moisture_control(self, address ):
       return_value = {}
       data =  self.instrument.read_floats( address,  self.moisture_control_start, len(self.moisture_control_list) )

       for i in range(0,len(self.moisture_control_list)):
          
           return_value[  self.moisture_control_list[i]  ] = data[i]
           
       return return_value
       


       
   def read_moisture_data( self ,address ):
        return_value = {}
        data =  self.instrument.read_floats( address,  self.moisture_data_start ,self.moisture_configuration_number  )
        return data
        
         
   def read_moisture_resistive_data( self ,address ):
        return_value = {}
        data =  self.instrument.read_floats( address,  self.moisture_data_resistive_start ,self.moisture_resistive_configuration_number  )
        return data
        
        
      
      
      
      
        
   def read_moisture_configuration( self, address ):
       return_value = {}
     
       data = self.instrument.read_registers( address,self.moisture_configuration_start,self.moisture_configuration_number )
       return data
       
  
   def check_one_wire_presence ( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.check_one_wire_presence_addr, [0] )
         
   def make_soil_temperature ( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.make_soil_temperature_addr, [0] )
         
         
   def make_air_temp_humidity( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.make_air_temp_humidity_addr, [0] )

  
   def clear_new_moisture_data_flag( self, address):
       self.instrument.write_registers( address, self.clear_moisture_flag_addr, [0] )
       
 
   
   def force_moisture_reading ( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.force_moisture_reading_addr, [0] )
         
        
   def  update_moisture_sensor_configuration ( self,address, sensor_data ): # sensor data consisting of 0,1,2
        if len( sensor_data) != self.sensor_length :
            raise
        valid_data = set([0,1,2])
        for i in sensor_data:
          if i not in valid_data:
             raise
          
        self.instrument.write_registers( address, self.update_moisture_sensor_configuration_addr ,sensor_data )
  


        
 
if __name__ == "__main__": 
       import new_instrument_py3
       import time
       new_instrument  =  new_instrument_py3.Modbus_Instrument()
       new_instrument.set_ip(ip= "192.168.1.84", port = 5005)       
       
       psoc_moisture = PSOC_4M_MOISTURE_UNIT( new_instrument )

       
       #psoc_moisture.update_current_time( 40 )
       #print( psoc_moisture.clear_new_moisture_data_flag(40))
       print( psoc_moisture.check_status(40))

       print(psoc_moisture.check_one_wire_presence(40))
       time.sleep(.3)
       print( psoc_moisture.make_soil_temperature(40))
       time.sleep(.3)
       print( psoc_moisture.make_air_temp_humidity(40))
       time.sleep(.3)
       print( psoc_moisture.make_air_temp_humidity(40))
       time.sleep(.3)
       # test read functions first
 
       print( psoc_moisture.check_status(40))
       print( psoc_moisture.read_moisture_control(40))
       print( psoc_moisture.read_moisture_configuration( 40 ))
       print( psoc_moisture.force_moisture_reading(40))
       time.sleep(1.)
       print( psoc_moisture.read_moisture_data(40))
       print( psoc_moisture.read_moisture_resistive_data(40))
       quit()
       #print( psoc_moisture.force_moisture_reading(40))
       time.sleep(1)
       print( psoc_moisture.read_moisture_resistive_data( 40 ))
       print( psoc_moisture.read_moisture_data(40))
       print( psoc_moisture.check_status(40))
       
       quit()

        
       '''            
       # test directed actions
  
       #psoc_moisture.check_one_wire_presence(40)
       #psoc_moisture.make_soil_temperature(40)
       #psoc_moisture.force_moisture_reading(40)
       '''       
       '''
       #print( "new_data_flag",psoc_moisture.check_new_data_flag( 40))
       #print( "capacitance_mask", psoc_moisture.read_capacitor_mask(40))
       #print( psoc_moisture.read_moisture_control( 40 ))
       #print( psoc_moisture.read_moisture_configuration( 40 ))
       #psoc_moisture.change_capacitance_sensor_mask( 40, 0xf)
       '''
       #psoc_moisture.update_moisture_sensor_configuration ( 40,[ 2,1,1,0,2,1,1,0,2,1,1,0,2,1,1,0] )
       #psoc_moisture.update_flash(40)
       #print( "capacitance_mask", psoc_moisture.read_capacitor_mask(40))
       #print( psoc_moisture.read_moisture_control( 40 ))
       print( psoc_moisture.read_moisture_configuration( 40 ))
       '''
       print( "force moisture measurement", psoc_moisture.force_moisture_reading(40))
       
       print( psoc_moisture.read_moisture_data(40))
       '''
       
       '''
if __name__ == "__main__": 
       import new_instrument_py3
       import time
       instrument  =  new_instrument.Modbus_Instrument()
       instrument.set_ip(ip= "192.168.1.84",port = 5005)
       #new_instrument.set_ip(ip= "192.168.1.82", port = 5005)       
       psoc_4m = PSOC_BASE_4M( instrument, 0x201 )
       #for i in range(0,100):
       #   print( i, psoc_4m.read_system_variables(40))
       for i in range(0,1):
           print(  psoc_4m.read_system_variables(40))

           print( psoc_4m.read_time( 40 ))
           #print( psoc_4m.update_current_time(40))
           print( psoc_4m.read_time( 40 ))
           print( psoc_4m.clear_watch_dog_flag(40))
           print(  psoc_4m.read_system_variables(40))
       
           print( psoc_4m.set_controller_watch_dog_flag(40))
           print(  psoc_4m.read_system_variables(40))

           print( psoc_4m.clear_power_on_reset(40))
           print( psoc_4m.clear_minute_rollover(40))
           print( psoc_4m.verify_unit(40))
           print(  psoc_4m.read_system_variables(40))
           print( psoc_4m.clear_watch_dog_flag(40))
           print(  psoc_4m.read_system_variables(40))
           print( psoc_4m.process_event_queue( 40, 0 ))
       
           #psoc_4m.commission_modbus_address(40)
           '''       
       


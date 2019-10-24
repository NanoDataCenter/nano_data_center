
"""
File: psoc_rtu_base.py
This file is the base class that all modbus 5lp modules use


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
class PSOC_BASE_4M():
    
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
        print "now",now
        self.instrument.write_longs(address, self.change_time_addr, [int(now),0],functioncode=16, signed=False) 
        
   def commission_modbus_address( self, new_address , new_commissioning_address =  None ):
        if new_commissioning_address == None:
            new_commissioning_address = self.commission_address
        print new_commissioning_address
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

       
 
if __name__ == "__main__": 
       import new_instrument_serial
       import time
       new_instrument  =  new_instrument_serial.new_instrument( "/dev/ttyUSB0" )
       psoc_4m = PSOC_BASE_4M( new_instrument, 0x201 )
       #for i in range(0,100):
       #   print i, psoc_4m.read_system_variables(40)
       
       print  psoc_4m.read_system_variables(40)

       print psoc_4m.read_time( 40 )
       print psoc_4m.update_current_time(40)
       time.sleep(10.0)
       print "time out over"
       print "made it here"
       print psoc_4m.read_time( 40 )
       
       print psoc_4m.clear_watch_dog_flag(40)
       print  psoc_4m.read_system_variables(40)
       
       print psoc_4m.set_controller_watch_dog_flag(40)
       print  psoc_4m.read_system_variables(40)

       print psoc_4m.clear_power_on_reset(40)
       print psoc_4m.clear_minute_rollover(40)
       print psoc_4m.verify_unit(40)
       print  psoc_4m.read_system_variables(40)
       print psoc_4m.clear_watch_dog_flag(40)
       print  psoc_4m.read_system_variables(40)
       print psoc_4m.process_event_queue( 40, 0 )
       
       #psoc_4m.commission_modbus_address(40)
       

#
#
#  File: io_controller_class.py
#
#
#
#
#

import struct    

import os
import sys
import time
import select
import socket
import json
import redis


import datetime
class PSOC_BASE_4M():
    
   def __init__(self,ip,port, modbus_address,instrument,  system_id):
       self.ip = ip
       self.port = port
       self.instrument = instrument
       self.modbus_address = modbus_address
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
     
       
       
 
   def set_ip( self, ip ):
      self.ip = ip

   def set_port( self, port ):
       self.port = port

   def set_modbus_address( self, address ):
       self.modbus_address = address

   def set_instrument( self, instrument ):
       self.instrument = instrument

   def set_system_id( self, system_id ):
        self.system_id = system_id

   # 
   #
   #  Read Variables
   #
   #
 
 
   def read_system_variables( self ):
       return_value = {}
       self.instrument.set_ip( self.ip,self.port )
       data =  self.instrument.read_registers( self.modbus_address,   self.system_var_start ,len(self.system_var_list) , 3 ,False)
       for i in range(0,len(self.system_var_list)):
          return_value[self.system_var_list[i]] = data[i]
       return return_value

   def read_time( self ):
      self.instrument.set_ip( self.ip,self.port )
      return_value = {}
      data = self.instrument.read_longs( self.modbus_address, 8, 2, 3, False)
      return data[0]

       
   #
   #
   #  Write routines
   #
   #
       
   def update_current_time(self):
        self.instrument.set_ip( self.ip,self.port )
        now = int(time.time())
        self.instrument.write_longs( self.modbus_address, self.change_time_addr, [int(now),0],functioncode=16, signed=False) 
        
   def commission_modbus_address( self, new_address , new_commissioning_address =  None ):
        if new_commissioning_address == None:
            new_commissioning_address = self.commission_address
        print( new_commissioning_address)
        self.instrument.set_ip( self.ip,self.port )
        self.instrument.write_registers(  new_commissioning_address,  self.change_modbus_addr , [new_address, new_commissioning_address ] )   


   def clear_watch_dog_flag(self):
        self.instrument.set_ip( self.ip,self.port )
        self.instrument.write_registers( self.modbus_address, self.clear_watch_dog_flags_addr, [0] )

   def set_controller_watch_dog_flag(self ):
        self.instrument.set_ip( self.ip,self.port )
        self.instrument.write_registers( self.modbus_address, self.clear_controller_watch_dog_flags_addr, [1] )

        
   def clear_power_on_reset(self):
       self.instrument.set_ip( self.ip,self.port )
       self.instrument.write_registers(self.modbus_address, self.clear_power_up_event_addr, [0] )
      
       
   def clear_minute_rollover(self):
        self.instrument.set_ip( self.ip,self.port )
        self.instrument.write_registers(self.modbus_address, self.clear_minute_rollover_addr, [0] )
       
   def verify_unit(self ):
        self.instrument.set_ip( self.ip,self.port )
        data = self.instrument.read_registers( self.modbus_address,self.system_var_list.index(  "MOD_UNIT_ID"),1)
        if data[0] == self.system_id:
           return_value = True
        else:
           return_value = False
        return return_value

   def process_event_queue( self,  fifo_index ):
        #returns a list of a list [ event, event_data]
        #event id's are system depenedent but 0 is POWER_UP
        self.instrument.set_ip( self.ip,self.port )
        return self.instrument.read_fifo( self.modbus_address,fifo_index)
        
   def update_flash( self ):
       self.instrument.set_ip( self.ip,self.port )
       self.instrument.write_registers( self.modbus_address, self.update_flash_addr, [0])

       
                 


class PSOC_4M_MOISTURE_UNIT(PSOC_BASE_4M):

   def __init__(self, ip,port,subordinate_address, instrument ):
       self.ip = ip
       self.port = port
       self.subordinate_address = subordinate_address
       self.instrument = instrument
       self.system_id = 0x201
       super().__init__( self,ip,port,subordinate_address, instrument, self.system_id)
       
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
 
 
   def check_status( self ):
       return_value = {}
       self.instrument.set_ip( self.ip,self.port )

       data =  self.instrument.read_registers( self.subordinate_address,  self.status_start, len(self.status_list) )

       for i in range(0,len(self.status_list)):
          
           return_value[  self.status_list[i]  ] = data[i]
           
       return return_value
       

   
        
   def read_moisture_control(self  ):
       return_value = {}
       self.instrument.set_ip( self.ip,self.port )
       data =  self.instrument.read_floats( self.subordinate_address,  self.moisture_control_start, len(self.moisture_control_list) )

       for i in range(0,len(self.moisture_control_list)):
          
           return_value[  self.moisture_control_list[i]  ] = data[i]
           
       return return_value
       


       
   def read_moisture_data( self  ):
        return_value = {}
        self.instrument.set_ip( self.ip,self.port )
        data =  self.instrument.read_floats( self.subordinate_address,  self.moisture_data_start ,self.moisture_configuration_number  )
        return data
        
         
   def read_moisture_resistive_data( self  ):
        return_value = {}
        self.instrument.set_ip( self.ip,self.port )
        data =  self.instrument.read_floats( self.subordinate_address,  self.moisture_data_resistive_start ,self.moisture_resistive_configuration_number  )
        return data
        
        
      
      
      
      
        
   def read_moisture_configuration( self ):
       return_value = {}
       self.instrument.set_ip( self.ip,self.port )
       data = self.instrument.read_registers( self.subordinate_address, self.moisture_configuration_start, self.moisture_configuration_number )
       return data
       
  
   def check_one_wire_presence ( self): #sampling rate is in minutes
         self.instrument.set_ip( self.ip,self.port )
         self.instrument.write_registers(self.subordinate_address, self.check_one_wire_presence_addr, [0] )
         
   def make_soil_temperature ( self ): #sampling rate is in minutes
         self.instrument.set_ip( self.ip,self.port )
         self.instrument.write_registers(self.subordinate_address, self.make_soil_temperature_addr, [0] )
         
   def make_air_temp_humidity( self): #sampling rate is in minutes
         self.instrument.set_ip( self.ip,self.port )
         self.instrument.write_registers(self.subordinate_address, self.make_air_temp_humidity_addr, [0] )

  
   def clear_new_moisture_data_flag( self ):
       self.instrument.set_ip( self.ip,self.port )
       self.instrument.write_registers( self.subordinate_address, self.clear_moisture_flag_addr, [0] )
       
 
   
   def force_moisture_reading ( self): #sampling rate is in minutes
         self.instrument.set_ip( self.ip,self.port )
         self.instrument.write_registers( self.subordinate_address, self.force_moisture_reading_addr, [0] )
         
        
   def  update_moisture_sensor_configuration ( self, sensor_data ): # sensor data consisting of 0,1,2
        if len( sensor_data) != self.sensor_length :
            raise
        valid_data = set([0,1,2])
        for i in sensor_data:
          if i not in valid_data:
             raise ValueError("Bad Value for Sensor should be 0,1 or 2 Got "+i)
        self.instrument.set_ip( self.ip,self.port )  
        self.instrument.write_registers( self.subordinate_address, self.update_moisture_sensor_configuration_addr ,sensor_data )
  


        
 




           
if __name__ == "__main__":     
   import new_instrument
   client_driver       = new_instrument.Modbus_Instrument()
   moisture_controller = PSOC_4M_MOISTURE_UNIT( "192.168.1.82",5005,40,client_driver )
 
   print( "time",moisture_controller.read_time())
   print( time.time())
   print( moisture_controller.clear_new_moisture_data_flag())
   print( moisture_controller.check_status())

   print( moisture_controller.check_one_wire_presence())
   time.sleep(.3)
   print( moisture_controller.make_soil_temperature())
   time.sleep(.3)
   print( moisture_controller.make_air_temp_humidity())
   time.sleep(.3)
   print( moisture_controller.make_air_temp_humidity())
   time.sleep(.3)
   # test read functions first
 
   print( moisture_controller.check_status())
   print( moisture_controller.read_moisture_control())
   print( moisture_controller.read_moisture_configuration( ))
   print( moisture_controller.force_moisture_reading())
   time.sleep(1.)
   print( moisture_controller.read_moisture_data())
   print( moisture_controller.read_moisture_resistive_data())
   '''
if __name__ == "__main__": 
       import new_instrument
       import time
       instrument  =  new_instrument.Modbus_Instrument()    
       psoc_4m = PSOC_BASE_4M( "192.168.1.82",5005,40, instrument, 0x201 )
       for i in range(0,100):
          print( i, psoc_4m.read_system_variables())
       
       print(  psoc_4m.read_system_variables())

       print( psoc_4m.read_time(  ))
       print( psoc_4m.update_current_time())
       print( psoc_4m.read_time( ))
       print( psoc_4m.clear_watch_dog_flag())
       print(  psoc_4m.read_system_variables())
       
       print( psoc_4m.set_controller_watch_dog_flag())
       print(  psoc_4m.read_system_variables())

       print( psoc_4m.clear_power_on_reset())
       print( psoc_4m.clear_minute_rollover())
       print( psoc_4m.verify_unit())
       print(  psoc_4m.read_system_variables())
       print( psoc_4m.clear_watch_dog_flag())
       print(  psoc_4m.read_system_variables())
       print( psoc_4m.process_event_queue(  0 ))
       
       #psoc_4m.commission_modbus_address()
   '''      
       
  


    
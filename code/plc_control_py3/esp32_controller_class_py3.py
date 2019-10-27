#
#
#  File: io_controller_class.py
#
#
#
#
#

import struct    

import time





class Esp32_Controller_Base_Class(object):
    
   def __init__(self,instrument, click_io = [], m_tags = {}):
       
       self.instrument  = instrument
       self.click_reg_address = {}
       self.click_bit_address = {}
       self.click_io          = click_io
   
       m_tags["turn_on_valves"] = self.turn_on_valves
       m_tags["turn_off_valves"] = self.turn_off_valves
       m_tags["load_duration_counters"] = self.load_duration_counters
       m_tags["clear_duration_counters"] = self.clear_duration_counters
       m_tags["read_mode_switch"]        = self.read_mode_switch
       m_tags["read_mode"]               = self.read_mode
       m_tags["read_wd_flag"]            = self.read_wd_flag
       m_tags["write_wd_flag"]           = self.write_wd_flag
       m_tags["read_input_bit"]          = self.read_input_bit
       self.m_tags = m_tags
       self.disable_reg                  = 3
       self.load_duration_reg            = 2
       self.wd_flag_reg                  = 1
       self.wd_flag_reg_rd               = 5
       self.load_duration_reg_rd         = 6
       self.reset_reg                    = 4
       

 
       
 
      
   def disable_all_sprinklers( self, modbus_address, input_list = [] ):
 
      self.instrument.write_registers(modbus_address,self.disable_reg,  [1] )


   def turn_on_valves( self, modbus_address, input_list ):
      
       for valve in input_list:  
          self.instrument.write_bits( modbus_address, valve-1,[0])

   def turn_off_valves( self,  modbus_address, input_list  ):
          
       for valve in input_list:  
          
          self.instrument.write_bits( modbus_address,valve-1,[1])


   def load_duration_counters( self, modbus_address, duration ):
        
        self.instrument.write_registers(modbus_address,self.load_duration_reg, [duration] )


       
                         
   def clear_duration_counters( self, modbus_address  ):
        duration = 0
        self.instrument.write_registers(modbus_address,self.load_duration_reg, [duration] )

   def read_duration_counters( self, modbus_address  ):
        
        return self.instrument.read_registers(modbus_address,self.load_duration_reg_rd, 1 )

   def read_input_bit( self, modbus_address, input_list ):
      
      read_bit      = input_list[0]
     
      return self.instrument.read_bits(modbus_address, read_bit-1,1 )[0]


   def read_mode_switch( self, modbus_address ):
      
      return 1 # no mode switch

   def read_mode( self, modbus_address ):
      # mode is always on

      return 1

  
   def read_wd_flag( self, modbus_address ):
     
      return self.instrument.read_registers( modbus_address, self.wd_flag_reg_rd,1)[0]
      

   def write_wd_flag( self, modbus_address ):
      
      self.instrument.write_registers( modbus_address,self.wd_flag_reg,[1])

   def reboot(self, modbus_address):
       self.instrument.write_registers( modbus_address, self.reset_reg,[1])



      
if __name__ == "__main__":
   def iterate( esp32_serial_driver, address, duration ):
    
 
 
       esp32_serial_driver.disable_all_sprinklers( address )
       #esp32_serial_driver.turn_off_valves(address,[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] )
       #instrument.write_bits( 121, 0,[1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1])
       print(instrument.read_bits(121,0,16,1))
   
  
       print(esp32_serial_driver.read_duration_counters(address))
       esp32_serial_driver.load_duration_counters(address, [duration]  )
       time.sleep(.1)
       print(esp32_serial_driver.read_duration_counters(address))
       #esp32_serial_driver.turn_on_valves(address,[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] )
       esp32_serial_driver.turn_on_valves(address,[1,9] )
       for i in range(0,70  ):
          #esp32_serial_driver.turn_on_valves(address,[1,9] )
          print(instrument.read_bits(121,0,16,1))
          esp32_serial_driver.write_wd_flag(address)
          print(esp32_serial_driver.read_duration_counters(address))
          time.sleep(60)
   import sys
   print("made it here")
   from .new_instrument_py3 import Modbus_Instrument
   address= int(sys.argv[1])
   instrument = Modbus_Instrument()
   
   esp32_serial_driver = Esp32_Controller_Base_Class(instrument)
   while True:
       iterate( esp32_serial_driver,address,60*60)
       exit()
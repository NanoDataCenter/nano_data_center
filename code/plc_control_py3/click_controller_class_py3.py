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





class Click_Controller_Base_Class(object):
    
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
   
       for i in range(0,500): 
           temp ="DF"+str(i+1)
           self.click_reg_address[temp] = 0x7000+(i)*2

       for i in range(0,1000):
           temp = "DS"+str(i+1)
           self.click_reg_address[ temp ] = i

       for i in range(0,256):
           temp = "C"+str(i+1)
           self.click_bit_address[ temp ] = 0x4000 + i


       temp = [ "01","02","03","04","05","06","07","08","09","10","12","13","14","15","16" ]
       count = 0
       for i in temp:
          temp = "X0"+i
          self.click_bit_address[temp] = count
          temp = "X1"+i
          self.click_bit_address[temp] = 0x20 + count
          temp = "X2"+i
          self.click_bit_address[temp] = 0x40 + count
          temp = "X3"+i
          self.click_bit_address[temp] = 0x60 + count
          temp = "X4"+i
          self.click_bit_address[temp] = 0x80 + count
          temp = "X5"+i
          self.click_bit_address[temp] = 0xA0 + count
          temp = "X6"+i
          self.click_bit_address[temp] = 0xc0 + count
          temp = "X7"+i
          self.click_bit_address[temp] = 0xe0 + count
          temp = "X8"+i
          self.click_bit_address[temp] = 0x100 + count
          temp = "Y0"+i
          self.click_bit_address[temp] = 0x2000 +count
          temp = "Y1"+i 
          self.click_bit_address[temp] = 0x2020 + count
          temp = "Y2"+i
          self.click_bit_address[temp] = 0x2040 + count
          temp = "Y3"+i
          self.click_bit_address[temp] = 0x2060 + count
          temp = "Y4"+i
          self.click_bit_address[temp] = 0x2080 + count
          temp = "Y5"+i
          self.click_bit_address[temp] = 0x20A0 + count
          temp = "Y6"+i
          self.click_bit_address[temp] = 0x20c0 + count
          temp = "Y7"+i
          self.click_bit_address[temp] = 0x20e0 + count
          temp = "Y8"+i
          self.click_bit_address[temp] = 0x2100 + count
          count = count+1

       for i in range(1,999):
           temp = "SC"+str(i)
           self.click_bit_address[temp] = 0xf000 + i-1
       
   def disable_all_sprinklers( self, modbus_address, input_list ):
      write_bit      = self.click_bit_address["C1"]
      
      self.instrument.write_bits(modbus_address,write_bit, [0] )
      self.instrument.write_bits(modbus_address,write_bit, [1] )
      self.instrument.write_bits(modbus_address,write_bit, [0] )



   def turn_on_valves( self, modbus_address, input_list ):
      
       for valve in input_list:  
          valve           = valve -1
          bit_symbol      = self.click_io[ valve ]
          bit_address     = self.click_bit_address[bit_symbol]
          self.instrument.write_bits( modbus_address, bit_address,[1])

   def turn_off_valves( self,  modbus_address, input_list  ):
          
       for valve in input_list:  
          valve           = valve -1
          bit_symbol      = self.click_io[ valve ]
          bit_address     = self.click_bit_address[bit_symbol]
          self.instrument.write_bits( modbus_address, bit_address,[0])


   def load_duration_counters( self, modbus_address,input_list  ):
        duration = input_list[0]
        write_bit      = self.click_bit_address["C2"]
        write_register = self.click_reg_address["DS2"]
        self.instrument.write_registers( modbus_address, write_register, [duration] )
        self.instrument.write_bits( modbus_address, write_bit,[0])
        self.instrument.write_bits( modbus_address, write_bit,[1])

       
                         
   def clear_duration_counters( self, modbus_address  ):
        write_bit      = self.click_bit_address["C2"]
        write_register = self.click_reg_address["DS2"]
        self.instrument.write_registers( modbus_address, write_register, [0] )
        self.instrument.write_bits( modbus_address, write_bit,[0])
 

   def read_input_bit( self, modbus_address, input_list ):
      
      read_bit      = self.click_bit_address[input_list[0]]
     
      return self.instrument.read_bits(modbus_address, read_bit,1 )[0]


   def read_mode_switch( self, modbus_address ):
      read_bit      = self.click_bit_address["SC11"]
      return self.instrument.read_bits( modbus_address, read_bit,1 )[0]

   def read_mode( self, modbus_address ):
      read_bit      = self.click_bit_address["SC10"]

      return self.instrument.read_bits( modbus_address, read_bit,1 )[0]

  
   def read_wd_flag( self, modbus_address ):
      read_bit      = self.click_bit_address["C200"]
      return self.instrument.read_bits( modbus_address, read_bit,1 )[0]
      

   def write_wd_flag( self, modbus_address ):
      write_bit      = self.click_bit_address["C200"]
      self.instrument.write_bits(modbus_address,write_bit, [1] )


      

   def measure_counter( self, modbus_address, io_dict ):
 
       counter_register    = io_dict["read_register"]      

       latch_bit           = io_dict["latch_bit"]
       
      
       write_bit      = self.click_bit_address[ latch_bit ]

       # These three statements create a rising pulse
       self.instrument.write_bits( modbus_address, write_bit,[0])
       self.instrument.write_bits( modbus_address, write_bit,[1]) 
       self.instrument.write_bits( modbus_address, write_bit,[0])
       time.sleep(.1)

       read_register = self.click_reg_address[ counter_register ]  
           
       counter_value = self.instrument.read_registers( modbus_address, read_register ,1 )[0]
         
      
       return counter_value




class Click_Controller_Base_Class_44(Click_Controller_Base_Class):
    
   def __init__(self,instrument):
       
       click_io = [
                  "Y001","Y002","Y003","Y004", # 1-4
                  "Y101","Y102","Y103","Y104","Y105","Y106","Y107","Y108", # 5 -12
                  "Y201","Y202","Y203","Y204","Y205","Y206","Y207","Y208", # 13 -20
                  "Y301","Y302","Y303","Y304","Y305","Y306","Y307","Y308", # 21 -28
                  "Y401","Y402","Y403","Y404","Y405","Y406","Y407","Y408", # 29 -36
                  "Y501","Y502","Y503","Y504", # 37 -40
                  "Y601","Y602","Y603","Y604" # 41 -44
               ]

       m_tags = {}
       m_tags["measure_analog"] = self.measure_analog
       m_tags["measure_counter"] = self.measure_counter
       super().__init__(instrument, click_io, m_tags = m_tags )
    
   def measure_analog( self, modbus_address, list_input ):
       read_register     = str(list_input[0])
       conversion_factor = list_input[1]
       
       if isinstance( read_register, str):
           register           = self.click_reg_address[read_register]
       
       value              = self.instrument.read_floats( modbus_address, register,1 )
 
       
       conv_value         = value[0] * conversion_factor
       return conv_value
    
       
        

class Click_Controller_Base_Class_22(Click_Controller_Base_Class):
    
   def __init__(self,instrument):
       click_io = [
                      "Y001","Y002","Y003","Y004", "Y005","Y006", # 1-6
                      "Y101","Y102","Y103","Y104","Y105","Y106","Y107","Y108", # 7 -14
                      "Y201","Y202","Y203","Y204","Y205","Y206","Y207","Y208" # 15 -22
                ]

       super().__init__(instrument,click_io)
       
    
 
class Click_Controller_Base_Class_Power_Control(Click_Controller_Base_Class):
    
   def __init__(self,instrument):
       
       click_io = [
                  "Y001","Y002","Y003","Y004", # 1-4
                  "Y101","Y102","Y103","Y104", # 4-8
               ]

       m_tags = {}
       m_tags["measure_analog"] = self.measure_analog
       m_tags["measure_counter"] = self.measure_counter
       super().__init__(instrument, click_io, m_tags = m_tags )
    
   def measure_analog( self, modbus_address, list_input ):
       read_register     = str(list_input[0])
       conversion_factor = list_input[1]
       
       if isinstance( read_register, str):
           register           = self.click_reg_address[read_register]
       
       value              = self.instrument.read_floats( modbus_address, register,1 )
 
       
       conv_value         = value[0] * conversion_factor
       return conv_value
    

           
if __name__ == "__main__":  
   from  .new_instrument_py3 import Modbus_Instrument
   instrument  =  Modbus_Instrument()
     

   x = Click_Controller_Base_Class_44( instrument )
   y = Click_Controller_Base_Class_22( instrument )  
   print (x.m_tags)
   print (y.m_tags)
   print(x.read_wd_flag( 100 ))
   x.write_wd_flag(100)
   print(x.read_wd_flag( 100 ))
    

    
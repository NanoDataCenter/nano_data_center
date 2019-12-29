#
# File: rs485_mgr.py
# This file handles low level rs485 communication
#
#
#
#
#
import os
import time

import struct
from  .myModbus_py3 import *

class RS485_Mgr():
   def __init__( self ):
       pass

   def open( self, interface_parameters ):
       try:
           print( "interface_parameters",interface_parameters)
           self.instrument = Instrument(interface_parameters["interface"],40 )  # 10 is instrument address
           print( "timeout", interface_parameters["timeout"])
           self.instrument.serial.timeout = interface_parameters["timeout"]
           self.instrument.serial.parity = serial.PARITY_NONE
           self.instrument.serial.baudrate = interface_parameters["baud_rate"]
           self.instrument.debug = None
           self.interface_parameters = interface_parameters
           return True
       except:
           print( "open return false ")
           return False
       

   def close( self ):
     try:
       self.instrument.serial.close()
       del(self.instrument)
       self.params = None
     except:
       pass 

   def process_message( self, parameters, message, counters = None ):

       retries = 0
       total_failures = 0

       for i in range(0,5):
           
           try:

               response = b""
             
               response =  self.instrument._communicate( message, 1024)
               time.sleep(.05)
               #print "response ",len(response)
              
               if len(response  ) > 4:
                   receivedChecksum          = response[-2:]
                   responseWithoutChecksum   = response[0 : len(response) - 2]
                   calculatedChecksum = self._calculateCrcString(responseWithoutChecksum)
                   #print "crc",[receivedChecksum, calculatedChecksum], ord(message[0]),parameters["address"]
                   if (receivedChecksum == calculatedChecksum) and (message[0] == parameters["address"] ): # check checksum
                        
                        return  total_failures, retries ,response
              
               if counters != None:
                   retries +=1
               
           except:
              raise # serial errror              
              response = ""
 
       total_failures =1 
       return total_failures , retries , response
     


   def find_address( self, parameters):
      return parameters["address"]


   def probe_register( self, address,register,number, counters = None ):
       parameters = {}
       parameters["address"] = address
       payload     = struct.pack("<BBBBBB",address,3,(register>>8)&255,register&255,0,number)  # read register 0 1 length
       calculatedChecksum = self._calculateCrcString(payload)
       payload = payload+calculatedChecksum
       failure,retries, response = self.process_message(parameters,payload,counters )

       #receivedChecksum          = response[-2:]
       #responseWithoutChecksum   = response[0 : len(response) - 2]
       #calculatedChecksum = self._calculateCrcString(responseWithoutChecksum)
       
       #return_value = receivedChecksum == calculatedChecksum # check checksum
       
       if failure == 0 :
             return_value = address == (response[0])  # check address
             
       else:
             return_value = False
       return return_value
 
       

   def _rightshift( self, inputInteger):
       shifted = inputInteger >> 1
       carrybit = inputInteger & 1
       return shifted, carrybit




   def _calculateCrcString(self,inputstring):
       # Constant for MODBUS CRC-16
       POLY = 0xA001
       # Preload a 16-bit register with ones
       register = 0xFFFF
       for character in inputstring:
           # XOR with each character
           register = register ^ character
           # Rightshift 8 times, and XOR with polynom if carry overflows
           for i in range(8):
               register, carrybit = self._rightshift(register)
               if carrybit == 1:
                register = register ^ POLY

       return    struct.pack("<H",register)
     

if __name__ == "__main__":
   rs485_mgr = RS485_Mgr()
   interface_parameters = {}
   interface_parameters["interface"]   = "/dev/ttyUSB0"
   interface_parameters["baud_rate"]   = 38400
   interface_parameters["timeout"]     = .02
   parameters = {}
   parameters["address"] = 100
   parameters["search_register"] = 0
   parameters["register_number"] =  1
   counters = {}
   counters["failures"]        = 0
   counters["counts"]          = 0
   counters["total_failures"]  = 0
   if rs485_mgr.open(interface_parameters ):
     for i in range(0,100):
        
        print( i, rs485_mgr.probe_register( parameters,counters ))
       
     rs485_mgr.close()
   



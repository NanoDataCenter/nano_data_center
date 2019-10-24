#
#  File: modbus_tcp_control.py
#
#
#
#
#

import socket
import sys
import struct
import time

class Modbus_TCP_Control:

   def __init__( self ):
       self.modbus_devices = {}


   def connect_socket( self, modbus_device ):
       
       try:
           
           sock = modbus_device["sock"]    
                                                                                                                                        
           sock.connect(modbus_device["address_port"])
           
           modbus_device["connected"] = True
       except:
           print "connect socket exception --- should not happen"
           modbus_device["connected"] = False
       
   def disconnect_socket( self, modbus_device ):
      
       modbus_device["connected"] = False
       sock = modbus_device["sock"]
       try:
          
          sock.shutdown(1)
          sock.close()
    
       except:
          print "disconnect exception --- should not happen"
       

   def send_message( self, address, message ):
         
       modbus_device = self.modbus_devices[address]
       if modbus_device["connected"] != True:
          self.connect_socket( modbus_device )
       try:
           sock = modbus_device["sock"]
           
           sock.sendall(message)
           
           message = sock.recv(1024)
           
       except:
           "this should not happen"
           message = ""
       return message

   def add_device( self, address ,port = 502 ):
       self.modbus_devices[address]                      = {}
       self.modbus_devices[address]["address_port"]      = ( address,port )
       self.modbus_devices[address]["sock"]              = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.connect_socket( self.modbus_devices[address] )


   def ping_device( self,address ,register ):
       slave_id = 1
       payload     = struct.pack("<BBBBBB",slave_id,3,(register>>8)&255,register&255,0,1)  # read register 0 1 length
       calculatedChecksum = self._calculateCrcString(payload)
       payload = payload+calculatedChecksum
     
       response = self.process_message(address,payload )
       receivedChecksum          = response[-2:]
       responseWithoutChecksum   = response[0 : len(response) - 2]
       calculatedChecksum = self._calculateCrcString(responseWithoutChecksum)
       return_value = receivedChecksum == calculatedChecksum # check checksum
       return return_value

   def unpack_message( self, message):
       payload = message[6:]
       calculatedChecksum = self._calculateCrcString(payload)
       payload = payload+calculatedChecksum
       return payload

   def format_message( self, message):
   
       no_crc_msg = message[0:len(message)-2]
       no_crc_length = len(no_crc_msg)
       length_high = chr( (no_crc_length >> 8)&0xff)
       length_low  = chr(no_crc_length&0xff)
       temp_message = "".join( [chr(0),chr(0),chr(0),chr(0),length_high,length_low,no_crc_msg])
       return temp_message

   def _calculateCrcString(self,inputstring):
       """Calculate CRC-16 for Modbus.
          Args:
             inputstring (str): An arbitrary-length message (without the CRC).
          Returns:
             A two-byte CRC string, where the least significant byte is first.
          Algorithm from the document 'MODBUS over serial line specification and implementation guide V1.02'.
       """
 

       # Constant for MODBUS CRC-16
       POLY = 0xA001

       # Preload a 16-bit register with ones
       register = 0xFFFF

       for character in inputstring:

           # XOR with each character
           register = register ^ ord(character)

           # Rightshift 8 times, and XOR with polynom if carry overflows
           for i in range(8):
               carrybit = register & 1
               register = register >> 1
               
    

               if carrybit == 1:
                register = register ^ POLY
       
       return struct.pack('<H', register)



   def process_message( self, ip_address, message, counters = None ):
      
       message = self.format_message( message)
       
      
       for i in range(0,10):
           
           try:
               
               response =  self.send_message( ip_address, message  )
               response = self.unpack_message( response)
 
               if len(response  ) > 4:
                   receivedChecksum          = response[-2:]
                   responseWithoutChecksum   = response[0 : len(response) - 2]
                   calculatedChecksum = self._calculateCrcString(responseWithoutChecksum)
                   
                   if (receivedChecksum == calculatedChecksum): 
                       
                       if counters != None:
                           counters["counts"] = counters["counts"] +1
                       return response
                   else:
                       
                       if counters != None:
                           counters["failures"] = counters["failures"] +1
               time.sleep(.1)
           except:
              print "except should not happen"
              response = ""
              
       if counters != None:  
           counters["total_failures"] = counters["total_failures"] +1
       return response

if __name__ == "__main__":
   tcp_mgr = Modbus_TCP_Control()
   tcp_mgr.add_device( "192.168.1.153"  )
   print tcp_mgr.ping_device("192.168.1.153" ,0 )


   #print tcp_mgr.modbus_devices
   #tcp_mgr.disconnect_socket(tcp_mgr.modbus_devices["192.168.1.153"])
   #print tcp_mgr.modbus_devices      


'''
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
import myModbus
import struct
from  myModbus import *

class RS485_Mgr():
   def __init__( self ):
       pass

   def open( self, interface_parameters ):
       try:
           
           self.instrument = Instrument(interface_parameters["interface"],31 )  # 10 is instrument address
           self.instrument.serial.timeout = interface_parameters["timeout"]
           self.instrument.serial.parity = serial.PARITY_NONE
           self.instrument.serial.baudrate = interface_parameters["baud_rate"]
           self.instrument.debug = None
           self.interface_parameters = interface_parameters
           return True
       except:
           return False
       

   def close( self ):
     try:
       self.instrument.serial.close()
       del(self.instrument)
       self.params = None
     except:
       pass 

   def process_message( self, parameters, message, counters = None ):
       print "made it to rs485"
       for i in range(0,10):
           try:

               response = ""
               response =  self.instrument._communicate( message, 1024)
               print "message",[message],len(response),[response]
               if len(response  ) > 4:
                   receivedChecksum          = response[-2:]
                   responseWithoutChecksum   = response[0 : len(response) - 2]
                   calculatedChecksum = self._calculateCrcString(responseWithoutChecksum)
                   print "crc",[receivedChecksum, calculatedChecksum], ord(message[0]),parameters["address"]
                   if (receivedChecksum == calculatedChecksum) and (ord(message[0]) == parameters["address"] ): # check checksum
                       print "made it here",counters
                       if counters != None:
                           counters["counts"] = counters["counts"] +1
                       return response
                   else:
                       if counters != None:
                           counters["failures"] = counters["failures"] +1
               time.sleep(self.instrument.timeout)
           except:
              response = ""
       if counters != None:  
           counters["total_failures"] = counters["total_failures"] +1
       return response
     


   def find_address( self, parameters):
      return parameters["address"]


   def probe_register( self, parameters ):
       address     = parameters["address"]
       register    = parameters["search_register"]
       payload     = struct.pack("<BBBBBB",address,3,(register>>8)&255,register&255,0,1)  # read register 0 1 length
       calculatedChecksum = self._calculateCrcString(payload)
       payload = payload+calculatedChecksum
       response = self.process_message(parameters,payload )
       receivedChecksum          = response[-2:]
       responseWithoutChecksum   = response[0 : len(response) - 2]
       calculatedChecksum = self._calculateCrcString(responseWithoutChecksum)
       return_value = receivedChecksum == calculatedChecksum # check checksum
       if return_value == True :
             return_value = address == ord(response[0])  # check address
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
           register = register ^ ord(character)
           # Rightshift 8 times, and XOR with polynom if carry overflows
           for i in range(8):
               register, carrybit = self._rightshift(register)
               if carrybit == 1:
                register = register ^ POLY

       return    struct.pack("<H",register)
     

if __name__ == "__main__":
   rs485_mgr = RS485_Mgr()
   interface_parameters = {}
   interface_parameters["interface"]   = "/dev/ttyACM0"
   interface_parameters["baud_rate"]   = 38400
   interface_parameters["timeout"]     = .15
   parameters = {}
   parameters["address"] = 31
   parameters["search_register"] = 0
   if rs485_mgr.open(interface_parameters ):
     print rs485_mgr.probe_register( parameters )
     rs485_mgr.close()
      

'''

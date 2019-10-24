#
#
#  File: io_controller_class.py
#
#
#
#
#

import struct    
import bitstruct 
import os
import sys
import time
import select
import socket
import json
import redis





class IO_Controller_Class:
    
    def __init__(self,name, new_instrument, ip, port = 5005  ):
        self.name            = name
        self.new_instrument = new_instrument
        self.ip             = ip
        self.port           = port
                          


    def ping_device( self,  address_list ):
        self.new_instrument.set_ip( self.ip, self.port )
        return self.new_instrument.ping_device( address_list )
       

    def ping_all_devices( self ):
        self.new_instrument.set_ip( self.ip, self.port )
        return self.new_instrument.ping_all_devices()

    def clear_all_counters( self ):
        self.new_instrument.set_ip( self.ip, self.port )
        return self.new_instrument.clear_all_counters()

    def get_all_counters( self ):
        self.new_instrument.set_ip( self.ip, self.port )
        return self.new_instrument.get_all_counters()

    def clear_counter_list( self, address_list ):
        self.new_instrument.set_ip( self.ip, self.port )
        return self.new_instrument.clear_counter_list( address_list)
 
class Build_Controller_Classes:

   def __init__( self, new_instrument ):
      self.controller_classes = {}
      self.redis_handle =  redis.StrictRedis(host='localhost', port=6379, db=3)
      self.io_controller_list  = self.redis_handle.hkeys("IO_CONTROLLER_HASH" )
      for i in self.io_controller_list:
          temp_json= self.redis_handle.hmget( "IO_CONTROLLER_HASH",i )
 
          temp_data = json.loads(temp_json[0])
          temp_class = IO_Controller_Class( temp_data["name"], new_instrument, temp_data["ip"], temp_data["port"] )
          self.controller_classes[temp_data["ip"] ] = temp_class

   def get_controller_class( self, ip ):
       try:
           return self.controller_classes[ip]
       except:
           raise ValueError("Unknown io_controller ip "+ip)


           
if __name__ == "__main__":     
   import new_instrument
   client_driver = new_instrument.Modbus_Instrument()
   controller_classes = Build_Controller_Classes(client_driver)
  
   controller_driver = controller_classes.get_controller_class( "192.168.1.82" )
   print controller_driver.ping_all_devices()
   print controller_driver.ping_device( [40,100] )


    
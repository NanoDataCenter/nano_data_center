#
#
#  File: io_controller
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





class IO_Controller(object):
    
    def __init__(self, instrument  ):
        self.instrument = instrument
        self.m_tags = {}                          
        self.m_tags["modbus_statistics"] = self.get_modbus_statistics


       

    def clear_all_counters( self ):
        return self.instrument.clear_all_counters()

    def get_all_counters( self ):
        return self.instrument.get_all_counters()

    def get_modbus_statistics( self, modbus_address, list_parameters ):
        return_value = self.get_all_counters()
        self.clear_all_counters()
        return return_value

   
if __name__ == "__main__":     
    pass    
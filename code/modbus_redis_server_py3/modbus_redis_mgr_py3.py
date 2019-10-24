import struct
import redis
import json


#
#
# TBD:  Need to look at this module again
#
#
#
#
#



class ModbusRedisServer():  # manages the local functions of io server
   def __init__(self, message_handler,host = "127.0.0.1", redis_db = 0 ):
       self.redis_handle            = redis.StrictRedis( host , port=6379, db = redis_db )
       self.message_handler = message_handler
       self.commands              = {}
       self.commands[255]         = self.set_redis_registers 
       self.commands[254]         = self.read_redis_registers
       self.commands[253]         = self.ping_functions
       self.commands[252]         = self.counter_functions
       self.ping_functions_dict   = {"ping_device": self.ping_device_a,"ping_all_devices":   self.ping_all_devices_a }
       self.counter_functions     = {"clear_all_counters": self.clear_all_counters, "get_all_counters": self.get_all_counters, "clear_counter_list": self.clear_counter_list }

   def set_redis_registers( self, json_object ):
       keys = json_object.keys()
       for i in keys:
           self.redis_handle.set( i, json_object[i] )
       return None

   def read_redis_registers( self, json_object ):
      return_dict = {}
      for i in json_object:
          return_dict[i] = self.redis_handle.get(i)
      return return_dict

   def counter_functions( self, json_object ):

      temp             = json_object["parameters"]
      action           = temp["sub_action"]
      parameters       = temp["sub_parameter"]
      if self.counter_functions.has_key(action):
          return self.counter_functions[ action ](parameters)
      else:
          return None
                          
   def clear_counter_list( self , parameters ):
       for i in parameters:
          self.message_handler.clear_counter( i )
       return None
   
   def get_all_counters( self, parameters = None ):
        return self.message_handler.get_counters()
        

   def clear_all_counters( self,parameters = None ):
        self.message_handler.clear_all_counters()
        return None

   def ping_functions( self, json_object ):
     
      temp             = json_object["parameters"]
      action           = temp["sub_action"]
      parameters       = temp["sub_parameter"]
      return self.ping_functions_dict[action](parameters)
        

              
   def ping_device_a( self, parameters  ):
        return self.message_handler.ping_devices(parameters)
        

   def ping_all_devices_a( self,parameters = None ):
        return self.message_handler.ping_all_devices()
      

   #handles local functions to UDP IO SERVER
   def process_msg( self, 
                    address,   # not used
                    msg, 
                    counter   ):  
       
       #try:
           
           # message length = msg[0]
           function_code  = ord(msg[1])
           json_string    = msg[2:-2]
           return_list = []
           return_list.append(msg[0:2])
           json_object = json.loads(json_string)
           result = json.dumps(None)

           if self.commands.has_key( int(function_code)):
              result = json.dumps( self.commands[function_code](json_object ) )
           else:
              result = json.dumps(None)
           return_list.append(result)

           return_string = "".join(return_list)
    
           return_string = return_string +self._calculateCrcString(return_string)
           return return_string
           
             


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



if __name__ == "__main__":          

   server = ModbusRedisServer(None, 2) 
   msg_list = []
   msg_list.append([chr(23),chr(255)]) # dummy message length
   msg_list.append( json.dumps({ "test_1":21,"test_2":22 }))
   msg_string = "".join(msg_list[0])
   msg_string = msg_string + msg_list[1] +"dc" #dummy dc crc

   return_string = server.process_msg(0,msg_string,0)
   print( "return string",return_string)
   msg_list = []
   msg_list.append([chr(23),chr(254)]) # dummy message length
   msg_list[0] = "".join(msg_list[0])
   msg_list.append( json.dumps( [ "test_1","test_2" ])) # dummy dc crc
   msg_list.append("dc")
   msg_string = "".join(msg_list)

   return_string = server.process_msg(0,msg_string,0)
   print( "return string",return_string[2:-2])

   
    

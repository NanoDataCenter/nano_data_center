#
#
#  File: modbus_instrument_udp.py
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

class new_instrument_network:
    
    def __init__(self ):

        self.precalculate_read_size = True
        self.sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM) # UDP
                          
                          
    #sets the ip and port of udp server
    def set_ip( self,ip ="127.0.0.1", port = 5005 ):
         self.ip    = ip
         self.port  = port
        

#read_bits
#Request
#Function code 1 Byte 0x02
#Starting Address 2 Bytes 0x0000 to 0xFFFF
#Quantity of Inputs 2 Bytes 1 to 2000 (0x7D0)
#Response
#Function code 1 Byte 0x02
#Byte count 1 Byte N*
#Input Status N* x 1 Byte

    def redis_write( self,   json_data ):
       return self.redis_communicate( 255, json_data )

    def redis_read( self,   json_data):
       return self.redis_communicate( 254,  json_data)

    def ping_device( self,  address_list ):

        json_data = {"action":"ping"   ,"parameters":{ "sub_action":"ping_device"   , "sub_parameter":address_list   } }
        return self.redis_communicate( 253, json_data)

    def ping_all_devices( self ):

        json_data = {"action":"ping"  ,"parameters":{ "sub_action":"ping_all_devices"    , "sub_parameter": None  } }
        return self.redis_communicate( 253, json_data)

    def clear_all_counters( self ):

        json_data = {"action":"counter"   ,"parameters":{ "sub_action":"clear_all_counters"   , "sub_parameter":None   } }
        return self.redis_communicate(  252, json_data)

    def get_all_counters( self ):

        json_data = {"action":"counter"   ,"parameters":{ "sub_action": "get_all_counters" , "sub_parameter":None   } }
        return self.redis_communicate( 252,json_data)

    def clear_counter_list( self, address_list ):

        json_data = {"action":"counter"   ,"parameters":{ "sub_action":"clear_counter_list"   , "sub_parameter":address_list   } }
        return self.redis_communicate(252, json_data)

  
    def read_bits(self, modbus_address, registeraddress, bit_number,  functioncode=2):
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(registeraddress) + self._numToTwoByteString(bit_number)
        
        return_value = []        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
    
        crc_flag, return_data = self.check_crc( response )
        if crc_flag != 0:

            byte_count = ord(return_data[0])
            for i in return_data[1:]:
                if bit_number >= 8 :
                    bit_number -= 8
                    return_value.extend( self.unpack_bits( 8, ord(i) ) )
                else:
                    
                    return_value.extend( self.unpack_bits(bit_number, ord(i) ) )
                    bit_number = 0
    
        return return_value 
    

#Request PDU
#Function code 1 Byte 0x0F
#Starting Address 2 Bytes 0x0000 to 0xFFFF
#Quantity of Outputs 2 Bytes 0x0001 to 0x07B0
#Byte Count 1 Byte N*
#Outputs Value N* x 1 Byte
#*N = Quantity of Outputs / 8, if the remainder is different of 0 ? N = N+1
#Response PDU
#Function code 1 Byte 0x0F
#Starting Address 2 Bytes 0x0000 to 0xFFFF
#Quantity of Outputs 2 Bytes 0x0001 to 0x07B0


    def write_bits(self, modbus_address, registeraddress, value, functioncode=15):
        number_of_bits = len( value )
        
        bit_data = ""
         # pack bit fields in word array
        # use pack to pact into network string
        loop_count = number_of_bits/8
        if (number_of_bits % 8) != 0:
             loop_count += 1
 
        for i in range(0, loop_count  ):
             if len( value ) > 8 :
                 data = value[:8]
                 value = value[8:]
             else:
                 data = value                 
             bit_data +=  chr( self.pack_bits( data ) )
             
        
        payloadToSlave =  self._numToOneByteString(modbus_address ) + self._numToOneByteString(functioncode) + \
                          self._numToTwoByteString(registeraddress) + self._numToTwoByteString(number_of_bits) + self._numToOneByteString( loop_count ) +bit_data
        message = payloadToSlave + self._calculateCrcString(payloadToSlave)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )
        if crc_flag != 0:
                pass
        else:
                 raise
           
        return 

#Request
#Function code 1 Byte 0x03
#Starting Address 2 Bytes 0x0000 to 0xFFFF
#Quantity of Registers 2 Bytes 1 to 125 (0x7D)
#Response
#Function code 1 Byte 0x03
#Byte count 1 Byte 2 x N*
#Register value N* x 2 Bytes
#*N = Quantity of Registers 
    def read_registers(self, modbus_address, registeraddress, register_number, functioncode=3, signed=False):
        
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(registeraddress) + self._numToTwoByteString(register_number)
                        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )
        if crc_flag != 0:
            return self._twoByteStringToShort(return_data[1:], register_number, signed)

#Request
#Slave Address 11
#Function 10
#Starting Address Hi 00
#Starting Address Lo 01
#No. of Registers Hi 00
#No. of Registers Lo 02
#Byte Count 04
#Data Hi 00
#Data Lo 0A
#Data Hi 01
#Data Lo 02

#Response
#Field Name (Hex)
#Slave Address 11
#Function 10
#Starting Address Hi 00
#Starting Address Lo 01
#No. of Registers Hi 00
#No. of Registers Lo 02
#Error Check (LRC or CRC) 


    def write_registers(self, modbus_address, registeraddress, value, functioncode=16, signed=False):
        register_number = len(value)
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(registeraddress) + self._numToTwoByteString(register_number) +\
                        self._numToOneByteString( len(value)*2 )
        first_part += self.packShorts( value, signed )
        
                        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )


 

#Request
#Function code 1 Byte 0x03
#Starting Address 2 Bytes 0x0000 to 0xFFFF
#Quantity of Registers 2 Bytes 1 to 125 (0x7D) ( 2 X number of longs )
#Response
#Function code 1 Byte 0x03
#Byte count 1 Byte 2 x N*
#Register value N* x 2 Bytes  ( 4 x Number of longs )
#*N = Quantity of Registers
    def read_longs(self, modbus_address, registeraddress,  register_number, functioncode=3, signed=False):
        
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(registeraddress) + self._numToTwoByteString(register_number*2)
                        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )
        if crc_flag != 0:
            return self._bytestringToLong(return_data[1:], register_number, signed)


    def write_longs(self,modbus_address, registeraddress, value, functioncode=16, signed=False):
        register_number = len(value )*2
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(registeraddress) + self._numToTwoByteString(register_number) +\
                        self._numToOneByteString( len(value)*4 )
        first_part += self.packLongs( value, signed )
        
                        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )
  
 
#Request
#Function code 1 Byte 0x03
#Starting Address 2 Bytes 0x0000 to 0xFFFF
#Quantity of Registers 2 Bytes 1 to 125 (0x7D) ( 2 X number of longs )
#Response
#Function code 1 Byte 0x03
#Byte count 1 Byte 2 x N*
#Register value N* x 2 Bytes  ( 4 x Number of longs )
#*N = Quantity of Registers

    def read_floats(self, modbus_address, registeraddress, register_number, functioncode=3):
        
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(registeraddress) + self._numToTwoByteString(register_number*2)
                        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )
        if crc_flag != 0:
            return self._bytestringToFloat(return_data[1:], register_number)

    def write_floats(self, modbus_address, registeraddress, value, functioncode = 16):
        register_number = len(value )*2
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(registeraddress) + self._numToTwoByteString(register_number) +\
                        self._numToOneByteString( len(value)*4 )
        first_part += self.packFloats( value)
        
                        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )
   
    

# Request
#Function code 1 Byte 0x18
#FIFO Pointer Address 2 Bytes 0x0000 to 0xFFFF

#Response
#Function code 1 Byte 0x18
#Byte Count 2 Bytes
#FIFO Count 2 Bytes = 31
#FIFO Value Register N* x 2 Bytes
#*N = FIFO Count

      
    def read_fifo(self, modbus_address, fifo_index , functioncode=24):
        
        return_value = []
        
        first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(functioncode) + \
                        self._numToTwoByteString(fifo_index) 
                        
        message = first_part + self._calculateCrcString(first_part)
        response = self._communicate(message)
        crc_flag, return_data = self.check_crc( response )
        if crc_flag != 0:
            byte_count = self._twoByteStringToShort(return_data[:2], 1, False)[0]
            fifo_count = self._twoByteStringToShort(return_data[2:4], 1, False )[0]
            
            if fifo_count > 0:
                byte_stream = return_data[4:]
                for i in range( 0,  fifo_count ):
                    extract_stream = byte_stream[:2]
                    byte_stream = byte_stream[2:]
                    temp = self._twoByteStringToShort( extract_stream, 1, False)
                    return_value.extend( temp )
        return return_value
            
#
#
# This command talkes with the UDP server
#
#
    def redis_communicate( self,  function_code, json_data , modbus_address = 255):
       pay_load_data =  json.dumps(json_data)
       first_part  = self._numToOneByteString(modbus_address) + self._numToOneByteString(function_code) + \
                        pay_load_data
                        
       message = first_part + self._calculateCrcString(first_part)
       response = self._communicate(message, 1024)
       return self.check_crc( response )
        

       

    
    def _communicate(self, message, number_of_bytes_to_read= 1024):
         
        #print "made it here", self.ip, self.port
        self.sock.sendto(message, (self.ip, self.port))        


        
        self.sock.setblocking(0)
        ready = select.select([self.sock], [], [], 5.0)
        answer = ""
        if ready[0]:
            data = self.sock.recvfrom(1024)
            answer = data[0]
            
        if len(answer) == 0:
            print "no communication with the instrument"
            raise IOError('No communication with the instrument (no answer)')

        return answer


    def check_crc( self, response ):
         receivedChecksum = response[-2:]
         responseWithoutChecksum = response[0 : len(response) - 2]
         calculatedChecksum = self._calculateCrcString(responseWithoutChecksum)
         crc_check = receivedChecksum == calculatedChecksum
         return crc_check, responseWithoutChecksum[2:]
         
    def _calculateCrcString(self,inputstring):
      # Constant for MODBUS CRC-16
      POLY = 0xA001
      # Preload a 16-bit register with ones
      register = 0xFFFF

      for character in inputstring:
        # XOR with each character
        register = self._XOR(register, ord(character))

        # Rightshift 8 times, and XOR with polynom if carry overflows
        for i in range(8):
            register, carrybit = self._rightshift(register)
            if carrybit == 1:
                register = self._XOR(register, POLY)

      return self._numToTwoByteString(register, LsbFirst=True)

    def _XOR(self,integer1, integer2):
       return integer1 ^ integer2


    def _setBitOn( self,x, bitNum):
       return x | (1 << bitNum)


    def _rightshift(self,inputInteger):
       shifted = inputInteger >> 1
       carrybit = inputInteger & 1
       return shifted, carrybit
    


    def _numToTwoByteString(self,value,  LsbFirst=False, signed=False):

    
        if LsbFirst:
              formatcode = '<'  # Little-endian
        else:
              formatcode = '>'  # Big-endian
        if signed:
             formatcode += 'h'  # (Signed) short (2 bytes)
        else:
             formatcode += 'H'  # Unsigned short (2 bytes)
        
       
        outstring = struct.pack(formatcode, int(value)&0xffff )

        assert len(outstring) == 2
        return outstring
        
        
    def _numToOneByteString( self,inputvalue):
         return chr(inputvalue)
         
          
    def _twoByteStringToShort(self,bytestring, numberOfRegisters, signed=False):

        formatcode = '>'  # BIG-end
        for i in range(0,numberOfRegisters):
             if signed:
                 formatcode += 'h'  # (Signed) short (2 bytes)
             else:
                 formatcode += 'H'  # Unsigned short (2 bytes)

        return list(struct.unpack(formatcode, bytestring))
     

   

    def _bytestringToLong(self,bytestring, numberOfRegisters, signed ):
      
      packcode   = '<'
      formatcode = '<'  # Little end
      for i in range( 0, numberOfRegisters ):
          packcode += "HH"
          if signed:
              formatcode += 'l'  # (Signed) long (4 bytes)
          else:
              formatcode += 'L'  # Unsigned long (4 bytes)
              
      temp_list    = self._twoByteStringToShort( bytestring, numberOfRegisters*2, signed=False)
      print "temp_list",temp_list
      temp_string  = struct.pack(packcode,*temp_list )
      return list(struct.unpack(formatcode, temp_string ))

    def _bytestringToFloat(self,bytestring, numberOfRegisters=2):
      formatcode = '<'  # little end
      packcode   = "<"
      
      for i in range( 0, numberOfRegisters ): 
          formatcode += 'f'  
          packcode += 'HH'
          
      temp_list    = self._twoByteStringToShort( bytestring, numberOfRegisters*2, signed=False)
      temp_string  = struct.pack(packcode,*temp_list )
      return list(struct.unpack(formatcode, temp_string ))

    def _floatToBytestring(self,value, numberOfRegisters=2):

      formatcode = '<'  # BIG end
      if numberOfRegisters == 2:
        formatcode += 'f'  # Float (4 bytes)
        lengthtarget = 4
      elif numberOfRegisters == 4:
        formatcode += 'd'  # Double (8 bytes)
        lengthtarget = 8
      else:
        raise ValueError('Wrong number of registers! Given value is {0!r}'.format(numberOfRegisters))

      outstring = self._unpack(formatcode, value)
      assert len(outstring) == lengthtarget
      return outstring


    def packFloats( self, value ):
        short_list = []
        for i in value:
            self.pack32bit( short_list, i,"f" )
       
        formatcode = ">"
        for i in range( 0, len(value )):
           formatcode += 'HH'  # Unsigned short (2 bytes)
        return struct.pack( formatcode, *short_list)         
        
    def packLongs( self, value, signed ):
        short_list = []
        
        if signed:
              format_code = 'l'  # (Signed) long (4 bytes)
        else:
              format_code = 'L'  # Unsigned long (4 bytes)

        for i in value:
            self.pack32bit( short_list, i,format_code, signed )
            
        formatcode = ">"
        for i in range( 0, len(value )):
            if signed:
               formatcode += 'hh'  # (Signed) short (2 bytes)
            else:
                formatcode += 'HH'  # Unsigned short (2 bytes)
        return struct.pack( formatcode, *short_list )         
           

    def packShorts( self, value, signed ):
        formatcode = ">"
        for i in range( 0, len(value )):
            if signed:
               formatcode += 'h'  # (Signed) short (2 bytes)
            else:
                formatcode += 'H'  # Unsigned short (2 bytes)
        return struct.pack( formatcode, *value )    
            
    def pack32bit( self, return_value, value, format, signed = False ):
        
        formatcode = "<"+format
        bytestream = struct.pack(formatcode, value )
        if signed :
           values = list( struct.unpack("<hh",bytestream ) )
        else:
           values = list( struct.unpack("<HH",bytestream ))
        return_value.extend( values)
    

    def unpack_bits( self, bit_number,bit_data ):
        k = 1
        return_value = []

        for i in range( 0, bit_number ):
            if k & bit_data:
                return_value.append( 1)
            else:
                 return_value.append(0)
            k = k + k
 
        return return_value

    def pack_bits( self, bit_array ):
        k = 1

        return_value = 0
        for i in range( 0,len(bit_array) ):
            if  bit_array[i] > 0:
                return_value |= k
        
            k = k + k
 
        return return_value
        
            
if __name__ == "__main__":     
    #
    # Remove window fire wall before running this test
    #
    instrument = new_instrument_network()
    instrument.set_ip("192.168.1.82",5005)
    print instrument.read_bits( 100, 0x4063, 7 ,  functioncode=1)
    print instrument.write_bits( 100, 0x4063,  value = [ 1,1,0,0,0,0,0,1,1] ,functioncode=15)   
    print instrument.read_bits( 100, 0x4063, 15 ,  functioncode=1)   
    print instrument.write_bits( 100, 0x4063,   value = [ 0,0,0,0,0,0,0,0,0,0] ,functioncode=15)   
    print instrument.read_bits( 100, 0x4063, 15 ,  functioncode=1)   

    print instrument.read_registers( modbus_address=100, registeraddress = 20, register_number=10, functioncode = 3 )
    print instrument.write_registers( modbus_address=100, registeraddress = 20, functioncode = 16,value=[ 10,20,30,40,50,60,70,80,90,100] )
    print instrument.read_registers( modbus_address=100, registeraddress=20, register_number=10, functioncode = 3)
    print instrument.write_registers( modbus_address=100, registeraddress = 20, functioncode = 16,value=[ 0,0,0,0,0,0,0,0,0,0] )
    print instrument.read_registers( modbus_address=100, registeraddress=1, register_number=10, functioncode=3, signed=False)
    print instrument.read_bits( 100, 61449, 1, functioncode = 2 )
	
    quit()
    #instrument.set_ip()
    #print  instrument.redis_write( {"test1":123,"test2":124 } )
    #print  instrument.redis_read(["test1","test2"] )
    #print  instrument.redis_write( {"test1":34,"test2":35 } )
    #print  instrument.redis_read(["test1","test2"] )
    #print instrument.ping_device( [31] )
    #print instrument.ping_all_devices(  )

    #print instrument.get_all_counters(  )
    #print instrument.clear_all_counters( )
    #print instrument.clear_counter_list( [31] )
    #print instrument.get_all_counters(  )
    #print instrument.read_fifo( 31, 0  )
    
    #print instrument.read_registers( modbus_address=31, registeraddress = 20, register_number=10, functioncode = 34 )
    #print instrument.write_registers( modbus_address=31, registeraddress = 20, functioncode = 35,value=[ 10,20,30,40,50,60,70,80,90,100] )
    #print instrument.read_registers( modbus_address=31, registeraddress=20, register_number=10, functioncode = 34 )
    

    #quit()
    instrument.set_ip()
    for i in range( 0, 1):
        print instrument.read_registers( modbus_address=31, registeraddress=1, register_number=10, functioncode=3, signed=False)
        print instrument.read_registers( modbus_address=31, registeraddress=10, register_number=1, functioncode=3, signed=False)
        print instrument.read_registers( modbus_address=31, registeraddress=11, register_number=3, functioncode=3, signed=False)
        print instrument.read_longs( modbus_address=31,registeraddress=20,register_number=2,functioncode = 3, signed=True )
        print instrument.read_longs( modbus_address=31,registeraddress=21,register_number=2,functioncode = 3, signed=True )
        print instrument.read_longs( modbus_address=31,registeraddress=22,register_number=2,functioncode = 3, signed=True )
        print instrument.read_longs( modbus_address=31,registeraddress=23,register_number=2,functioncode = 3, signed=True )
        print instrument.read_longs( modbus_address=31,registeraddress=30,register_number=3,functioncode = 3, signed=True )
        print instrument.read_longs( modbus_address=31,registeraddress=31,register_number=3,functioncode = 3, signed=True )
        print instrument.read_longs( modbus_address=31,registeraddress=32,register_number=3,functioncode = 3, signed=True )
        print instrument.read_longs( modbus_address=31,registeraddress=33,register_number=3,functioncode = 3, signed=True )
        print instrument.read_floats( modbus_address=31,registeraddress=40,register_number=2,functioncode = 3 )
        print instrument.read_registers( modbus_address=31, registeraddress=11, register_number=3, functioncode=3, signed=False)
        print instrument.write_registers( modbus_address=31, registeraddress = 20,  functioncode = 16, signed = False , value = [ 0x0303,0x0303,2016 ] )
        print instrument.read_registers( modbus_address=31, registeraddress=11, register_number=3, functioncode=3, signed=False)
        print instrument.write_floats( modbus_address=31, registeraddress= 40, functioncode=16, value = [2.34] )
        print instrument.write_longs( modbus_address=31, registeraddress=30, functioncode=16, value = [0xa5a55a5a])
        
    
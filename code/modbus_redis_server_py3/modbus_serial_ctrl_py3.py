#
#
# File: modbus_serial_ctrl.py
#
#
#
import os
import serial
import struct

            

class ModbusSerialCtrl():
   def __init__( self, logical_interface, remote_devices ):
      
      
       self.logical_interface       = logical_interface
       self.remote_devices          = remote_devices
       
       self.serial_devices              = self.find_physical_serial_interfaces()
       
       self.open_logical_interfaces(logical_interface)
       

       

   def find_remote( self, address):
       
       if address in self.remote_devices:
           temp = self.remote_devices[address]
           handler =  self.logical_interface["handler"]
           parameters   =temp
           interface_parameters =  self.logical_interface["interface_parameters"]
           return handler,interface_parameters, parameters
       else:   
           return None,None,None

   def ping_all_devices( self ):
       
       return_value = {}
       for i , j, in self.remote_devices.items():

           logical_interface         = j["interface"]
           handler                   = self.serial_interfaces[ logical_interface ]["handler"]
           interface_parameters      = self.serial_interfaces[ logical_interface ]["interface_parameters"]
           parameters                = j["parameters"]
           address                   = handler.find_address( parameters )
          
           flag                      = handler.probe_register( parameters )
           if flag == False:
              return_value[address] = False
           else:
               return_value[address] = True
       
       return return_value
        

   def ping_device( self,address ):
      handler, interface_parameters, parameters   = self.find_remote( address)
      if handler != None:
           flag  = handler.probe_register( address,parameters["search_register"],parameters["register_number"] )
           return flag
      else:
           return False          

   def process_msg(self,  address, msg ):
      #print "made it here",address
      handler, interface_parameters, parameters   = self.find_remote( address)
      #print "handler",handler,interface_parameters,parameters
      if handler != None:
           return handler.process_message( parameters, msg )
      else:
          raise "no address recognized"
     
   def find_physical_serial_interfaces( self ):  # this new and needs tested 
 
    
       os.system("ls /dev/ttyUS* > serial_files.txt")
       with open('serial_files.txt') as f:
           ttyUSB_interfaces = f.read().splitlines()
       os.system("ls /dev/ttyACM* > serial_files.txt")
       with open('serial_files.txt') as f:
           ttyACM_interfaces = f.read().splitlines()

       serial_devices = ttyUSB_interfaces
       serial_devices.extend(ttyACM_interfaces)
       return serial_devices

   def open_logical_interfaces( self,logical_interface  ):
        
      
       #print("logical_interface",type(logical_interface),logical_interface)     
       if  logical_interface["interface_parameters"]["interface"] != None:
           self.open_fixed_interface( logical_interface )
       else:
           self.open_floating_interface(logical_interface )

 
     
   def open_fixed_interface( self, interface ):
       handler    = interface["handler"]
       parameters = interface["interface_parameters"]
       flag = handler.open(parameters)
       if flag == False:
          raise Exception('interface_error', interface_id )
 
   def open_floating_interface( self,logical_serial_interface ):
       
       for serial_device in  self.serial_devices:
          
          if self.try_interface( serial_device ,logical_serial_interface):
            
             if self.try_ping(logical_serial_interface):
                return
       
       raise Exception('interface_error', serial_interface )

   def try_interface( self, serial_device, logical_serial_interface ):
      
      
       handler    = logical_serial_interface["handler"]
       parameters = logical_serial_interface["interface_parameters"]
       parameters["interface"] = serial_device
       flag = handler.open(parameters)
       return flag

   

   def try_ping( self, logical_serial_interface ):
       handler                   = logical_serial_interface["handler"]
       search_device             = logical_serial_interface["search_device"]
       temp = self.remote_devices[search_device] 
       search_register           = temp["search_register"]
       register_number           = temp["register_number"]      
     
       flag   = handler.probe_register( search_device,search_register,register_number )
       #print("try ping flag",flag)
       if flag == False:
           logical_serial_interface["interface_parameters"] = None
           handler.close()
       return flag

 
            
              
if __name__ == "__main__":
    from .msg_manager_py3 import *
    from .rs485_mgr_py3   import *
    #
    #  USB interface id's can change based upon startup processes
    #  if device is null then the device was found by locating a search device on the network
    #  if the device is specified then the search device is not needed
   
    rs485_interface_2 = RS485_Mgr()
    serial_interfaces = {}
    
    serial_interfaces[ "rtu_2" ] = { "handler":rs485_interface_2,"interface_parameters":{ "interface":None, "timeout":.15, "baud_rate":38400 } ,"search_device":"main_controller" } 
    remote_devices = {}
    
    remote_devices["main_controller"] = { "interface": "rtu_2", "parameters":{ "address":100 , "search_register":0,"register_number":5} }
    message_manager = MessageManager()
   
    message_manager.add_device( 100, rs485_interface_2 )
     
    modbus_serial_ctrl = ModbusSerialCtrl( serial_interfaces,remote_devices,message_manager)
    
    print( modbus_serial_ctrl.ping_device( 100 ))
 


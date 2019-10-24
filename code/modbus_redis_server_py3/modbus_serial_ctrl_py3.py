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
   def __init__( self,  serial_interfaces, remote_devices, message_manager ):
       self.dict                    = {}
       self.ping_results            = {}
       self.serial_interfaces       = serial_interfaces
       self.remote_devices          = remote_devices
       self.message_manager         = message_manager
       self.interfaces              = self._find_interfaces()
       
       self._open_modbus_logical_interfaces()
       #print(self.ping_device(100))

       

   def find_remote( self, address):
       
       for i in self.remote_devices.keys():
          logical_interface          = self.remote_devices[i]["interface"]
          parameters                 = self.remote_devices[i]["parameters"]
          handler                    = self.serial_interfaces[logical_interface]["handler"]
          interface_parameters       = self.serial_interfaces[ logical_interface ]["interface_parameters"]
          remote_addr                = handler.find_address(  parameters)
          
          if address == remote_addr :
             
             return handler,interface_parameters, parameters
          
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
           flag  = handler.probe_register( parameters )
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
     
   def _find_interfaces( self ):  # this new and needs tested 
 
    
       os.system("ls /dev/ttyUS* > serial_files.txt")
       with open('serial_files.txt') as f:
           ttyUSB_interfaces = f.read().splitlines()
       os.system("ls /dev/ttyACM* > serial_files.txt")
       with open('serial_files.txt') as f:
           ttyACM_interfaces = f.read().splitlines()

       usb_interfaces = ttyUSB_interfaces
       usb_interfaces.extend(ttyACM_interfaces)
       return usb_interfaces

   def _open_modbus_logical_interfaces( self  ):
        
        for i,j in self.serial_interfaces.items():
           
           if  j["interface_parameters"]["interface"] != None:
              self._open_fixed_interface( j )
           else:
              self._open_floating_interface( j )

 
     
   def _open_fixed_interface( self, interface ):
       handler    = interface["handler"]
       parameters = interface["interface_parameters"]
       flag = handler.open(parameters)
       if flag == False:
          raise Exception('interface_error', interface_id )
 
   def _open_floating_interface( self,serial_interface ):
       
       for interface in  self.interfaces:
          
          if self._try_interface( interface ,serial_interface):
            
             if self._try_ping(serial_interface):
                return
       
       raise Exception('interface_error', serial_interface )

   def _try_interface( self, interface, serial_interface ):
      
       if self.check_other_interfaces(interface) == True:
           handler    = serial_interface["handler"]
           parameters = serial_interface["interface_parameters"]
           parameters["interface"] = interface
           flag = handler.open(parameters)
           return flag
       else:
           return False


   def check_other_interfaces( self, interface ):
       return_value = True
       for i in self.serial_interfaces.keys():
         temp = self.serial_interfaces[i]
         if temp["interface_parameters"]["interface"] == interface:
              return False
       return True

   def _try_ping( self, serial_interface ):
       handler                   = serial_interface["handler"]
       interface_parameters      = serial_interface["interface_parameters"]
       search_device             = serial_interface["search_device"]
       parameters                = self.remote_devices[search_device]["parameters"]
     
       flag   = handler.probe_register( parameters )
      
       if flag == False:
           serial_interface["interface_parameters"]["interface"] = None
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
 


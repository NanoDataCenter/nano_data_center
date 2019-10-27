# File: construct_classes.py
#
#
#
#
#

from  .psoc_4m_devices_py3 import PSOC_4M_MOISTURE_UNIT
from  .click_controller_class_py3 import Click_Controller_Base_Class_44
from  .click_controller_class_py3 import Click_Controller_Base_Class_22
from  .click_controller_class_py3 import Click_Controller_Base_Class_Power_Control
from  .esp32_controller_class_py3 import Esp32_Controller_Base_Class
from  .io_controller_py3 import IO_Controller
from  .new_instrument_py3 import Modbus_Instrument


class Construct_Access_Classes(object):

   def __init__( self ):
       # find ip and port for ip server
       instrument  =  Modbus_Instrument()
       self.instrument = instrument   

       self.access_classes = {}
       self.type_classes   = {}
       self.type_classes["PSOC_4_Moisture"] = PSOC_4M_MOISTURE_UNIT( instrument )
       self.type_classes["click_44"]        = Click_Controller_Base_Class_44( instrument )
       self.type_classes["click_22"]        = Click_Controller_Base_Class_22( instrument )
       self.type_classes["click_22"]        = Click_Controller_Base_Class_22( instrument )
       self.type_classes["power_control"]  = Click_Controller_Base_Class_Power_Control(instrument)
       self.type_classes["io_controller"]   = IO_Controller( instrument )
       self.type_classes["esp32_relay"]     = Esp32_Controller_Base_Class(instrument)
   
   def find_class( self, type,rpc_queue ):
       self.instrument.set_rpc_queue(rpc_queue)
       return self.type_classes[type]  

 
if __name__ == "__main__":
   
   access_class = Construct_Access_Classes( "127.0.0.1" , 6379 ) ### dummy values
   print (access_class.find_class("esp32_relay"))

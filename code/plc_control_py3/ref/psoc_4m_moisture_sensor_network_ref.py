

import datetime
from  psoc_4m_base_network import *

class PSOC_4M_MOISTURE_UNIT(PSOC_BASE_4M):
    
   def __init__(self,instrument):
       self.system_id = 0x201
       PSOC_BASE_4M.__init__( self, instrument, self.system_id)
       
       # additional write address definitions definitions
       self.check_one_wire_presence_addr                     = 27
       self.make_soil_temperature_addr                       = 28
       self.make_air_temp_humidity_addr                      = 29
       self.force_moisture_reading_addr                      = 30  
       self.update_moisture_sensor_configuration_addr        = 31
  
       self.update_flash_addr                                = 33
       self.clear_moisture_flag_addr                         = 34
       
       self.sensor_length                                    = 16
       
       self.new_measurement_flag_start = 20
       self.new_measurement_flag_list = [ "NEW_MOISTURE_DATA_FLAG"]
       
       # status
       self.status_start   =    13
       self.status_list    =  [
                                          
                                          "ONE_WIRE_DEVICE_FOUND",
                                          "NEW_MOISTURE_DATA_FLAG"
                               ]
       self.moisture_control_start = 15   
       self.moisture_control_list  = [
                             
                           
                           
                           "AIR_HUMIDITY_FLOAT" ,       
                           "AIR_TEMP_FLOAT",
                           "MOISTURE_SOIL_TEMP_FLOAT",
                           "RESISTOR_FLOAT",
                           


                        ]
       self.capacitance_mask_start = 23
       self.capacitance_mask_list  = [ "CAPACITANCE_MASK"]
       
       # Moisture Data
       self.moisture_data_start  =    30   
       self.moisture_data_number =    16      
       
       self.moisture_data_resistive_start              = 70                
       self.moisture_resistive_configuration_number    = 16                      
    
     
       # Moisture Configuration Data
       self.moisture_configuration_start  =    110
       self.moisture_configuration_number =     16
 
                                             
       
       
 


   # 
   #
   #  Read Variables
   #
   #
 
 
   def check_status( self, address):
       return_value = {}
       data =  self.instrument.read_registers( address,  self.status_start, len(self.status_list) )

       for i in range(0,len(self.status_list)):
          
           return_value[  self.status_list[i]  ] = data[i]
           
       return return_value
       

   
        
   def read_moisture_control(self, address ):
       return_value = {}
       data =  self.instrument.read_floats( address,  self.moisture_control_start, len(self.moisture_control_list) )

       for i in range(0,len(self.moisture_control_list)):
          
           return_value[  self.moisture_control_list[i]  ] = data[i]
           
       return return_value
       


       
   def read_moisture_data( self ,address ):
        return_value = {}
        data =  self.instrument.read_floats( address,  self.moisture_data_start ,self.moisture_configuration_number  )
        return data
        
         
   def read_moisture_resistive_data( self ,address ):
        return_value = {}
        data =  self.instrument.read_floats( address,  self.moisture_data_resistive_start ,self.moisture_resistive_configuration_number  )
        return data
        
        
      
      
      
      
        
   def read_moisture_configuration( self, address ):
       return_value = {}
     
       data = self.instrument.read_registers( address,self.moisture_configuration_start,self.moisture_configuration_number )
       return data
       
  
   def check_one_wire_presence ( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.check_one_wire_presence_addr, [0] )
         
   def make_soil_temperature ( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.make_soil_temperature_addr, [0] )
         
   def make_air_temp_humidity( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.make_air_temp_humidity_addr, [0] )

  
   def clear_new_moisture_data_flag( self, address):
       self.instrument.write_registers( address, self.clear_moisture_flag_addr, [0] )
       
 
   
   def force_moisture_reading ( self, address): #sampling rate is in minutes
         self.instrument.write_registers(address, self.force_moisture_reading_addr, [0] )
         
        
   def  update_moisture_sensor_configuration ( self,address, sensor_data ): # sensor data consisting of 0,1,2
        if len( sensor_data) != self.sensor_length :
            raise
        valid_data = set([0,1,2])
        for i in sensor_data:
          if i not in valid_data:
             raise
          
        self.instrument.write_registers( address, self.update_moisture_sensor_configuration_addr ,sensor_data )
  


        
 
if __name__ == "__main__": 
       import new_instrument_network
       import time
       new_instrument  =  new_instrument_network.new_instrument_network()
       new_instrument.set_ip(ip= "192.168.1.82", port = 5005)       
       
       psoc_moisture = PSOC_4M_MOISTURE_UNIT( new_instrument )
       #psoc_moisture.update_current_time( 40 )
       print psoc_moisture.clear_new_moisture_data_flag(40)
       print psoc_moisture.check_status(40)

       print psoc_moisture.check_one_wire_presence(40)
       time.sleep(.3)
       print psoc_moisture.make_soil_temperature(40)
       time.sleep(.3)
       print psoc_moisture.make_air_temp_humidity(40)
       time.sleep(.3)
       print psoc_moisture.make_air_temp_humidity(40)
       time.sleep(.3)
       # test read functions first
 
       print psoc_moisture.check_status(40)
       print psoc_moisture.read_moisture_control(40)
       print psoc_moisture.read_moisture_configuration( 40 )
       print psoc_moisture.force_moisture_reading(40)
       time.sleep(1.)
       print psoc_moisture.read_moisture_data(40)
       print psoc_moisture.read_moisture_resistive_data(40)
       quit()
       #print psoc_moisture.force_moisture_reading(40)
       time.sleep(1)
       print psoc_moisture.read_moisture_resistive_data( 40 )
       print psoc_moisture.read_moisture_data(40)
       print psoc_moisture.check_status(40)
       
       

       '''             
       # test directed actions
  
       #psoc_moisture.check_one_wire_presence(40)
       #psoc_moisture.make_soil_temperature(40)
       psoc_moisture.force_moisture_reading(40)
       '''       
       '''
       print "new_data_flag",psoc_moisture.check_new_data_flag( 40)
       print "capacitance_mask", psoc_moisture.read_capacitor_mask(40)
       print psoc_moisture.read_moisture_control( 40 )
       print psoc_moisture.read_moisture_configuration( 40 )
       psoc_moisture.change_capacitance_sensor_mask( 40, 0xf)
       psoc_moisture. update_moisture_sensor_configuration ( 40,[ 2,1,1,1,1,0,0,0] )
       psoc_moisture.update_flash(40)
       print "capacitance_mask", psoc_moisture.read_capacitor_mask(40)
       print psoc_moisture.read_moisture_control( 40 )
       print psoc_moisture.read_moisture_configuration( 40 )

       print "force moisture measurement", psoc_moisture.force_moisture_reading(40)
       quit()
       print psoc_moisture.read_moisture_data(40)
       '''
       
       
       


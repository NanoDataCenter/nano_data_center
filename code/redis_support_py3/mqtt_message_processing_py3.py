
import time

class MQTT_Message_Processing(object):

   def __init__(self):
       self.message_handlers = {}
       self.message_handlers["analog_input" ] = self.process_analog_input
       self.message_handlers["flat" ] = self.process_flat_input
       self.message_handlers["pulse_flow" ] = self.process_pulse_flow 
       self.analog_handlers = {}
       self.analog_handlers["analog" ] = self.process_raw_analog
       self.analog_handlers["pressure_gauge" ] = self.process_pressure_gauge
       self.analog_handlers["rms_current_transformer" ] = self.process_current_transformer
       
        
        
   def process_mqtt_message(self,data_def,data_key,data):
       if data_def["type"] in self.message_handlers:
         return self.message_handlers[data_def["type"]](data_def,data_key,data)
       else:
          raise ValueError("unsupported message type")

   def find_definition_record(self,data_key,data_def):
      
       for i in data_def["fields"]:
          if i["name"] == data_key:
            return i
       raise ValueError("no matching data key")     
   
   
   
   def process_analog_input(self,data_def,data_key,total_data):
       if data_key == None:
           raise ValueError("requires data_key")
       definition_record = self.find_definition_record(data_key,data_def)
      
       measurement_key = data_def["main_field"]
       data = total_data[str.encode(measurement_key)]
 
       return self.analog_handlers[definition_record["type"]](definition_record,data)
  
   def process_raw_analog(self,definition_record,raw_data):
       sensor_field = str.encode(definition_record["channel_field"]) 
       sensor_element = definition_record["channel_value"]
       for i in raw_data:
         if i[sensor_field] == sensor_element:
           #print("sensor data",i[b"DC"] )
           return i[b"DC"]
       raise ValueError("sensor field not found")
       

   def process_pressure_gauge(self,definition_record,raw_data):
       sensor_data = self.process_raw_analog(definition_record,raw_data)
       reduction = definition_record["reduction"]
       range     = definition_record["range"]
       sensor_data = (sensor_data*reduction) -.5
       sensor_data = (sensor_data/4.0)*range

       return sensor_data
      

   def  process_current_transformer(self,definition_record,raw_data):
       sensor_data = self.process_raw_analog(definition_record,raw_data)
       resistor = definition_record["resistor"]
       range     = definition_record["range"] 
          
       current = sensor_data/resistor
       
       current = current - .004
       
       value = current/.016*range
      

      
       return value

   #{"name":"MAIN_FLOW_METER", "GPIO_PIN":5,"data_field":"COUNTS","conversion":4./2./60./2.0 },
   def process_pulse_flow(self,data_def,data_key,total_data):
       if data_key == None:
           raise ValueError("requires data_key")
       definition_record = self.find_definition_record(data_key,data_def)
       measurement_value = definition_record["GPIO_PIN"]
      
       measurement_key = data_def["main_field"]
       data = total_data[str.encode(measurement_key)]
      
       for i in data:
         if i[b"GPIO_PIN"] == measurement_value:
            rate = i[b"COUNTS"]*definition_record["conversion"]
           
            return rate
       raise ValueError("Flow meter not in data")
       
   def process_flat_input(self,data_def,data_key,data):
       result = {}
       print("data",data)
       for i in data_def["fields"]:
         result[i["name"]] = data[str.encode(i["field"])]
       result["timestamp"] = time.time()
       return result
      

   


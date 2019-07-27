import base64
import json

class Valve_Reistance( object ):

   def __init__( self, render_template, redis_handle, app_files):
       self.render_template = render_template
       self.redis_handle = redis_handle
       self.app_files = app_files
       self.history = 14
       
       
       




   def overall_resistance(self,controller_id):
       
       controller_list,valve_list   = self.get_controller_list(controller_id)
       controller_name              = controller_list[controller_id]

       data_object = self.resistance_canvas_list( controller_name, valve_list)
       return self.render_template("statistics/resistance_template", 
                               controller_id     = controller_id,
                               controller_name   = controller_name,
                               valve_list        = valve_list,
                               valve_number      = len(valve_list),
                               header_name       = "Valve Resistance ", 
                               controller_list   = controller_list,
                               data_object      = data_object )
                               
                               
                               
   def get_controller_list( self,controller_id ):
       
       base64_object     = self.redis_handle.get(  "SPRINKLER_RESISTANCE_DICTIONARY")
       json_string       = base64.b64decode(base64_object)
       resistance_dictionary = json.loads(json_string.decode())
       
       controllers = list(resistance_dictionary.keys())
       controllers.sort()
       controller_name = controllers[controller_id]
       valve_data = resistance_dictionary[ controller_name ]
       valve_list  = list(valve_data.keys())
       valve_list  = list(map(int, valve_list)) 
       valve_list.sort()
       valve_list  = list(map(str,valve_list))
       return  controllers, valve_list    

   
   def resistance_canvas_list( self, controller_name, valve_list):
       
       data_object = []       
       for i in range(0,len(valve_list)):
           
           try:
               
                   temp_entry = {}
                   temp_entry["limit"] = self.get_limit_data("log_data:resistance_log_limit:"+controller_name+":"+str(valve_list[i]))
                   temp_entry["data"]  = self.get_schedule_list_data( self.history,"log_data:resistance_log:"+controller_name+":"+str(valve_list[i]))
           except:
               
               temp_entry = "None"
           data_object.append(temp_entry) 

       return data_object
  
 
   def get_limit_data(self, redis_key ):
       
           temp_data_json = self.redis_handle.get( redis_key )
        
           limit_data = json.loads(temp_data_json)
           
           return limit_data
           
   def get_schedule_list_data(self, history, redis_key ):
       temp_data_list = self.redis_handle.lrange(redis_key,0,history)
       data_list = []
       for list_element_json in temp_data_list:
           list_element = json.loads(list_element_json)
           
           data_list.append(list_element)
       return data_list

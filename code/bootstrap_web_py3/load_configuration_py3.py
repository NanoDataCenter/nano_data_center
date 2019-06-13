import os
import json
import base64

class Load_Configuration_Data(object):

   def __init__( self, app, auth,render_template,request,
                 app_files,sys_files ,handlers = None):
       self.app      = app
       self.auth     = auth
       self.render_template = render_template
       self.request = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.handlers = handlers
       

       a1 = auth.login_required( self.system_actions )
       app.add_url_rule('/system_actions',"system_actions",a1,methods=["GET"])
       '''
       a1 = auth.login_required( self.add_schedule )
       app.add_url_rule('/create_schedule',"add_schedule",a1,methods=["GET"])

       a1 = auth.login_required( self.edit_schedules )
       app.add_url_rule('/edit_schedules',"edit_schedules",a1,methods=["GET"])
       '''
 
       a1 = auth.login_required( self.copy_schedule )
       app.add_url_rule('/copy_schedule',"copy_schedule",a1,methods=["GET"])

       a1 = auth.login_required( self.delete_schedules )
       app.add_url_rule('/delete_schedules',"delete_schedules",a1,methods=["GET"])

       a1 = auth.login_required( self.update_schedule )
       app.add_url_rule("/ajax/update_schedule",
                          "ajax_update_schedule",a1,methods=["POST"])

                      



   def system_actions(self):  
       system_actions = self.sys_files.load_file( "system_actions.json" )
       
       
       return self.render_template( "irrigation_configuration/system_actions",  
                               title="Configure System Events",
                               system_actions       =  system_actions ,
                               system_actions_json  =  json.dumps(system_actions) )

   def create_schedule(self): 
       schedule_data = self.get_schedule_data() 
       
   
       return self.render_template( "configuration/create_schedule",
                               template_type = "add", 
                               title="Add Schedule",
                               schedule_list      =  schedule_data.keys(),
                               pin_list           =  json.dumps(self.sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(schedule_data)  ) 


   def copy_schedule(self):  
       schedule_data = self.get_schedule_data() 
      
       return self.render_template( "irrigation_configuration/copy_schedule", 
                               template_type = "copy", 
                               title="Copy Schedule",
                               schedule_list      =  schedule_data.keys(),
                               schedule_data_json =  json.dumps(schedule_data)  ) 


   def delete_schedules(self):  
       schedule_data = self.get_schedule_data()
       return self.render_template( "irrigation_configuration/delete_schedule", 
                               template_type = "delete", 
                               title="Delete Schedules",
                               schedule_list      =  schedule_data.keys(),
                               schedule_data_json =  json.dumps(schedule_data)  ) 



   def edit_schedules(self):
       schedule_data = self.get_schedule_data()  
       return self.render_template( "configuration/edit_schedule", 
                               template_type = "edit",
                               title="Edit Schedule",
                               schedule_list      =  schedule_data.keys(),
                               pin_list           =  json.dumps(self.sys_files.load_file("controller_cable_assignment.json")),
                               schedule_data_json =  json.dumps(schedule_data)  ) 

 
  
 
  
 
  


   def update_schedule(self ):
       return_value     = {}
       param              = self.request.get_json()
       action             = param["action"] 
       schedule           = param["schedule"] 
       schedule_data      = param["data"] 
       
       if action == "delete":
           self.delete_schedule( schedule )
           self.delete_link_file( schedule )
           
       else:
           self.save_link_file( schedule, schedule_data[schedule] )
           self.save_schedule( schedule_data[schedule]  )
           
       return json.dumps("SUCCESS")

       

   #
   #  Internal functions
   #
   def get_schedule_data( self, *args):
       sprinkler_ctrl           = self.app_files.load_file("sprinkler_ctrl.json")
     
       returnValue = {}
       for j in sprinkler_ctrl:
           data           = self.app_files.load_file(j["link"])
           
           j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(data)         
           returnValue[j["name"]] = j
       return returnValue

   def generate_steps( self, file_data):
       returnValue = []
       controller_pins = []
       if file_data["schedule"] != None:
           schedule = file_data["schedule"]        
           for i  in schedule:
               returnValue.append(i[0][2])
               temp = []
               for l in  i:
                   temp.append(  [ l[0], l[1][0] ] )
               controller_pins.append(temp)
  
  
       return len(returnValue), returnValue, controller_pins



   def find_sched_index( self,  name, ref_sched_data ):
      
        for i in range(0, len(ref_sched_data) ):
           
           if ref_sched_data[i]["name"] == name:
              return i
        return None

  


   def save_schedule( self, schedule_data ):
       name = schedule_data["name"]
       ref_sched_data  = self.app_files.load_file( "sprinkler_ctrl.json" )

       index = self.find_sched_index( name, ref_sched_data )
       
       if index != None:
            ref_sched_data[ index ] = schedule_data
       else:
            ref_sched_data.append( schedule_data)
  
       self.app_files.save_file( "sprinkler_ctrl.json",ref_sched_data)
      

   def save_link_file( self, schedule, schedule_data ):
       
       link_data = {}
       link_data["bits"] = {'1':'C201', '3':'DS2', '2':'C2'}
       link_data["schedule"] = []
       for step in range(0,len(schedule_data["controller_pins"] ) ):
           valve_data = schedule_data["controller_pins"][step]
           time       = schedule_data["steps"][step]
           valve_return = []
           for valve_index in range(0,len(valve_data)):
                 valve_return.append( [ valve_data[valve_index][0], [ valve_data[valve_index][1] ] , time ])
           link_data["schedule"].append( valve_return )
       
       self.app_files.save_file( schedule+".json", link_data )

   def delete_link_file( self, schedule ):
       try:
         self.app_files.delete_file( schedule+".json" )
       except:
          pass
   def delete_schedule( self, schedule ):
       
       ref_sched_data  = self.app_files.load_file( "sprinkler_ctrl.json" )
       index = self.find_sched_index( schedule, ref_sched_data )
       
       if index != None:

            del ref_sched_data[ index ] 
            self.app_files.save_file( "sprinkler_ctrl.json" , ref_sched_data )
           



   def get_controller_list( self,controller_id ):
       base64_object     = self.redis_old_handle.get(  "SPRINKLER_RESISTANCE_DICTIONARY")
       json_string       = base64.b64decode(base64_object)
       resistance_dictionary = json.loads(json_string.decode())
       
       controllers = list(resistance_dictionary.keys())
       controllers.sort()
       controller_name = controllers[controller_id]
       valve_data = resistance_dictionary[ controller_name ]
       valve_list  = valve_data.keys()
       valve_list  = list(map(int, valve_list))   
       valve_list.sort()
       valve_list  = list(map(str,valve_list))
       return  controllers, valve_list    


   def resistance_canvas_list( self, controller_id,  *args,**kwargs):
       controller_list, valve_list = self.get_controller_list(controller_id)
       controller_name = controller_list[controller_id]
       limit = []
       for j in range(0,len(valve_list)):
          temp = []
          redis_key = "log_data:resistance_log_limit:"+controller_name+":"+valve_list[j]
          limit_value = self.redis_old_handle.get(redis_key)
          if limit_value == None:
              redis_list = "log_data:resistance_log:"+controller_name+":"+valve_list[j]
              limit_value = self.redis_old_handle.lindex(redis_list,0)
              self.redis_old_handle.set(redis_key,limit_value)
         
          limit.append(limit_value)
 
       resistance = []
       for j in valve_list:
          temp = []
          redis_list = "log_data:resistance_log:"+controller_name+":"+j
          length = self.redis_old_handle.llen(redis_list)
          for i in range(0,length):
             value = self.redis_old_handle.lindex(redis_list,i)
     
             temp.append(value)
          resistance.append(temp)
    
       
       return_value = []
      
       for i in range(0,len(valve_list)):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +  valve_list[i]
           temp["titleText"]                   = "Valve "    +  valve_list[i]
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           try:
                temp["qualScale1"]             =  float(int(float(float(limit[i])*100)))/100.
           except:
                temp["qualScale1"]             = 0

           try:
               temp["featuredMeasure"]         = resistance[i]
           except:
               temp["featuredMeasure"]         = 0
           try:
               temp["limit"]                   = 0 # limit_values[i]['limit_std']
           except:
               temp["limit"]                   = 0
           return_value.append(temp)
       
      
       return return_value


   def process_resistance_limit_values( self, controller, data ):
       for i in data :
          redis_key = "log_data:resistance_log_limit:"+controller+":"+i["valve"]
          self.redis_old_handle.set(redis_key,i["value"] )

   def  generate_current_canvas_list( self, schedule_name,schedule_data ,*args, **kwargs ):
       return_value = []
       
       self.schedule_name = schedule_name
       data = schedule_data[ schedule_name ]

       current_data      = self.get_current_data( data["step_number"],schedule_name )
       limit_values      = self.get_current_limit_values( data["step_number"],schedule_name )
       for i in range(0,data["step_number"]):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +str(i+1)
           temp["titleText"]                   = "Step "     +str(i+1)
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           temp["featuredMeasure"]             = current_data[i] 
           try:
              temp["qualScale1"]                  = limit_values[i]['limit_avg']  
              temp["limit"]                       = limit_values[i]['limit_std']
           except:
              temp["qualScale1"]                  = 0  
              temp["limit"]                       = 0
           temp["step"]                        = i
           return_value.append(temp)
           
       return return_value
          
   def get_current_data( self, step_number, schedule_name ):
       returnValue = []
       for i in range(0,step_number):
           key = "log_data:coil:"+schedule_name+":"+str(i+1)
           value_array = []
           for j in range(0,10):
               composite_string = self.redis_old_handle.lindex(key,j)
              
               try:
                   composite_object = json.loads( composite_string )
                   value = composite_object["fields"]["coil_current"]["average"] 
               
               except:
                   value = 0
               value_array.append(value)
           returnValue.append(value_array)   
       return returnValue

   def get_current_limit_values( self,  step_number, schedule_name ):
       key = "log_data:coil_limits:"+schedule_name
       data = self.redis_old_handle.get( key )
       if data == None:
           returnValue = self.generate_default_limits( step_number )
       else:
           returnValue = json.loads(data)
       return returnValue

   def generate_default_limits( self, step_number ):
       returnValue = []
       for i in range(0,step_number):
           temp = {}
           temp["limit_avg"] = 0
           temp["limit_std"] = 0
           returnValue.append(temp)
    
       return returnValue

   def update_current_limit(self):
       return_value     = {}
       param            = self.request.get_json() 
       schedule           = param["schedule"]
       data               = param["limit_data"]
       key = "log_data:coil_limits:"+schedule
       corrected_data = self.assemble_corrected_data( data, 1. )
       self.redis_old_handle.set( key , json.dumps(corrected_data) )
       return json.dumps("SUCCESS")

   def assemble_corrected_data( self, data, conversion_rate):
       corrected_data = []
       for i in data:

           corrected_data.append( {"limit_avg":float(i)*conversion_rate, "limit_std" : 0 } )
       return corrected_data 

   def process_flow_limit_values( self, sensor_name, schedule, data):
        sensor_id = self.find_sensor_id( sensor_name )
        inverse_conversion_rate = 1./self.get_conversion_rates()[sensor_id]
        corrected_data = self.assemble_corrected_data( data, inverse_conversion_rate )
        self.save_flow_limit_values( sensor_name, schedule, corrected_data )

   def assemble_corrected_data( self, data, conversion_rate):
       corrected_data = []
       for i in data:

           corrected_data.append( {"limit_avg":float(i)*conversion_rate, "limit_std" : 0 } )
       return corrected_data 
 
   def save_flow_limit_values( self, sensor_name, schedule_name, data ):
       json_data = json.dumps(data)
       key = "log_data:flow_limits:"+schedule_name+":"+sensor_name
       self.redis_old_handle.set( key , json_data )

   def find_sensor_id( self, sensor_name ):
     
       try:
           sensor_id = self.get_flow_rate_sensor_names.index( sensor_name )
       except:
           sensor_id = 0
       return sensor_id  
   
   def get_flow_rate_sensor_names( self  ):
       return_data = []

       data           = self.redis_old_handle.hget("FILES:SYS","global_sensors.json")

       temp           = json.loads(data)

       for i in temp:
           
           return_data.append(i[0])

       return return_data

   def generate_canvas_list(self, schedule_name, flow_id , schedule_data, *args,**kwargs):
       return_value = []
       
       
       data = schedule_data[ schedule_name ]
       flow_sensors = self.get_flow_rate_sensor_names() 
       flow_sensor_name = flow_sensors[flow_id]

       conversion_rate   = self.get_conversion_rates()[flow_id]

       flow_data      = self.get_average_flow_data( data["step_number"], flow_sensor_name, schedule_name )
       limit_values = self.get_flow_limit_values( data["step_number"], flow_sensor_name, schedule_name )
       
       for i in limit_values:
           try:
               i['limit_avg'] = float(i['limit_avg'])*conversion_rate
               i['limit_std'] = float(i['limit_std'])*conversion_rate
           except:
               i['limit_avg'] = 0
               i['limit_std'] = 0
          
       corrected_flow = []
       for i in flow_data:
           temp1 = []
           
           for j in i:
               temp1.append( j *conversion_rate)
           corrected_flow.append(temp1)
       
       
       for i in range(0,data["step_number"]):
           
           temp                                = {}
           temp["canvasName"]                  = "canvas1"   +str(i+1)
           temp["titleText"]                   = "Step "     +str(i+1)
           temp["qualScale1Color"]             = "Black"
           temp["featuredColor"]               = "Red"
           try:
                temp["qualScale1"]             = limit_values[i]['limit_avg']
           except:
                temp["qualScale1"]             = 0

           try:
               temp["featuredMeasure"]         = corrected_flow[i]
           except:
               temp["featuredMeasure"]         = 0
           try:
               temp["limit"]                       = limit_values[i]['limit_std']
           except:
               temp["limit"]                   = 0
           return_value.append(temp)
           
       return return_value

   def get_conversion_rates( self ):
       return_data = []

       data           = self.redis_old_handle.hget("FILES:SYS","global_sensors.json")
       temp           = json.loads(data)
   
       for i in temp:
           
           return_data.append(i[3])

       return return_data

   def get_average_flow_data( self,  step_number, sensor_name, schedule_name ):  
       returnValue = []
       for i in range(0,step_number):
           key = "log_data:flow:"+schedule_name+":"+str(i+1)
           value_array = []
           for j in range(0,10):
               composite_string = self.redis_old_handle.lindex(key,j)
               try:
                   composite_object = json.loads( composite_string )
                   value = composite_object["fields"][sensor_name]["average"] 
               
               except:
                   value = 0
               value_array.append(value)
           returnValue.append(value_array)   
       return returnValue

   def get_flow_limit_values( self, step_number, sensor_name, schedule_name ):
       key = "log_data:flow_limits:"+schedule_name+":"+sensor_name
       data = self.redis_old_handle.get( key )
       if data == None :
            returnValue = self.generate_default_limits( step_number )
       else:
          temp = json.loads(data)
          if (data == None) or (len(temp) != step_number):
              returnValue = self.generate_default_limits( step_number )
          else:
              returnValue = temp
       return returnValue 

   def generate_default_limits( self, step_number ):
       returnValue = []
       for i in range(0,step_number):
           temp = {}
           temp["limit_avg"] = 0
           temp["limit_std"] = 0
           returnValue.append(temp)
    
       return returnValue

   '''
   discontinued code
         a1 = auth.login_required( self.overall_flow_limits )
       app.add_url_rule('/configure_flow_limits/<int:flow_id>/<int:schedule_id>',
                        "configure_flow_limits",a1,methods=["GET"])

       a1 = auth.login_required( self.overall_current_limits )
       app.add_url_rule('/configure_current_limits/<int:schedule_id>',
                           "configure_current_limits",a1,methods=["GET"])

         #a1 = auth.login_required( self.update_current_limit )
       #app.add_url_rule('/ajax/update_current_limit',
                          "update_current_limit",a1,methods=["POST"])

       #a1 = auth.login_required( self.update_flow_limit )
       #app.add_url_rule('/ajax/update_flow_limit',
                          "update_flow_limit",a1,methods=["POST"])
   '''

import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing
from  collections import OrderedDict
class Load_Irrigation_Pages(Base_Stream_Processing):

   def __init__( self, app, auth, request, app_files, sys_files,
                   render_template,redis_handle, handlers):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.render_template = render_template
       self.redis_handle = redis_handle
       self.handlers = handlers
                                      
       a1 = auth.login_required( self.get_index_page )
       app.add_url_rule('/index.html',"get_index_page",a1) 
       
       a1 = auth.login_required( self.get_slash_page )
       app.add_url_rule("/","get_slash_page",a1)

       a1 = auth.login_required( self.get_diagnostic_page )
       app.add_url_rule('/diagnostics/<filename>',"get_diagnostic_page",a1 )
       

       a1= auth.login_required( self.irrigation_control )
       app.add_url_rule("/control/control","irrigation_control",a1)
       
       
       a1= auth.login_required( self.manage_parameters )
       app.add_url_rule("/control/parameters","manage_parameters",a1)
 
       ### manage pending operations
       a1= auth.login_required( self.irrigation_queue )
       app.add_url_rule("/control/irrigation_queue","irrigation_queue",a1)

       ### past actions
       a1= auth.login_required( self.display_past_actions )
       app.add_url_rule("/control/display_past_actions/<string:event>","display_past_actions",a1)
 
       a1 = auth.login_required( self.mode_change )
       app.add_url_rule('/ajax/mode_change',"get_mode_change",a1, methods=["POST"]) 

       '''
     
       
       a1 = auth.login_required( self.schedule_data )
       app.add_url_rule('/ajax/schedule_data',"get_schedule_data",a1 )


       '''
  
   def irrigation_control(self):
       schedule_data = self.schedule_data()
      
       return self.render_template("irrigation_templates/irrigation_control",schedule_data = schedule_data)
      
   def get_index_page(self):
       return self.get_diagnostic_page( filename = "schedule_control" )
   def get_slash_page(self):
       return self.get_diagnostic_page( filename = "schedule_control" )

   def get_diagnostic_page(self, filename): 
       if filename == "schedule_control":
          title = 'Irrigation Diagnostics Turn On by Schedule'
          
       if filename == "controller_pin":
          title = 'Irrigation Diagnostics Turn On by Controller/Pin'
          
       if filename == "valve_group":
          title = 'Irrigation Diagnostics Turn On by Valve Group'
       schedule_data = self.schedule_data()
       controller_pin = self.sys_files.load_file("controller_cable_assignment.json")
       controller_pin_json = json.dumps(controller_pin)
       controller_valve_group_json = json.dumps(self.sys_files.load_file("valve_group_assignments.json"))
       return self.render_template("irrigation_templates/irrigation_diagnostics", 
             filename = filename,
             title = title,
             schedule_data = schedule_data ,
             controller_pin = controller_pin_json , 
             controller_valve_group_json = controller_valve_group_json             )

   def irrigation_queue(self):
       return self.render_template("irrigation_templates/irrigation_queue" )


   def manage_parameters(self):
       self.handlers["IRRIGATION_CONTROL"].delete_all()
       control_data = self.handlers["IRRIGATION_CONTROL"].hgetall()
       control_data_json = json.dumps(control_data)
       print("control_data",control_data)
       return self.render_template("irrigation_templates/manage_parameters",
                                    title = "Manage Irrigation Parameters",
                                    control_data_json = control_data_json  )
       

      

   def display_irrigation_queue(self):
       return self.render_template("irrigation_templates/display_irrigation_queue" )

   #  
   #  Function serves a post operation
   #
   def schedule_data(self):
     sprinkler_ctrl           = self.app_files.load_file("sprinkler_ctrl.json")
     
     returnValue = []
     for j in sprinkler_ctrl:
         temp          = self.app_files.load_file(j["link"])

         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         returnValue.append(j)
     return json.dumps(returnValue)   

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

   def mode_change( self):
       json_object = self.request.json
       self.handlers["IRRIGATION_JOB_SCHEDULING"].push(json_object)
       return json.dumps("SUCCESS")
 

   def display_past_actions( self,event):
       fields = self.alarm_queue.get_events()
       fields['ALL'] = time.time()
       time_data = self.alarm_queue.get_time_data()
       sorted_data = []
       if event in fields:
           if event == "ALL":
              sorted_data = time_data
           else:
               for i in time_data:
                   print(i,event)
                   if i["event"] == event:
                       sorted_data.append(i)   
                             
       
       for i in sorted_data:
          temp = i["time"]
          i["time"]  = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(temp))
       return self.render_template("irrigation_templates/display_action_queue" ,time_history = sorted_data, events = fields, ref_field_index=event,
                  header_name="Past Events"       )
                
  
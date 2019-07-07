
import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing
from  collections import OrderedDict
class Load_Irrigation_Pages(Base_Stream_Processing):

   def __init__( self, app, auth, request, app_files, sys_files,
                   render_template,redis_handle, handlers,irrigation_control):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.render_template = render_template
       self.redis_handle = redis_handle
       self.handlers = handlers
       self.irrigation_control = irrigation_control
                                      
       a1 = auth.login_required( self.get_index_page )
       app.add_url_rule('/index.html',"get_index_page",a1) 
       
       a1 = auth.login_required( self.get_slash_page )
       app.add_url_rule("/","get_slash_page",a1)

       a1 = auth.login_required( self.get_diagnostic_page )
       app.add_url_rule('/diagnostics/<filename>',"get_diagnostic_page",a1 )
       

       a1= auth.login_required( self.queue_irrigation_jobs )
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


       a1 = auth.login_required( self.parameter_update )
       app.add_url_rule('/ajax/parameter_update',"get_parameter_update",a1, methods=["POST"]) 
       
       a1 = auth.login_required( self.irrigation_job_delete )
       app.add_url_rule('/ajax/irrigation_job_delete',"irrigation_job_delete",a1, methods=["POST"]) 


  
   def queue_irrigation_jobs(self):
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
       jobs = self.get_queued_irrigation_jobs()
      
       return self.render_template("irrigation_templates/irrigation_queue",jobs = jobs )


   def manage_parameters(self):
      
       control_data = {}
       control_data["RAIN_FLAG"] = self.irrigation_control.get_rain_flag()
       control_data["ETO_MANAGEMENT"] = self.irrigation_control.get_eto_management_flag()
       control_data["FLOW_CUT_OFF"]   =    self.irrigation_control.get_flow_cutoff()
       control_data["CLEANING_INTERVAL"] = self.irrigation_control.get_cleaning_interval()
 
       control_data_json = json.dumps(control_data)
     
       return self.render_template("irrigation_templates/manage_parameters",
                                    title = "Manage Irrigation Parameters",
                                    control_data_json = control_data_json  )
       

      

   def display_irrigation_queue(self):

       return self.render_template("irrigation_templates/display_irrigation_queue" )
    
   def display_past_actions( self,event):
       temp_data = self.handlers["IRRIGATION_PAST_ACTIONS"].revrange("+","-" , count=1000)
      
       for i in temp_data:
         i["time"] = str(datetime.fromtimestamp(i["timestamp"]))
       return self.render_template("irrigation_templates/irrigation_history_queue" ,time_history = temp_data )
                 
        

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
       print("json_object",json_object)
       self.handlers["IRRIGATION_JOB_SCHEDULING"].push(json_object)
       print(self.handlers["IRRIGATION_JOB_SCHEDULING"].length())
       return json.dumps("SUCCESS")

   def parameter_update(self):
       json_object = self.request.json
      
       field = json_object["field"]
       data = json_object["data"]
       self.irrigation_control.set_field(field,data)
      
       return json.dumps("SUCCESS")

        
   def get_queued_irrigation_jobs(self):
      
       results = self.handlers["IRRIGATION_PENDING"].list_range(0,-1)
       results.reverse()
       return_value = []
       for i in results:
          temp = {}
          temp["schedule_name"] = i["schedule_name"]
          temp["step"]   = i["step"]
          temp["run_time"] = i["run_time"]
          return_value.append(temp)
       
       return return_value
       
   def irrigation_job_delete(self):
        json_object = self.request.json
        list_index = json_object["list_indexes"]        
       
        self.handlers["IRRIGATION_PENDING"].delete_jobs(list_index)
        return json.dumps("SUCCESS")
  
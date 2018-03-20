import json
import base64
import time

class Load_Irrigation_Pages(object):

   def __init__( self, app, auth, render_template, redis_handle, redis_new_handle, request,alarm_queue ):
       self.app             = app
       self.auth            = auth
       self.redis_handle    = redis_handle
       self.redis_new_handle = redis_new_handle
       self.render_template = render_template
       self.request         = request
       self.alarm_queue     = alarm_queue

       a1 = auth.login_required( self.get_index_page )
       app.add_url_rule('/index.html',"get_index_page",a1) 
       app.add_url_rule("/","get_slash_page",a1)

       a1 = auth.login_required( self.get_diagnostic_page )
       app.add_url_rule('/diagnostics/<filename>',"get_diagnostic_page",a1 )

       a1 = auth.login_required( self.schedule_data )
       app.add_url_rule('/ajax/schedule_data',"get_schedule_data",a1 )

       a1 = auth.login_required( self.mode_change )
       app.add_url_rule('/ajax/mode_change',"get_mode_change",a1, methods=["POST"])

       a1= auth.login_required( self.irrigation_control )
       app.add_url_rule("/control/control","irrigation_control",a1)
 
       a1= auth.login_required( self.irrigation_queue )
       app.add_url_rule("/control/irrigation_queue","irrigation_queue",a1)

       a1= auth.login_required( self.display_irrigation_queue )
       app.add_url_rule("/control/display_irrigation_queue","display_irrigation_queue",a1)

       a1= auth.login_required( self.manage_parameters )
       app.add_url_rule("/control/parameters","manage_parameters",a1)
       
       a1= auth.login_required( self.display_past_actions )
       app.add_url_rule("/control/display_past_actions/<string:event>","display_past_actions",a1)

       

   def irrigation_control(self):
       return self.render_template("irrigation_templates/irrigation_control")
      
   def get_index_page(self):
       return self.get_diagnostic_page( filename = "schedule_control" )

   def get_diagnostic_page(self, filename):   
       return self.render_template("irrigation_templates/irrigation_diagnostics", filename = filename )

   def irrigation_queue(self):
       return self.render_template("irrigation_templates/irrigation_queue" )

   def display_irrigation_queue(self):
       return self.render_template("irrigation_templates/display_irrigation_queue" )

   def manage_parameters(self):
       return self.render_template("irrigation_templates/manage_parameters" )
       

      


   #  
   #  Function serves a post operation
   #
   def schedule_data(self):
     data           = self.redis_handle.hget("FILES:APP","sprinkler_ctrl.json")
     sprinkler_ctrl = json.loads(data)
     returnValue = []
     for j in sprinkler_ctrl:
         data           = self.redis_handle.hget("FILES:APP",j["link"])
         temp           = json.loads(data)
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
       scratch = json.dumps(json_object).encode()
       self.redis_handle.lpush("QUEUES:SPRINKLER:CTRL", base64.b64encode(scratch) )
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
  
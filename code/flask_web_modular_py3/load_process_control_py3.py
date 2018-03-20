import os
import json
import datetime

class Load_Process_Control(object):

   def __init__( self, app, auth, request,render_template,redis_new_handle, redis_old_handle,gm ):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.render_template  = render_template
       self.redis_new_handle = redis_new_handle
       self.redis_old_handle = redis_old_handle
       self.gm               = gm
       
       
       a1 = auth.login_required( self.process_control )
       app.add_url_rule('/start_and_stop_processes',"start_and_stop_processes",a1)
       process_data = gm.match_terminal_relationship("PROCESS_CONTROL")[0]      
       self.web_command_queue_key =process_data['web_command_key'] 
       self.web_process_data_key = process_data["web_process_data"]
       self.web_display_list_key = process_data["web_display_list"]
       
       

   def process_control(self):
      display_list_json = self.redis_old_handle.get(self.web_display_list_key)
      display_list  = json.loads(display_list_json)
      process_data_json = self.redis_old_handle.get(self.web_process_data_key)
      process_data  = json.loads(process_data_json)
      return self.render_template("process_control_templates/process_control",
                                  display_list = display_list, 
                                  command_queue_key = self.web_command_queue_key,
                                  process_data_key = self.web_process_data_key )
      

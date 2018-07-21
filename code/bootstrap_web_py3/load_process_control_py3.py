
import os
import json
from datetime import datetime
import time

class Load_Process_Management(object):

   def __init__( self, app, auth, request, render_template,controller_names, handlers):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.render_template = render_template
       self.controller_names = controller_names
       self.handlers = handlers
       
       #
       #  Adding Rules
       #

       a1 = auth.login_required( self.process_control )
       app.add_url_rule('/start_and_stop_processes/<int:controller_id>',"start_and_stop_processes",a1)
       
       # internal callable
       a1 = auth.login_required( self.load_processes )
       app.add_url_rule('/manage_processes/load_process',"load_process",a1,methods=["POST"])
       
       # internal call
       a1 = auth.login_required( self.manage_processes )
       app.add_url_rule('/manage_processes/change_process',"change_process",a1,methods=["POST"])



   def process_control(self,controller_id):
      
      display_list = self.handlers[controller_id]["WEB_DISPLAY_DICTIONARY"].hkeys()
      return self.render_template("process_control/process_control",
                                  display_list = display_list, 
                                  command_queue_key = "WEB_COMMAND_QUEUE",
                                  process_data_key = "WEB_DISPLAY_DICTIONARY",
                                  controller_id = controller_id,
                                  controllers = self.controller_names )
      


   def load_processes(self):
       param = self.request.get_json()
      
       controller = int(param["controller"])
       
       if controller >= len(self.controller_names):
          return "BAD"
       else:
          result = self.handlers[controller]["WEB_DISPLAY_DICTIONARY"].hgetall()
          result_json = json.dumps(result)
          
          return result_json.encode()
          

   def manage_processes(self):
       param = self.request.get_json()
      
       controller = int(param["controller"])
       process_state_json = param["process_data"]
       process_state = json.loads(process_state_json)
       if controller >= len(self.controller_names):
          return "BAD"
       else:
          
          self.handlers[controller]["WEB_COMMAND_QUEUE"].push(process_state)
          return json.dumps("SUCCESS")
 
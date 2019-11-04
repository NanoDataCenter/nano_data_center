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
                                      


       a1= auth.login_required( self.irrigation_composite_statistics )
       app.add_url_rule("/irrigation_statistics/composite_statistics,"irrigation_composite_statistics",a1)
       
       
       a1= auth.login_required( self.irrigation_detail_statistics )
       app.add_url_rule("/irrigation_statistics/detail_statistics","irrigation_detail_statistics",a1)
 
       
       a1= auth.login_required( self.irrigation_valve_resistance )
       app.add_url_rule("/irrigation_statistics/valve_resistance/","irrigation_valve_resistance",a1)

   def irrigation_composite_statistics(self,valve_id):
       pass
       
   def irrigation_detail_statistics(self,valve_id):
       pass
       
   def irrigation_valve_resistance(self):
       # get keys
       # sort keys
       # get all objects
       # call template
       #   construct header
       #   for i in keys
       #     draw bubble graph
       #
       pass

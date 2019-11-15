import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing
from  collections import OrderedDict
from statistics import median
class Load_Irrigation_Statistics(Base_Stream_Processing):

   def __init__( self, app, auth, request, app_files, sys_files,
                   render_template,redis_handle, handlers,irrigation_control,valve_current_limits):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.render_template = render_template
       self.redis_handle = redis_handle
       self.handlers = handlers
       self.irrigation_control = irrigation_control
       self.valve_current_limits = valve_current_limits
                                      


       a1= auth.login_required( self.irrigation_composite_statistics )
       app.add_url_rule("/irrigation_statistics/composite_statistics","irrigation_composite_statistics",a1)
       
      
       a1= auth.login_required( self.irrigation_detail_statistics )
       app.add_url_rule("/irrigation_statistics/detail_statistics/<valve_id>","irrigation_detail_statistics",a1)
 
       
       a1= auth.login_required( self.irrigation_valve_resistance )
       app.add_url_rule("/irrigation_statistics/valve_resistance","irrigation_valve_resistance",a1)

   def irrigation_composite_statistics(self):
       return "Irrigation Composite Statistisc"
       
   def irrigation_detail_statistics(self,valve_id):
       return "Irrigation Detailed Statistics"
       
   def irrigation_valve_resistance(self):
       valve_dict = self.handlers["IRRIGATION_VALVE_TEST"]
       keys = valve_dict.hkeys()
       data = valve_dict.hgetall()
       controllers,measurement_list,median_list,value_colors = self.sort_valve_resistance_irrigation_data(keys,data)
       controller_keys = list(controllers.keys())
       controller_keys.sort()
 
       #
       return self.render_template( "streams/valve_resistance_bar_graph",
                                     title = "Valve Current Measurement",
                                     controller_keys = controller_keys,
                                     controllers     = controllers,
                                     measurement_list = measurement_list,
                                     median_list = median_list,
                                     value_colors = value_colors)
                                
       
   ###################################### Local Functions ##################################
      
   def sort_valve_resistance_irrigation_data(self,valve_dict,data):
      return_value = {}
      measurement_list = {}
      median_list = {}
      value_colors = {}
      for i in valve_dict:
         temp = i.split(":")
         controller = temp[0]
         channel = temp[1]
         if controller not in return_value:
            return_value[controller] = []
         return_value[controller].append(int(channel))
     
      for i in return_value.keys():
         return_value[i].sort()
         
      for i in return_value.keys():
         if i not in measurement_list:
            measurement_list[i] = []
            median_list[i] =[]
            value_colors[i] = []
         for j in return_value[i]:
            
            key = str(i)+":"+str(j)
            measurement_list[i].append(data[key][0])
            median_list[i].append(median(data[key]))
            if data[key][0] > self.valve_current_limits["high"]:
                value_colors[i].append('rgba(255,0,0,1.0)')
            elif data[key][0] <self.valve_current_limits["low"]:
                value_colors[i].append('rgba(255,0,0,1.0)')
            else:
                 value_colors[i].append('rgba(0,255,0,1.0)')
            
      for i in return_value.keys():
         temp = []
         for j in return_value[i]:
            temp.append("Channel "+str(j))
         return_value[i] = temp
     
      return return_value,measurement_list,median_list,value_colors

              

          
          
       



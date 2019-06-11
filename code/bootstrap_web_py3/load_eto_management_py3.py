
import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing
from  collections import OrderedDict
class Load_ETO_Management(Base_Stream_Processing):

   def __init__( self, app, auth, request, app_files, sys_files,
                   render_template,redis_access,eto_update_table, handlers):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.render_template = render_template
       self.eto_update_table = eto_update_table
       self.handlers = handlers
       
       #
       #  Adding Rules
       #

       a1 = auth.login_required( self.eto_manage )
       app.add_url_rule('/eto/eto_manage',"eto_manage",a1)
            
       a1 = auth.login_required( self.eto_readings )
       app.add_url_rule('/eto/eto_readings',"eto_raw_data",a1)

       
       a1 = auth.login_required( self.eto_queue )
       app.add_url_rule('/eto/eto_queue',"eto_queue",a1)

       a1 = auth.login_required( self.rain_queue )
       app.add_url_rule('/eto/rain_queue',"rain_queue",a1)
       
       
        
       a1 = auth.login_required( self.eto_setup )
       app.add_url_rule('/eto/eto_setup',"eto_setup",a1)
    
       a1 = auth.login_required( self.weather_station_problems )
       app.add_url_rule('/eto/eto_exception_values','exception_values',a1)

   def weather_station_problems(self):    
       station_data = self.handlers["EXCEPTION_VALUES"].hgetall()
       return self.render_template( "eto_templates/eto_weather_station_issues",station_data = station_data,station_keys = station_data.keys() )
                                
      
       
   def eto_manage( self ):
       return self.render_template("eto_templates/eto_manage",eto_update_table = "eto_update_table")
       
       
   def eto_readings(self):
       eto_data =  self.handlers["ETO_VALUES"].hgetall()
       
       temp_data = {}
       for i,item in eto_data.items():
           temp_data[i] = item["priority"]
       temp_data =[(k, temp_data[k]) for k in sorted(temp_data, key=temp_data.get, reverse=True)]
       eto_keys = []
       for i in temp_data:
          
          eto_keys.append(i[0])
       eto_keys.reverse()
       rain_data =  self.handlers["RAIN_VALUES"].hgetall()
      
       temp_data = {}
       for i,item in rain_data.items():
           temp_data[i] = item["priority"]
       temp_data =[(k, temp_data[k]) for k in sorted(temp_data, key=temp_data.get, reverse=True)]
       rain_keys = []
       for i in temp_data:
          
          rain_keys.append(i[0])
       rain_keys.reverse()
   
       eto_data =  self.handlers["ETO_VALUES"].hgetall()
       
       rain_data = self.handlers["RAIN_VALUES"].hgetall()
       print("rain daa",rain_data)
       return self.render_template( "eto_templates/eto_readings",eto_data = eto_data,eto_keys = eto_keys, 
                               rain_data = rain_data,rain_keys =rain_keys ) 

       
   def eto_queue(self):
   
       temp_data = self.handlers["ETO_HISTORY"].revrange("+","-" , count=1000)
       temp_data.reverse()
       
       chart_title = " ETO Log For Weather Station : "
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       eto_data =  self.handlers["ETO_VALUES"].hgetall()
       temp_data = {}
       for i,item in eto_data.items():
           temp_data[i] = item["priority"]
       temp_data =[(k, temp_data[k]) for k in sorted(temp_data, key=temp_data.get, reverse=True)]
       stream_keys = []
       for i in temp_data:

          stream_keys.append(i[0])
       stream_keys.reverse()
       
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = .5,
                                     min_value = 0.,
                                     
                                     )


  
   def rain_queue(self):
       temp_data = self.handlers["RAIN_HISTORY"].revrange("+","-" , count=1000)
       
       temp_data.reverse()
      
       chart_title = " Rain Log For Weather Station : "
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")

       print("stream keys",stream_keys)
       rain_data = self.handlers["RAIN_VALUES"].hgetall()
       print("rain data",rain_data)
       rain_data =  self.handlers["RAIN_VALUES"].hgetall()
       temp_data = {}
       print("rain_data",rain_data)
       for i,item in rain_data.items():
           temp_data[i] = item["priority"]
       print("temp data",temp_data)
       temp_data =[(k, temp_data[k]) for k in sorted(temp_data, key=temp_data.get, reverse=True)]
       stream_keys = []
       for i in temp_data:
          
          stream_keys.append(i[0])
       stream_keys.reverse()
       print("stream keys ",stream_keys)
     
       stream_data = temp_data
       print("stream_keys",stream_keys)
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = 10.,
                                     min_value = 0.,
                                      
                                     
                                     )
      

   def eto_setup(self):
       eto_data  = self.app_files.load_file( "eto_site_setup.json" )
       pin_list  = self.sys_files.load_file("controller_cable_assignment.json")
       return self.render_template("eto_templates/eto_setup",eto_data_json = json.dumps(eto_data),pin_list_json=json.dumps(pin_list),
                 eto_data = eto_data       )
 
     

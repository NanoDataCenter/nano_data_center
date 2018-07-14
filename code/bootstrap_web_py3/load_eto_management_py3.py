
import os
import json
from datetime import datetime
import time

class Load_ETO_Management(object):

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

       
       a1 = auth.login_required( self.eto_rain_queue )
       app.add_url_rule('/eto/eto_rain_queue',"eto_rain_queue",a1)
       
        
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
       rain_data = self.handlers["RAIN_VALUES"].hgetall()
       return self.render_template( "eto_templates/eto_readings",eto_data = eto_data,eto_keys = eto_data.keys(), 
                               rain_data = rain_data,rain_keys =rain_data.keys() ) 

       
   def eto_rain_queue(self):
       rain_data = self.handlers["RAIN_HISTORY"].revrange("+","-" , count=100)
       rain_data.reverse()
       eto_data = self.handlers["ETO_HISTORY"].revrange("+","-" , count=100)
       eto_data.reverse()

       return self.render_template("eto_templates/streaming_data",eto_data=eto_data, rain_data = rain_data ) 
  
       

   def eto_setup(self):
       eto_data  = self.app_files.load_file( "eto_site_setup.json" )
       pin_list  = self.sys_files.load_file("controller_cable_assignment.json")
       return self.render_template("eto_templates/eto_setup",eto_data_json = json.dumps(eto_data),pin_list_json=json.dumps(pin_list),
                 eto_data = eto_data       )
 
     

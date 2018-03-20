
import os
import json
from datetime import datetime
import time

class Load_ETO_Management(object):

   def __init__( self, app, auth, request, app_files, sys_files,gm ,
                   redis_new_handle,render_template):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.gm        = gm
       self.redis_new_handle = redis_new_handle
       self.render_template  = render_template
 
       temp = gm.match_terminal_relationship("ETO_SITES")
       self.eto_measurement    = temp[0]["measurement"]
       temp = gm.match_terminal_relationship("RAIN_SOURCES")
       self.rain_measurement    =  temp[0]["measurement"]
       temp = gm.match_terminal_relationship("RAIN_QUEUE")[0]
       self.rain_queue = temp["name"]
       temp = gm.match_terminal_relationship("ETO_QUEUE")[0]
       self.eto_queue = temp["name"]
       
 
       a1 = auth.login_required( self.eto_setup )
       app.add_url_rule('/eto/eto_setup',"eto_setup",a1)

       a1 = auth.login_required( self.eto_readings )
       app.add_url_rule('/eto/eto_readings',"eto_raw_data",a1)


       a1 = auth.login_required( self.eto_manage )
       app.add_url_rule('/eto/eto_manage',"eto_manage",a1)
       
       a1 = auth.login_required( self.eto_rain_queue )
       app.add_url_rule('/eto/eto_rain_queue',"eto_rain_queue",a1)
       
       a1 = auth.login_required( self.eto_eto_queue )
       app.add_url_rule('/eto/eto_eto_queue',"eto_eto_queue",a1)
        


   def eto_setup(self):
       eto_data  = self.app_files.load_file( "eto_site_setup.json" )
       pin_list  = self.sys_files.load_file("controller_cable_assignment.json")
       return self.render_template("eto_templates/eto_setup",
                               eto_data = eto_data, 
                               eto_data_json = json.dumps(eto_data), 
                               st = str, 
                               pin_list_json = json.dumps(pin_list) ) 


   def eto_readings(self):
       
       eto_data =  self.redis_new_handle.get(self.eto_measurement)
       rain_data = self.redis_new_handle.get(self.rain_measurement)
       return self.render_template( "eto_templates/eto_readings",eto_data = eto_data, rain_data = rain_data ) 


   def eto_manage( self ):
       return self.render_template("eto_templates/eto_manage")
       
   def eto_rain_queue(self):
       temp = self.redis_new_handle.lrange(self.rain_queue,0,-1)
       rain_data = []
       for i_json in temp:
           i = json.loads(i_json)
           print(i)
           temp = {}
         
           temp["timestamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(i["timestamp"]))
          
           del i["timestamp"]
           value = 0.0
           for j, item in i.items():
               if float(item) > value:
                   value = float(item)
           temp["value"] = value
           rain_data.append(temp)
       return self.render_template("eto_templates/streaming_data",title="Rain TIME HISTORY",y_axis = "Rain data hundreds of inch",
                               header_name = "RAIN_TIME_HISTORY", data = rain_data ) 
  
       
   def eto_eto_queue(self):
       temp = self.redis_new_handle.lrange(self.eto_queue,0,-1)
       eto_data = []
       for i_json in temp:
           i = json.loads(i_json)
           print(i)
           temp = {}
         
           temp["timestamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(i["timestamp"]))
          
           del i["timestamp"]
           value = 0.0
           for j, item in i.items():
               if float(item) > value:
                   value = float(item)
           temp["value"] = value
           eto_data.append(temp)
       return self.render_template("eto_templates/streaming_data",title="ETO TIME HISTORY",y_axis = "ETO data hundreds of inch",
                               header_name = "ETO_TIME_HISTORY", data = eto_data ) 
        
         
         

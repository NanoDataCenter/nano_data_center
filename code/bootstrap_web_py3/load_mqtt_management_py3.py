import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing
from  collections import OrderedDict
class Load_MQTT_Pages(Base_Stream_Processing):

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
      
                                      

       a1 = auth.login_required( self.mqtt_device_status )
       app.add_url_rule('/mqtt/mqtt_device_status',"mqtt_device_status",a1 )
       

       a1= auth.login_required( self.mqtt_reboot_status )
       app.add_url_rule('/mqtt/mqtt_reboot_status',"mqtt_reboot_status",a1)
       
       
       a1= auth.login_required( self.mqtt_unknown_devices )
       app.add_url_rule('/mqtt/mqtt_unknown_devices',"mqtt_unknown_devices",a1)
 
       
       a1= auth.login_required( self.mqtt_unknown_commands )
       app.add_url_rule('/mqtt/mqtt_unknown_commands',"mqtt_unknown_commands",a1)




       a1= auth.login_required( self.mqtt_past_actions )
       app.add_url_rule("/mqtt/mqtt_past_actions","mqtt_past_actions",a1)

       a1= auth.login_required( self.mqtt_device_reset )
       app.add_url_rule('/mqtt/mqtt_device_reset',"mqtt_device_reset",a1)

       a1= auth.login_required( self.mqtt_ajax_reset )
       app.add_url_rule('/mqtt/mqtt_ajax_reset',"mqtt_ajax_reset",a1,methods=["POST"])



   def mqtt_device_status( self):
       temp_data = self.handlers["MQTT_CONTACT_LOG"].hgetall()
       
       for key,item in temp_data.items():
 
         item["time"] = str(datetime.fromtimestamp(item["time"]))
         item["detail"] = "--- Device Id: "+ item["device_id"]+"  Date:  "+item['time'] + " Status "+str(item["status"])
       
       return self.render_template("mqtt_templates/mqtt_status_template" ,time_history = temp_data ,title = "Device Status"  )



   def mqtt_reboot_status( self):
       temp_data = self.handlers["MQTT_REBOOT_LOG"].hgetall()
      
       for key,i in temp_data.items():
           i["time"] = str(datetime.fromtimestamp(int(i["timestamp"]))) 
           i["detail"] = "--- Device Id: "+ i["device_id"]+" Reboot Date:  "+i['time'] 
       return self.render_template("mqtt_templates/mqtt_status_template" ,time_history = temp_data, title ="Reboot Status" )


   def mqtt_unknown_devices( self):
       temp_data = self.handlers["MQTT_UNKNOWN_DEVICES"].hgetall()
      
       for key, i in temp_data.items():
         
         i["detail"] = "--- Unknown Device Topic: "+ i["device_topic"]
       return self.render_template("mqtt_templates/mqtt_status_template" ,time_history = temp_data,title="Unknown Devices" )


   def mqtt_unknown_commands( self):
       temp_data = self.handlers["MQTT_UNKNOWN_SUBSCRIPTIONS"].hgetall()
      
       for key,i in temp_data.items():
         i["time"] = str(datetime.fromtimestamp(i["timestamp"]))
         i["detail"] = "--- Date:  "+i['time'] + " Topic "+str(i['topic'])
       return self.render_template("mqtt_templates/mqtt_status_template" ,time_history = temp_data,title ="Unknown Commands" )



   def mqtt_past_actions( self):
       temp_data = self.handlers["MQTT_PAST_ACTION_QUEUE"].revrange("+","-" , count=1000)
      
       collated_data = []
       for  j in temp_data:
         i= j["data"]
         i["time"] = str(datetime.fromtimestamp(j["timestamp"]))
         i["detail"] = "---Date: "+i["time"]+"  Action: "+i["action"]+"  Device Id: "+i["device_id"] +" Status: "+str(i["status"] )
         collated_data.append(i)
       return self.render_template("mqtt_templates/mqtt_past_actions_template" ,time_history = collated_data,title="PAST ACTIONS" )

   def mqtt_device_reset( self):
      return self.render_template("mqtt_templates/mqtt_reset_device" )

   def mqtt_ajax_reset( self):
       # reset MQTT Devices
       return json.dumps("SUCCESS")


import os
import json
import datetime

class Load_Modbus_Data(object):

   def __init__( self, app, auth, request,render_template,redis_new_handle, redis_old_handle, rpc_client, address_list,logging_key ):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.render_template  = render_template
       self.redis_new_handle = redis_new_handle
       self.redis_old_handle = redis_old_handle
       self.rpc_client  = rpc_client
       
       self.logging_key = logging_key
       
       #self.rpc_client =     Redis_Rpc_Client(redis_rpc_handle  , server_dict["redis_rpc_key"])   
       a1 = auth.login_required( self.ping_device )
       app.add_url_rule('/ping_device',"ping_device",a1)
       
       a1 = auth.login_required( self.modbus_current_status )
       app.add_url_rule("/modbus_current_status","modbus_current_status",a1)

       a1 = auth.login_required( self.modbus_basic_status )
       app.add_url_rule("/modbus_basic_status","modbus_basic_status",a1)

       
       a1 = auth.login_required( self.modbus_device_status )
       app.add_url_rule("/modbus_device_status/<int:remote_index>","modbus_device_status",a1)
       
       a1 = auth.login_required( self.ajax_ping_modbus_device )
       app.add_url_rule('/ajax/ping_modbus_device',"ajax_ping_modbus_device",a1,methods=["POST"])
       
       temp = []
       for i in address_list:
          temp.append(int(i))
       temp.sort()
       address_list = []
       for i in temp:
          address_list.append(str(i))
          
       self.address_list = address_list
          
         

 
       
 

   def ping_device( self ):
       
       return self.render_template("modbus/modbus_ping",address_list = self.address_list)

   def modbus_current_status(self):
       recent_data = json.loads(self.redis_old_handle.get(self.logging_key+":RECENT_DATA"))
 
       remote_list = list(recent_data["remotes"].keys())
       temp = []
       for i in remote_list:
         temp.append(int(i))
       remote_list = temp
       remote_list.sort()
       temp = []
       for i in remote_list:
          temp.append(str(i))
       remote_list = temp
       now = datetime.datetime.now()
       date_string = now.isoformat()
       print(date_string)
       return self.render_template("modbus/current_conditions",data = recent_data, remote_list = remote_list,date_string=date_string )

   def modbus_basic_status( self ):
       recent_data_json = self.redis_old_handle.lrange(self.logging_key+":HOUR_DATA:BASIC_STATS",0,-1)
       recent_data = []
       for i in recent_data_json:
           recent_data.append(json.loads(i))
       sel_prop = {}
       sel_prop["flow"] = {}
       return self.render_template("streaming_data/streaming_data",title="Modbus_Streaming_Data",
                               header_name  ="Modbus_Streaming_Data", data = recent_data, start_index = 0) 


   def modbus_device_status( self,remote_index ):
       recent_data_json = self.redis_old_handle.lrange(self.logging_key+":HOUR_DATA:REMOTES:"+str(self.address_list[remote_index]),0,-1)
       recent_data = []
       for i in recent_data_json:
           recent_data.append(json.loads(i))
       sel_prop = {}
       sel_prop["flow"] = {}
       return self.render_template("modbus/remote_data",title="Modbus Data For Remote "+str(self.address_list[remote_index]),address_list = self.address_list,
                               header_name  ="Modbus Data For Remote "+str(self.address_list[remote_index]), data = recent_data, start_index = 0, 
                               remote_index = remote_index) 

       
       
   def ajax_ping_modbus_device(self):
      
      param            = self.request.get_json()
      remote           = param["remote"]
      
      try:
          result           = self.rpc_client.send_rpc_message( "ping_message",remote,timeout=30 )
          if result == True:
               return_value = "ping received for remote: "+remote
          else:
               return_value = "ping NOT received for remote: "+remote
      except:
          print("ping exception")
          return_value = "ping NOT received for remote: "+remote
      return json.dumps(return_value)


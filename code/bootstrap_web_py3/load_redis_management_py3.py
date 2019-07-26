
import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing

class Load_Redis_Management(Base_Stream_Processing):

   def __init__( self, app, auth, request, app_files, sys_files,render_template, handlers):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.render_template = render_template
       
       
       self.handlers = handlers
       
       #
       #  Adding Rules
             

       
       a1 = auth.login_required( self.redis_key_stream )
       app.add_url_rule('/redis/redis_key_stream',"redis_key_stream",a1)
            
       a1 = auth.login_required( self.redis_client_stream )
       app.add_url_rule('/redis/redis_client_stream',"redis_client_stream",a1)

       a1 = auth.login_required( self.redis_memory_stream )
       app.add_url_rule('/redis/redis_memory_stream',"redis_memory_stream",a1)
       
       a1 = auth.login_required( self.redis_call_stream )
       app.add_url_rule('/redis/redis_call_stream',"redis_call_stream",a1)
       
        
       a1 = auth.login_required( self.redis_cmd_time_stream  )
       app.add_url_rule('/redis/redis_cmd_time_stream',"redis_cmd_time_stream",a1)
    
       a1 = auth.login_required( self.redis_server_time_stream )
       app.add_url_rule('/redis/redis_server_time_stream','redis_server_time_stream',a1)
       
       


   def redis_key_stream(self):
       
       temp_data = self.handlers["REDIS_MONITOR_KEY_STREAM"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Number of Redis Key in : "
      
       stream_keys,stream_range,stream_data = self.format_data_specific_key(temp_data,title=chart_title,title_y="Deg F",title_x="Date",specific_key = "keys")
       
       
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = 10000000,
                                     min_value = 0
                                     
                                     )

      



  

   def redis_client_stream(self):
       temp_data = self.handlers["REDIS_MONITOR_CLIENT_STREAM"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Redis Client : "
       
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
      
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = 10000000,
                                     min_value = 0
                                     
                                     )



   def redis_memory_stream(self):
       temp_data = self.handlers["REDIS_MONITOR_MEMORY_STREAM"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Redis Memory Utilization : "
       
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
      
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = 10000000,
                                     min_value = 0

                                     
                                     )




   def redis_call_stream(self):
       temp_data = self.handlers["REDIS_MONITOR_CALL_STREAM"].revrange("+","-" , count=1000)
       print(temp_data)
       temp_data.reverse()
       chart_title = " Number of Redis Command Calls/hour : "
       
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
       print("made it here",stream_keys,stream_data)
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = 10000000,
                                     min_value = 0
                                     
                                     )

        
 
   def redis_cmd_time_stream (self):
       temp_data = self.handlers["REDIS_MONITOR_CMD_TIME_STREAM"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Redis Command Time in us : "
       
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
      
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = 10000000,
                                     min_value = 0
                                     
                                     )

    
        
   def redis_server_time_stream(self):
       temp_data = self.handlers["REDIS_MONITOR_SERVER_TIME"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Redis Execution time/hour : "
       
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
      
       return self.render_template( "streams/base_stream",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     max_value = 10000000,
                                     min_value = 0
                                     
                                     )
       
 
      
 
 

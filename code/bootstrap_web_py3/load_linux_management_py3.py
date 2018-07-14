
import os
import json
from datetime import datetime
import time

class Load_Linux_Management(object):

   def __init__( self, app, auth, request, app_files, sys_files,render_template, handlers,controllers):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.render_template = render_template
       self.controllers = controllers
       
       self.handlers = handlers
       
       #
       #  Adding Rules
       #
 
       
       a1 = auth.login_required( self.free_cpu )
       app.add_url_rule('/linux/free_cpu/<int:controller_id>',"free_cpu",a1)
            
       a1 = auth.login_required( self.ram )
       app.add_url_rule('/linux/ram/<int:controller_id>',"ram",a1)

       
       a1 = auth.login_required( self.disk_space )
       app.add_url_rule('/linux/disk_space/<int:controller_id>',"disk_space",a1)
       
        
       a1 = auth.login_required( self.temperature )
       app.add_url_rule('/linux/temperature/<int:controller_id>',"temperature",a1)
    
       a1 = auth.login_required( self.process_vsz )
       app.add_url_rule('/linux/vsz','vsz',a1)
       
       
       a1 = auth.login_required( self.process_rss )
       app.add_url_rule('/linux/rss','rss',a1)

       a1 = auth.login_required( self.process_state )
       app.add_url_rule('/linux/state','state',a1)

       
       a1 = auth.login_required( self.process_cpu_core )
       app.add_url_rule('/linux/vsz','cpu_core',a1)

   
       a1 = auth.login_required( self.process_swap_space)
       app.add_url_rule('/linux/swap_space','swap_space',a1)

       a1 = auth.login_required( self.process_io_space )
       app.add_url_rule('/linux/io_space','io_space',a1)

       a1 = auth.login_required( self.process_block_dev )
       app.add_url_rule('/linux/block_dev','block_dev',a1)

       a1 = auth.login_required( self.process_context_switches )
       app.add_url_rule('/linux/context_switches','context_switches',a1)

       a1 = auth.login_required( self.process_run_queue )
       app.add_url_rule('/linux/run_queue','run_queue',a1)

       a1 = auth.login_required( self.process_dev )
       app.add_url_rule('/linux/dev','dev',a1)

             
       a1 = auth.login_required( self.process_sock )
       app.add_url_rule('/linux/sock','sock',a1)

       a1 = auth.login_required( self.process_tcp )
       app.add_url_rule('/linux/tcp','tcp',a1)
 
       a1 = auth.login_required( self.process_udp )
       app.add_url_rule('/linux/udp','udp',a1)


   def free_cpu(self,controller_id):
       print("made it here",controller_id)
       
       temp_data = self.handlers[controller_id]["FREE_CPU"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Free CPU Profile for Linux Controller: "+self.controllers[controller_id]
       print("chart_title",chart_title)
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
       print("stream_keys",stream_keys)
       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )



   def ram(self,controller_id):
      
       
       temp_data = self.handlers[controller_id]["RAM"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Free RAM Profile for Linux Controller: "+self.controllers[controller_id]
       print("chart_title",chart_title)
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
       print("stream_keys",stream_keys)
       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )
            


   def disk_space(self,controller_id):
       
       temp_data = self.handlers[controller_id]["DISK_SPACE"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Disk Space Utilization Linux Controller: "+self.controllers[controller_id]
       print("chart_title",chart_title)
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
       print("stream_keys",stream_keys)
       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )
            

   def temperature(self,controller_id):
       
       temp_data = self.handlers[controller_id]["TEMPERATURE"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Temperature Profile for Linux Controller: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )

        
 
   def process_vsz(self):
       return "SUCCESS"
    

   def process_rss(self):
       return "SUCCESS"
       

   def process_state(self):
       return "SUCCESS"

 
   def process_cpu_core(self):
           return "SUCCESS"



   def process_swap_space(self):
           return "SUCCESS"

   def process_io_space(self):
       return "SUCCESS"

   def process_block_dev(self):
       return "SUCCESS"

   def process_context_switches(self):
       return "SUCCESS"


   def process_run_queue(self):
      return "SUCCESS"
      
   def process_dev(self):
       return "SUCCESS"

      

   def process_sock(self):
       return "SUCCESS"


   def process_tcp(self):
       return "SUCCESS"

       

   def process_udp(self):
       return "SUCCESS"
 
   def format_data(self,stream_data,show_legend = False, title = "",title_x="",title_y="",ntick_x = 20,ntick_y=20):
      return_value = {}
      keys = list(stream_data[0]["data"].keys())
         
      for i in keys:
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')
         return_value[new_key] = self.format_key(i,stream_data,show_legend,title,"Date",i,ntick_x,ntick_y)
     
      old_keys = keys
      keys = []
      for i in old_keys:
                  
         new_key = i
         new_key = new_key.replace('%','')
         new_key = new_key.replace('/','')


         keys.append(new_key)
         
      stream_range = []
      for i in range(0,len(keys)):
         stream_range.append(i)

      return   keys,stream_range,return_value
      
   def format_key(self,key,stream_data,show_legend = False, title = "",title_x="",title_y="",ntick_x = 20,ntick_y=20):   
       data = {}
      
       x_axis = {
          "showgrid":True,
          "zeroline":True,
          "ntick": ntick_x,
          "showline":True,
          "title":title_x,
          "mirror":"all"
          }
       y_axis = {
           "showgrid":True,
           "zeroline":True,
           "ntick": ntick_y,
           "showline":True,
           "title":title_y,
           "mirror":"all"
      
            }      
       layout = {
           'title':title,
		   'showlegend': show_legend,
		   
            'xaxis':x_axis,
            'yaxis':y_axis,
	       };

       data = {}
         
       data["x"] = []
       data["y"] = []
        
      
      # assigning type
      
       data["type"] ="lines"+"markers"
     
       for i in stream_data:
           ts = i["timestamp"]
         
           data["x"].append(ts)
           data["y"].append(i["data"][key])
       return {"data":data,"layout" : layout}     
      
       
     

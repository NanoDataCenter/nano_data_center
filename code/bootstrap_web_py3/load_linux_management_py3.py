
import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing
class Load_Linux_Management(Base_Stream_Processing):

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
       app.add_url_rule('/linux/vsz/<int:controller_id>','vsz',a1)
       
       
       a1 = auth.login_required( self.process_rss )
       app.add_url_rule('/linux/rss/<int:controller_id>','rss',a1)

       a1 = auth.login_required( self.process_cpu )
       app.add_url_rule('/linux/cpu/<int:controller_id>','cpu',a1)
      
       a1 = auth.login_required( self.process_cpu_core )
       app.add_url_rule('/linux/cpu_core/<int:controller_id>','cpu_core',a1)

   
       a1 = auth.login_required( self.process_swap_space)
       app.add_url_rule('/linux/swap_space/<int:controller_id>','swap_space',a1)

       a1 = auth.login_required( self.process_io_space )
       app.add_url_rule('/linux/io_space/<int:controller_id>','io_space',a1)

       a1 = auth.login_required( self.process_block_dev )
       app.add_url_rule('/linux/block_dev/<int:controller_id>','block_dev',a1)

       a1 = auth.login_required( self.process_context_switches )
       app.add_url_rule('/linux/context_switches/<int:controller_id>','context_switches',a1)

       a1 = auth.login_required( self.process_run_queue )
       app.add_url_rule('/linux/run_queue/<int:controller_id>','run_queue',a1)

       a1 = auth.login_required( self.process_dev )
       app.add_url_rule('/linux/dev/<int:controller_id>','dev',a1)

             
       a1 = auth.login_required( self.process_sock )
       app.add_url_rule('/linux/sock/<int:controller_id>','sock',a1)

       a1 = auth.login_required( self.process_tcp )
       app.add_url_rule('/linux/tcp/<int:controller_id>','tcp',a1)
 
       a1 = auth.login_required( self.process_udp )
       app.add_url_rule('/linux/udp/<int:controller_id>','udp',a1)


   def free_cpu(self,controller_id):
       
       
       temp_data = self.handlers[controller_id]["FREE_CPU"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Free CPU Profile for Linux Controller: "+self.controllers[controller_id]
       
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
       
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
      
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
      
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
       
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
       
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

        
 
   def process_vsz(self,controller_id):
       temp_data = self.handlers[controller_id]["PROCESS_VSZ"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " VSZ Profile for Python Process: "
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       
      
       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )

        
   def process_rss(self,controller_id):
       temp_data = self.handlers[controller_id]["PROCESS_RSS"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " RSS Profile for Python Process: "
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )

       

   def process_cpu(self,controller_id):
       temp_data = self.handlers[controller_id]["PROCESS_CPU"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = "% Loading for Python Process: "
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )


 
   def process_cpu_core(self,controller_id):
       temp_data = self.handlers[controller_id]["CPU_CORE"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Temperature Profile for CPU Core: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )



   def process_swap_space(self,controller_id):
       temp_data = self.handlers[controller_id]["SWAP_SPACE"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " SWAP SPACE Used: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )


   def process_io_space(self,controller_id):
       temp_data = self.handlers[controller_id]["IO_SPACE"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " IO Space Activity: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )


   def process_block_dev(self,controller_id):
       temp_data = self.handlers[controller_id]["BLOCK_DEV"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Block Space Activity: "
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )


   def process_context_switches(self,controller_id):
       temp_data = self.handlers[controller_id]["CONTEXT_SWITCHES"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " Context Switches: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )



   def process_run_queue(self,controller_id):
       temp_data = self.handlers[controller_id]["RUN_QUEUE"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " RUN QUEUE Activity: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )

      
   def process_dev(self,controller_id):
       temp_data = self.handlers[controller_id]["DEV"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " NETWORK DEVICE ERRORS: "
       stream_keys,stream_range,stream_data = self.format_data_variable_title(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )


      

   def process_sock(self,controller_id):
       temp_data = self.handlers[controller_id]["IO_SPACE"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " IO Space Activity: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )



   def process_tcp(self,controller_id):
       temp_data = self.handlers[controller_id]["TCP"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " TCP Activity: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )


       

   def process_udp(self,controller_id):
       temp_data = self.handlers[controller_id]["UDP"].revrange("+","-" , count=1000)
       temp_data.reverse()
       chart_title = " UDP Activity: "+self.controllers[controller_id]
       stream_keys,stream_range,stream_data = self.format_data(temp_data,title=chart_title,title_y="Deg F",title_x="Date")
       

       return self.render_template( "streams/stream_multi_controller",
                                     stream_data = stream_data,
                                     stream_keys = stream_keys,
                                     title = stream_keys,
                                     stream_range = stream_range,
                                     controllers = self.controllers,
                                     controller_id = controller_id
                                     
                                     )

 


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
       
       
        <!–Manage Running Processes –>    
<div class="modal fade" id="running_processes" tabindex="-1" role="dialog" aria-labelledby="accountModalLabel" aria-hidden="true">
    <div class="modal-dialog" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="accountModalLabel">ETO Functons</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="close">
                    <span aria-hidden="true">&times;</span>
                </button>
                 
            </div>
            <div class="modal-body">
                <ul >
                   <li><a href ="/start_and_stop_processes" , target="_self">Start and Stop Running Processes</a></li>        
                </ul>
            </div>
            <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                    
            </div>
        </div>
    </div>
</div>   
       

 
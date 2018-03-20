import os
import json
import base64

class Load_Streaming_Data(object):

   def __init__( self, app, auth,render_template,request,
                 app_files,sys_files,redis_old_handle, redis_new_handle,gm ):
       self.app      = app
       self.auth     = auth
       self.render_template = render_template
       self.request = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.redis_old_handle = redis_old_handle
       self.redis_new_handle = redis_new_handle
       self.gm               = gm
       temp                  = self.gm.match_terminal_relationship( "MINUTE_ACQUISITION")[0]
       self.minute_store     =  temp["measurement"]
      
       a1 = auth.login_required( self._one_minute )
       app.add_url_rule('/irrigation_streaming_data/display_minute_irrigation/<int:stream_index>',
                             "display_minute_irrigation",a1,methods=["GET"])

   def _one_minute(self,stream_index): 
       sel_prop = {}
       sel_prop["flow"] = {}
       irrigation_data = []
       temp_data = self.redis_new_handle.lrange(self.minute_store, 0,1440) 
       for i in temp_data:
           irrigation_data.append(json.loads(i))
       return self.render_template("streaming_data/streaming_data",title="Irrigation Streaming Data",
                               header_name = "Irrigation Streaming Data", data = irrigation_data, start_index = stream_index) 




if __name__ == "__main__":
   pass


'''
sel_prop = {}
sel_prop["flow"] = {}
sel_prop["flow"]["header"]        = "Flow Rate History GPM"
sel_prop["flow"]["queue"]          = "/ajax/sel_strip_chart/QUEUES:SPRINKLER:FLOW:"
sel_prop["flow"]["limit_low"]     = 0
sel_prop["flow"]["limit_high"]    = 40
sel_prop["flow"]["sel_function"]  = '/ajax/flow_sensor_names'
sel_prop["flow"]["sel_label"]     = "Flow Sensors"
sel_prop["flow"]["x_axis"]        = "Time"
sel_prop["flow"]["y_axis"]        = "GPM"
@app.route('/sel_chart/<filename>',methods=["GET"])
@authDB.requires_auth
def sel_chart(filename):
   if sel_prop.has_key(filename ):
       header_name   = sel_prop[filename]["header"]
       queue         = sel_prop[filename]["queue"]
       limit_low     = sel_prop[filename]["limit_low"]
       limit_high    = sel_prop[filename]["limit_high"]
       sel_function  = sel_prop[filename]["sel_function"]
       sel_label     = sel_prop[filename]["sel_label"]
       x_axis        = sel_prop[filename]["x_axis"]
       y_axis        = sel_prop[filename]["y_axis"]

    
       return render_template("sel_chart", queue= queue, header_name = header_name,limit_low = limit_low,limit_high=limit_high, 
                               sel_function = sel_function,sel_label = sel_label, x_axis=x_axis,y_axis=y_axis )


   
'''
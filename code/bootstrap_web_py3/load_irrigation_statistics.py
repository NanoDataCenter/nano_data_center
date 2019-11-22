import os
import json
from datetime import datetime
import time
from .base_stream_processing_py3 import Base_Stream_Processing
from  collections import OrderedDict
from statistics import median
import json
class Load_Irrigation_Statistics(Base_Stream_Processing):

   def __init__( self, app, auth, request, app_files, sys_files,
                   render_template,redis_handle, handlers,irrigation_control,valve_current_limits):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.app_files = app_files
       self.sys_files = sys_files
       self.render_template = render_template
       self.redis_handle = redis_handle
       self.handlers = handlers
       self.irrigation_control = irrigation_control
       self.valve_current_limits = valve_current_limits
                                      


       a1= auth.login_required( self.irrigation_composite_statistics )
       app.add_url_rule("/irrigation_statistics/composite_statistics","irrigation_composite_statistics",a1)
       
 
       a1= auth.login_required( self.irrigation_time_history )
       app.add_url_rule("/irrigation_statistics/time_history/<valve_id>/<start_id>/<curve_number>","irrigation_time_history",a1)
       
       a1= auth.login_required( self.mark_irrigation_statistics )
       app.add_url_rule("/irrigation_statistics/mark_irrigation_run","mark_irrigation_statistics",a1)
       
       a1= auth.login_required( self.reset_irrigation_statistics )
       app.add_url_rule("/irrigation_statistics/reset_irrigation_logs","reset_irrigation_statistics",a1)

       
       a1= auth.login_required( self.irrigation_valve_resistance )
       app.add_url_rule("/irrigation_statistics/valve_resistance","irrigation_valve_resistance",a1)

       a1= auth.login_required( self.reset_irrigation_valve_resistance )
       app.add_url_rule("/irrigation_statistics/reset_valve_logs","reset_irrigation_valve_resistance",a1)  

       #
       #  ajax updates
       #
       a1 = auth.login_required( self.mark_irrigation_data )
       app.add_url_rule('/ajax/mark_irrigation_data',"mark_irrigation_data",a1, methods=["POST"]) 
       
       a1 = auth.login_required( self.reset_irrigation_data )
       app.add_url_rule('/ajax/reset_irrigation_logs',"rest_irrigation_logs",a1, methods=["POST"]) 

       a1 = auth.login_required( self.reset_valve_data )
       app.add_url_rule('/ajax/reset_valve_logs',"reset_valve_logs",a1, methods=["POST"])        
       
   def irrigation_composite_statistics(self):

       valve_dict = self.handlers["IRRIGATION_TIME_HISTORY"]
       mark_dict  = self.handlers["IRRIGATION_MARK_DATA"]
       valves = valve_dict.hkeys()
       valves.sort()
       
    
       all_data = valve_dict.hgetall()

       ref_std =  []
       ref_flow =  []
       data_std =  []
       data_flow = []
       for i in valves:
            
            data_flow.append(all_data[i][0]["MAIN_FLOW_METER"]["mean"])
            data_std.append(all_data[i][0]["MAIN_FLOW_METER"]["sd"])
 
            if mark_dict.hexists(i) != True:
               data = all_data[i]
               mark_dict.hset(i,data)
               temp = mark_dict.hget(i)
               temp["time_stamp"] = time.time()
               mark_dict.hset(i,temp)
            mark_data = mark_dict.hget(i)
            ref_flow.append(all_data[i][0]["MAIN_FLOW_METER"]["mean"])
            ref_std.append(all_data[i][0]["MAIN_FLOW_METER"]["sd"])           
            time_stamp = mark_data["time_stamp"]
            date_time =  datetime.fromtimestamp(time_stamp)
            date_time_string = date_time.strftime("%m/%d/%Y, %H:%M:%S")


                        
       
       return self.render_template( "streams/stream_composite_time_history",
                                    date_string = date_time_string,
                                    ref_std =  ref_std,
                                    ref_flow =  ref_flow,
                                    data_std =  data_std,
                                    data_flow = data_flow,
                                   
                                     valves = valves ,
                                     
                                     title = "Irrigation Composite History",
                                     header = "Irrigation Composite History"
                                     )

     
 

   def irrigation_time_history(self,valve_id,start_id,curve_number):
       valve_id = int(valve_id)
       start_id = int(start_id)
       curve_number = int(curve_number)
       valve_dict = self.handlers["IRRIGATION_TIME_HISTORY"]
       mark_dict  = self.handlers["IRRIGATION_MARK_DATA"]
       valves = valve_dict.hkeys()
       valves.sort()
       
       if valve_dict.hexists(valves[valve_id]) == True:
            data = valve_dict.hget(valves[valve_id])
            data.reverse()
            
            if mark_dict.hexists(valves[valve_id]) != True:
               mark_dict.hset(valves[valve_id],data[0])
               temp = mark_dict.hget(valves[valve_id])
               temp["time_stamp"] = time.time()
               mark_dict.hset(valves[valve_id],temp)
            mark_data = mark_dict.hget(valves[valve_id])
            
            
             
            
            stream_length = 0
            measurement_length = 0
            # find names
            
            
           
           
            time_stamp = mark_data["time_stamp"]
            date_time =  datetime.fromtimestamp(time_stamp)
            date_time_string = date_time.strftime("%m/%d/%Y, %H:%M:%S")
            if curve_number > len(data):
                curve_number = len(data)
            names = self.assemble_names(data,mark_data)
            names.sort()
            
            
            ref_x,ref_y = self.assemble_time_reference_data(names,mark_data)
            
            
            data_x,data_y = self.assemble_time_data(curve_number,names,data)
                        
       
            return self.render_template( "streams/stream_irrigation_time_history",
                                    date_string = date_time_string,
                                    stream_length = len(names),
                                    measurement_length  = curve_number,
                                    data_x =  data_x,
                                    data_y =  data_y,
                                    ref_x  =  ref_x,
                                     ref_y =  ref_y,
                                     names   = names,
                                     valves = valves ,
                                     valve_id = valve_id,
                                     start_id = start_id,
                                     curve_number = curve_number,
                                     title = "Irrigation Time History",
                                     header = "Time History for Selected Valve"
                                     )
       else:
           return self.render_template( "streams/stream_multi_curve",
                                     stream_data = [],
                                     stream_keys = [],
                                     titles = [],
                                     stream_range = [],
                                     valves = valves ,
                                     valve_id = valve_id,
                                     title = "Irrigation Time History",
                                     header = "Selected Valve Has No Data"
                                     )       
       
   def mark_irrigation_statistics(self):
       schedule_data = self.schedule_data()
       
       return self.render_template("irrigation_statistics/mark_irrigation_parameters",
                                    schedule_data = schedule_data,
                                    valve_keys_json = json.dumps(self.handlers["IRRIGATION_VALVE_TEST"].hkeys())) 
   
   def reset_irrigation_statistics(self):
       return self.render_template("irrigation_statistics/reset_irrigation_statistics")
 
   def irrigation_valve_resistance(self):
       valve_dict = self.handlers["IRRIGATION_VALVE_TEST"]
       keys = valve_dict.hkeys()
       data = valve_dict.hgetall()
       controllers,measurement_list,median_list,value_colors = self.sort_valve_resistance_irrigation_data(keys,data)
       controller_keys = list(controllers.keys())
       controller_keys.sort()
 
       #
       return self.render_template( "streams/valve_resistance_bar_graph",
                                     title = "Valve Current Measurement",
                                     controller_keys = controller_keys,
                                     controllers     = controllers,
                                     measurement_list = measurement_list,
                                     median_list = median_list,
                                     value_colors = value_colors)
                                
   


   def reset_irrigation_valve_resistance(self):
       
       return self.render_template( "irrigation_statistics/reset_valve_statistics")
   
   ####################################### Ajax Functions #################################
   def mark_irrigation_data(self):
       json_object = self.request.json
       valve_list = json_object["valve_list"]
 
       for i in valve_list:
           if self.handlers["IRRIGATION_TIME_HISTORY"].hexists(i):
               #print("updating ",i)
               reference_data = self.handlers["IRRIGATION_TIME_HISTORY"].hget(i)
               reference_entry = reference_data[-1]
               reference_entry["time_stamp"] = time.time()
               self.handlers["IRRIGATION_MARK_DATA"].hset(i,reference_entry)
       return json.dumps("SUCCESS")    
          
       
   def reset_irrigation_data(self):
      print("reset irrigation data")
      return json.dumps("SUCCESS")
      self.handlers["IRRIGATION_TIME_HISTORY"].delete_all()
      self.handlers["IRRIGATION_MARK_DATA"].delete_all()
      return json.dumps("SUCCESS")
   def reset_valve_data(self):
       print("reset valve data")
       return json.dumps("SUCCESS")
       self.handlers["IRRIGATION_VALVE_TEST"].delete_all()
       return json.dumps("SUCCESS")
       
       

   ###################################### Local Functions ##################################
      
   def sort_valve_resistance_irrigation_data(self,valve_dict,data):
      return_value = {}
      measurement_list = {}
      median_list = {}
      value_colors = {}
      for i in valve_dict:
         temp = i.split(":")
         controller = temp[0]
         channel = temp[1]
         if controller not in return_value:
            return_value[controller] = []
         return_value[controller].append(int(channel))
     
      for i in return_value.keys():
         return_value[i].sort()
         
      for i in return_value.keys():
         if i not in measurement_list:
            measurement_list[i] = []
            median_list[i] =[]
            value_colors[i] = []
         for j in return_value[i]:
            
            key = str(i)+":"+str(j)
            measurement_list[i].append(data[key][-1])
            median_list[i].append(median(data[key]))
            if data[key][0] > self.valve_current_limits["high"]:
                value_colors[i].append('rgba(255,0,0,1.0)')
            elif data[key][0] <self.valve_current_limits["low"]:
                value_colors[i].append('rgba(255,0,0,1.0)')
            else:
                 value_colors[i].append('rgba(0,255,0,1.0)')
            
      for i in return_value.keys():
         temp = []
         for j in return_value[i]:
            temp.append("Channel "+str(j))
         return_value[i] = temp
     
      return return_value,measurement_list,median_list,value_colors

              
   def schedule_data(self):
     sprinkler_ctrl           = self.app_files.load_file("sprinkler_ctrl.json")
     
     returnValue = []
     for j in sprinkler_ctrl:
         temp          = self.app_files.load_file(j["link"])

         j["step_number"], j["steps"], j["controller_pins"] = self.generate_steps(temp)
         returnValue.append(j)
     return json.dumps(returnValue)   
          
          
   def generate_steps( self, file_data):
  
       returnValue = []
       controller_pins = []
       if file_data["schedule"] != None:
           schedule = file_data["schedule"]
           for i  in schedule:
               returnValue.append(i[0][2])
               temp = []
               for l in  i:
                   temp.append(  [ l[0], l[1][0] ] )
               controller_pins.append(temp)
  
  
       return len(returnValue), returnValue, controller_pins      


   def assemble_names(self,data,mark_data):
       names_set = set(list(mark_data.keys()))
       for i in data:
           names_set &= set(list(i.keys()))
                  
       return list(names_set)
       
       
   def assemble_time_reference_data(self,names,mark_data):
        mark_x = {}
        mark_y = {}
        for i in names:
            temp = mark_data[i]["data"]
            mark_x[i] = list(range(1,len(temp)+1))
            mark_y[i] = temp
        return mark_x,mark_y
        
        
   def assemble_time_data(self,curve_number,names,data):
       data_x = {}
       data_y = {}
       
       length = curve_number
       if length > len(data):
          length = len(data)
       
       for j in range(0,length):
           for i in names:
               if i not in data_x:
                   data_x[i] = []
                   data_y[i] = []
               temp = data[j][i]["data"]
               data_x[i].append(list(range(1,len(temp)+1)))
               data_y[i].append(temp)
              
       return data_x,data_y       

import os
import json

class Load_Linux_Controller_Data(object):

   def __init__( self, app, auth, request,render_template,redis_new_handle ):
       self.app      = app
       self.auth     = auth
       self.request  = request
       self.render_template  = render_template
       self.redis_new_handle = redis_new_handle

       a1 = auth.login_required( self.view_running_process )
       app.add_url_rule('/view_running_process',"view_running_process",a1)
       
       a1 = auth.login_required( self.list_reboot_files )
       app.add_url_rule('/list_reboot_files',"list_reboot_files",a1)

       a1 = auth.login_required( self.display_environmental_conditions )
       app.add_url_rule('/display_environmental_conditions',"display_environmental_conditions",a1)

       a1 = auth.login_required( self.linux_time_history )
       app.add_url_rule('/list_linux_time_history/<int:stream_index>',"linux_time_history",a1)

       a1 = auth.login_required( self.linux_process_time_history_RSS )
       app.add_url_rule('/linux_process_time_history_RSS/<int:stream_index>',"linux_process_time_history_RSS",a1)
       
       a1 = auth.login_required( self.linux_process_time_history_VSZ )
       app.add_url_rule('/linux_process_time_history_VSZ/<int:stream_index>',"linux_process_time_history_VSZ",a1)

       a1 = auth.login_required( self.list_reboot_data )
       app.add_url_rule('/list_reboot_file_data',"list_reboot_file_data",a1)
      
       
   def view_running_process(self):
       os.system("/home/pi/new_python/python_process.bsh > tmp_file")
       
       with open("tmp_file","r") as myfile:
           data = myfile.readlines()
       title_a = "View Python Running Processes"
       header_name_a = title_a
       header_a = title_a
      
       return self.render_template( "view_file_list",title =title_a, header_name= header_name_a, file_list = data ,header = header_a) 


   def list_reboot_files(self):

       os.system("ls -l /tmp/*.errr > tmp_file")
       data = ""
       with open("tmp_file","r") as myfile:
           data = myfile.readlines()
           
       title_a = "View Python Error Entries"
       header_name_a = title_a
       header_a = title_a
       return self.render_template( "view_file_list",title =title_a, header_name= header_name_a, file_list = data ,header = header_a) 

   def list_reboot_data( self ):
       os.system("ls /tmp/*.errr > tmp_file")
       output = []
       with open("tmp_file","r") as myfile:
           data = myfile.readlines()
       for i in data:
           output.append("")
           output.append("Log Data for File: "+i)
           output.append("")
           with open(i.strip(),"r" ) as my_file:
              output.extend( my_file.readlines())
       print(output)
       if len(output) == 0:
          output.append("No Error Files")
       title_a = "View Python Error Data"
       header_name_a = title_a
       header_a = title_a
       return self.render_template( "view_file_list_unordered",title =title_a, header_name= header_name_a, file_list = output ,header = header_a) 
       

   def display_environmental_conditions(self):
       
       data = self.redis_new_handle.lindex("LINUX_HOUR_LIST_STORE",0)
       data = json.loads(data)
       for i,item in data.items():
           if isinstance(item, list):
              pass
           else:
              data[i] = [ item ]

       return self.render_template( "linux_system/display_environmental_conditions",data  = data, keys = data.keys() ) 
       
   def linux_time_history( self,stream_index ):
 
       linux_data = []
       temp_data = self.redis_new_handle.lrange("LINUX_HOUR_LIST_STORE", 0,-1) 
       for i in temp_data:
           linux_data.append(self.parse_linux_stream_data(i))

       return self.render_template("linux_system/streaming_data",title="Linux Streaming Data",
              header_name = "Linux Controller Streaming Data", data = linux_data, start_index = stream_index) 
              
   def parse_linux_stream_data(self, block_json):
         return_value = {}
         block_data = json.loads( block_json )

         temp = block_data["proc_mem"][1]
         temp_list = temp.split()
         
         return_value["Free_Memory"] = int(temp_list[1])
         return_value["time_stamp"] = block_data["time_stamp"]
         return_value["cpu_temp"] = int(block_data["pi_temperature_hourly"])
         temp = block_data['free_cpu'][-1]
         temp_list = temp.split()
         
         return_value["free_cpu"] = float(temp_list[1])
         temp = block_data["linux_disk"][-2]
         temp_list = temp.split()
         return_value[temp_list[1]] = float(temp_list[-1])*100
         temp = block_data["linux_disk"][-1]
         temp_list = temp.split()
         return_value[temp_list[1]] = float(temp_list[-1])*100


         return return_value
         
   def linux_process_time_history_RSS(self,stream_index):
 
       linux_data = []
       temp_data = self.redis_new_handle.lrange("LINUX_HOUR_LIST_STORE", 0,-1) 
       for i in temp_data:
           linux_data.append(self.parse_linux_stream_data_memory_RSS(i))

       return self.render_template("linux_system/streaming_data",title="RSS Useage Process",
              header_name = "Python Process Memory Useage RSS", data = linux_data, start_index = stream_index) 
       return "SUCCESS"
       
   def parse_linux_stream_data_memory_RSS(self, block_json):
         return_value = {}
         block_data = json.loads( block_json )
        
         temp_data = block_data["python_processes"]
         for i_json in temp_data:
             i_dict = json.loads(i_json)
             name = i_dict["python_process"]
             if len(name.split(".")) > 1:
               return_value[i_dict["python_process"]] = float(i_dict["RSS"])

         return_value["time_stamp"] = block_data["time_stamp"]
         return return_value

                  
   def linux_process_time_history_VSZ(self,stream_index):
 
       linux_data = []
       temp_data = self.redis_new_handle.lrange("LINUX_HOUR_LIST_STORE", 0,-1) 
       for i in temp_data:
           temp_value = self.parse_linux_stream_data_memory_VSZ(i)
           if temp_value != None:
               linux_data.append(temp_value)

       return self.render_template("linux_system/streaming_data",title="RSS Useage Process",
              header_name = "Python Process Memory Useage VSZ", data = linux_data, start_index = stream_index) 
       return "SUCCESS"
       
   def parse_linux_stream_data_memory_VSZ(self, block_json):
         return_value = {}
         block_data = json.loads( block_json )
        
         temp_data = block_data["python_processes"]
         for i_json in temp_data:
             i_dict = json.loads(i_json)
             name = i_dict["python_process"]
             
             if (len(name.split(".")) > 1) and ("VSZ" in i_dict):
               return_value[i_dict["python_process"]] = float(i_dict["VSZ"])
         if len(return_value ) > 1:
             return_value["time_stamp"] = block_data["time_stamp"]
         else:
             return_value = None
         return return_value

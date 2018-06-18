import time
import json
import redis
import subprocess
from subprocess import Popen, check_output
import shlex
import os
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
from redis_support_py3.graph_query_support_py3 import  Query_Support
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
import msgpack
import pickle
import zlib

class Process_Control(object ):

   def __init__(self):
       pass
  
   def run_process_to_completion(self,command_string, shell_flag = False, timeout_value = None):

       try:
          command_parameters = shlex.split(command_string)
          return_value = check_output(command_parameters, stderr=subprocess.STDOUT , shell = shell_flag, timeout = timeout_value)
          return [0,return_value.decode()]
       except subprocess.CalledProcessError as cp:

           return [ cp.returncode  , cp.output.decode() ]
       except :
           return [-1,""]
       
   def launch_process(self,command_string,stderr=None,shell=True):
       command_parameters = shlex.split(command_string)
       try:

           process_handle = Popen(command_parameters, stderr=open(self.error_file,'w' ))
           return [ True, process_handle ]  
       except:
           return [False, None]       
           
      
   
   def monitor_process(self, process_handle):
       returncode = process_handle.poll()
     
       if returncode == None:
          return [ True, 0]
       else:
       
           process_handle.kill()
           process_handle.wait()        
           del process_handle
           
           return [ False, returncode ]
       
   def kill_process(self,process_handle):
      try:
         process_handle.kill()
         process_handle.wait()
         del process_handle
        
      except:
         pass
    
       
class Manage_A_Python_Process(Process_Control):

   def __init__(self,command_string, restart_flag = True,  error_directory = "/tmp"):

       super(Process_Control,self)
       
       self.restart_flag = restart_flag
       command_string = "python3   "+command_string
       self.command_string = command_string
       command_list= shlex.split(command_string)

       script_file_list = command_list[1].split("/")
     
       self.script_file_name = script_file_list[-1].split(".")[0]
       temp  = error_directory + "/"+self.script_file_name
       self.error_file = temp+".err"
       self.error_file_rollover = temp +".errr"
       self.error = False
       self.enabled = True
       self.active = False
       
   def get_script(self):
       return self.script_file_name
       

   def launch(self):
       if( (self.enabled == True) and (self.active == False )):
           temp = self.launch_process(self.command_string, stderr=self.error_file)
           return_value = temp[0]
           self.handle = temp[1]
           self.active = return_value
           if self.active == False:
               self.rollover()
               self.error = True
           else:
              self.error = False
          
       

    
   def monitor(self):
       self.rollover_flag = False
       if self.enabled == True:
          if self.active == True:
             return_value = self.monitor_process(self.handle)
             
             if return_value[0] == True:
                  self.error = False
             else:     
                 self.error = True
                 self.active = False
                 self.rollover()
                 self.rollover_flag = True
                 if self.restart_flag == True:
                        self.launch()
        


   def rollover(self):
        os.system("mv "+self.error_file+"  " +self.error_file_rollover)
           
   def kill(self):
       self.active = False
       self.error = False
       self.enabled = False
       self.kill_process(self.handle)
       self.rollover()
       
           
       
             
 

class System_Control(object):
   def __init__(self,processor_node, package_node, generate_handlers):
            
               
       self.command_list = processor_node["command_list"]
       data_structures = package_node["data_structures"]
       
       self.ds_handlers = {}
       self.ds_handlers["ERROR_STREAM"]        = generate_handlers.construct_stream_writer(data_structures["ERROR_STREAM"])
       self.ds_handlers["WEB_COMMAND_QUEUE"]   = generate_handlers.construct_job_queue_server(data_structures["WEB_COMMAND_QUEUE"])
       
       self.ds_handlers["WEB_DISPLAY_DICTIONARY"]   =  generate_handlers.construct_hash(data_structures["WEB_DISPLAY_DICTIONARY"])
 
       self.startup_list = []
       self.process_hash = {}
      
       for command in self.command_list:
          temp_class = Manage_A_Python_Process( command_string = command["file"], restart_flag = command["restart"] )
          python_script = temp_class.get_script()
          self.startup_list.append(python_script)
          self.process_hash[python_script] = temp_class


       self.update_web_display()
       
      
       
    

       
   def launch_processes( self,*unused ):
 
       for script in self.startup_list:
           temp = self.process_hash[script]
           temp.launch()
           if temp.error == True:
               with open(temp.error_file_rollover, 'r') as myfile:
                     data=myfile.read()
               if data != None:
                    data = data.encode()
                    crc = zlib.crc32(data)
                    data = zlib.compress(data)
               else:
                    crc = 0
                    data = ""
               self.self.ds_handlers["ERROR_STREAM"].push( data = { "script": script,"crc":crc, "error_output" : data } )
               temp.error = False

   
   def monitor( self, *unused ):
     
       for script in self.startup_list:
           
           temp = self.process_hash[script]
           temp.monitor()
          
           if temp.rollover_flag == True:
               print("process has died",script)
               with open(temp.error_file_rollover, 'r') as myfile:
                     data=myfile.read()
               if data != None:
                    data = data.encode()
                    crc = zlib.crc32(data)
                    data = zlib.compress(data)
               else:
                    crc = 0
                    data = ""
               self.self.ds_handlers["ERROR_STREAM"].push( data = { "script": script,"crc":crc, "error_output" : data } )
               temp.rollover_flag = False
      
       self.update_web_display()
           
   def process_web_queue( self, *unused ):
       data = self.ds_handlers["WEB_COMMAND_QUEUE"].pop()
       
       if data[0] == True :
           for script,item in data[1].items():
               temp = self.process_hash[script]
               try:
                   if item["enabled"] == True:
                        if temp.enabled == False:
                           temp.enabled = True 
                           temp.active = False
                           #print(script,"---------------------------launch")
                           temp.launch()
                   else:
                       if temp.enabled == True:
                          temp.enabled = False
                          #print(script,"----------------------------kill")
                          temp.kill()
               except:
                   pass
          
           self.update_web_display()    
                      

                
   def update_web_display(self):
     
       old_keys = self.ds_handlers["WEB_DISPLAY_DICTIONARY"].hkeys()
       for script in self.startup_list:
           temp = self.process_hash[script]
           self.ds_handlers["WEB_DISPLAY_DICTIONARY"].hset(script,{"name":script,"enabled":temp.enabled,"active":temp.active,"error":temp.error})
      
       new_keys = self.ds_handlers["WEB_DISPLAY_DICTIONARY"].hkeys()
       keys_to_delete_set = set(old_keys).difference(set(new_keys))
       keys_to_delete_list = set(keys_to_delete_set)
       for i in keys_to_delete_list:
          sekf.ds_handlers["WEB_DISPLAY_DICTIONARY"].hdelete(i)
 
 

  


      
   def add_chains(self,cf):

       cf.define_chain("initialization",True)
       
       cf.insert.one_step(self.launch_processes)
       cf.insert.enable_chains( ["monitor_web_command_queue","monitor_active_processes"] )
       
       cf.insert.terminate()
   
   
       cf.define_chain("monitor_web_command_queue", False)
       cf.insert.wait_event_count( event = "TIME_TICK", count = 1)
       cf.insert.one_step(self.process_web_queue)
       cf.insert.reset()
       
       cf.define_chain("monitor_active_processes",False)
       cf.insert.wait_event_count( event = "TIME_TICK",count = 10)
       cf.insert.one_step(self.monitor)
       
       cf.insert.reset()




 
  

if __name__ == "__main__":
   
   cf = CF_Base_Interpreter()
    #
    #
    # Read Boot File
    # expand json file
    # 
   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   site_data = json.loads(data)

   qs = Query_Support( redis_server_ip = site_data["host"], redis_server_port=site_data["port"], db = site_data["graph_db"] )
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_terminal( query_list,relationship="PROCESSOR",label=site_data["local_node"] )

   processor_sets, processor_nodes = qs.match_list(query_list)
    
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
   query_list = qs.add_match_relationship( query_list,relationship="PROCESSOR",label=site_data["local_node"] )
   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", label = "DATA_STRUCTURES" )
                                        
                                        
                                           
   package_sets, package_nodes = qs.match_list(query_list)  
   

   generate_handlers = Generate_Handlers(package_nodes[0],site_data)
   system_control = System_Control(processor_nodes[0],package_nodes[0],generate_handlers)
   cf = CF_Base_Interpreter()
   system_control.add_chains(cf)
   #
   # Executing chains
   #
    
   cf.execute()
else:
   pass



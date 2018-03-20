import time
import json
import redis
import subprocess
from subprocess import Popen, check_output
import shlex
import os
from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
from redis_graph_py3 import farm_template_py3

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
       if self.enabled == True:
          if self.active == True:
             return_value = self.monitor_process(self.handle)
             if return_value[0] == True:
                  return True
            
          self.active = False
          self.rollover()
           
          if self.restart_flag == True:
               self.launch()
          return False


   def rollover(self):
        os.system("mv "+self.error_file+"  " +self.error_file_rollover)
           
   def kill(self):
       self.active = False
       self.error = False
       self.enabled = False
       self.kill_process(self.handle)
       self.rollover()
       
           
       
             
 

class System_Control(object):
   def __init__(self,
               redis_handle,
               error_queue_key,
               web_command_queue_key,
               web_process_data_key,
               web_display_list_key,
               command_string_list ):
               
       self.redis_handle = redis_handle
       self.error_queue_key = error_queue_key
       self.web_command_queue_key = web_command_queue_key
       self.web_process_data_key = web_process_data_key
       self.web_display_list_key = web_display_list_key
       self.command_string_list = command_string_list
        
       self.startup_list = []
       self.process_hash = {}
       self.process_state = {}
       for command_string in command_string_list:
          temp_class = Manage_A_Python_Process( command_string )
          python_script = temp_class.get_script()
          self.startup_list.append(python_script)
          self.process_hash[python_script] = temp_class
          
       self.redis_handle.set(self.web_display_list_key,json.dumps(self.startup_list))
       self.update_web_display()
      
       
    

       
   def launch_processes( self,*unused ):
 
       for script in self.startup_list:
           temp = self.process_hash[script]
           temp.launch()
           if temp.error == True:
               return_data = json.dumps({ "script": script, "error_file" : temp.temp.error_file_rollover})
               self.redis_handle.publish(self.error_queue_key,return_data)
               temp.error = False

   
   def monitor( self, *unused ):
     
       for script in self.startup_list:
           temp = self.process_hash[script]
           temp.monitor()
           if temp.error == True:
               return_data = json.dumps({ "script": script, "error_file" : temp.temp.error_file_rollover})
               self.redis_handle.publish(self.error_queue_key,return_data)
               temp.error = False
      
       self.update_web_display()
           
   def process_web_queue( self, *unused ):
     
       if self.redis_handle.llen(self.web_command_queue_key) > 0 :
           data_json = redis_handle.lpop(self.web_command_queue_key)
           self.redis_handle.ltrim(self.web_command_queue_key,0,-1) # empty redis queue
           data = json.loads(data_json)
           print("made it here")
           for script,item in data.items():
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
               print(self.process_hash[script].active)
               print(self.process_hash[script].enabled)
          
           self.update_web_display()    
                      

                
   def update_web_display(self):
     
       process_state = {}
       for script in self.startup_list:
           temp = self.process_hash[script]
           process_state[script] = {"name":script,"enabled":temp.enabled,"active":temp.active,"error":temp.error}
       self.redis_handle.set(self.web_process_data_key,json.dumps(process_state))
      
      
 
 

  


      
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
   gm = farm_template_py3.Graph_Management(
        "PI_1", "main_remote", "LaCima_DataStore")
        
        
   process_data = gm.match_terminal_relationship("PROCESS_CONTROL")[0]
  
   redis_data = process_data["redis"]
   redis_handle = redis.StrictRedis(
        host=redis_data["ip"], port=redis_data["port"], db=redis_data["db"], decode_responses=True)
   web_command_queue_key =process_data['web_command_key'] 
   error_queue_key = process_data['error_queue_key']
   command_string_list  = process_data["command_string_list"]
   web_process_data_key = process_data["web_process_data"]
   web_display_list_key = process_data["web_display_list"]
   print(web_process_data_key,web_display_list_key)
   system_control = System_Control(   redis_handle    = redis_handle,
                                      error_queue_key = error_queue_key,
                                      web_command_queue_key = web_command_queue_key,
                                      web_process_data_key = web_process_data_key,
                                      web_display_list_key = web_display_list_key,
                                      command_string_list = command_string_list )

   system_control.add_chains(cf)

   cf.execute()
 

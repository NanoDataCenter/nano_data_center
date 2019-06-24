import json

class Irrigation_Scheduling(object):
   def __init__(self,handlers,app_files,sys_files,eto_control_field):
       self.handlers = handlers
       self.app_files = app_files
       self.sys_files = sys_files
       self.eto_control_field = eto_control_field
       
       
   def queue_schedule(self,queue_data):
       self.load_auto_schedule(queue_data["schedule_name"])
       
   def queue_schedule_step(self,queue_data):
       self.load_step_data( queue_data["schedule_name"], int(queue_data["step"]) ,None,True )
   
   def queue_schedule_step_time(self,queue_data):
      self.load_step_data( queue_data["schedule_name"], queue_data["schedule_step"] ,queue_data["schedule_step_time"],True ) 
       
   def queue_schedule_step_time_no_eto(self,queue_data):
      self.load_step_data( queue_data["schedule_name"], queue_data["schedule_step"] ,queue_data["schedule_step_time"],False ) 

   def  direct_valve_control(self,queue_data):

       json_object = {}
       json_object["type"]            =  "IRRIGATION_STEP"
       json_object["schedule_name"]   =  queue_data["controller"]
       json_object["step"]            =  queue_data["pin"] 
       json_object["io_setup"]        =  [{ "remote":queue_data["controller"], "bits":[queue_data["pin"]] }]
       json_object["run_time"]        =  queue_data["run_time"] 
       json_object["elasped_time"]    =  0
       json_object["eto_enable"]      =  False
       self.handlers["IRRIGATION_PENDING"].push(json_object)
 
    
   


 

       
 
   def load_auto_schedule( self, schedule_name):
       schedule_control = self.app_files.load_file("sprinkler_ctrl.json")
       print("schedule_control",type(schedule_control),schedule_control)
       step_number      = len( schedule_control )

       ###
       ### load step data
       ###
       ###
       for i in range(1,step_number+1):
           self.load_step_data( schedule_name, i ,None,True )

     
  





   # note schedule_step_time can be None then use what is in the schedule
   def load_step_data( self, schedule_name, schedule_step,  schedule_step_time ,eto_flag ):
       print( "load step data schedule name ----------------->",schedule_name, schedule_step, schedule_step_time) 
         
       temp = self.get_schedule_data( schedule_name, schedule_step)
       if temp != None :
           schedule_io = temp[0]
           schedule_time = temp[1]
           if  schedule_step_time == None:
               schedule_step_time = schedule_time
           json_object = {}
           json_object["type"]            = "IRRIGATION_STEP"
           json_object["schedule_name"]   =  schedule_name
           json_object["step"]            =  schedule_step
           json_object["io_setup"]        =  schedule_io
           json_object["run_time"]        =  schedule_step_time
           json_object["elasped_time"]    =  0
           json_object["eto_enable"]      =  eto_flag
           self.handlers["IRRIGATION_PENDING"].push(json_object)
          
       else:
           print("bad schedule ",schedule_name)
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"load step data","details":"NonExisting Schedule "+schedule_name,"level":"RED"})
           #raise  # non schedule




   def get_schedule_data( self, schedule_name, schedule_step):
       schedule_control = self.get_json_data( schedule_name )
    
       if schedule_control != None:
           if len(schedule_control ) < schedule_step -1:
              return None
           io_control = schedule_control["schedule"][schedule_step -1] 
           m               = io_control[0]
           schedule_time   = m[2]
           # format io_control
           new_io_control = []
           for i in io_control:
         
              temp = { }
              temp["remote"] = i[0]
              temp["bits"]  =  i[1]
              new_io_control.append(temp)
           return [ new_io_control, schedule_time ]
       return None
 
   def get_json_data( self, schedule_name ):
      
       sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")
    
       for j in sprinkler_ctrl :  
           if j["name"] == schedule_name:
               json_data=self.app_files.load_file(j["link"]) 
               return json_data    
       return None
      
       


     



class Incomming_Queue_Management(object):
   def __init__(self,cf, handlers,app_files,sys_files,eto_control_field):
       self.cf = cf
       self.handlers = handlers
       self.app_files = app_files
       self.sys_files = sys_files
       self.eto_control_field = eto_control_field
       self.irrigation_sched = Irrigation_Scheduling(handlers,app_files,sys_files,eto_control_field)
       
       

       self.commands = {}

       self.commands["CLEAR"]                     = self.clear                   
       self.commands["QUEUE_SCHEDULE"]            = self.irrigation_sched.queue_schedule
       self.commands["QUEUE_SCHEDULE_STEP"]       = self.irrigation_sched.queue_schedule_step     
       self.commands["QUEUE_SCHEDULE_STEP_TIME"]  = self.irrigation_sched.queue_schedule_step_time
       self.commands["QUEUE_SCHEDULE_STEP_TIME_NO_ETO"]  = self.irrigation_sched.queue_schedule_step_time_no_eto   
       self.commands["DIRECT_VALVE_CONTROL"]      = self.irrigation_sched.direct_valve_control       
       self.commands["CLEAN_FILTER"]              = self.clean_filter                
       self.commands["OPEN_MASTER_VALVE"]         = self.open_master_valve           
       self.commands["CLOSE_MASTER_VALVE"]        = self.close_master_valve         
       self.commands["RESET_SYSTEM_QUEUE"]        = self.reset_system_queue
       self.commands["RESET_SYSTEM_NOW"]          = self.reset_system_now       
       self.commands["CHECK_OFF"]                 = self.check_off       
       self.commands["SUSPEND"]                   = self.suspend                    
       self.commands["RESUME"  ]                  = self.resume                      
       self.commands["SKIP_STATION"]              = self.skip_station     
       self.commands["RESISTANCE_CHECK"]          = self.resistance_check         

       self.add_chains(cf)

   def dispatch_sprinkler_mode(self,chainFlowHandle, chainObj, parameters,event):


           try: 
               length = self.handlers["IRRIGATION_JOB_SCHEDULING"].length()
             
               
               data = self.handlers["IRRIGATION_JOB_SCHEDULING"].pop()
               object_data = data[1]
               if object_data != None:
                  print(type(object_data))             
                  if isinstance(object_data, str):
                     object_data = json.loads(object_data)
                  print("object_data",object_data)
       
                  if object_data["command"] in self.commands :
                       self.commands[object_data["command"]]( object_data )
                  else:
                      self.alarm_queue.store_past_action_queue("Bad_Irrigation_Command","RED",object_data["command"]  )
                      raise
              
           except Exception as tst:
               self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"IRRIGATION_CONTROLLER_EXCEPTION","details":[tst,object_data["command"]],"level":"RED"})
               
               raise
      

   def add_chains( self, cf ):
   
       cf.define_chain( "sprinkler_command_queue", True ) 
       cf.insert.log("sprinkler_command_queue")
       cf.insert.wait_event_count(count = 1 ) # wait 1 seconds
       cf.insert.one_step(  self.dispatch_sprinkler_mode  ) 
       cf.insert.reset()

  



      


   def suspend( self, *args ):
       
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.sprinkler_ctrl.suspend_operation()
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"SUSPEND_OPERATION","level":"YELLOW"})
       self.cf.send_event("IRI_MASTER_VALVE_SUSPEND",None)
       self.handlers["IRRIGATION_CONTROL"].hset("SUSPEND",1)

   def resume( self, *args ):
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"RESUME_OPERATION","level":"YELLOW"})
       self.sprinkler_ctrl.resume_operation()
       self.cf.send_event("IRI_MASTER_VALVE_RESUME",None)
       self.handlers["IRRIGATION_CONTROL"].hset("SUSPEND",0)

   def skip_station( self, *args ):
       self.sprinkler_ctrl.skip_operation()

   def resistance_check( self, object_data ):
        json_object = {}
        json_object["type"]   = "RESISTANCE_CHECK"
        self.handlers["IRRIGATION_PENDING"].push(json_object)
        
             


   def check_off( self,object_data ):
        json_object = {}
        json_object["type"]            = "CHECK_OFF"
        self.handlers["IRRIGATION_PENDING"].push(json_object)
       

   def clean_filter( self, object_data ):
        json_object = {}
        json_object["type"]  = "CLEAN_FILTER"
        self.handlers["IRRIGATION_PENDING"].push(json_object)       

  
 
   def clear( self, object_data ):
        self.cf.send_event("IRI_CLEAR",None)         


         
 

   def open_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"OPEN_MASTER_VALVE","level":"YELLOW"})
       chainFlowHandle.send_event("IRI_OPEN_MASTER_VALVE",None)

     
  
   def close_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"CLOSE_MASTER_VALVE","level":"YELLOW"})
       chainFlowHandle.send_event("IRI_CLOSE_MASTER_VALVE",None)
      
    
 


   def  reset_system_now( self, *args ):
      self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"REBOOT_NOW","level":"YELLOW"})
      self.redis_handle.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","RESET_SYSTEM")
      os.system("reboot")  

   def reset_system_queue( self, object_data,chainFlowHandle, chainObj, parameters,event ):
        json_object = {}
        json_object["type"]  = "RESET_SYSTEM_QUEUE"
        self.handlers["IRRIGATION_PENDING"].push(json_object)     


       



 
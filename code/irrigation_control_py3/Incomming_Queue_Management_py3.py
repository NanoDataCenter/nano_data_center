
import time
import os



class Irrigation_Scheduling(object):
   def __init__(self,handlers,app_files,sys_files,eto_management,irrigation_hash_control ):
       self.handlers = handlers
       self.app_files = app_files
       self.sys_files = sys_files
       self.irrigation_hash_control = irrigation_hash_control
       self.eto_management = eto_management  
              
       
   def queue_schedule(self,queue_data):
       self.load_auto_schedule(queue_data["schedule_name"])
       
   def queue_schedule_step(self,queue_data):
       self.load_step_data( queue_data["schedule_name"], int(queue_data["step"]) ,None,True )
   
   def queue_schedule_step_time(self,queue_data):
      #print("made it here",queue_data)
      #print(queue_data["schedule_name"], queue_data['step'] ,queue_data["run_time"])
      self.load_step_data( queue_data["schedule_name"], queue_data['step'] ,queue_data["run_time"],True ) 
       
   def queue_schedule_step_time_no_eto(self,queue_data):
      #print("made it here",queue_data)
      self.load_step_data( queue_data["schedule_name"], queue_data['step'] ,queue_data["run_time"],False ) 

   def  direct_valve_control(self,queue_data):
       #print("made it here",queue_data)
       json_object = {}
       json_object["type"]            =  "IRRIGATION_STEP"
       json_object["schedule_name"]   =  queue_data["controller"]
       json_object["step"]            =  int(queue_data["pin"] )
       json_object["io_setup"]        =  [{ "remote":queue_data["controller"], "bits":[int(queue_data["pin"])] }]
       json_object["run_time"]        =  int(queue_data["run_time"] )
       json_object["elasped_time"]    =  0
       json_object["eto_enable"]      =  False
       self.handlers["IRRIGATION_PENDING"].push(json_object)
 
    
   


 

       
 
   def load_auto_schedule( self, schedule_name):
       schedule_control = self.app_files.load_file("sprinkler_ctrl.json")
       try:
         link_data = self.get_json_data( schedule_name )["schedule"]

         for schedule_step in range(1,len(link_data)+1):
              
             try:
               
                  step_data = self.get_schedule_data( link_data, schedule_name, schedule_step)
                  schedule_step_time = step_data[1]
                  #print( "load step data schedule name ----------------->",schedule_name, schedule_step, schedule_step_time,step_data)
                  self.queue_step_data(step_data,schedule_name,schedule_step,schedule_step_time,eto_flag=True)
          
             except Exception as tst:
                print("bad schedule ",schedule_name,schedule_step,tst)
                details = schedule_name +"  "+str(schedule_step)+" "+str(tst)
                self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"load schedule data","details":details,"level":"RED"})
          
       except Exception as tst:
           details = "Schedule is not defined "+ str(schedule_name) +" " + str(tst)
           print(details)
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"load schedule data","details":details,"level":"RED"})
    
  





   
   def load_step_data( self, schedule_name, schedule_step,  schedule_step_time ,eto_flag ):
       print(schedule_name,schedule_step,schedule_step_time)
       try:
           schedule_step = int(schedule_step)
           if schedule_step_time != None:
                schedule_step_time = int(schedule_step_time)
           link_data = self.get_json_data( schedule_name )["schedule"] 
           
           step_data = self.get_schedule_data( link_data,schedule_name, schedule_step)
           if schedule_step_time == None:
              schedule_step_time = step_data[1]
           #print( "load step data schedule name ----------------->",schedule_name, schedule_step, schedule_step_time,step_data)
           self.queue_step_data(step_data,schedule_name,schedule_step,schedule_step_time,eto_flag)
       except Exception as tst:
           print("bad schedule ",schedule_name,schedule_step,tst)
           details = schedule_name +"  "+str(schedule_step)+" "+tst
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"load schedule data","details":details,"level":"RED"})


   def queue_step_data(self,step_data,schedule_name,schedule_step,schedule_step_time,eto_flag = True):
       schedule_io = step_data[0]
       schedule_step = int(schedule_step)
       schedule_step_time = int(schedule_step_time)
      
       if ( self.irrigation_hash_control.hget("ETO_MANAGEMENT") == True ) and (eto_flag == True): 
          schedule_step_time,eto_flag,eto_list = self.eto_management.determine_eto_management(schedule_step_time, schedule_io )
       else:
          eto_flag = False
          eto_list = None 
          
       if schedule_step_time > 0:          
          json_object = {}
          json_object["type"]            = "IRRIGATION_STEP"
          json_object["schedule_name"]   =  schedule_name
          json_object["step"]            =  int(schedule_step)
          json_object["io_setup"]        =  schedule_io
          json_object["run_time"]        =  int(schedule_step_time)
          json_object["elasped_time"]    =  0
          json_object["eto_enable"]      =  eto_flag
          json_object["eto_list"]        =  eto_list
          json_object["eto_flag"]        = eto_flag
         
          self.handlers["IRRIGATION_PENDING_CLIENT"].push(json_object)
       else:
           details = "Schedule "+ schedule_name +" step "+str(schedule_step)+" IRRIGATION_ETO_RESTRICTION"
           
           self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"IRRIGATION_ETO_RESTRICTION","details":details,"level":"YELLOW"})
       
       
   def get_schedule_data( self,link_data, schedule_name, schedule_step):
       
      schedule_step = int(schedule_step)
      io_control = link_data[schedule_step -1] 
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
  
 
   def get_json_data( self, schedule_name ):
      
       sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")
       
       for j in sprinkler_ctrl :  
           if j["name"] == schedule_name:
               json_data=self.app_files.load_file(j["link"]) 
               if isinstance(json_data, str):
                     object_data = json.loads(json_data)
               
               return json_data    
       return None
      
       


     




class Process_External_Commands(object):
   def __init__(self,cf, cluster_control, handlers,app_files,sys_files,eto_management,irrigation_io,
                  irrigation_hash_control,generate_control_events,equipment_current_limit ,current_operations,failure_report ):
       self.cf = cf
       self.handlers = handlers
       self.app_files = app_files
       self.sys_files = sys_files
       
       
       self.generate_control_events = generate_control_events
       self.eto_management = eto_management 
       self.irrigation_io = irrigation_io
       self.irrigation_hash_control = irrigation_hash_control
       self.equipment_current_limit = equipment_current_limit
       self.current_operations = current_operations
       self.failure_report = failure_report       
       self.irrigation_sched = Irrigation_Scheduling(handlers,app_files,sys_files,eto_management,irrigation_hash_control)

       self.clear_redis_sprinkler_data()              
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
                  if isinstance(object_data, str):
                     object_data = json.loads(object_data)
                 
                  print("command",object_data["command"])
                  self.commands[object_data["command"]]( object_data )

              
           except Exception as tst:
               print("IRRIGATION_CONTROLLER_EXCEPTION "+str(tst))
               self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"IRRIGATION_CONTROLLER_EXCEPTION","details":[str(tst),object_data["command"]],"level":"RED"})
               
               
      

   def add_chains( self, cf ):
       self.turn_on_equipment_relay()
       cf.define_chain( "sprinkler_command_queue", True ) 
       #cf.insert.log("sprinkler_command_queue")
       cf.insert.wait_event_count(count = 1 ) # wait 1 seconds
       cf.insert.one_step(  self.dispatch_sprinkler_mode  ) 
       cf.insert.one_step( self.update_time_stamp)       
       cf.insert.reset()

       cf.define_chain("check_equipment_current",True)
       cf.insert.wait_event_count(count = 15 ) # wait 15 seconds 
       cf.insert.one_step(self.check_equipment_relay)
       cf.insert.one_step(self.check_equipment_current)
       cf.insert.reset()       



      
   def update_time_stamp(self,*args):
       self.irrigation_hash_control.hset( "TIME_STAMP",time.time())

   def suspend( self, *args ):
       
       self.irrigation_hash_control.hset("SUSPEND",True)
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"SUSPEND_OPERATION","level":"YELLOW"})
       self.cf.send_event("IRI_MASTER_VALVE_SUSPEND",None)
      

   def resume( self, *args ):
       self.irrigation_hash_control.hset("SUSPEND",False)
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"RESUME_OPERATION","level":"YELLOW"})
       self.cf.send_event("IRI_MASTER_VALVE_RESUME",None)
      


   def skip_station( self, *args ):
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"SKIP_OPERATION","level":"YELLOW"})
       self.cf.send_event("RELEASE_IRRIGATION_CONTROL",None)
           


   def resistance_check( self, object_data ):
        json_object = {}
        json_object["type"]   = "RESISTANCE_CHECK"
        json_object["schedule_name"] ="RESISTANCE_CHECK"
        json_object["step"] = 1
        json_object["run_time"] = 0
        self.handlers["IRRIGATION_PENDING_CLIENT"].push(json_object)
        
             


   def check_off( self,object_data ):
        json_object = {}
        json_object["type"]            = "CHECK_OFF"
        json_object["schedule_name"] ="CHECK_OFF"
        json_object["step"] = 1
        json_object["run_time"] = 0
        self.handlers["IRRIGATION_PENDING_CLIENT"].push(json_object)
       

   def clean_filter( self, object_data ):
        json_object = {}
        json_object["type"]  = "CLEAN_FILTER"
        json_object["schedule_name"] ="CLEAN_FILTER"
        json_object["step"] = 1
        json_object["run_time"] = 0
        self.handlers["IRRIGATION_PENDING_CLIENT"].push(json_object)       

  
 
   def clear( self, object_data ):
       self.clear_redis_sprinkler_data()
       self.handlers["IRRIGATION_CURRENT_CLIENT"].delete_all()
       self.handlers["IRRIGATION_PENDING_SERVER"].delete_all()
       self.cf.send_event("RELEASE_IRRIGATION_CONTROL",None)
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"CLEAR","level":"YELLOW"})         

   def clear_redis_sprinkler_data(self):
      self.irrigation_hash_control.hset("SCHEDULE_NAME","OFFLINE")  
      self.irrigation_hash_control.hset("STEP",0)  
      self.irrigation_hash_control.hset("RUN_TIME",0)  
      self.irrigation_hash_control.hset("ELASPED_TIME",0)  
      self.irrigation_hash_control.hset("TIME_STAMP",time.time())
      
 

   def open_master_valve( self, object_data ):
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"OPEN_MASTER_VALVE","level":"YELLOW"})
       self.generate_control_events.change_to_timed_state()

     
  
   def close_master_valve( self, object_data ):
       self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"CLOSE_MASTER_VALVE","level":"YELLOW"})
       self.generate_control_events.cancel_timed_state()
      
    
 


   def  reset_system_now( self, *args ):
      self.handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"REBOOT_NOW","level":"RED"})
    
      time.sleep(5)
      os.system("reboot")  

   def reset_system_queue( self,  *args ):
        json_object = {}
        json_object["type"]  = "RESET_SYSTEM_QUEUE"
        json_object["schedule_name"] ="RESET_QUEUE"
        json_object["step"] = 1
        json_object["run_time"] = 0
        self.handlers["IRRIGATION_PENDING_CLIENT"].push(json_object)       
      
     
   def turn_on_equipment_relay(self,*args):
       self.irrigation_io.turn_on_equipment_relay()
   
   def check_equipment_relay(self,*args):
       if self.irrigation_io.check_equipment_relay() != True:
          self.failure_report(self.current_operations,"EQUIPMENT_RELAY_TRIP",None,{"value":False})
          time.sleep(5)  # let entry settle in db
          raise
          os.system("reboot") 
   def check_equipment_current(self,*args):
       if self.irrigation_io.check_equipment_current() > self.equipment_current_limit:
          self.failure_report(self.current_operations,"EQUIPMENT_OVER_CURRENT",None,{"value":value,"limit":self.equipment_current_limit})
          time.sleep(5)  # let entry settle in db
          raise
          os.system("reboot") 
          

 
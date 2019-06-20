

if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json
    import datetime
    import os
    import copy
   
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
    from redis_support_py3.load_files_py3 import APP_FILES
    from redis_support_py3.load_files_py3 import SYS_FILES
    from   py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
    from   py_cf_new_py3.cluster_control_py3 import Cluster_Control
   
    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
                            
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGIGATION_SCHEDULING_CONTROL_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)
    package = package_sources[0]    
    data_structures = package["data_structures"]
    generate_handlers = Generate_Handlers(package,redis_site)
    redis_handle = generate_handlers.get_redis_handle()    
    app_files        =  APP_FILES(redis_handle,redis_site)     
    sys_files        =  SYS_FILES(redis_handle,redis_site)
    ds_handlers = {}
    ds_handlers["IRRIGATION_PAST_ACTIONS"] = generate_handlers.construct_redis_stream_writer(data_structures["IRRIGATION_PAST_ACTIONS"] )
    ds_handlers["IRRIGATION_CURRENT"] = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_CURRENT"] )
    ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"REBOOT","level":"RED"})
    remote_classes = None #construct_classes_py3.Construct_Access_Classes(io_server_ip,io_server_port)
    io_control  = None #  IO_Control(gm,remote_classes, redis_old_handle,redis_new_handle)
     
    cf = CF_Base_Interpreter()
    cluster_control = Cluster_Control(cf)   
    #
    # Instanciate Key Data Structures
    #
    #  Instanciate Sub modules
    #  
    #  Instanciate sub modules
    #     Incomming job queue
    #     Job Dispacther
    #     Job Workers
    #         
    
    try:
       raise
       cf.execute()
    except:
      #
      #Deleting current irrigation job to prevent circular reboots
      #
      ds_handlers["IRRIGATION_CURRENT"].delete_all()
      ds_handlers["IRRIGATION_PAST_ACTIONS"].push({"action":"IRRIGATION_CONTROLLER_EXCEPTION","level":"RED"})
      raise

'''

class SprinklerControl():
   def __init__(self, irrigation_control,alarm_queue,redis_handle,
                          cf,master_valve_ctrl,sprinkler_ctrl):
       self.irrigation_control                    = irrigation_control
       self.alarm_queue                           = alarm_queue
       self.redis_handle                          = redis_handle
       self.cf                                    = cf
       self.master_valve_ctrl                      = master_valve_ctrl
       self.sprinkler_ctrl                          = sprinkler_ctrl
       self.commands = {}
       self.commands["OFFLINE"]                   = self.clear # command to be removed
       self.commands["CLEAR"]                     = self.clear                   
       self.commands["QUEUE_SCHEDULE"]            = self.queue_schedule
       self.commands["QUEUE_SCHEDULE_STEP"]       = self.queue_schedule_step     
       self.commands["QUEUE_SCHEDULE_STEP_TIME"]  = self.queue_schedule_step_time
       self.commands["QUEUE_SCHEDULE_STEP_TIME_A"]  = self.queue_schedule_step_time_a
       self.commands["RESTART_PROGRAM"]           = self.restart_program  #ok          
       self.commands["NATIVE_SCHEDULE"]           = self.queue_schedule_step_time  ###command soon to be deleted    
       self.commands["DIRECT_VALVE_CONTROL"]      = self.direct_valve_control       
       self.commands["CLEAN_FILTER"]              = self.clean_filter    # ok            
       self.commands["OPEN_MASTER_VALVE"]         = self.open_master_valve   #ok        
       self.commands["CLOSE_MASTER_VALVE"]        = self.close_master_valve  #ok       
       self.commands["RESET_SYSTEM"]              = self.reset_system        #ok       
       self.commands["CHECK_OFF"]                 = self.check_off           #ok              
       self.commands["SUSPEND"]                   = self.suspend                    
       self.commands["RESUME"  ]                  = self.resume                      
       self.commands["SKIP_STATION"]              = self.skip_station     
       self.commands["RESISTANCE_CHECK"]          = self.resistance_check   #ok        
       self.app_files                             = load_files_py3.APP_FILES(redis_handle) 
       self.add_chains(cf)

   def dispatch_sprinkler_mode(self,chainFlowHandle, chainObj, parameters,event):


           try: 
               length = self.redis_handle.llen( "QUEUES:SPRINKLER:CTRL")
               #print("--length",length)
               if length > 0:
                  data = self.redis_handle.rpop("QUEUES:SPRINKLER:CTRL") 
                  data = base64.b64decode(data)
                  object_data = json.loads(data.decode())
 
                 
                  if object_data["command"] in self.commands :
                       self.commands[object_data["command"]]( object_data,chainFlowHandle, chainObj, parameters,event )
                  else:
                      self.alarm_queue.store_past_action_queue("Bad_Irrigation_Command","RED",object_data["command"]  )
                      raise
           except:
               print( "exception in dispatch mode") # issue log message
               raise
      


   def suspend( self, *args ):
       self.alarm_queue.store_past_action_queue("SUSPEND_OPERATION","YELLOW"  )
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.sprinkler_ctrl.suspend_operation()
       self.cf.send_event("IRI_MASTER_VALVE_SUSPEND",None)
       self.redis_handle.hset("CONTROL_VARIABLES","SUSPEND","ON")

   def resume( self, *args ):
       self.alarm_queue.store_past_action_queue("RESUME_OPERATION","YELLOW"  )
       self.sprinkler_ctrl.resume_operation()
       self.cf.send_event("IRI_MASTER_VALVE_RESUME",None)

       self.alarm_queue.store_past_action_queue("RESUME_OPERATION","GREEN"  )
       self.redis_handle.hset("CONTROL_VARIABLES","SUSPEND","OFF")

   def skip_station( self, *args ):
       self.alarm_queue.store_past_action_queue("SKIP_STATION","YELLOW"  )
       self.sprinkler_ctrl.skip_operation()

   def resistance_check( self, object_data, chainFlowHandle, chainObj, parameters, event ):
        json_object = {}
        json_object["type"]   = "RESISTANCE_CHECK"
        json_string = json.dumps( json_object)
        self.redis_handle.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string )
             


   def check_off( self,object_data,chainFlowHandle, chainObj, parameters,event ):
        json_object = {}
        json_object["type"]            = "CHECK_OFF"
        json_string = json.dumps( json_object)
        
        self.redis_handle.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string )
        #alarm_queue.store_past_action_queue( "CHECK_OFF", "GREEN",  { "action":"start" } )        

   def clean_filter( self, object_data,chainFlowHandle, chainObj, parameters,event ):
        json_object = {}
        json_object["type"]  = "CLEAN_FILTER"
        json_string = json.dumps( json_object)
        self.redis_handle.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string )
        #alarm_queue.store_past_action_queue( "CLEAN_FILTER", "GREEN",  { "action":"start" } )        

  
 
   def clear( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.clear_redis_sprinkler_data()
       self.clear_redis_irrigate_queue()
       self.sprinkler_ctrl.skip_operation() 
       alarm_queue.store_past_action_queue( "CLEAR", "YELLOW"  )          


         
   def queue_schedule( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       
       self.schedule_name =  object_data["schedule_name"]
       self.load_auto_schedule(self.schedule_name)
       #self.redis_handle.hset("CONTROL_VARIABLES","SUSPEND","OFF")  
       self.redis_handle.hset("CONTROL_VARIABLES","SKIP_STATION","OFF") 
    
    
   
   def queue_schedule_step( self,  object_data,chainFlowHandle, chainObj, parameters,event ):
       
       self.schedule_name =  object_data["schedule_name"]
       self.schedule_step =  object_data["step"]
       self.schedule_step =   int(self.schedule_step)
       self.load_step_data( self.schedule_name, self.schedule_step ,None,True ) 
       self.redis_handle.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  

   def queue_schedule_step_time_a( self, object_data,chainFlowHandle, chainObj, parameters,event ):   
       self.schedule_name =  object_data["schedule_name"]
       self.schedule_step =  object_data["step"]
       self.schedule_step =   int(self.schedule_step)
       self.schedule_step_time        =  object_data["run_time"]

       #self.alarm_queue.store_past_action_queue("QUEUE_SCHEDULE_STEP","GREEN",{ "schedule":self.schedule_name,"step":self.schedule_step } )      
       self.load_step_data( self.schedule_name, self.schedule_step ,self.schedule_step_time,True ) 
       self.redis_handle.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  

 
   def queue_schedule_step_time( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.schedule_name             = object_data["schedule_name"]
       self.schedule_step             =  object_data["step"]
       self.schedule_step_time        =  object_data["run_time"]
       self.schedule_step             = int(self.schedule_step)
       self.schedule_step_time        = int(self.schedule_step_time)  
       self.load_step_data( self.schedule_name, self.schedule_step, self.schedule_step_time,False ) 
       
    
     

   def direct_valve_control( self,  object_data,chainFlowHandle, chainObj, parameters,event ): 
       print("direct valve control")     
       remote                = object_data["controller"] 
       pin                   = object_data["pin"]         
       schedule_step_time    = object_data["run_time"]  
       data = {}
       data["remote"] =remote
       data["pin"]  = pin
       data["time"] = schedule_step_time
       alarm_queue.store_past_action_queue( "DIRECT", "YELLOW", data )        
       pin = int(pin)
       schedule_step_time = int(schedule_step_time)  
       self.load_native_data( remote,pin,schedule_step_time)
       
 
       


   def open_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("OPEN_MASTER_VALVE","YELLOW" )
      
       chainFlowHandle.send_event("IRI_OPEN_MASTER_VALVE",None)

     
  
   def close_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("CLOSE_MASTER_VALVE","GREEN"  )
       chainFlowHandle.send_event("IRI_CLOSE_MASTER_VALVE",None)
      
    
 


   def  reset_system( self, *args ):
      self.alarm_queue.store_past_action_queue("REBOOT","RED"  )
      self.redis_handle.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","RESET_SYSTEM")
      os.system("reboot")  


   def restart_program( self, *args ):
       self.alarm_queue.store_past_action_queue("RESTART","RED"  )
       self.redis_handle.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","RESTART_PROGRAM")
       quit()
       

   def clear_redis_irrigate_queue( self,*args ):
       #print "clearing irrigate queue"
       self.redis_handle.delete( "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       self.redis_handle.delete( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")


   def clear_redis_sprinkler_data(self):
       self.redis_handle.hset("CONTROL_VARIABLES", "sprinkler_ctrl_mode","OFFLINE")
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_name","offline" )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_step_number",0 )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_step",0 )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_time_count",0 )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_max",0 )


   def load_auto_schedule( self, schedule_name):
       schedule_control = self.get_json_data( schedule_name )
       step_number      = len( schedule_control["schedule"] )
       ###
       ### load schedule start
       ###
       ###
       #json_object = {}
       #json_object["type"]            = "START_SCHEDULE"
       #json_object["schedule_name"]   =  schedule_name
       #json_object["step_number"]     =  step_number
       #json_string = json.dumps( json_object)
       #self.redis_handle.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string )
       ###
       ### load step data
       ###
       ###
       for i in range(1,step_number+1):
           self.load_step_data( schedule_name, i ,None,True )
       ###
       ### load schedule end
       ###
       ###
       #json_object = {}
       #json_object["type"]            = "END_SCHEDULE"
       #json_object["schedule_name"]   =  schedule_name
       #json_object["step_number"]     =  step_number
       #json_string = json.dumps( json_object)
       #self.redis_handle.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string  )
     
  





   # note schedule_step_time can be None then use what is in the schedule
   def load_step_data( self, schedule_name, schedule_step,  schedule_step_time ,eto_flag ):
       #print "load step data schedule name ----------------->",schedule_name, schedule_step, schedule_step_time 
         
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
           json_string = json.dumps( json_object)
           #print "load step data ===== step data is queued"
           self.redis_handle.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string )
          
       else:
           self.store_event_queue( "non_existant_schedule", json_object )
           raise  # non schedule



   # this is for loading user specified data
   def load_native_data( self, remote,bit,time ):
       print("load native_data")
       json_object = {}
       json_object["type"]            =  "IRRIGATION_STEP"
       json_object["schedule_name"]   =  remote
       json_object["step"]            =  bit
       json_object["io_setup"]        =  [{ "remote":remote, "bits":[bit] }]
       json_object["run_time"]        =  time
       json_object["elasped_time"]    =  0
       json_object["eto_enable"]      =  False
       json_string = json.dumps( json_object)    
       self.redis_handle.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string)


   def get_schedule_data( self, schedule_name, schedule_step):
       schedule_control = self.get_json_data( schedule_name )

       if schedule_control != None:
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
       #print("get json data ",schedule_name)
       sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")
    
       for j in sprinkler_ctrl :  
           if j["name"] == schedule_name:
               json_data=open("app_data_files/"+j["link"]) 
               json_data = json.load(json_data)
               #print "json data",json_data
               return json_data    
       return None
      
   def add_chains( self, cf ):
   
       cf.define_chain( "sprinkler_command_queue", True ) 
       #cf.insert.log("sprinkler_command_queue")
       cf.insert.wait_event_count(count = 1 ) # wait 1 seconds
       cf.insert.one_step(  self.dispatch_sprinkler_mode  ) 
       cf.insert.reset()
  



if __name__ == "__main__":
   import time
   import redis
   import load_files_py3
   import base64
   import json


   from redis_graph_py3.farm_template_py3 import Graph_Management 
   from irrigation_control_py3.misc_support_py3 import IO_Control
   from irrigation_control_py3.master_valve_control_py3 import Master_Valve
   from irrigation_control_py3.irrigation_queue_processing_py3 import Irrigation_Queue_Management

   from   io_control_py3 import construct_classes_py3
   from   io_control_py3 import new_instrument_py3
   from   irrigation_control_py3.alarm_queue_py3 import AlarmQueue
   from   py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
   from   py_cf_new_py3.cluster_control_py3 import Cluster_Control
   



   gm =Graph_Management("PI_1","main_remote","LaCima_DataStore")

   data_store_nodes = gm.find_data_stores()
   io_server_nodes  = gm.find_io_servers()
  
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   
   redis_new_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 12, decode_responses=True)
   redis_old_handle  = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 0, decode_responses=True)


   

   app_files        =  load_files_py3.APP_FILES(redis_old_handle)     
   sys_files        =  load_files_py3.SYS_FILES(redis_old_handle)

   
   io_server_ip     = io_server_nodes[0]["ip"]
   io_server_port   = io_server_nodes[0]["port"]

   remote_classes = construct_classes_py3.Construct_Access_Classes(io_server_ip,io_server_port)
   io_control  = IO_Control(gm,remote_classes, redis_old_handle,redis_new_handle)
   alarm_queue = AlarmQueue(redis_old_handle)
   alarm_queue.store_past_action_queue("REBOOT", "RED" )
   cf = CF_Base_Interpreter()
   cluster_control = Cluster_Control(cf)



   master_valve = Master_Valve( "MASTER_VALVE",cf, cluster_control, io_control, redis_old_handle )
   irrigation_queue_management =  Irrigation_Queue_Management( "IRRIGATION_CONTROL", cf, cluster_control, 
                                  io_control, redis_old_handle, redis_new_handle, gm,
                                  alarm_queue, app_files, sys_files )
                                    
   sprinkler_control = SprinklerControl(io_control, alarm_queue, 
                           redis_old_handle,cf,master_valve,irrigation_queue_management )

   try:
       cf.execute()
   except:
      #
      #Deleting current irrigation job to prevent circular reboots
      #
      redis_old_handle.delete("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")  
      raise
'''
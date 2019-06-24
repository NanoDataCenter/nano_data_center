import datetime
import time
import string
import urllib2
import math
import redis

import json
import eto
import py_cf
import os
import base64
import load_files
import watch_dog
  

class SprinklerQueueElementControl( ):
   def __init__(self,redis,io_control,alarm_queue,counter_devices):
       self.redis            = redis
       self.alarm_queue      = alarm_queue
       self.io_control       = io_control
       self.counter_devices  = counter_devices
       self.app_files        =  load_files.APP_FILES(redis)

       self.redis.hset("CONTROL_VARIBALES","MAX_FLOW_TIME",0)

   def check_for_excessive_flow_rate( self,*args ):
       flow_value  =  float( check_redis_value( "global_flow_sensor_corrected" ) )
       max_flow    =  float( check_redis_value( "FLOW_CUT_OFF"))
       if max_flow  == 0:
           return   # feature is not turned on

       compact_data                             = self.redis.lindex( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE",0 )
       json_string                              = base64.b64decode(compact_data)
       json_object                             = json.loads(json_string)
       run_time                                = int( json_object["run_time"])
       elasped_time                            = int(json_object["elasped_time"])
       schedule_step                           = int(json_object["step"])
       step_number                             = json_object["step"]
       schedule_name                           = json_object["schedule_name"]

       
       if elasped_time < 3 :
           return # let flow stabilize 
       
       if flow_value > max_flow:
           over_load_time = int(self.redis.hget("CONTROL_VARIBALES","MAX_FLOW_TIME")) +1
           if over_load_time > 2:
              self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","ON")
              self.alarm_queue.store_past_action_queue("IRRIGATION:FLOW_ABORT","RED", { "schedule_name":json_object["schedule_name"],"step_number":json_object["step"],
                                   "flow_value":flow_value,"max_flow":max_flow } )
              self.redis.hset("CONTROL_VARIBALES","MAX_FLOW_TIME",0)
           else:
              self.redis.hset("CONTROL_VARIBALES","MAX_FLOW_TIME",over_load_time)
       else:
         self.redis.hset("CONTROL_VARIBALES","MAX_FLOW_TIME",0)

   def check_redis_value( self,key):
       value =  redis.hget( "CONTROL_VARIABLES",key )
       if value == None:
           value = 0
       return value


   def check_current(self,*args):
       compact_data                             = self.redis.lindex( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE",0 ) 
       
       json_string = base64.b64decode(compact_data)

       #print "json_string",json_string

       json_object                             = json.loads(json_string)
       temp = float( self.redis.hget( "CONTROL_VARIABLES","coil_current" ))
       print "check_current temp",temp
       if temp > 24:
           self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","ON")
           self.clean_up_irrigation_cell( json_object )
           self.alarm_queue.store_past_action_queue("IRRIGATION:CURRENT_ABORT","RED", { "schedule_name":json_object["schedule_name"],"step_number":json_object["step"] } )
           return "RESET"
       else:
           return "DISABLE"


   def start(self, *args ):
       #print "start ------------------------------------------------->"
       self.redis.hset("CONTROL_VARIBALES","MAX_FLOW_TIME",0)
       compact_data                             = self.redis.lindex( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE",0 )
       json_string = base64.b64decode(compact_data)
       json_object                             = json.loads(json_string)

       if  self.check_redis_value("SUSPEND") == "ON":
           #self.log_start_step( schedule_name, json_object["step"])
           #self.io_control.turn_off_io(json_object["io_setup"])
           #self.io_control.disable_all_sprinklers()
           return #  System is not processing commands right now

       #print "start --- #1" 
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")
       #print "made it here"
       
       run_time                                = int( json_object["run_time"])
       elasped_time                            = int(json_object["elasped_time"])
       schedule_step                           = int(json_object["step"])
       step_number                             = json_object["step"]
       schedule_name                           = json_object["schedule_name"]
       #print "run_time",run_time
       if json_object["eto_enable"] == True:
            run_time  = self.eto_update( run_time , json_object["io_setup"] )
       #print "start ---#2  runtime",run_time
    
       
       if  run_time  == 0:
           self.clean_up_irrigation_cell(json_object)
           json_object["run_time"] = 0
           self.alarm_queue.store_past_action_queue("IRRIGATION:START:ETO_RESTRICTION","YELLOW", json_object  ) 
           return "RESET"

       self.io_control.load_duration_counters( run_time  )
       #print "made it here"
       self.io_control.turn_on_master_valves()
       self.io_control.turn_on_io(  json_object["io_setup"] )
       station_by_pass = 0       
       
       elasped_time = 1
       
       self.redis.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","AUTO")
       self.redis.hset( "CONTROL_VARIABLES","schedule_name", schedule_name )
       self.redis.hset( "CONTROL_VARIABLES","schedule_step_number", step_number )
       self.redis.hset( "CONTROL_VARIABLES","schedule_step", schedule_step )
       self.redis.hset( "CONTROL_VARIABLES","schedule_time_count", elasped_time )
       self.redis.hset( "CONTROL_VARIABLES","schedule_time_max",   run_time )  
       self.log_start_step( schedule_name, json_object["step"])
       #print "current_log",self.current_log_object  
       #print "flow_log",   self.flow_log_object         

       json_object["elasped_time"]       = elasped_time
       json_object["run_time"]           = run_time
       json_string                       = json.dumps( json_object )
       compact_data = base64.b64encode(json_string)
       #print "start #end json string ",json_string 
       self.redis.lset( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", 0, compact_data )
       return "DISABLE"

   def monitor( self, *args ):
     
       #print "monitor  --------------->"
       # check to see if something is in the queue
       length =   self.redis.llen( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" )
       #print "length",length
       if length == 0 :
           return "CONTINUE"
       compact_data                             = self.redis.lindex( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE",0 )
       json_string                              = base64.b64decode(compact_data)
       json_object                             = json.loads(json_string)
       run_time                                = int( json_object["run_time"])
       elasped_time                            = int(json_object["elasped_time"])
       schedule_step                           = int(json_object["step"])
       step_number                             = json_object["step"]
       schedule_name                           = json_object["schedule_name"]
       if  (self.check_redis_value("SUSPEND") == "ON") :
           #self.io_control.turn_off_io(json_object["io_setup"])
           #self.io_control.disable_all_sprinklers()
           return  "HALT" #  System is not processing commands right now

       elasped_time  = elasped_time +1
       self.log_sensors( schedule_name, schedule_step)
       if json_object["eto_enable"] == True:
            self.update_eto_queue_a( 1, json_object["io_setup"] )
       if (elasped_time <= run_time ) and ( self.check_redis_value("SKIP_STATION") != "ON" ):
           
           self.io_control.turn_on_io( json_object["io_setup"] )
           self.io_control.turn_on_master_valves()
          
           self.redis.hset( "CONTROL_VARIABLES","schedule_time_count", elasped_time )
           json_object["elasped_time"] = elasped_time
           json_string                       = json.dumps( json_object )
           compact_data = base64.b64encode(json_string)
           self.redis.lset( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", 0, compact_data )
           return_value = "RESET"
       else:
           #print "normal end"    
           self.log_step_stop()
           self.clean_up_irrigation_cell(json_object)
           return_value = "DISABLE"
       #print "cell returnValue is ",return_value
       return return_value

   def clean_up_irrigation_cell( self ,json_object ):
       #print "made it to cleanup"
       self.redis.delete("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")
       self.redis.hset("CONTROL_VARIABLES", "schedule_name","offline" )
       self.redis.hset("CONTROL_VARIABLES", "schedule_step_number",0 )
       self.redis.hset("CONTROL_VARIABLES", "schedule_step",0 )
       self.redis.hset("CONTROL_VARIABLES", "schedule_time_count",0 )
       self.redis.hset( "CONTROL_VARIABLES","schedule_time_max",0 ) 
       self.redis.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","AUTO")
       self.redis.hset( "CONTROL_VARIABLES","SKIP_STATION","OFF")
       self.io_control.turn_off_io(json_object["io_setup"])
       self.io_control.disable_all_sprinklers()
       self.io_control.clear_duration_counters()
       self.io_control.turn_off_master_valves()
       

   def log_sensors(self,  schedule_name,step):
       if hasattr(self, 'current_log_object') == False:
           self.current_log_object      = self.initialize_object( "current_log",schedule_name,step)
       if hasattr(self, 'flow_log_object') == False:
             self.flow_log_object         = self.initialize_object( "flow_log",schedule_name,step )

       coil_current = float( self.redis.hget( "CONTROL_VARIABLES","coil_current" ))
       self.log_coil_current ( coil_current )
       for i in self.counter_devices.keys():
        
           sensor_name = i
           flow_value = self.redis.lindex("QUEUES:SPRINKLER:FLOW:"+str(i),0)
           self.log_flow_rate( sensor_name, flow_value )
      
  
    

           
      

   def log_flow_rate( self, sensor_name, flow_value ):
    
       if self.flow_log_object["fields"].has_key( sensor_name ) == False: 
           self.initialize_field( self.flow_log_object, sensor_name ) 
       temp = self.flow_log_object["fields"][ sensor_name ]
       temp["count"] = temp["count"]+1
       temp["data"].append( flow_value)
       if flow_value > temp["max"] :
          temp["max"] = flow_value
       if flow_value < temp["min"] : 
          temp["min"] = flow_value  

   def log_coil_current ( self,coil_current ):
       if self.current_log_object["fields"].has_key( "coil_current" ) == False: 
          self.initialize_field( self.current_log_object, "coil_current") 
       temp = self.current_log_object["fields"]["coil_current"]
       temp["count"] = temp["count"]+1
       temp["data"].append( coil_current ) 
       if coil_current > temp["max"] :
           temp["max"] = coil_current
       if coil_current < temp["min"] :
          temp["min"] = coil_current
  



   def log_start_step( self, schedule_name, step):
       #print "made it log start step"
       self.current_log_object      = self.initialize_object( "current_log",schedule_name,step)
       self.flow_log_object         = self.initialize_object( "flow_log",schedule_name,step )
       self.alarm_queue.store_event_queue( "start_step", { "schedule":schedule_name, "step":step } )
       

   def log_step_stop( self ):
       if hasattr(self, 'flow_log_object')  == False:
           return  # case when eto abort

       obj = self.flow_log_object
       
       self.alarm_queue.store_past_action_queue("IRRIGATION:END","GREEN", { "schedule_name":obj["schedule_name"],"step_name":obj["step"] } )
       self.store_object( self.current_log_object,   "coil"    )
       self.store_object( self.flow_log_object,      "flow"    )
       obj                        = {}
       obj["coil"]                = self.current_log_object
       obj["flow"]                = self.flow_log_object
       self.alarm_queue.store_event_queue( "irrigatation_store_object", obj )
       self.current_log_object    = None
       self.flow_log_object       = None


   def store_object( self, obj ,queue_type ):
       if obj == None:
           return
       #self.add_limits(obj, queue_type )
       self.compute_object_statistics( obj )
       queue = "log_data:"+queue_type+":"+obj["schedule_name"]+":"+str(obj["step"])
       json_string = json.dumps(obj)
       compact_data = base64.b64encode(json_string)
       self.redis.lpush( queue, json_string )
       self.redis.ltrim( queue,0,100)

   def initialize_object( self, name,schedule_name,step ):
       obj                 = {}
       obj["name"]         = name
       obj["time"]         = time.time()
       obj["schedule_name"] = schedule_name
       obj["step"]          = step
       obj["fields"]        = {}
       return obj

 


   def initialize_field( self, obj ,field):
       if obj["fields"].has_key(field) == False:
           obj["fields"][field]            = {}
           obj["fields"][field]["max"]     = -1000000
           obj["fields"][field]["min"]     =  1000000
           obj["fields"][field]["count"]   = 0
           obj["fields"][field]["data"]    = []
   

   def compute_object_statistics( self, obj ):
       #print "compute object statistics", obj
       for j in obj["fields"] :
           temp = obj["fields"][j]
           temp["total"] = 0
           count = 0
           
           for  m in temp["data"]:
               m = float(m)
               count = count +1
               if count > 5: 
                   temp["total"] = temp["total"] + m
           #print "count ",count
           if count > 5:
               temp["average"] = temp["total"]/(count -5)
           else:
               temp["average"] = 0
           temp["std"] = 0
           count = 0
           for m in temp["data"]:
               m =  float(m)
               count = count +1
           if count > 5 :
             temp["std"] = temp["std"] + (m -temp["average"])*(m-temp["average"])
             temp["std"] = math.sqrt(temp["std"]/(count-5))
           else:
             temp["std"] = 0

## 1 gallon is 0.133681 ft3
## assuming a 5 foot radius
## a 12 gallon/hour head 0.2450996343 inch/hour
## a 14	gallon/hour head 0.2859495733 inch/hour
## a 16	gallon/hour head 0.3267995123 inch/hour
##
##
##
##
## capacity of soil
## for silt 2 feet recharge rate 30 % recharge inches -- .13 * 24 *.3 = .936 inch 
## for sand 1 feet recharge rate 30 % recharge inches -- .06 * 12 *.3 = .216 inch
##
## recharge rate for is as follows for 12 gallon/hour head:
## sand 1 feet .216/.245 which is 52 minutes
## silt 2 feet recharge rate is 3.820 hours or 229 minutes
##
## {"controller":"satellite_1", "pin": 9,  "recharge_eto": 0.216, "recharge_rate":0.245 },
## eto_site_data






   def eto_update( self, schedule_run_time, io_list ):
       self.eto_site_data = self.app_files.load_file( "eto_site_setup.json" )
       manage_eto = self.redis.hget( "CONTROL_VARIABLES","ETO_MANAGE_FLAG" )
       if manage_eto == None:
           manage_eto = 1
           self.redis.hset("CONTROL_VARIABLES", "ETO_MANAGE_FLAG",manage_eto)
       manage_eto = int( manage_eto )   
       if manage_eto == 1:
           sensor_list = self.find_queue_names( io_list )
           if len(sensor_list) != 0:
               run_time = self.find_largest_runtime( schedule_run_time, sensor_list )
               if run_time < schedule_run_time :
                   schedule_run_time = run_time 
       return schedule_run_time

   def find_queue_names( self, io_list ):
       eto_values = []
       for j in io_list:
           controller = j["remote"]
           bits       = j["bits"]
           bit        = bits[0] 
           index = 0
           for m in self.eto_site_data:
               if (m["controller"] == controller) and (m["pin"] == bit): 
                   queue_name = controller+"|"+str(bit)
                   data = self.redis.hget( "ETO_RESOURCE", queue_name )
                   eto_values.append( [index, data, queue_name ] )
               index = index +1
       #print "eto values ",eto_values
       return eto_values


   def find_largest_runtime( self, run_time, sensor_list ):
       runtime = 0
       for j in sensor_list:
           index = j[0]
           deficient = float(j[1])
           eto_temp = self.eto_site_data[index]
           recharge_eto = float( eto_temp["recharge_eto"] )
           recharge_rate = float(eto_temp["recharge_rate"])
           if float(deficient) > recharge_eto :
               runtime_temp = (deficient  /recharge_rate)*60
               if runtime_temp > runtime :
                   runtime = runtime_temp
       #print "run time",runtime
       return runtime


   def update_eto_queue_a( self, run_time, io_list ):
       self.eto_site_data = self.app_files.load_file( "eto_site_setup.json" )
       manage_eto = self.redis.hget( "CONTROL_VARIABLES","ETO_MANAGE_FLAG" )
       if manage_eto == None:
           manage_eto = 1
           self.redis.hset( "CONTROL_VARIABLES","ETO_MANAGE_FLAG",manage_eto)
       manage_eto = int( manage_eto )   
       if manage_eto == 1:
           sensor_list = self.find_queue_names( io_list )
           if len(sensor_list) != 0:
               self.update_eto_queue(run_time,sensor_list)

   def update_eto_queue( self, run_time, sensor_list ):
       for l in  sensor_list:
           j_index = l[0]
           queue_name = l[2]
           j = self.eto_site_data[ j_index ]
           deficient = self.redis.hget("ETO_RESOURCE",  queue_name )
           if deficient == None:
               deficient = 0
           else:
               deficient = float(deficient)
           recharge_rate = float(j["recharge_rate"])
           deficient = deficient - (recharge_rate/60)*run_time 
           if deficient < 0 :
               deficient = 0 
           self.redis.hset( "ETO_RESOURCE", queue_name, deficient )

     




class SprinklerQueueControl():
   def __init__(self,alarm_queue,redis):
       self.alarm_queue = alarm_queue
       self.redis       = redis

   #
   # This function takes data from the IRRIGATION QUEUE And Transferrs it to the IRRIGATION_CELL_QUEUE
   # IRRIGATION_CELL_QUEUE only has one element in it
   #
   def load_irrigation_cell(self,chainFlowHandle, chainObj, parameters,event ): 
       #print "load irrigation cell ######################################################################"
       ## if queue is empty the return
       ## this is for resuming an operation
       length =   self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" )
       #print "made it here  cell ", length
       if length > 0:
           return "RESET" 

       length = self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE")
       #print "length  queue  ",length
       if length == 0:
           return "RESET"
       if self.redis.hget("CONTROL_VARIABLES","SUSPEND") == "ON":
           return "RESET"

 

       compact_data = self.redis.rpop(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       json_string = base64.b64decode(compact_data)
       json_object = json.loads(json_string)

      
       
       if json_object["type"] == "RESISTANCE_CHECK":
           chainFlowHandle.enable_chain_base( ["resistance_check"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"
       
       
       if json_object["type"] == "CHECK_OFF":
           chainFlowHandle.enable_chain_base( ["check_off_chain"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"

       if json_object["type"] == "CLEAN_FILTER":
           chainFlowHandle.enable_chain_base( ["clean_filter_action_chain"])
           self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           return "RESET"
 
       if json_object["type"] == "IRRIGATION_STEP":
           #print "irrigation step"
           self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", compact_data )
       '''    
       if json_object["type"] == "START_SCHEDULE" :
           self.redis.set( "schedule_step_number", json_object["step_number"] ) 
           self.store_event_queue( "irrigation_schedule_start", json_object )
  
       if json_object["type"] == "END_SCHEDULE" :
           self.store_event_queue( "irrigation_schedule_stop", json_object )
       '''
       #print "load irrigation cell   CONTINUE"
       return "DISABLE"





class SprinklerControl():
   def __init__(self, irrigation_control,alarm_queue,redis):
       self.irrigation_control                    = irrigation_control
       self.alarm_queue                           = alarm_queue
       self.redis                                 = redis
       self.commands = {}
       self.commands["OFFLINE"]                   = self.go_offline          
       self.commands["QUEUE_SCHEDULE"]            = self.queue_schedule
       self.commands["QUEUE_SCHEDULE_STEP"]       = self.queue_schedule_step     
       self.commands["QUEUE_SCHEDULE_STEP_TIME"]  = self.queue_schedule_step_time
       self.commands["RESTART_PROGRAM"]           = self.restart_program         #tested   
       self.commands["NATIVE_SCHEDULE"]          = self.queue_schedule_step_time      
       self.commands["NATIVE_SPRINKLER"]          = self.direct_valve_control       
       self.commands["CLEAN_FILTER"]              = self.clean_filter            #tested    
       self.commands["OPEN_MASTER_VALVE"]         = self.open_master_valve       #tested     
       self.commands["CLOSE_MASTER_VALVE"]        = self.close_master_valve      #tested    
       self.commands["RESET_SYSTEM"]              = self.reset_system            #tested    
       self.commands["CHECK_OFF"]                 = self.check_off               #tested          
       self.commands["SUSPEND"]                   = self.suspend                 #tested   
       self.commands["RESUME"  ]                  = self.resume                  #tested    
       self.commands["SKIP_STATION"]              = self.skip_station     
       self.commands["RESISTANCE_CHECK"]          = self.resistance_check           
       self.app_files                              =  load_files.APP_FILES(redis)

   def dispatch_sprinkler_mode(self,chainFlowHandle, chainObj, parameters,event):


           #try: 
               length = self.redis.llen( "QUEUES:SPRINKLER:CTRL")
               #print length
               if length > 0:
                  data = self.redis.rpop("QUEUES:SPRINKLER:CTRL") 
                  data = base64.b64decode(data)
                  object_data = json.loads(data )
                  #print object_data["command"]
                  print "object_data",object_data
                  if self.commands.has_key( object_data["command"] ) :
                       self.commands[object_data["command"]]( object_data,chainFlowHandle, chainObj, parameters,event )
                  else:
                      self.alarm_queue.store_past_action_queue("Bad Irrigation Command","RED",object_data  )
                      raise
           #except:
               #print "exception in dispatch mode"
               #quit()
      


   def suspend( self, *args ):
       self.alarm_queue.store_past_action_queue("SUSPEND_OPERATION","YELLOW"  )
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")

   def resume( self, *args ):
       self.alarm_queue.store_past_action_queue("RESUME_OPERATION","GREEN"  )
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")

   def skip_station( self, *args ):
       self.alarm_queue.store_past_action_queue("SKIP_STATION","YELLOW" ,{"skip: on"} )
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","ON" )


   def resistance_check( self, object_data, chainFlowHandle, chainObj, parameters, event ):
        json_object = {}
        json_object["type"]   = "RESISTANCE_CHECK"
        json_string = json.dumps( json_object)
        compact_data = base64.b64encode(json_string)
        self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
        alarm_queue.store_past_action_queue( "RESISTANCE_CHECK", "GREEN",  { "action":"start" } )        


   def check_off( self,object_data,chainFlowHandle, chainObj, parameters,event ):
        json_object = {}
        json_object["type"]            = "CHECK_OFF"
        json_string = json.dumps( json_object)
        compact_data = base64.b64encode(json_string)
        self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
        alarm_queue.store_past_action_queue( "CHECK_OFF", "GREEN",  { "action":"start" } )        

   def clean_filter( self, object_data,chainFlowHandle, chainObj, parameters,event ):
        json_object = {}
        json_object["type"]  = "CLEAN_FILTER"
        json_string = json.dumps( json_object)
        compact_data = base64.b64encode(json_string)
        self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
        alarm_queue.store_past_action_queue( "CLEAN_FILTER", "GREEN",  { "action":"start" } )        

  
 
   def go_offline( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("OFFLINE","RED"  )
       self.redis.hset("CONTROL_VARIABLES","sprinkler_ctrl_mode","OFFLINE")
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.clear_redis_sprinkler_data()
       self.clear_redis_irrigate_queue()
       self.redis.hset( "CONTROL_VARIABLES","schedule_name","OFFLINE")
       self.redis.hset( "CONTROL_VARIABLES","current_log_object",  None )
       self.redis.hset( "CONTROL_VARIABLES","flow_log_object", None )          ### not sure of
       self.redis.hset( "CONTROL_VARIABLES","SUSPEND","ON")
       chainFlowHandle.disable_chain_base( ["monitor_irrigation_job_queue","monitor_irrigation_cell"])
       chainFlowHandle.enable_chain_base( ["monitor_irrigation_job_queue"])
  
   def queue_schedule( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       
       self.schedule_name =  object_data["schedule_name"]
       self.load_auto_schedule(self.schedule_name)
       #self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")  
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF") 
       self.alarm_queue.store_past_action_queue("QUEUE_SCHEDULE","GREEN",{ "schedule":self.schedule_name } ) 
    
   
   def queue_schedule_step( self,  object_data,chainFlowHandle, chainObj, parameters,event ):
       
       self.schedule_name =  object_data["schedule_name"]
       self.schedule_step =  object_data["step"]
       self.schedule_step =   int(self.schedule_step)
       self.alarm_queue.store_past_action_queue("QUEUE_SCHEDULE_STEP","GREEN",{ "schedule":self.schedule_name,"step":self.schedule_step } )
       #print "queue_schedule",self.schedule_name,self.schedule_step
       self.load_step_data( self.schedule_name, self.schedule_step ,None,True ) 
       #self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  
    

 
   def queue_schedule_step_time( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.schedule_name              = object_data["schedule_name"]
       self.schedule_step        =  object_data["step"]
       self.schedule_step_time   =  object_data["run_time"]
       self.alarm_queue.store_past_action_queue("DIAGNOSTICS_SCHEDULE_STEP_TIME","YELLOW" , {"schedule_name":self.schedule_name, "schedule_step":self.schedule_step,"schedule_time":self.schedule_step_time})
       self.schedule_step             = int(self.schedule_step)
       self.schedule_step_time        = int(self.schedule_step_time)  
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.clear_redis_sprinkler_data()
       self.clear_redis_irrigate_queue()

 
       self.load_step_data( self.schedule_name, self.schedule_step, self.schedule_step_time,False ) 
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  
       
    
     

   def direct_valve_control( self,  object_data,chainFlowHandle, chainObj, parameters,event ):      
       remote                = object_data["controller"] 
       pin                   = object_data["pin"]         
       schedule_step_time    = object_data["run_time"]  
       
       pin = int(pin)
       schedule_step_time = int(schedule_step_time) 
       self.alarm_queue.store_past_action_queue("DIRECT_VALVE_CONTROL","YELLOW" ,{"remote":remote,"pin":pin,"time":schedule_step_time }) 
       #print "made it here",object_data
       self.irrigation_control.turn_off_master_valves()
       self.irrigation_control.disable_all_sprinklers()
       self.clear_redis_sprinkler_data()
       self.clear_redis_irrigate_queue()
       #print "direct_valve_control",remote,pin,schedule_step_time
       self.load_native_data( remote,pin,schedule_step_time)
       self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
       self.redis.hset("CONTROL_VARIABLES","SKIP_STATION","OFF")  
 
       


   def open_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("OPEN_MASTER_VALVE","YELLOW" )
       self.irrigation_control.turn_on_master_valves()
       chainFlowHandle.enable_chain_base([ "monitor_master_on_web"])

     
  
   def close_master_valve( self, object_data,chainFlowHandle, chainObj, parameters,event ):
       self.alarm_queue.store_past_action_queue("CLOSE_MASTER_VALVE","GREEN"  )
       chainFlowHandle.disable_chain_base( ["manual_master_valve_on_chain"])
       chainFlowHandle.disable_chain_base( ["monitor_master_on_web"])
       self.irrigation_control.turn_off_master_valves()
      
    
 


   def  reset_system( self, *args ):
      self.alarm_queue.store_past_action_queue("REBOOT","RED"  )
      self.redis.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","RESET_SYSTEM")
      os.system("reboot")  


   def restart_program( self, *args ):
       self.alarm_queue.store_past_action_queue("RESTART","RED"  )
       self.redis.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","RESTART_PROGRAM")
       quit()
       

   def clear_redis_irrigate_queue( self,*args ):
       #print "clearing irrigate queue"
       self.redis.delete( "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       self.redis.delete( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")


   def clear_redis_sprinkler_data(self):
       self.redis.hset("CONTROL_VARIABLES", "sprinkler_ctrl_mode","OFFLINE")
       self.redis.hset( "CONTROL_VARIABLES","schedule_name","offline" )
       self.redis.hset("CONTROL_VARIABLES", "schedule_step_number",0 )
       self.redis.hset("CONTROL_VARIABLES", "schedule_step",0 )
       self.redis.hset("CONTROL_VARIABLES", "schedule_time_count",0 )
       self.redis.hset( "CONTROL_VARIABLES","schedule_time_max",0 )


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
       #self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string )
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
       #self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", json_string  )
     
  





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
           compact_data = base64.b64encode(json_string)
           #print "load step data ===== step data is queued"
           self.redis.lpush(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data )
          
       else:
           self.store_event_queue( "non_existant_schedule", json_object )
           raise  # non schedule



   # this is for loading user specified data
   def load_native_data( self, remote,bit,time ):
       json_object = {}
       json_object["type"]            =  "IRRIGATION_STEP"
       json_object["schedule_name"]   =  "MANUAL"
       json_object["step"]            =  1
       json_object["io_setup"]        =  [{ "remote":remote, "bits":[bit] }]
       json_object["run_time"]        =  time
       json_object["elasped_time"]    =  0
       json_object["eto_enable"]      =  False
       json_string = json.dumps( json_object)    
       compact_data = base64.b64encode(json_string)
       #print "native load",json_string
       self.redis.lpush( "QUEUES:SPRINKLER:IRRIGATION_QUEUE", compact_data)
       #print self.redis.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE")


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
      



class Monitor():
  #
  # Measures current and flow rate every minute
  # Up
  #
   def __init__(self, redis, basic_io_control,counter_devices,analog_devices, gpio_bit_input_devices, alarm_queue, udp_servers ):
      self.redis                  = redis
      self.basic_io_control       = basic_io_control
      self.counter_devices        = counter_devices
      self.analog_devices         = analog_devices
      self.gpio_inputs            = gpio_bit_input_devices
      self.alarm_queue            = alarm_queue
      self.counter_time_ref       = time.time()

      self.udp_servers            = udp_servers

   def log_clean_filter( self,*args):
        self.redis.hset
        self.alarm_queue.store_past_action_queue("CLEAN_FILTER","GREEN"  )
        self.redis.hset("CONTROLLER_STATUS","clean_filter",time.time() )

   def set_suspend( self, *args):
      self.redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
   
   def set_resume( self,*args):
      
      self.redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")

   def verify_resume( self, *args):
       if  self.redis.hget("CONTROL_VARIABLES","SUSPEND") == "OFF":
          return "DISABLE"
       else:
          return "HALT"

   def clear_cleaning_sum(self, *args):
       redis.hset("CONTROL_VARIABLES","cleaning_sum",0)

        
   def check_to_clean_filter( self, chainFlowHandle, chainObj, parameters,event ):
       cleaning_interval = redis.hget("CONTROL_VARIABLES","CLEANING_INTERVAL")
       flow_value   =  float( check_redis_value( "global_flow_sensor_corrected" ) )
       cleaning_sum =  float( check_redis_value( "cleaning_sum") )
       cleaning_sum = cleaning_sum + flow_value
       redis.hset("CONTROL_VARIABLES","cleaning_sum",cleaning_sum)
       if cleaning_interval == 0 :
           return  # no cleaning interval active

       if cleaning_sum > cleaning_interval :
           chainFlowHandle.enable_chain_base(["clean_filter_action_chain"])
         
           
  
   def update_modbus_statistics( self, *args ):
       servers = []
       for i in self.udp_servers:
           temp = modbus_control.get_all_counters(i)
           if temp[0] == True:
               servers.append(i)   
               data = json.loads(temp[1])
              
               for j in data.keys():
                    if redis.hexists("MODBUS_STATISTICS:"+i,j) == False:
                       self.redis.hset("MODBUS_STATISTICS:"+i,j,json.dumps(data[j]))
                    else:
                       
                       temp_json = redis.hget("MODBUS_STATISTICS:"+i,j)
                       
                       temp_value = json.loads(temp_json)
                       
                       
                       temp_value["address"]  = j
                       temp_value["failures"] = int(temp_value["failures"]) +int(data[j]["failures"])
                       temp_value["counts"] = int(temp_value["counts"]) + int(data[j]["counts"])
                       temp_value["total_failures"] = int(temp_value["total_failures"]) +int(data[j]["total_failures"])
                       temp_json = json.dumps(temp_value)
                       self.redis.hset("MODBUS_STATISTICS:"+i,j,temp_json)
               modbus_control.clear_all_counters(i)
       self.redis.set("MODBUS_INTERFACES",json.dumps(servers))
     

      
   def clear_modbus_statistics( self,*args):
       interfaces_json = self.redis.get("MODBUS_INTERFACES")
       interfaces_value = json.loads(interfaces_json)
       for i in interfaces_value:
           self.redis.delete("MODBUS_STATISTICS:"+i) 


   def update_time_stamp( self, *args):
      self.alarm_queue.update_time_stamp()

   def measure_input_gpio( self, *args ):
       for i in self.gpio_inputs:
          self.basic_io_control.get_gpio_bit(i)  # need to store values


   def measure_flow_rate ( self, *args ):
    
     deltat = time.time()-self.counter_time_ref
     self.counter_time_ref = time.time()

     for i in counter_devices.keys():
        
        flow_value = self.basic_io_control.measure_counter(deltat,i)  
        self.redis.lpush("QUEUES:SPRINKLER:FLOW:"+str(i),flow_value )
        self.redis.ltrim("QUEUES:SPRINKLER:FLOW:"+str(i),0,800)

        if i == "main_sensor":
          self.redis.hset("CONTROL_VARIABLES","global_flow_sensor",flow_value )
          conversion_rate = counter_devices[i]["conversion_factor"]
          self.redis.hset("CONTROL_VARIABLES","global_flow_sensor_corrected",flow_value*conversion_rate )
    

   def measure_current( self, *args ):
       for i in  analog_devices.keys():
           current = self.basic_io_control.get_analog( i )
           self.redis.lpush( "QUEUES:SPRINKLER:CURRENT:"+i,current )
           self.redis.ltrim( "QUEUES:SPRINKLER:CURRENT:"+i,0,800)
           self.redis.hset( "CONTROL_VARIABLES",i, current )

   def measure_current_a( self, *args ):
       for i in  analog_devices.keys():
           current = self.basic_io_control.get_analog( i )
           self.redis.hset( "CONTROL_VARIABLES",i, current )

       

class PLC_WATCH_DOG():

   def __init__(self, redis, alarm_queue,watch_dog_interface ):
       self.redis                  = redis
       self.alarm_queue            = alarm_queue
       self.watch_dog_interface    = watch_dog_interface

   def read_wd_flag( self,*arg ):
       try:
          return_value = self.watch_dog_interface.read_wd_flag()
          #print "read_wd_flag",return_value
       except:
          pass
       return "DISABLE"
     

   def write_wd_flag( self,value,*arg ):
       try:
          self.watch_dog_interface.write_wd_flag(1)
       except:
           pass
       return "DISABLE"
      
   def read_mode_switch( self,value,*arg ):
 
       return_value = self.watch_dog_interface.read_mode_switch()
       #print "read_mode_switch",return_value
       return "DISABLE"

   def read_mode( self,value,*arg ):
       return_value = self.watch_dog_interface.read_mode()
       #print "read_mode_switch",return_value
       return "DISABLE"


if __name__ == "__main__":
   import datetime
   import time
   import string
   import urllib2
   import math
   import redis

   import json
   import eto
   import py_cf
   import os
   import base64
   import io_control_backup.alarm_queue
   import io_control_backup.modbus_UDP_device
   import io_control_backup.click
   import io_control_backup.basic_io_control
   import io_control_backup.irrigation_ctl
   import io_control_backup.new_instrument
   import watch_dog   

   

   #ir_ctl = Irrigation_Control("/media/mmc1/app_data_files","/media/mmc1/system_data_files")
   from data_management.configuration import *

   redis                     = redis.StrictRedis( host = '192.168.1.84', port=6379, db = 0 )
   app_files        =  load_files.APP_FILES(redis)     
   sys_files        =  load_files.SYS_FILES(redis)
   redis_dict  = {}
   redis_dict["GPIO_BITS"]    = "GPIO_BITS"
   redis_dict["GPIO_REGS"]    = "GPIO_REGS"
   redis_dict["GPIO_ADC"]     = "GPIO_ADC"
   redis_dict["COUNTER"]      = "COUNTER"
   redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
   redis.hincrby("CONTROLLER_STATUS", "irrigation_resets") 
   alarm_queue = io_control_backup.alarm_queue.AlarmQueue( redis,"cloud_alarm_queue" )
   io_server  =  io_control_backup.modbus_UDP_device.ModbusUDPDeviceClient(remote_devices , "192.168.1.84")
   plc_click   = io_control_backup.click.PLC_Click( alarm_queue, io_server, redis, redis_dict )

   modbus_control = io_control_backup.modbus_UDP_device.ModbusUDPDeviceClient( [], "192.168.1.84")
   

   plc_map = { "CLICK":plc_click }

   basic_io_control  = io_control_backup.basic_io_control.BasicIo( redis_dict = redis_dict, redis_server=redis,  plc_interface=plc_map , 
                                                            gpio_bit_input_devices=gpio_bit_input_devices, gpio_bit_output_devices= None, 
                                                            gpio_reg_input_devices=None, gpio_reg_output_devices= None,
                                                            analog_devices=analog_devices, counter_devices=counter_devices )

   irrigation_io_control     = io_control_backup.irrigation_ctl.IrrigationControl( irrigation_io, master_valve_list, plc_map, redis )
   plc_watch_dog_interface   = io_control_backup.irrigation_ctl.WatchDogControl( remote_devices, plc_map )
   plc_watch_dog             = PLC_WATCH_DOG( redis, alarm_queue,plc_watch_dog_interface )

   monitor           = Monitor(redis, basic_io_control, counter_devices, analog_devices, gpio_bit_input_devices,alarm_queue, ["192.168.1.84"] )
   monitor.update_modbus_statistics()

   wd_client         = watch_dog.Watch_Dog_Client(redis, "irrigation_ctrl","irrigation control")
   sprinkler_control = SprinklerControl(irrigation_io_control,alarm_queue,redis)
   sprinkler_element = SprinklerQueueElementControl(redis,irrigation_io_control,alarm_queue,counter_devices )
   sprinkler_queue   = SprinklerQueueControl( alarm_queue, redis )
   
   def check_redis_value( key):
       value =  redis.hget( "CONTROL_VARIABLES",key )
       if value == None:
           value = 0
  
       return value


         

    
   def clear_counters(*args):
       for i,j in remote_devices.items():
           ip = j["UDP"]
           io_server.clear_all_counters(ip)  


   def check_off ( *args ):
        temp = float(redis.hget( "CONTROL_VARIABLES","global_flow_sensor_corrected" ))
        redis.hset("CONTROLLER_STATUS", "check_off",temp )
        if temp   > 1.:
           redis.hset("ALARM","check_off",True)
           redis.hset("CONTROL_VARIABLES","SUSPEND","ON")
           alarm_queue.store_past_action_queue( "CHECK_OFF", "RED",  { "action":"bad","flow_rate":temp } )           
           return_value = "DISABLE"
        else:
           redis.hset("CONTROL_VARIABLES","SUSPEND","OFF")
           redis.hset("ALARMS","check_off",False)
           alarm_queue.store_past_action_queue( "CHECK_OFF", "GREEN",  { "action":"good","flow_rate":temp } )
           return_value = "DISABLE"
        return return_value


   def detect_on_switch_on( self,*args):
       
       for i in master_switch_keys:
           try:
              value = int(redis.hget("GPIO_BITS",i))
             
           except:
              value = 0 
           if value != 0:
               print "++++++++++",value
               return "DISABLE"
       return "RESET"



   def detect_off_switches(*args):
       #print "detect off", master_reset_keys
       for i in master_reset_keys:
           
           try:
              value = int(redis.hget("GPIO_BITS",i))
              
           except:
              value = 0 
           if value != 0:
               print "-------",value
               return True
       return False




   def clear_redis_set_keys( *args):
       for i in master_switch_keys:
           redis.hset("GPIO_BITS",i,0)

   def clear_redis_clear_keys( *args):
       for i in master_reset_keys:
           redis.hset("GPIO_BITS",i,0)


   def detect_switch_off(  chainFlowHandle, chainObj, parameters, event ):
       returnValue = "RESET"
       
       
       
       if detect_off_switches() == True:
             clear_redis_clear_keys()   
             returnValue = "DISABLE"
   
       return returnValue



   def check_for_uncompleted_sprinkler_element( chainFlowHandle,chainObj,parameters,event ):
       #alarm_queue.store_past_action_queue("START_UP","RED"  )
       length = redis.llen("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" )
       if length > 0:
         #print "enabling chain"
         chainFlowHandle.enable_chain_base( ["monitor_irrigation_cell"])
           



   def check_irrigation_queue( chainFlowHandle,chainObj,parameters,event ):
       #alarm_queue.store_past_action_queue("START_UP","RED"  )
       length = redis.llen("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" )
       if length > 0:
         print "Jobs in Queue"
         return "TERMINATE"
       else:
         return "DISABLE"

   def add_resistance_entry( remote_dictionary,  pin_dictionary, remote, pin ):
       if ( remote not in remote_dictionary ) or ( pin not in pin_dictionary ):
               remote_dictionary.union( remote)
               pin_dictionary.union(pin)
               json_object = [ remote,pin]
               json_string = json.dumps(json_object)
               print "json_string",json_string
               queue_object = base64.b64encode(json_string)
               redis.lpush(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE",queue_object )


   def update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary ):
       if dictionary.has_key( remote ) == False:
           dictionary[remote] = {}
       if dictionary[remote].has_key( pin ) == False:
           dictionary[remote][pin] = list(set())
       dictionary[remote][pin] = set( dictionary[remote][pin])
       dictionary[remote][pin].union(schedule) 
       dictionary[remote][pin] = list( dictionary[remote][pin])
       add_resistance_entry( remote_dictionary, pin_dictionary, remote, pin )



   def assemble_relevant_valves( *args):
       remote_dictionary = set()
       pin_dictionary    = set()
       dictionary        = {}
       
       print "assemble relevant valves"
       redis.delete(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" )
       sprinkler_ctrl = app_files.load_file("sprinkler_ctrl.json")

       for j in sprinkler_ctrl:
	  schedule = j["name"]
          json_data  =app_files.load_file(j["link"]) 
          for i in json_data["schedule"]:
             for k in i:
                remote = k[0]
                pin    = str(k[1][0])
                update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )

       master_valve = sys_files.load_file("master_valve_setup.json")

       for j in master_valve:
	  remote = j[0]
          pin    = str(j[1][0])
          update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )         
	  remote = j[2]
          pin    = str(j[3][0])
          update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )  
       json_string = json.dumps(dictionary)         
       queue_object = base64.b64encode(json_string)
       redis.set(  "SPRINKLER_RESISTANCE_DICTIONARY",queue_object)
               
            

   def test_individual_valves( chainFlowHandle,chainObj,parameters,event ):
   
       returnValue = "HALT"
      
       if event["name"] == "INIT" :
          parameters[1] = 0  # state variable

       else:
	 if event["name"] == "TIME_TICK":
           if parameters[1] == 0:
               if redis.llen(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" ) == 0:
                  returnValue = "DISABLE"
               else:
                  compact_data = redis.rpop(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" )
                  json_string = base64.b64decode(compact_data)
                  json_object = json.loads(json_string)
                  print "json object",json_object
                  irrigation_io_control.disable_all_sprinklers()
                  irrigation_io_control.load_duration_counters( 1  ) #  1 minute
                  irrigation_io_control.turn_on_valve(  [{"remote": json_object[0], "bits":[int(json_object[1])]}] ) #  {"remote":xxxx,"bits":[] } 
                  parameters[1] = 1
                  parameters[2] = json_object[0]
                  parameters[3] = json_object[1]
           else:
               monitor.measure_current()
               try:
                  coil_current = float( redis.hget( "CONTROL_VARIABLES","coil_current" ))
                  print "coil current",coil_current
                  queue = "log_data:resistance_log:"+parameters[2]+":"+parameters[3]
                  redis.lpush(queue, coil_current )  # necessary for web server
                  redis.ltrim(queue,0,10)
                  queue = "log_data:resistance_log_cloud:"+parameters[2]+":"+parameters[3]
                  redis.lpush(queue, json.dumps( { "current": coil_current, "time":time.time()} ))  #necessary for cloud
                  redis.ltrim(queue,0,10)

               except:
                   raise #should not happen
               irrigation_io_control.disable_all_sprinklers()
               parameters[1] = 0
 
       return returnValue

      
    
#
# Adding chains
#
   cf = py_cf.CF_Interpreter()

   cf.define_chain("reboot_message", True)  #tested
   cf.insert_link( "link_1",  "One_Step", [  clear_redis_set_keys ] )
   cf.insert_link( "link_2",  "One_Step", [ clear_redis_clear_keys ] )
   cf.insert_link( "link_2",  "One_Step",   [ plc_watch_dog.read_mode ] )
   cf.insert_link( "link_3",  "One_Step",   [ plc_watch_dog.read_mode_switch ] ) 
   cf.insert_link( "link_3",  "One_Step", [ irrigation_io_control.disable_all_sprinklers ] )
   cf.insert_link( "link_4",  "One_Step" ,[ check_for_uncompleted_sprinkler_element ] )
   cf.insert_link( "link_5",  "Terminate",  [] )


   cf.define_chain( "monitor_flow_rate", True) #tested
   cf.insert_link(  "link_1",  "WaitEvent",  [ "MINUTE_TICK" ] )
   cf.insert_link(  "link_2",  "One_Step",   [ monitor.measure_flow_rate ] )
   cf.insert_link(  "link_3",  "One_Step",   [ monitor.measure_current ] )
   cf.insert_link(  "link_5",  "Reset",      [] )


   cf.define_chain("measure_input_gpio", False )# TBD
   cf.insert_link( "link_1",  "WaitTime",    [30,0,0,0] )
   cf.insert_link( "link_2",  "One_Step",    [ monitor.measure_input_gpio ] )
   cf.insert_link( "link_3",  "Reset",       [] )


   cf.define_chain("update_time_stamp", True) #tested
   cf.insert_link( "link_1",  "WaitTime",    [10,0,0,0] )
   cf.insert_link( "link_3",  "One_Step",    [ monitor.update_time_stamp ] )
   cf.insert_link( "link_4",  "Reset",       [] )

   cf.define_chain("watch_dog_thread",True) #tested
   cf.insert_link( "link_0",   "Log",       ["Watch dog thread"] )
   cf.insert_link(  "link_1",  "WaitEvent",  [ "MINUTE_TICK" ] )
   cf.insert_link( "link_3",   "One_Step",  [ wd_client.pat_wd ])
   cf.insert_link( "link_5",   "Reset",     [])  





   cf.define_chain("clean_filter_chain", False)  #tested
   cf.insert_link( "link_1",  "WaitTod",        ["*",17,"*","*"] )
   #cf.insert_link( "link_2",  "Enable_Chain",   [["clean_filter_action_chain"]] )
   cf.insert_link( "link_3",  "WaitTod",        ["*",18,"*","*" ] )
   cf.insert_link( "link_4",  "Reset",          [] )


   
 
  

   cf.define_chain("clean_filter_action_chain", False)  #tested
   cf.insert_link( "link_0",   "Code",             [ check_irrigation_queue ] )
   cf.insert_link( "link_1",   "Log",              ["Clean Step 1"] )
   cf.insert_link( "link_2",   "One_Step",         [ monitor.set_suspend ])
   cf.insert_link( "link_3",   "One_Step",         [ irrigation_io_control.disable_all_sprinklers ] )
   cf.insert_link( "link_4",   "One_Step",         [ irrigation_io_control.turn_off_cleaning_valves ] )# turn off cleaning valve
   cf.insert_link( "link_5",   "One_Step",         [ irrigation_io_control.turn_on_master_valves ] )# turn turn on master valve
   cf.insert_link( "link_6",   "WaitTime",         [120,0,0,0] )
   cf.insert_link( "link_1",   "Log",           ["Clean Step 3"] )
   cf.insert_link( "link_7",   "One_Step",         [ irrigation_io_control.turn_on_cleaning_valves ] )# turn on cleaning valve
   cf.insert_link( "link_8",   "One_Step",         [ irrigation_io_control.turn_off_master_valves ] )# turn turn off master valve
   cf.insert_link( "link_9",   "WaitTime",         [30,0,0,0] ) 
   cf.insert_link( "link_1",   "Log",           ["Clean Step 4"] ) 
   cf.insert_link( "link_10",  "One_Step",         [ irrigation_io_control.turn_on_master_valves ] )# turn turn on master valve
   cf.insert_link( "link_11",  "WaitTime",         [10,0,0,0] )
   cf.insert_link( "link_1",   "Log",           ["Clean Step 5"] )
   cf.insert_link( "link_12",  "One_Step",         [ irrigation_io_control.turn_off_cleaning_valves ] )# turn turn off master valve
   cf.insert_link( "link_13",  "One_Step",         [ irrigation_io_control.turn_off_master_valves ] )# turn turn off cleaning valve
   cf.insert_link( "link_14",  "One_Step",         [ irrigation_io_control.disable_all_sprinklers ] )
   cf.insert_link( "link_15",  "One_Step",         [ monitor.clear_cleaning_sum ] )
   cf.insert_link( "link_16",  "One_Step",         [ monitor.set_resume ])
   cf.insert_link( "link_17",  "One_Step",         [ monitor.log_clean_filter ] )
   cf.insert_link( "link_17",  "Terminate",        [] )


   cf.define_chain("check_off", False )         # tested
   cf.insert_link( "link_1",  "WaitTod",        ["*",16,"*","*"] )
   #cf.insert_link( "link_2",  "Enable_Chain",   [["check_off_chain"]] )
   cf.insert_link( "link_3",  "WaitTod",        ["*",17,"*","*" ] )
   cf.insert_link( "link_4",  "Reset",          [] )



   cf.define_chain("check_off_chain", False ) #tested
   #cf.insert_link( "link_1",   "Log",           ["check off is active"] )
   cf.insert_link( "link_16",  "One_Step",      [ monitor.set_suspend ] )
   cf.insert_link( "link_2",   "One_Step",      [ irrigation_io_control.disable_all_sprinklers ] )
   cf.insert_link( "link_3",   "WaitTime",      [15,0,0,0] )
   cf.insert_link( "link_4",   "One_Step",      [ irrigation_io_control.turn_on_master_valves ] )# turn turn on master valve
   cf.insert_link( "link_5",   "One_Step",      [ irrigation_io_control.turn_off_cleaning_valves ] )# turn turn off master valve
   cf.insert_link( "link_6",   "WaitTime",      [300,0,0,0] ) 
   cf.insert_link( "link_7",   "Code",          [ check_off ] )
   cf.insert_link( "link_16",  "One_Step",         [ monitor.set_resume ])
   cf.insert_link( "link_8",   "One_Step",      [ irrigation_io_control.turn_off_master_valves ] )# turn turn on master valve
   cf.insert_link( "link_9",  "Terminate",     [] )
        
   cf.define_chain("manual_master_valve_on_chain",False) #tested
   #cf.insert_link( "link_1",    "Log",                  ["manual master"] )
   cf.insert_link( "link_2",    "Code",                 [ monitor.verify_resume ])
   cf.insert_link( "link_3",    "One_Step",             [ irrigation_io_control.turn_on_master_valves ] )
   cf.insert_link( "link_4",    "One_Step",             [ irrigation_io_control.turn_off_cleaning_valves ] )# turn turn off master valve
   cf.insert_link( "link_5",    "WaitTime",             [ 5,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_6",    "Reset",                [] )

   cf.define_chain("monitor_master_on_switch",False) #TBD
   #cf.insert_link("link_1",  "WaitTime",             [5,0,0,0] ) 
   #cf.insert_link("link_2",  "Code",                 [ detect_on_switch_on ] )
   #cf.insert_link("link_3",  "One_Step",             [ clear_redis_set_keys ] )
   #cf.insert_link("link_4",  "Enable_Chain",         [["manual_master_valve_on_chain"]] )
   #cf.insert_link("link_5",  "Enable_Chain",         [["manual_master_valve_off_chain"]] )
   #cf.insert_link("link_6",  "WaitTime",             [3600*8,0,0,0] ) # wait 8 hours
   #cf.insert_link("link_7",  "Disable_Chain",        [["manual_master_valve_on_chain"]] )
   #cf.insert_link("link_8",  "One_Step",             [ irrigation_io_control.turn_off_master_valves ])   
   #cf.insert_link("link_9",  "Reset",                [])
   cf.insert_link("link_9",  "Halt",                [])


   cf.define_chain("monitor_master_on_web",False) #TBD
   cf.insert_link( "link_0",    "Log",                  ["monitor master on web"] )
   cf.insert_link("link_1",  "Enable_Chain",         [["manual_master_valve_on_chain"]] )
   cf.insert_link("link_2",  "WaitTime",             [ 3600*8,0,0,0] ) # wait 8 hour
   cf.insert_link("link_3",  "Enable_Chain",         [["manual_master_valve_on_chain"]] )
   cf.insert_link("link_4",  "Disable_Chain",        [["manual_master_valve_off_chain"]] )
   cf.insert_link("link_5",  "One_Step",             [ irrigation_io_control.turn_off_master_valves ])   
   cf.insert_link("link_6",  "Disable_Chain",        [["monitor_master_on_web"]] )
  

     


   cf.define_chain("manual_master_valve_off_chain",False ) #TBD
   cf.insert_link("link_1",    "WaitTime",             [5,0,0,0] ) 
   #cf.insert_link("link_1",    "Code",                 [ detect_switch_off ] )
   #cf.insert_link("link_2",    "One_Step",             [ clear_redis_clear_keys ] )
   #cf.insert_link("link_3",    "One_Step",             [ clear_redis_set_keys ] )
   #cf.insert_link("link_4",    "Enable_Chain",         [["monitor_master_on_switch"]] ) 
   #cf.insert_link("link_5",    "Disable_Chain",        [["manual_master_valve_on_chain"]] ) 
   #cf.insert_link("link_6",    "Disable_Chain",        [["monitor_master_on_web"]] )     
   #cf.insert_link("link_7",    "One_Step",             [ irrigation_io_control.turn_off_master_valves ] )# turn turn on master valve
   #cf.insert_link("link_8",    "One_Step",             [ irrigation_io_control.turn_off_cleaning_valves ] )# turn turn off master valve
   cf.insert_link("link_6",    "Disable_Chain",        [["manual_master_valve_off_chain"]] )


   cf.define_chain("gpm_triggering_clean_filter",True) #TBDf

   cf.insert_link( "link_1",  "WaitEvent",      [ "MINUTE_TICK" ] )
   #cf.insert_link( "link_1",  "Log",            ["check to clean filter"] )
   cf.insert_link( "link_2",  "One_Step",       [ monitor.check_to_clean_filter ] )
   cf.insert_link( "link_3",  "Reset",      [] )

   cf.define_chain("update_modbus_statistics",True) #tested
   
   #cf.insert_link( "link_1",  "Log",            ["update modbus statistics"] )
   cf.insert_link( "link_2",  "One_Step",       [ monitor.update_modbus_statistics ] )
   cf.insert_link( "link_3",  "WaitTime",       [ 15,25,0,0] ) # wait 15 minutes
   cf.insert_link( "link_4",  "Reset",      [] )

   cf.define_chain("clear_modbus_statistics",True) #tested
   cf.insert_link( "link_1",  "WaitTod",        ["*",1,"*","*"] )
   #cf.insert_link( "link_2",  "Log",            ["clear modbus statistics"] )
   cf.insert_link( "link_3",  "One_Step",       [ monitor.clear_modbus_statistics ] )
   cf.insert_link( "link_4",  "WaitTod",        ["*",2,"*","*"] )
   cf.insert_link( "link_5",  "Reset",          [] )
   

   cf.define_chain("resistance_check",False) #not tested
   cf.insert_link( "link_1",  "Log",            ["resistance check"] )
   cf.insert_link( "link_2",   "One_Step",         [ monitor.set_suspend ])
   cf.insert_link( "link_3",  "One_Step",       [ assemble_relevant_valves ] )
   cf.insert_link( "link_4",  "Code",           [ test_individual_valves,0,0,0 ] )
   cf.insert_link( "link_5",  "One_Step",       [ monitor.set_resume ])  
   cf.insert_link( "link_6",   "Disable_Chain", [["resistance_check"]] )



   cf.define_chain("plc_watch_dog", True ) #TBD
   #cf.insert_link( "link_1",  "Log",        ["plc watch dog thread"] )
   #cf.insert_link( "link_2",  "One_Step",   [ plc_watch_dog.read_mode ] )
   #cf.insert_link( "link_3",  "One_Step",   [ plc_watch_dog.read_mode_switch ] ) 
   cf.insert_link( "link_4",  "One_Step",   [ plc_watch_dog.read_wd_flag  ]      )
   cf.insert_link( "link_5",  "One_Step",   [ plc_watch_dog.write_wd_flag ]      )
   cf.insert_link( "link_1", "WaitTime",    [ 30,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_7",  "Reset",    [] )



   cf.define_chain( "plc_monitor_control_queue", True ) #tested
   cf.insert_link( "link_1", "WaitTime", [ 1,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_2", "One_Step", [ sprinkler_control.dispatch_sprinkler_mode ] ) 
   cf.insert_link( "link_3", "Reset",    [] )
  




   cf.define_chain("monitor_irrigation_job_queue", True ) # tested
   cf.insert_link( "link_1",  "WaitTime",       [ 5,0,0,0] ) # wait 5 seconds
   cf.insert_link( "link_2",  "Code",           [ sprinkler_queue.load_irrigation_cell ] )
   cf.insert_link( "link_3",  "Code",           [ sprinkler_element.start] )
   cf.insert_link( "link_4",  "WaitTime",       [ 1,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_5",  "One_Step",       [ monitor.measure_current ] )
   cf.insert_link( "link_6",  "Code",            [ sprinkler_element.check_current ] )
   cf.insert_link( "link_7",  "Enable_Chain",   [["monitor_irrigation_cell","monitor_current_sub" ]])
   cf.insert_link( "link_8",  "WaitEvent",      ["CELL_DONE" ] )
   cf.insert_link( "link_9",  "Reset",          [] )


   cf.define_chain("monitor_current_sub", False )
   cf.insert_link( "link_0",  "Log"  ,           [["monitor_current_sub chain is working"]])
   cf.insert_link( "link_1",  "WaitTime",       [ 15,0,0,0] ) # wait 15 second
   cf.insert_link( "link_2",  "One_Step",       [ monitor.measure_current_a ] )
   cf.insert_link( "link_3",  "One_Step",       [ sprinkler_element.check_current ] )
   cf.insert_link( "link_4",  "Reset",          [] )


   cf.define_chain("monitor_irrigation_cell", False ) #Tested
   cf.insert_link( "link_1",  "WaitEvent",      [ "MINUTE_TICK" ] )
   cf.insert_link( "link_2",  "One_Step",       [ sprinkler_element.check_current ] )
   cf.insert_link( "link_3",  "One_Step",       [ sprinkler_element.check_for_excessive_flow_rate ] )
   cf.insert_link( "link_3",  "Code",           [ sprinkler_element.monitor ] )
   cf.insert_link( "link_4",  "SendEvent",      ["CELL_DONE"] ) 
   cf.insert_link( "link_5",  "Disable_Chain",  [["monitor_irrigation_cell","monitor_current_sub" ]])


   length = redis.llen("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" )
   
   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()
   
  

       
     

      


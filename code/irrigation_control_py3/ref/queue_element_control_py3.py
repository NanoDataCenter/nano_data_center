
  

class SprinklerQueueElementControl( ):
   def __init__(self,redis_handle,io_control,alarm_queue,counter_devices):
       self.redis            = redis
       self.alarm_queue      = alarm_queue
       self.io_control       = io_control
       self.counter_devices  = counter_devices
       self.app_files        =  load_files.APP_FILES(redis_handle)

       self.redis_handle.hset("CONTROL_VARIBALES","MAX_FLOW_TIME",0)

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

     

if __name__ == "__main__":
  pass

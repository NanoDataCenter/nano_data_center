
class Irrigation_Step_Monitoring(object):


   def __init__(self,handlers,manage_eto,io_manager,cf):
       self.manage_eto = manage_eto
       self.handlers   = handlers
       self.io_manager = io_manager
       self.cf         = cf



   def step_monitoring(self, json_object):
       # update io
       # check clean filter
       # update_eto_queue_minute
       # update logging data
       # look for safety checks
       return True
       
       
'''       
   def check_to_clean_filter( self, chainFlowHandle, chainObj, parameters,event ):
       if event["name"] == "INIT":
          return True
       cleaning_interval = self.redis_handle.hget("CONTROL_VARIABLES","CLEANING_INTERVAL")
       cleaning_interval = float( cleaning_interval)
       flow_value   =  float( self.check_redis_value( "global_flow_sensor_corrected" ) )
       cleaning_sum =  float( self.check_redis_value( "cleaning_sum") )
       cleaning_sum = cleaning_sum + flow_value
       self.redis_handle.hset("CONTROL_VARIABLES","cleaning_sum",cleaning_sum)
       if cleaning_interval == 0 :
           return True  # no cleaning interval active

       if cleaning_sum > cleaning_interval :
           return False
       else:
           return True
           
   def update_eto_queue_minute( self, sensor_list ):
       for l in  sensor_list:
           j_index = l[0]
           queue_name = l[2]
           j = self.eto_site_data[ j_index ]
           deficient = self.redis_handle.hget("ETO_RESOURCE",  queue_name )
           
           if deficient == None:
               deficient = 0
           else:
               deficient = float(deficient)
           recharge_rate = float(j["recharge_rate"])
           deficient = deficient - (recharge_rate/60) # recharge rate is per hour
           if deficient < 0 :
               deficient = 0 
           
           self.redis_handle.hset( "ETO_RESOURCE", queue_name, deficient )
           
   
   #
   #
   # Support Functions
   #

   def check_redis_value( self,key):
       value =  self.redis_handle.hget( "CONTROL_VARIABLES",key )
       if value == None:
           value = 0
       return value
       
       
      def update_control_variables( self ):
       #self.redis_handle.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","AUTO")
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_name", self.json_object["schedule_name"] )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_step_number", self.json_object["step"] )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_step", self.json_object["step"] )

       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_count", self.json_object["elasped_time"] )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_max",  self.json_object[ "run_time"] )  

       json_string                       = json.dumps( self.json_object )
       self.redis_handle.lset( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", 0, json_string )

shutdown_irrigation
   def clean_up_irrigation_cell( self ,*arg):
       
       self.redis_handle.delete("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_name","offline" )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_step_number",0 )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_step",0 )
       self.redis_handle.hset("CONTROL_VARIABLES", "schedule_time_count",0 )
       self.redis_handle.hset( "CONTROL_VARIABLES","schedule_time_max",0 ) 
       self.redis_handle.hset( "CONTROL_VARIABLES","sprinkler_ctrl_mode","AUTO")
 
       self.io_control.disable_all_sprinklers()
       self.io_control.clear_duration_counters()
       self.io_control.turn_off_master_valves()








'''
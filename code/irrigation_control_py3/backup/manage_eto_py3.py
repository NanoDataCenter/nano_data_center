import time
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

class Manage_Eto(object):

   def __init__( self, redis_handle,alarm_queue, app_files ):
       self.redis_handle = redis_handle
       self.alarm_queue = alarm_queue
       self.app_files = app_files
     

   def setup_sprinkler( self, sprinkler_object ):
       print("made it here $$$$$$$$$$$$$$$$$$$$")
       return_value = True  # let sprinkler operation go thru
       self.json_object = sprinkler_object.json_object
      
       if ( self.json_object["restart"] == True) and ("eto_active" in self.json_object):
           return return_value  # all ready setup in previous pass       

       if self.json_object["eto_enable"] == False:
             self.json_object["eto_active"] = False
           
       elif self.get_manage_flag() == True:
          
           return_value = self.eto_run_time_correction() 
       else:
           self.json_object["eto_enabled"] = False #eto manage flag set to zero or False
  
       return return_value
           


   def minute_update( self, sprinkler_object ):

       if self.json_object["eto_enable"] == True:
           sensor_list = self.sensor_list
           self.update_eto_queue_minute( sensor_list ) # reduce eto deficiet
       return True 


   #
   #  Support functions
   # 

   def get_manage_flag( self ):
       manage_eto = self.redis_handle.hget( "CONTROL_VARIABLES","ETO_MANAGE_FLAG" )
       if manage_eto == None:
           manage_eto = 1
           self.redis_handle.hset("CONTROL_VARIABLES", "ETO_MANAGE_FLAG",manage_eto)
       manage_eto = int( manage_eto )
       if manage_eto > 0:
          return_value = True
       else:
          return_value = False
       return return_value   
   


   def eto_run_time_correction( self ):
      
       return_value = True
       
       self.eto_site_data = self.app_files.load_file( "eto_site_setup.json" )
       manage_eto = self.redis_handle.hget( "CONTROL_VARIABLES","ETO_MANAGE_FLAG" )
       self.sensor_list = self.find_queue_names( self.json_object["io_setup"] )
       
       if len(self.sensor_list) != 0:
               # irrigation valves under eto control
               self.json_object["eto_enable"] = True
               self.enabled = True
               run_time = self.find_largest_runtime( self.json_object["run_time"], self.sensor_list )
               
               if run_time == 0:
                   data = {}
                   data["io_setup"] = self.json_object["io_setup"]
                   data["run_time"] = self.json_object["run_time"]
                   self.alarm_queue.alarm_state = True
                   self.alarm_queue.store_past_action_queue("IRRIGATION:START:ETO_RESTRICTION",
                        "YELLOW", data  )
                   return_value = False
               if run_time < self.json_object["run_time"] :
                   self.json_object["run_time"] = run_time
       else: 
           # irrigation valves not under eto control
           self.json_object["eto_enable"] = False 
       return return_value



   def find_queue_names( self, io_list ):
       print("io_list ",io_list)
       eto_values = []
       for j in io_list:
           controller = j["remote"]
           bits       = j["bits"]
           bit        = bits[0] 
           index = 0
           for m in self.eto_site_data:
               

               if (m["controller"] == controller) and (int(m["pin"]) in bits): 
                   queue_name = controller+"|"+str(bit)
                   data = self.redis_handle.hget( "ETO_RESOURCE", queue_name )
                   if data == None :
                        self.redis_handle.hset( "ETO_RESOURCE", queue_name,0.0 )
                        data = 0.0
                   eto_values.append( [index, data, queue_name ] )
               index = index +1
       
       return eto_values


   def find_largest_runtime( self, run_time, sensor_list ):
       runtime = 0
       print("sensor list $$$$$$$$$$$$$$$$$$$ ",sensor_list)
       for j in sensor_list:
           index = j[0]
           deficient = float(j[1])
           eto_temp = self.eto_site_data[index]
           recharge_eto = float( eto_temp["recharge_eto"] )  # minium eto for sprinkler operation
           recharge_rate = float(eto_temp["recharge_rate"])
           if float(deficient) > recharge_eto :
               runtime_temp = (deficient  /recharge_rate)*60
               if runtime_temp > runtime :
                   runtime = runtime_temp
       return runtime



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

     
if __name__ == "__main__":
   pass
        
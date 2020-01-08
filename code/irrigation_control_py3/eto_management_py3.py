import json
import time
import os
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



class ETO_Management(object):
   def __init__(self,qs,redis_site,app_files,Generate_Handlers):
 
       self.app_files = app_files
       
       
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"WEATHER_STATION_DATA"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)  
       package = package_sources[0]
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,qs)
       self.eto_hash_table = generate_handlers.construct_hash(data_structures["ETO_ACCUMULATION_TABLE"])
       print(self.eto_hash_table.hgetall())
       
      
   def update_eto_values(self,sensor_list):
       self.eto_site_data = self.app_files.load_file( "eto_site_setup.json" )
       for l in  sensor_list:
           j_index = l[0]
           queue_name = l[1]
           j = self.eto_site_data[ j_index ]
           deficient = self.eto_hash_table.hget( queue_name )
           
           if deficient == None:
               deficient = 0
           else:
               deficient = float(deficient)
           recharge_rate = float(j["recharge_rate"])
           deficient = deficient - (recharge_rate/60) # recharge rate is per hour
           if deficient < 0 :
               deficient = 0 
           
           self.eto_hash_table.hset( queue_name , deficient) 
      
   def determine_eto_management(self,run_time, io_list):
      self.eto_site_data = self.app_files.load_file( "eto_site_setup.json" )
      
      sensor_list = self.find_queue_names( io_list )
      if len(sensor_list) == 0:
        return run_time, False,None
      print("made it here 4")
      run_time = self.find_largest_runtime(run_time,sensor_list)
      print("made it here 4 a",run_time)
      return run_time,True,sensor_list
      
      
      




   def find_queue_names( self, io_list ):
       
       eto_values = []
       for j in io_list:
           controller = j["remote"]
           bits       = j["bits"]
           bit        = bits[0] 
           index = 0
           for m in self.eto_site_data:

               if (m["controller"] == controller) and (int(m["pin"]) in bits): 
                   queue_name = controller+"|"+str(bit)
                   eto_values.append( [index,  queue_name ] )
               index = index +1
       
       return eto_values


   def find_largest_runtime( self, run_time, sensor_list ):
       runtime = 0
       print(sensor_list)
       for j in sensor_list:
           index = j[0]
           queue_name = j[1]
           print(self.eto_hash_table.hgetall())
           eto_temp = self.eto_site_data[index]
           recharge_eto = float( eto_temp["recharge_eto"] )  # minium eto for sprinkler operation
           recharge_rate = float(eto_temp["recharge_rate"])
           deficient = self.eto_hash_table.hget( queue_name )
           print(deficient)
           if deficient == None:
              deficient = 0
           if float(deficient) > recharge_eto :
               runtime_temp = (deficient  /recharge_rate)*60
           else:
               runtime_temp =  0
           if runtime_temp > runtime :
               runtime = runtime_temp
       if runtime > run_time:
          runtime = run_time
       return runtime

   def update_eto_queue_minute( self, sensor_list ):
       
       for l in  sensor_list:
           j_index = l[0]
           queue_name = l[1]
           j = self.eto_site_data[ j_index ]
           deficient = self.eto_hash_table.hget(  queue_name )
           
           if deficient == None:
               deficient = 0
           else:
               deficient = float(deficient)
           recharge_rate = float(j["recharge_rate"])
           deficient = deficient - (recharge_rate/60) # recharge rate is per hour
           if deficient < 0 :
               deficient = 0 
           
           self.eto_hash_table.hset(  queue_name, deficient )   


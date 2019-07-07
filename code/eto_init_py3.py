



from redis_support_py3.construct_data_handlers_py3 import Redis_Hash_Dictionary
from redis_support_py3.cloud_handlers_py3 import Cloud_TX_Handler
from redis_support_py3.load_files_py3  import APP_FILES
from redis_support_py3.load_files_py3  import SYS_FILES
import redis
import json
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from redis_support_py3.graph_query_support_py3 import  Query_Support

class Generate_Data_Handler():
   def __init__(self,redis_site_data):
       qs = Query_Support( redis_server_ip = redis_site_data["host"], redis_server_port=redis_site_data["port"] )
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site_data["site"] )

       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"WEATHER_STATION_DATA"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)  
       package = package_sources[0]
       data_structures = package["data_structures"]
       generate_handlers = Generate_Handlers(package,redis_site_data)
       self.eto_data_handler = generate_handlers.construct_hash(data_structures["ETO_ACCUMULATION_TABLE"])
       self.redis_handle = redis.StrictRedis(redis_site_data["host"], redis_site_data["port"], db=redis_site_data["redis_file_db"] )
       
   def get_data_handler(self):
       return self.eto_data_handler
       
   def get_redis_handle(self):
       return self.redis_handle
       
class User_Data_Tables(object):

   def __init__(self, redis_site_data ):
       
       self.redis_site_data = redis_site_data
       self.ds_handlers = {}
       generate_handler = Generate_Data_Handler(redis_site_data)
       self.eto_data_handler= generate_handler.get_data_handler()
       self.redis_handle = generate_handler.get_redis_handle()
       self.app_file_handle = APP_FILES( self.redis_handle,self.redis_site_data )
       self.sys_filie_handle = SYS_FILES( self.redis_handle,self.redis_site_data)
       
 
  
   
       
       
   def initialize_eto_tables(self):
       
       # the eto_site table may have changed
       # need to merge old table values into the new table
       # there may be insertions as well as deletions
       eto_file_data = self.app_file_handle.load_file("eto_site_setup.json")
       


      
       
       eto_redis_hash_data = self.eto_data_handler.hgetall()

       
       new_data = {}
       
       #
       # Step 1  Populate file dummy initial values
       #
       
       for j in eto_file_data:
          
           new_data[ j["controller"] + "|" + str(j["pin"])] = 0

       
       
       self.eto_data_handler.delete_all()
       
       #
       # merge old values and possible new values into new table.
       #
       
       for i in new_data.keys():
           
           
           if i in eto_redis_hash_data: #checking to see if entry in old table
             
              data = eto_redis_hash_data[i]   # key old values
           else:
              data = 0
              
           self.eto_data_handler.hset(i,data )         
           
           
if __name__ == "__main__":

    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site_data = json.loads(data)
    user_data = User_Data_Tables(redis_site_data)
    user_data.initialize_eto_tables()  

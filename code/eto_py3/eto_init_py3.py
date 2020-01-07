




from redis_support_py3.load_files_py3  import APP_FILES
from redis_support_py3.load_files_py3  import SYS_FILES

import json


       
class Initialize_ETO_Accumulation_Table(object):

   def __init__(self, qs,redis_site_data ):
       
       self.redis_site_data = redis_site_data
      
       
       
      
       self.app_file_handle = APP_FILES( qs.get_redis_data_handle(),self.redis_site_data )
       self.sys_filie_handle = SYS_FILES( qs.get_redis_data_handle(),self.redis_site_data)
       
 
  
   
       
       
   def initialize_eto_tables(self,eto_data_handler):
       
       self.eto_data_handler = eto_data_handler
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
           
           

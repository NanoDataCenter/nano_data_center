

from redis_support_py3.construct_data_handlers_py3 import Stream_Writer
from redis_support_py3.construct_data_handlers_py3 import Stream_Reader
from redis_support_py3.construct_data_handlers_py3 import Redis_Hash_Dictionary
from redis_support_py3.cloud_handlers_py3 import Cloud_TX_Handler
from redis_support_py3.load_files_py3  import APP_FILES
from redis_support_py3.load_files_py3  import SYS_FILES
import redis
import json
from redis_support_py3.user_data_tables_py3 import Generate_Table_Handlers


class ETO_Data(object):

   def __init__(self,generate_handlers):
        self.generate_handlers = generate_handlers
        self.redis_handle = generate_handlers.get_redis_handle()

   def get_hash_table(self):
       return  self.generate_handlers.construct_hash("ETO","ETO_TABLE")


class User_Data_Tables(object):

   def __init__(self, redis_site_data ):
       self.backup_db     = redis_site_data["redis_backup_db"]
       self.redis_site_data = redis_site_data
       self.table_handler = Generate_Table_Handlers( redis_site_data )
       self.redis_handle = self.table_handler.get_redis_handle()

       self.app_file_handle = APP_FILES( self.redis_handle,self.redis_site_data )
       self.sys_filie_handle = SYS_FILES( self.redis_handle,self.redis_site_data)
       
       self.eto_data = ETO_Data( self.table_handler )
 

   def get_redis_handle(self):
      return self.redis_handle   
       
   def initialize(self):
       self.initialize_eto_tables()
       
   def initialize_eto_tables(self):
       # the eto_site table may have changed
       # need to merge old table values into the new table
       # there may be insertions as well as deletions
       eto_file_data = self.app_file_handle.load_file("eto_site_setup.json")
       


       eto_redis_hash_table = self.eto_data.get_hash_table()
       
       eto_redis_hash_data = eto_redis_hash_table.hgetall()
       


       
       new_data = {}
       
       #
       # Step 1  Populate file dummy initial values
       #
       for j in eto_file_data:
           
           new_data[ j["controller"] + "|" + str(j["pin"])] = 0
       #
       # populate from redis hash table
       #
       #
       eto_redis_hash_table.delete_all()
       
       #
       # merge old values and possible new values into new table.
       #
       
       for i in new_data.keys():
           data = new_data[i]
           if i in eto_redis_hash_data:
              data = eto_redis_hash_data[i]   # key old values
           eto_redis_hash_table.hset(i,data )         
           
           
if __name__ == "__main__":

    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site_data = json.loads(data)
    user_data = User_Data_Tables(redis_site_data)
    user_data.initialize()    

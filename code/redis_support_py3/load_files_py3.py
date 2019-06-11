
#
# File: load_files.py
# load sys files and application files
# The data is stored in the following
#    System Files are stored in the following in json format
#    	As a dictionary with the key of FILES:SYS
#    	The key of the dictionary are the file names
#    APP Files are stored in the following in json format
#    	As a dictionary with the key of
#    	The key of the dictionary are the file names

#  import redis
#  make redis dictionary "SYS:FILES"
# store json_object to redis data "global_sensors"
import os
from os import listdir
from os.path import isfile, join
import redis
import json
import msgpack

from  .construct_data_handlers_py3 import Redis_Hash_Dictionary
from  .cloud_handlers_py3 import Cloud_TX_Handler
app_files = "app_data_files/"
sys_files = "system_data_files/"
limit_files = "limit_data_files/"
import base64


   
class BASIC_FILES( object ):
    def __init__(self, redis_handle,path, redis_site,label):
        self.path = path
        self.redis_site = redis_site
        self.cloud_handler = Cloud_TX_Handler(redis_handle)
        data = {}
        data["forward"] = True
  
        self.redis_handle = redis_handle
        self.key = "[SITE:"+redis_site["site"]+"][FILE:"+label+ "]"
        self.hash_driver = Redis_Hash_Dictionary(self.redis_handle,data,self.key,self.cloud_handler)

        
    def file_exists(self,name):
        return isfile(self.path+name)
    
        
    def file_directory(self):
        return self.hash_driver.hkeys()

    def delete_file(self, name):
        self.hash_driver.hdelete(name)

    
        
    def save_file(self, name, data):
        f = open(self.path + name, 'w')
        json_data = json.dumps(data)
        f.write(json_data)
        self.hash_driver.hset( name,json_data)

    def load_file(self, name):
        return json.loads(self.hash_driver.hget(name))
 

class APP_FILES( BASIC_FILES ):
   def __init__( self, redis_handle,redis_site ):
       BASIC_FILES.__init__(self,redis_handle,app_files, redis_site,"APP" )
       

class SYS_FILES(BASIC_FILES):
    def __init__(self, redis_handle,redis_site ):
        BASIC_FILES.__init__(self,redis_handle,sys_files,redis_site,"SYS" )
    
        
class LIMIT(BASIC_FILES):
    def __init__(self, redis_handle,redis_site ):
        BASIC_FILES.__init__(self,redis_handle,limit_files,redis_site,"LIMITS" )


if __name__ == "__main__":


   def load_file( file_list,path, redis_key,cloud_handler_tx):
       old_fields = set(redis_handle.hkeys(redis_key))
       for i in file_list:
           try:
               fileName, fileExtension = os.path.splitext(i)
           
               forward = {"forward":False}
               if fileExtension == ".json":
                   f = open(path+i, 'r')
                   data = f.read()

                   temp = json.loads(data) # test to ensure data has json format
              
                   pack_data = msgpack.packb(data,use_bin_type = True )
                   if redis_handle.hget(redis_key,i) != pack_data:
                       print("file miss match",i)
                       redis_handle.hset( redis_key, i , pack_data)
                       cloud_handler_tx.hset(forward,redis_key,i,pack_data)
           except:
              pass # add log
       new_fields = set(redis_handle.hkeys(redis_key))
       # remove old keys
       keys_to_delete = list(old_fields.difference(new_fields))
       for i in keys_to_delete:
           redis_handle.hdel(redis_key,i)
           cloud_handler_tx.hdel(redis_key,i)
  

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()

   redis_site = json.loads(data)

   redis_handle = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_file_db"] )




   key = "[SITE:"+redis_site["site"]+"][FILE:"
   cloud_handler_tx = Cloud_TX_Handler(redis_handle)
   files = [f for f in listdir(app_files)]

   
   
  
   # load app files
   load_file( files,app_files,key+"APP]",cloud_handler_tx )


   # load sys files

   files = [ f for f in listdir(sys_files)  ]
  
   load_file( files,sys_files, key+"SYS]",cloud_handler_tx )


   # load limit files

   files = [ f for f in listdir(limit_files)  ]
  
   load_file( files,limit_files,key+"LIMITS]",cloud_handler_tx )
   

else:
   pass


__TEST__= False 
if __TEST__ == True:
   print("made it to test")
   app_file_handler = APP_FILES( redis_handle,redis_site )
   sys_file_handler = SYS_FILES( redis_handle,redis_site)
   print(app_file_handler.file_directory())
   directory_list = app_file_handler.file_directory()
   print(app_file_handler.load_file(directory_list[0]))
   

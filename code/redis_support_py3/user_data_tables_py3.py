


import time

#from .construct_data_handlers_py3 import Stream_Writer

from .construct_data_handlers_py3 import Redis_Hash_Dictionary
from .cloud_handlers_py3 import Cloud_TX_Handler
from .load_files_py3  import APP_FILES
from .load_files_py3  import SYS_FILES
import redis
import json


class Generate_Table_Handlers(object):

   def __init__(self,site_data):
       self.site_data = site_data   
      
       self.redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["redis_table_db"] )
       self.prefix = "[SITE:"+site_data["site"]+"][TABLE_DATA:"
       self.cloud_handler = Cloud_TX_Handler(self.redis_handle) 
       

       
   def get_redis_handle(self):
       return self.redis_handle   


         
   def construct_hash(self,table_name,hash_name,forward = True):
         data = {}
         data["forward"] = forward
         key = self.prefix + table_name+"][HASH:"+hash_name+"]"
         return  Redis_Hash_Dictionary( self.redis_handle,data,key,self.cloud_handler )

   '''
   #for now redis streams are disabled for now
   def construct_stream_writer(self,table_name,stream_name,depth,forward=True):
         data = { "depth":depth}
         data["forward"] = True
         key = self.prefix + table_name+"][STREAM:"+stream_name+"]"
         return Stream_Writer(self.redis_handle,data,key,self.cloud_handler)
         
   def construct_stream_reader(self,table_name,stream_name):
         data = {}
         data["forward"] = True
         key = self.prefix + table_name+"][STREAM:"+stream_name+"]"
         return Stream_Reader(self.redis_handle,data,key)
  
   def construct_stream_writer(self,table_name,stream_name,depth,forward = True):
         data = { "depth":depth}
         data["forward"] = True
         key = self.prefix + table_name+"][STREAM_LIST:"+stream_name+"]"
         return Stream_List_Writer(self.redis_handle,data,key,self.cloud_handler)


   def construct_stream_reader(self,table_name,stream_name,forward = True):
        data = {}
        data["forward"] = True
      
        key = self.prefix + table_name+"][STREAM_LIST:"+stream_name+"]"
        return Stream_List_Reader(self.redis_handle,data,key)
  
  '''

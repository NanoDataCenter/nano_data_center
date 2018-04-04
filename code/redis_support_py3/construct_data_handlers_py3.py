
import json
import redis
import time
import base64

from .redis_stream_utilities_py3 import Redis_Stream
from .redis_rpc_client_py3 import Redis_Rpc_Client
from .redis_rpc_server_py3 import Redis_Rpc_Server

class Field_Not_Defined(Exception):
    pass       
      
class FIELD_TYPE_ERROR(Exception):
   pass
 
class RPC_Server(Redis_Rpc_Server):
    def __init__( self, redis_handle ,cloud_handler,key,data ):
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       self.handler = {}
       self.redis_handle.delete(redis_rpc_queue)
       self.timeout_function = None
       self.timeout_value  = data["timeout"]


    def add_time_out_function(self,time_out_function):
       self.timeout_function = time_out_function
       
      

      
 
class Redis_Hash_Dictionary( object ):
 
   def __init__(self,redis_handle,cloud_handler, key,data):
      self.redis_handle = redis_handle
      self.key = key
      self.data = data
      self.cloud_handler = cloud_handler

   def hset( self, field, data ):
      
      self.redis_handle.hset(self.key,field,json.dumps(data))      

   def hget( self, field):
      data = self.redis_handle.hget(self.key,field)
      if data == None:
         return None
      return json.loads(self.redis_handle.hget(self.key,field))

   def hgetall( self ):
      return_value = {}
      data = self.redis_handle.hgetall(self.key)
      if data == None:
         return None
      for key, item in data.items():
         return_value[key] = json.loads(item)
      return return_value
      
   def hkeys(self):
       return self.redis_handle.hkeys(self.key)
   
   def hexists(self,field):
     return self.redis_handle.hexists(self.key,field)
   
   
   def htrim(self,fields):
     keys = self.redis_handle.hkeys(self.key)
     extraneous_keys = list((set(fields)-set(keys)))
     for i in extraneous_keys:
         self.redis_handle.hdel(self,key,i)  

   def delete(self):
       self.redis_handle.delete(self.key)   
     
class Job_Queue_Client( object ):
 
   def __init__(self,redis_handle, name, depth):
      self.redis_handle = redis_handle
      self.key = name
      self.depth = depth

   def delete(self, index ):
       if index < self.llen(self.key):
           self.lset(self.key, index,"__#####__")
           self.lrem(self.key, 1,"__#####__") 
      
   def length(self):
       return self.redis_handle.llen(self.key)   
      
   def push(self,data):
       json_data = json.dumps(data)
       self.redis_handle.lpush(self.key,json_data)
       self.redis_handle.ltrim(self.key,0,self.depth)

 
class Job_Queue_Server( object ):
 
   def __init__(self,redis_handle, name):
      self.redis_handle = redis_handle
      self.key = name   
      self.redis_handle.delete(self.key)
 
   def length(self):
       return self.redis_handle.llen(self.key)
       
   def delete(self, index ):
       if index < self.llen(self.key):
           self.lset(self.key, index,"__#####__")
           self.lrem(self.key, 1,"__#####__") 

 
   def pop(self):
       json_data = self.redis_handle.rpop(self.key)
       if json_data == None:
          return False, None
       else:
          return True, json.loads(json_data)
          
   def last_get(self):
       json_data = self.redis_handle.lindex(self.key, -1)
       if json_data == None:
          return False, None
       else:
          return True, json.loads(json_data)

class  List_Handler(object):

   def __init__(self,redis_handle,cloud_handler,name,data):
       self.redis_handle = redis_handle
       self.cloud_handler = cloud_handler
       self.key = name
       self.length = data["length"] 
       self.__trim_list()       

   def __trim_list(self):
      length = self.redis_handle.llen(self.key)
      blank_data = json.dumps("")
      if length < self.length:
          for i in range(0,self.length-length):
              self.redis_handle.rpush(self.key,blank_data)
              
      if self.length < length:
          for i in range(0,self.length-length):
              self.redis_handle.rpop(self.ket)
              
              
   def lset(self,index,value):
       self.redis_handle.lset(self.key, index, json.dumps(value))
       
       
   def lget(self,index):
       return json.dumps(self.redis_handle.lindex(self.key, index))
       
   def lrange(self,start,end):
       return_value = []
       data_json_list = self.redis_handle.lrange(self.key, start, end)
       for data_json in data_json_list:
          data = json.loads(data_json)
          return_value.append(data)
       return return_value
   
class Stream_List_Writer(object):
       
  
   def __init__(self,redis_handle,cloud_handler, key, data):
     
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = key
      self.depth = data["depth"]
      
      
   def push(self,data):
       json_data = json.dumps(data)
       self.redis_handle.lpush(self.key,json_data)
      
       self.redis_handle.ltrim(self.key,0,self.depth-1)
       
class Stream_List_Reader(object):
       
   def __init__(self,redis_handle, redis_key):
      
      self.redis_handle = redis_handle
      self.key = redis_key
     
      
      
   def range(self,start,end):
       return_value = []
       data_json_list = self.redis_handle.lrange(self.key, start, end)
       for data_json in data_json_list:
          data = json.loads(data_json)
          return_value.append(data)
       return return_value

class Stream_Writer(Redis_Stream):
       
   def __init__(self,redis_handle, cloud_handler, redis_key, data):
      super().__init__(redis_handle)
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = redis_key
      self.depth = data["depth"]
      self.add_pad = "~"
      
   def change_add_flag(self, state):
      if state == True:
          self.add_pad = ""
      else:
          self.add_pad = "~"
   
      
   def add_json(self,id="*", data={} ):
       store_dictionary = {}
       if len(list(data.keys())) == 0:
           return
       for i , item in data.items():
           store_dictionary[i] = base64.b64encode(json.dumps(item).encode("ascii")).decode("ascii")
       print(self.xadd(key = self.key, max_len=self.depth,id=id,data_dict=store_dictionary ))
       
   
      

class Stream_Reader(Redis_Stream):
       
   def __init__(self,redis_handle, redis_key):
      super().__init__(redis_handle)
      self.redis_handle = redis_handle
      self.key = redis_key

      
      
   def xrange_json(self,start_timestamp, end_timestamp , count=100):
       return_value = []
       data_json = self.xrange(self.key,start_timestamp,end_timestamp, count)
       
       for i in data_json:
          return_item = {}
          for key, item64 in i["data"].items():
              item_json = base64.b64decode(item64.encode("ascii")).decode("ascii")
              item = json.loads(item_json)
      
              return_item[key] = item
          i["data"] = return_item
       return data_json

   def xrevrange_json(self,start_timestamp, end_timestamp , count=100):
       data_json = self.xrevrange(self.key,start_timestamp,end_timestamp, count)
       
       for i in data_json:
          return_item = {}
          for key, item64 in i["data"].items():
                        
              item_json = base64.b64decode(item64.encode("ascii")).decode("ascii")
              item = json.loads(item_json)
      
              return_item[key] = item
          i["data"] = return_item
       return data_json
   
       

       
class Generate_Handlers(object):
   
   def __init__(self,package,site_data , cloud_handler = None ):
       self.site_data = site_data
       self.package = package
       self.cloud_handler = cloud_handler

       self.redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["redis_io_db"] , decode_responses=True)
      
       
   def get_redis_handle(self):
       return self.redis_handle   

   def construct_list(self,data):
         assert(data["type"] == "LIST")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return List_Handler(self.redis_handler,self.cloud_handler,name, data )


         
   def construct_hash(self,data):
         assert(data["type"] == "HASH")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return  Redis_Hash_Dictionary( self.redis_handle,self.cloud_handler,key,data )


   def construct_stream_writer(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Writer(self.redis_handle,self.cloud_handler,key,data)
         
   def construct_stream_reader(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Reader(self.redis_handle,key)

   def construct_stream_list_writer(self,data):
         assert(data["type"] == "STREAM_LIST")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_List_Writer(self.redis_handle,self.cloud_handler,key,data)


   def construct_stream_list_reader(self,data):
         assert(data["type"] == "STREAM_LIST")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_List_Reader(self.redis_handle,key)

   def construct_job_queue_client(self,data):
         assert(data["type"] == "JOB_QUEUE")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Job_Queue_Client(self.redis_handle,key, data["depth"] )

   def construct_job_queue_server(self,data):
         assert(data["type"] == "JOB_QUEUE")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Job_Queue_Server(self.redis_handle,)

   def construct_rpc_client(self,data):
         assert(data["type"] ==  "RPC")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Redis_Rpc_Client(self.redis_handle,key)

   def construct_rpc_sever(self,data):
         assert(data["type"] ==  "RPC")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return RPC_Server(self.redis_handle,self.cloud_handler,key,data )
    

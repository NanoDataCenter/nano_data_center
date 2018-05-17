
import json
import redis
import time
import base64
import msgpack

from .redis_stream_utilities_py3 import Redis_Stream
from .cloud_handlers_py3 import Cloud_TX_Handler

class Field_Not_Defined(Exception):
    pass       
      
class FIELD_TYPE_ERROR(Exception):
   pass

class RPC_Server(object):
    def __init__( self, redis_handle ,key,data ):
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       self.handler = {}
       self.redis_handle.delete(redis_rpc_queue)
       self.timeout_function = None
       self.timeout_value  = data["timeout"]


    def add_time_out_function(self,time_out_function):
       self.timeout_function = time_out_function
       

    def register_call_back( self, method_name, handler):
        self.handler[method_name] = handler
    
    def start( self ):
        while True:
            try:
               input = self.redis_handle.brpop(self.redis_rpc_queue,self.timeout_value)
              
               if input == None:
                    if self.timeout_function != None:
                        self.timeout_function()
               else:
                   input = json.loads(input[1])  # 0 parameter is the queue
                   self.process_message(  input )
                       
            except:
                raise
 
    def process_message( self, input):

        id      = input["id"]
        method  =  input["method"]
        params  = input["params"]
        response = self.handler[method](params)
       
        self.redis_handle.lpush( id, json.dumps(response))        
        self.redis_handle.expire(id, 30)

      

      
 
class Redis_Hash_Dictionary( object ):
 
   def __init__(self,redis_handle, key,data,cloud_handler):
      self.redis_handle = redis_handle
      self.key = key
      self.data = data
      self.cloud_handler = cloud_handler

      
   def delete_all( self ):
       self.redis_handle.delete(self.key)
       self.cloud_handler.delete(self.key)     
      
      
   def hset( self, field, data ):
      json_data = json.dumps(data)
      self.redis_handle.hset(self.key,field,json_data)
      self.cloud_handler.hset(self.key,field,json_data)     

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
   

   def hdelete(self,field):
       self.redis_handle.hdel(self.key,field)
       self.cloud_handler.hdel(self.key,field)
          
       

  
       
class Job_Queue_Client( object ):
 
   def __init__(self,redis_handle, key, data, cloud_handler):
      self.redis_handle = redis_handle
      self.key = key
      self.depth =  data["depth"]
      self.cloud_handler = cloud_handler

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       self.cloud_handler.delete(self.key)     
      
      
   def delete(self, index ):
       if index < self.llen(self.key):
           self.redis_handle.lset(self.key, index,"__#####__")
           self.redis_handle.lrem(self.key, 1,"__#####__") 
           self.cloud_handler.list_delete(self,self.key,self.index)
      
   def length(self):
       return self.redis_handle.llen(self.key)   
      
   def push(self,data):
       json_data = json.dumps(data)
       self.redis_handle.lpush(self.key,json_data)
       self.redis_handle.ltrim(self.key,0,self.depth)
       self.cloud_handler.lpush(self.depth,self.key,json_data)
         

 
class Job_Queue_Server( object ):
 
   def __init__(self,redis_handle, key,cloud_handler):
      self.redis_handle = redis_handle
      self.key = key 
      self.cloud_handler = cloud_handler
 
   def delete_all( self ):
       self.redis_handle.delete(self.key)
       self.cloud_handler.delete(self.key)     
 
 
   def length(self):
       return self.redis_handle.llen(self.key)
       
   def delete(self, index ):
       if index < self.llen(self.key):
           self.redis_handle.lset(self.key, index,"__#####__")
           self.redis_handle.lrem(self.key, 1,"__#####__") 
           self.cloud_handler.list_delete(self,self.key,self.index)
                

 
   def pop(self):
       json_data = self.redis_handle.rpop(self.key)
       self.cloud_handler.rpop(self.key)

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


   
class Stream_List_Writer(object):
       
  
   def __init__(self,redis_handle, key, data,cloud_handler):
     
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = key
      self.depth = data["depth"]

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       self.cloud_handler.delete(self.key)     
      
      
   def push(self,data):
       compress_data = msgpack.compress(data)
       self.redis_handle.lpush(self.key,compress_data)
       self.redis_handle.ltrim(self.key,0,self.depth-1)
       self.cloud_handler.stream_list_write(self.depth, self.key, data )

       
class Stream_List_Reader(object):
       
   def __init__(self,redis_handle, redis_key):
      
      self.redis_handle = redis_handle
      self.key = redis_key
     
   def delete_all( self ):
       self.redis_handle.delete(self.key)
       self.cloud_handler.delete(self.key)     
      
      
   def range(self,start,end):
       return_value = []
       compress_list = self.redis_handle.lrange(self.key, start, end)
       for data_compressed in compress_list:
          data = msgpack.unpackb(data_compressed)
          return_value.append(data)
       return return_value

class Stream_Writer(Redis_Stream):
       
   def __init__(self,redis_handle,  redis_key, data,cloud_handler,):
      super().__init__(redis_handle)
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = redis_key
      self.depth = data["depth"]
      self.add_pad = "~"

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       self.cloud_handler.delete(self.key)     

      
   def change_add_flag(self, state):
      if state == True:
          self.add_pad = ""
      else:
          self.add_pad = "~"
   
      
   def add_compress(self,id="*", data={} ):
       store_dictionary = {}
       if len(list(data.keys())) == 0:
           return
       print("stream write",self.key,data)
       for i , item in data.items():
      
           store_dictionary[i] = msgpack.packb(item)
       self.xadd(key = self.key, max_len=self.depth,id=id,data_dict=store_dictionary )
       self.cloud_handler.stream_write(id, self.depth, self.key, store_dictionary ) 
       
   
      

class Stream_Reader(Redis_Stream):
       
   def __init__(self,redis_handle, redis_key):
      super().__init__(redis_handle)
      self.redis_handle = redis_handle
      self.key = redis_key

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       self.cloud_handler.delete(self.key)     
      
      
   def xrange_compress(self,start_timestamp, end_timestamp , count=100):
       data_list = self.xrevrange(self.key,start_timestamp,end_timestamp, count)
       
       for i in data_list:
          return_item = {}
          for key, item in i["data"].items():
                        
              
              item = msgpack.unpackb(item)
      
              return_item[key] = item
          i["data"] = return_item
       return data_list

   def xrevrange_compress(self,start_timestamp, end_timestamp , count=100):
       data_list = self.xrevrange(self.key,start_timestamp,end_timestamp, count)
       
       for i in data_list:
          return_item = {}
          for key, item in i["data"].items():
                        
              
              item = msgpack.unpackb(item)
      
              return_item[key] = item
          i["data"] = return_item
       return data_list
   
       

       
class Generate_Handlers(object):
   
   def __init__(self,package,site_data  ):
       self.site_data = site_data
       self.package = package
       self.redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["redis_io_db"] , decode_responses=True)
       self.cloud_handler = Cloud_TX_Handler(self.redis_handle) 
       
   def get_redis_handle(self):
       return self.redis_handle   




         
   def construct_hash(self,data):
         assert(data["type"] == "HASH")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return  Redis_Hash_Dictionary( self.redis_handle,key,data,self.cloud_handler )


   def construct_stream_writer(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Writer(self.redis_handle,key,data,self.cloud_handler)
         
   def construct_stream_reader(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Reader(self.redis_handle,key)

   def construct_stream_list_writer(self,data):
         assert(data["type"] == "STREAM_LIST")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_List_Writer(self.redis_handle,key,data,self.cloud_handler)


   def construct_stream_list_reader(self,data):
         assert(data["type"] == "STREAM_LIST")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_List_Reader(self.redis_handle,key,data)

   def construct_job_queue_client(self,data):
         assert(data["type"] == "JOB_QUEUE")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Job_Queue_Client(self.redis_handle,key, data,self.cloud_handler )

   def construct_job_queue_server(self,data):
         assert(data["type"] == "JOB_QUEUE")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Job_Queue_Server(self.redis_handle,key,data,self.cloud_handler)

   def construct_rpc_client(self,data):
         assert(data["type"] ==  "RPC")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Redis_Rpc_Client(self.redis_handle,key,data)

   def construct_rpc_sever(self,data):
         assert(data["type"] ==  "RPC")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return RPC_Server(self.redis_handle,key,data )
    
if "__name__" == "__main__":
       redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =0, decode_responses=True)
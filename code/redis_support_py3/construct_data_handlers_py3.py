

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
    def __init__( self, redis_handle ,data, key ):
       self.data = data
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
                   input = msgpack.unpackb(input[1])  # 0 parameter is the queue
                   self.process_message(  input )
                       
            except:
                raise
 
    def process_message( self, input):

        id      = input["id"]
        method  =  input["method"]
        params  = input["params"]
        response = self.handler[method](params)
       
        self.redis_handle.lpush( id, msgpack.packb(response))        
        self.redis_handle.expire(id, 30)

      
      
 
class Redis_Hash_Dictionary( object ):
 
   def __init__(self,redis_handle,data, key,cloud_handler):
      self.data = data
      self.redis_handle = redis_handle
      self.key = key
      self.cloud_handler = cloud_handler

      
   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
           self.cloud_handler.delete(self.data,self.key)     
      
      
   def hset( self, field, data ):
   
      pack_data = msgpack.packb(data,use_bin_type = True )
      
      self.redis_handle.hset(self.key,field,pack_data)
      if self.cloud_handler != None:
         self.cloud_handler.hset(self.data,self.key,field,pack_data)     

   def hmset(self,dictionary_table):
       for i,items in dictionary_table.items():
          self.hset(i,items)
       
         
         
   def hget( self, field):
      
      pack_data = self.redis_handle.hget(self.key,field)
      
      if pack_data == None:
         return None
      
      return  msgpack.unpackb(pack_data,encoding='utf-8')
      

   def hgetall( self ):
      return_value = {}
      keys = self.redis_handle.hkeys(self.key)
      
      for field in keys:
        
         return_value[field] = self.hget(field)
     
      return return_value
      
   def hkeys(self):
       return self.redis_handle.hkeys(self.key)
   
   def hexists(self,field):
     return self.redis_handle.hexists(self.key,field)
   

   def hdelete(self,field):
       self.redis_handle.hdel(self.key,field)
       if self.cloud_handler != None:
           self.cloud_handler.hdel(self.data,self.key,field)
          
       

  
       
class Job_Queue_Client( object ):
 
   def __init__(self,redis_handle,data, key, depth, cloud_handler):
      self.data = data
      self.redis_handle = redis_handle
      self.key = key
      self.depth =  depth
      self.cloud_handler = cloud_handler

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
          self.cloud_handler.delete(self.data, self.key)     
      
      
   def delete(self, index ):
       if index < self.redis_handle.llen(self.key):
           self.redis_handle.lset(self.key, index,"__#####__")
           self.redis_handle.lrem(self.key, 1,"__#####__") 
           if self.cloud_handler != None:
               self.cloud_handler.list_delete(self.data,self,self.key,self.index)
      
   def length(self):
       return self.redis_handle.llen(self.key)   
      
   def push(self,data):
       pack_data =  msgpack.packb(data,use_bin_type = True )
       self.redis_handle.lpush(self.key,pack_data)
       self.redis_handle.ltrim(self.key,0,self.depth)
       if self.cloud_handler != None:
           self.cloud_handler.lpush(self.data, self.depth,self.key,pack_data)
         

 
class Job_Queue_Server( object ):
 
   def __init__(self,redis_handle,data, key,cloud_handler):
      self.data = data
      self.redis_handle = redis_handle
      self.key = key 
      
      self.cloud_handler = cloud_handler
 
   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
          self.cloud_handler.delete(self.data,self.key)     
 
 
   def length(self):
       return self.redis_handle.llen(self.key)
       
   def delete(self, index ):
       if index < self.redis_handle.llen(self.key):
           self.redis_handle.lset(self.key, index,"__#####__")
           self.redis_handle.lrem(self.key, 1,"__#####__") 
           if self.cloud_handler != None:
               self.cloud_handler.list_delete(self.data,self.key,self.index)
                

 
   def pop(self):
       pack_data = self.redis_handle.rpop(self.key)
       if self.cloud_handler != None:
          self.cloud_handler.rpop(self.data ,self.key)

       if pack_data == None:
          return False, None
       else:
         
          return True,msgpack.unpackb(pack_data,encoding='utf-8')
          
   def show_next_job(self):
       pack_data = self.redis_handle.lindex(self.key, -1)
       if pack_data == None:
          return False, None
       else:
          
          return True, msgpack.unpackb(pack_data,encoding='utf-8')


   
class Stream_List_Writer(object):
       
  
   def __init__(self,redis_handle, data, depth, key, cloud_handler):
      self.data = data
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = key
      self.depth = depth

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
           self.cloud_handler.delete(self.data, self.key)     
      
      
   def push(self,data):
       assert(type(data)== type(dict()) )
       if "timestamp" not in data:
          data["timestamp"] = time.time()
       pack_data =  msgpack.packb(data,use_bin_type = True )

       self.redis_handle.lpush(self.key,pack_data)
       self.redis_handle.ltrim(self.key,0,self.depth-1)
       if self.cloud_handler != None:
           self.cloud_handler.stream_list_write(self.data, self.depth, self.key, data )

       
class Stream_List_Reader(object):
       
   def __init__(self,redis_handle,data, key,cloud_handler):
      self.cloud_handler = cloud_handler
      self.data = data
      self.redis_handle = redis_handle
      self.key = key
     
   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
           self.cloud_handler.delete(self.data, self.key)     
   
   def length(self):
       return self.redis_handle.llen(self.key)
      
   def range(self,start,end):
       return_value = []
       pack_list = self.redis_handle.lrange(self.key, start,end)  #read most recent first
       
       for pack_data in pack_list:
          
          data = msgpack.unpackb(pack_data,encoding='utf-8')
          return_value.append(data)
       return return_value

   def t_range(self,recent_time_stamp,early_time_stamp, count,start_range, end_range ):
       test_count =  0
       if count == None:
          count = self.redis_handle.llen(self.key)
       trial_data = self.range(start_range,end_range)
       return_value = []
       for i in trial_data:
          ts = i["timestamp"]
          if ts > recent_time_stamp:
             continue
          if ts < early_time_stamp:
              break
          return_value.append(i)
          test_count +=1
          if test_count == count:
             break
       return return_value
       
'''
class Stream_Writer(Redis_Stream):
       
   def __init__(self,redis_handle, data,  redis_key,cloud_handler,):
      super().__init__(redis_handle)
      self.data = data
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = redis_key
      self.depth = data["depth"]
      self.add_pad = "~"

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
          self.cloud_handler.delete(self.data,self.key)     

      
   def change_add_flag(self, state):
      if state == True:
          self.add_pad = ""
      else:
          self.add_pad = "~"
   
      
   def add_compress(self,id="*", data={} ):
       store_dictionary = {}
       if len(list(data.keys())) == 0:
           return
       
       for i , item in data.items():
           
           store_dictionary[i] = base64.b64encode(json.dumps(item)).decode()
       self.xadd(key = self.key, max_len=self.depth,id=id,data_dict=store_dictionary )
       if self.cloud_handler != None:
           self.cloud_handler.stream_write(self.data,id, self.depth, self.key, store_dictionary ) 
       
   
      

class Stream_Reader(Redis_Stream):
       
   def __init__(self,redis_handle,data, redis_key):
      super().__init__(redis_handle)
      self.data = data
      self.redis_handle = redis_handle
      self.key = redis_key

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
           self.cloud_handler.delete(self.data, self.key)     
      
      
   def xrange_compress(self,start_timestamp, end_timestamp , count=100):
       data_list = self.xrange(self.key,start_timestamp,end_timestamp, count)
       
       for i in data_list:
          return_item = {}
          for key, item in i["data"].items():
                             
              item = base64.b64decode(item)
              item = msgpack.unpackb(item ,encoding='utf-8')
      
              return_item[key] = item
          i["data"] = return_item
       return data_list

   def xrevrange_compress(self,start_timestamp, end_timestamp , count=100):
       data_list = self.xrevrange(self.key,start_timestamp,end_timestamp, count)
       
       for i in data_list:
          return_item = {}
          for key, item in i["data"].items():
               
              item = base64.b64decode(item)
              item = msgpack.unpackb(item ,encoding='utf-8')
      
              return_item[key] = item
          i["data"] = return_item
       return data_list
   
       
'''
       
class Generate_Handlers(object):
   
   def __init__(self,package,site_data  ):
       self.site_data = site_data
       self.package = package
       self.redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["redis_io_db"] ) #, decode_responses=True)
       self.cloud_handler = Cloud_TX_Handler(self.redis_handle) 
       
   def get_redis_handle(self):
       return self.redis_handle   




         
   def construct_hash(self,data):
         assert(data["type"] == "HASH")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return  Redis_Hash_Dictionary( self.redis_handle,data,key,self.cloud_handler )

   '''
   # Taking these structures off line
   def construct_stream_writer(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Writer(self.redis_handle,key,data,self.cloud_handler)
         
   def construct_stream_reader(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Reader(self.redis_handle,data,key)
   '''
   def construct_stream_writer(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_List_Writer(self.redis_handle,data,key,self.cloud_handler,data["depth"])


   def construct_stream_reader(self,data):
         assert(data["type"] == "STREAM_")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_List_Reader(self.redis_handle,data,key,self.cloud_handler)

   def construct_job_queue_client(self,data):
         assert(data["type"] == "JOB_QUEUE")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Job_Queue_Client(self.redis_handle,key,data, data["depth"],self.cloud_handler )

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
    
if __name__== "__main__":
       redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =10, decode_responses=True) # test_db
       print("starting hash test ************************************************")
       hash_handler = Redis_Hash_Dictionary( redis_handle,data = {}, key = "__TEST__HASH__" , cloud_handler = None )
       dict_table = {"a":235,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       print("hash input",dict_table)
       hash_handler.hmset(dict_table)
       print("hash_output", hash_handler.hgetall())
       print("hash_keys",hash_handler.hkeys())
       print("hash_hexists(a)",hash_handler.hexists("a"))
       print("hash_hexists(z)",hash_handler.hexists("z"))
       print("hash_hdelete(a)",hash_handler.hdelete("a"))
       print("hash_keys",hash_handler.hkeys())
       print("hash_delete",hash_handler.delete())
       print("key exists",redis_handle.exists(hash_handler.key))
       print("hash test done**********************************************")
       
       print("staring job client test********************************************************")
       job_queue_client = Job_Queue_Client(  redis_handle,data = {},key = "__TEST__JOB__" , depth= 16, cloud_handler = None )
       job_queue_client.push(dict_table)
       job_queue_client.push(dict_table)
       job_queue_client.push(dict_table)
       print(job_queue_client.length())
       job_queue_client.delete(1)
       print(job_queue_client.length())
       job_queue_client.delete_all()
       print(redis_handle.exists(job_queue_client.key)) # should be false
       print("ending job client test********************************************************")
       print("starting job_queue server test ***********************************************")
       job_queue_server =Job_Queue_Server(  redis_handle,data = {}, key = "__TEST__JOB__",cloud_handler = None)
       dict_table_1 = {"a":1,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       dict_table_2 = {"a":2,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       dict_table_3 = {"a":3,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       dict_table_4 = {"a":4,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       job_queue_client.push(dict_table_1) #0 first in job queue
       job_queue_client.push(dict_table_1) #1 
       job_queue_client.push(dict_table_2) # 2
       job_queue_client.push(dict_table_2) #3
       job_queue_client.push(dict_table_3) # 4
       job_queue_client.push(dict_table_3) # 5
       job_queue_client.push(dict_table_4) # 6
       job_queue_client.push(dict_table_4) # 7
       print(job_queue_server.length())
       print("show next job",job_queue_server.show_next_job())
       while True:
         return_values = job_queue_server.pop()
         print("poping job queue", return_values)
         if return_values[0] == False:
            break
            
       print("job queue length",job_queue_server.length())
       job_queue_client.push(dict_table_1) #0 first in job queue
       job_queue_client.push(dict_table_2) #1 
       job_queue_server.delete(-1)
       print("pop value",job_queue_server.pop())
       print("job queue length",job_queue_server.length())       
       print(job_queue_server.delete_all())  
       print("Done testing job sever *****************************************************************************")  
       print("Testing Stream Writer *******************************************************************************")
       stream_writer = Stream_List_Writer( redis_handle, {},depth = 64, key ="__STREAM__TEST__",cloud_handler = None )
       stream_writer.push(dict_table_1)
       stream_writer.delete_all()
       for i in range(0,16):
          stream_writer.push(dict_table_1)
          stream_writer.push(dict_table_2)
          stream_writer.push(dict_table_3)
          stream_writer.push(dict_table_4)
          
       print("******** ending stream writer test")
       print("******** starting stream reader list")
       print("testing stream reader test ")
       stream_reader = Stream_List_Reader( redis_handle,{},key = "__STREAM__TEST__",cloud_handler = None )
       print("stream length",stream_reader.length())
       print("stream_read 0 -- 64",stream_reader.range(0,stream_reader.length()))
       print("\n\n\n\n doing t_range \n\n\n\n")
       print("t_read", stream_reader.t_range(time.time(),time.time()-.25,count = 10,start_range = 0 , end_range = 50 ))
       stream_writer.push(dict_table_4)
       print("testing for stream limit should be 64", stream_reader.length())
       print("******* ending stream reader list")
       
       


   
 


import redis
import time
import base64
import msgpack


from .redis_stream_utilities_py3 import Redis_Stream
from .cloud_handlers_py3 import Cloud_TX_Handler
from .influxdb_driver.influxdb_driver_py3 import Influx_Handler

class Field_Not_Defined(Exception):
    pass       
      
class FIELD_TYPE_ERROR(Exception):
   pass
   
class Redis_RPC_Client(object):

   def __init__( self,redis_handle,data,rpc_queue ):
       self.redis_handle = redis_handle
       self.data = data
       self.rpc_queue = rpc_queue
   
     
       
   def send_rpc_message( self, method,parameters,timeout=30 ):
        request = {}
        request["method"] = method
        request["params"] = parameters
        request["id"]   = str(uuid.uuid1())    
        request_msg = msgpack.packb( request )
        self.redis_handle.delete(request["id"] )
        self.redis_handle.lpush(self.redis_rpc_queue, request_msg)
        data =  self.redis_handle.brpop(request["id"],timeout = timeout )
        
        self.redis_handle.delete(request["id"] )
        if data == None:
            raise Rpc_No_Communication("No Communication with Modbus Server")
        response = msgpack.unpackb(data[1])
        
        return response
                
class RPC_Server(object):
    def __init__( self, redis_handle ,data, redis_rpc_queue ):
       self.data = data
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       self.handler = {}
       self.redis_handle.delete(redis_rpc_queue)
       self.timeout_function = None
       #self.timeout_value  = data["timeout"]
       self.timeout_value = 5.0 # five seconds

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

class String_Field(object):
   def __init__(self,handler):
       self.handler = handler
       
   def hget(self,setup,field):
      result = self.handler.hget( field)
      if result == None:
        result = setup["init_value"]
      return str(result)
      
   def hset(self,setup,field,data):
       self.handler.hset(field,str(data))
       
class Float_Field(object):
   def __init__(self,handler):
       self.handler = handler
       
   def hget(self,setup,field):
      result = self.handler.hget(field)
      if result == None:
        result = setup["init_value"]
      return float(result)
      
   def hset(self,setup,field,data):

       self.handler.hset(field,float(data))
 

 
class Binary_Field(object):
   def __init__(self,handler):
       self.handler = handler
       
   def hget(self,setup,field):
      result = self.handler.hget(field)
      if result == None:
         result = setup["init_value"]
      return bool(result) 
      
   def hset(self,setup,field,data):
       if data == 0:
          data = False
       if data == 1:
          data = True
       if isinstance(data,bool):
           self.handler.hset(field,data)
       else:
         raise ValueError("not a boolean type "+str(data))
 

class List_Field(object):
   def __init__(self,handler):
       self.handler = handler
       
   def hget(self,setup,field):
      result = self.handler.hget(field)
      if result == None:
         result = setup["init_value"]
      return bool(result) 
      
   def hset(self,setup,field,data):
       if isinstance(data, list):
           self.handler.hset(field,data)
       else:
         raise ValueError("not a list type "+str(data))
 

 
class Dictionary_Field(object):
   def __init__(self,handler):
       self.handler = handler
       
   def hget(self,setup,field):
      
      temp = self.handler.hget(field)
      if temp == None:
        result = setup["fields"]
      else:
         result = {}
         for i in setup["fields"].keys():
            if i in temp:
               
               result[i] = temp[i]
            else:
               result[i] = setup["fields"][i]
               
      return result
      
   def hset(self,setup,field,data):
       temp = {}
       for i in setup["fields"].keys():
         if i in data:
            temp[i] = data[i]
         else:
            raise ValueError("key: "+str(i)+" not in "+str(data))
       self.handler.hset(field,temp)

                 
class Managed_Redis_Hash(object):
   def __init__(self,redis_handle,data, key,cloud_handler):
        self.handler = Redis_Hash_Dictionary(redis_handle,data, key,cloud_handler)
        self.fields = data["fields"]
        self.field_handlers = {}
        self.field_handlers["string"] = String_Field(self.handler)
        self.field_handlers["float"] = Float_Field(self.handler)
        self.field_handlers["binary"] = Binary_Field(self.handler)
        self.field_handlers["list"]   = List_Field(self.handler)
        self.field_handlers["dictionary"] = Dictionary_Field(self.handler)      
        self.validate_graph_data()
        self.sanitize_keys()
 

   def get_rid_of_bad_keys(self):
       keys = self.handler.hkeys()
       for i in keys:
         if i not in self.fields:
            print("key "+str(i)+" doesnot belong")
            self.handler.hdelete(i)
            
   def sanitize_keys(self):
       
       for key,item in self.fields.items():
         temp = self.hget(key)
         self.hset(key,temp)
                
       
   def validate_graph_data(self):
       for i,item in self.fields.items():

          instance_type = item["type"]
          if instance_type not in self.field_handlers:
             raise ValueError("improper type:  "+str(key)+"  "+str(item))          
       
   def hget(self,field):
       if field in self.fields:
          item = self.fields[field]
          return self.field_handlers[item["type"]].hget(item,field)
       else:
          raise ValueError("field is not registered:  "+field)
          
   def hget_all(self):
      result = {}
      for i,item in self.fields.items():
         result[i] = self.field_handlers[item["type"]].hget(item,i)
      return result
      
   def hset(self,field,data):
      if field in self.fields:
          item = self.fields[field]
          self.field_handlers[item["type"]].hset(item,field,data)
      else:
          raise ValueError("field is not registered:  "+field)
           
 
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
      
      if self.redis_handle.hget(self.key,field)== pack_data: # donot propagte identical values
         return
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
         try:
            new_field = field.decode('utf-8')
         except:
            new_field = field
         return_value[new_field] = self.hget(field)
     
      return return_value
      
   def hkeys(self):
       binary_list = self.redis_handle.hkeys(self.key)
       return_list = []
       for i in binary_list:
          return_list.append(i.decode())
       return return_list
   
   def hexists(self,field):
     return self.redis_handle.hexists(self.key,field)
   

   def hdelete(self,field):
       self.redis_handle.hdel(self.key,field)
       if self.cloud_handler != None:
           self.cloud_handler.hdel(self.data,self.key,field)
          
   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
          self.cloud_handler.delete(self.data, self.key)          

  
       
class Job_Queue_Client( object ):
 
   def __init__(self,redis_handle,data, key,  cloud_handler):
      self.data = data
      self.redis_handle = redis_handle
      self.key = key
      self.depth =  data["depth"]
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


   def list_range(self,start,stop):
      
      list_data =  self.redis_handle.lrange(self.key,0,-1)
     
      if list_data == None:
         return None
      return_value = []
      for pack_data in list_data:
        return_value.append(msgpack.unpackb(pack_data,encoding='utf-8'))
      return return_value
      
   def pop(self):
       pack_data = self.redis_handle.rpop(self.key)
        
       if self.cloud_handler != None:
          if pack_data != None:
              self.cloud_handler.rpop(self.data ,self.key)

       if pack_data == None:
          return False, None
       else:
         
          return True,msgpack.unpackb(pack_data,encoding='utf-8')     
   def push(self,data):
       pack_data =  msgpack.packb(data,use_bin_type = True )
       self.redis_handle.lpush(self.key,pack_data)
       self.redis_handle.ltrim(self.key,0,self.depth)
       if self.cloud_handler != None:
           self.cloud_handler.lpush(self.data, self.depth,self.key,pack_data)
           
   def delete_jobs(self,data):
       for i in data:
         self.redis_handle.lset(self.key,i,"__DELETE_ME__")
       self.redis_handle.lrem(self.key,0,"__DELETE_ME__")
         

 
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
          if pack_data != None:
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

   def push_front(self,data):
       pack_data =  msgpack.packb(data,use_bin_type = True )
       self.redis_handle.rpush(self.key,pack_data)
       self.redis_handle.ltrim(self.key,0,self.depth)
       if self.cloud_handler != None:
           self.cloud_handler.lpush(self.data, self.depth,self.key,pack_data)


'''  
class Stream_List_Writer(object):
       
  
   def __init__(self,redis_handle, data, key, cloud_handler):
      self.data = data
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = key
      self.depth = data["depth"]


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
       self.redis_handle.ltrim(self.key,0,self.depth)
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
       

class Stream_Redis_Writer(Redis_Stream):
       
   def __init__(self,redis_handle,   data,key,cloud_handler):
      super().__init__(redis_handle)
      
      self.data = data
     
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = key
      self.depth = data["depth"]
      self.add_pad = "~"
      self.redis_stream = Redis_Stream(redis_handle)

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
          self.cloud_handler.delete(self.data,self.key)     

      
   def change_add_flag(self, state):
      if state == True:
          self.add_pad = ""
      else:
          self.add_pad = "~"



   def push(self,id="*", data={} ):
       store_dictionary = {}
       if len(list(data.keys())) == 0:
           return
       packed_data  =msgpack.packb(data,use_bin_type = True )
       out_data = {}
       out_data["data"] = packed_data
       self.xadd(key = self.key, max_len=self.depth,id=id,data_dict=out_data )

       if self.cloud_handler != None:
           self.cloud_handler.stream_write(self.data,  self.depth,id, self.key, out_data ) 
       
  
      

class Stream_Reader(Redis_Stream):
       
   def __init__(self,redis_handle,data, key):
      super().__init__(redis_handle)
      self.data = data
      self.redis_handle = redis_handle
      self.key = key

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
           self.cloud_handler.delete(self.data, self.key)     
      
      
   def range(self,start_timestamp, end_timestamp , count=100):
       if isinstance(start_timestamp,str) == False:
           start_timestamp = int(start_timestamp*1000)
       if isinstance(end_timestamp,str) == False:
           end_timestamp = int(end_timestamp*1000)

       data_list = self.xrange(self.key,start_timestamp,end_timestamp, count)

       return data_list

   def revrange(self,start_timestamp, end_timestamp , count=100):
       if isinstance(start_timestamp,str) == False:
           start_timestamp = int(start_timestamp*1000)
       if isinstance(end_timestamp,str) == False:
           end_timestamp = int(end_timestamp*1000)


       data_list = self.xrevrange(self.key,start_timestamp,end_timestamp, count)

       return data_list
     
       
'''
class Influx_Stream_Writer(object):

   def __init__(self,influx_handler,data):
       self.influx_handler = influx_handler
       self.measurement = data["measurement"]
       self.data = data 
       
   def push(self,data,tags = {}): 
       influx_data = {}   
       tags["site"] = str(self.data["site"])
       tags["index"] = str(self.data["index"])
       influx_data["fields"] = data
       influx_data["measurement"] = self.measurement

       print("influx write",self.influx_handler.write_point(influx_data,tags))
       
class Stream_Redis_Writer(Redis_Stream):
       
   def __init__(self,redis_handle,   data,key,cloud_handler):
      super().__init__(redis_handle)
      
      self.data = data
     
      self.redis_handle = redis_handle
      self.cloud_handler = cloud_handler
      self.key = key
      self.depth = data["depth"]
      self.add_pad = "~"
      self.redis_stream = Redis_Stream(redis_handle)
      
   def save(self):
       self.redis_handle.save()

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
          self.cloud_handler.delete(self.data,self.key)     

      
   def change_add_flag(self, state):
      if state == True:
          self.add_pad = ""
      else:
          self.add_pad = "~"



   def push(self,data={} ,id="*" ):
       
       
       if len(list(data.keys())) == 0:
           return
       packed_data  =msgpack.packb(data,use_bin_type = True )
       out_data = {}
       out_data["data"] = packed_data
       self.xadd(key = self.key, max_len=self.depth,id=id,data_dict=out_data )

       if self.cloud_handler != None:
           self.cloud_handler.stream_write(self.data,  self.depth,id, self.key, out_data ) 
       
class Stream_Redis_Reader(Redis_Stream):
       
   def __init__(self,redis_handle,data, key):
      super().__init__(redis_handle)
      self.data = data
      self.redis_handle = redis_handle
      self.key = key

   def delete_all( self ):
       self.redis_handle.delete(self.key)
       if self.cloud_handler != None:
           self.cloud_handler.delete(self.data, self.key)     
      
      
   def range(self,start_timestamp, end_timestamp , count=100):
       if isinstance(start_timestamp,str) == False:
           start_timestamp = int(start_timestamp*1000)
       if isinstance(end_timestamp,str) == False:
           end_timestamp = int(end_timestamp*1000)

       data_list = self.xrange(self.key,start_timestamp,end_timestamp, count)

       return data_list

   def revrange(self,start_timestamp, end_timestamp , count=100):
       
       if isinstance(start_timestamp,str) == False:
           start_timestamp = int(start_timestamp*1000)
       if isinstance(end_timestamp,str) == False:
           end_timestamp = int(end_timestamp*1000)


       data_list = self.xrevrange(self.key,start_timestamp,end_timestamp, count)
       

       return data_list 
             
class Generate_Handlers(object):
   
   def __init__(self,package,qs ):
      
       self.package = package
       self.redis_handle = qs.get_redis_data_handle()
       
       
       '''
       redis_handle_password = redis.StrictRedis(site_data["host"], site_data["port"], db=site_data["redis_password_db"], decode_responses=True)
       self.influx_server = redis_handle_password.hget("influx_local_server","server")
       self.influx_user = redis_handle_password.hget("influx_local_server","user")
       self.influx_password = redis_handle_password.hget("influx_local_server","password")
       self.influx_retention = redis_handle_password.hget("influx_local_server", "retention" )
       self.influx_database = redis_handle_password.hget("influx_local_server","database" )
       self.influx_handler = None
       '''
       self.cloud_handler = Cloud_TX_Handler(self.redis_handle) 
       
   def get_redis_handle(self):
       return self.redis_handle   


   def construct_influx_handler(self):
 
       self.influx_handler =  Influx_Handler(self.influx_server,
                                             self.influx_user,
                                             self.influx_password,
                                             self.influx_database,
                                             self.influx_retention)
       self.influx_handler.switch_database(self.influx_database)
         
   def construct_hash(self,data):
         assert(data["type"] == "HASH")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         
         return  Redis_Hash_Dictionary( self.redis_handle,data,key,self.cloud_handler )

   def construct_managed_hash(self,data):
         assert(data["type"] == "MANAGED_HASH")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         
         return  Managed_Redis_Hash( self.redis_handle,data,key,self.cloud_handler)
   


   def construct_stream_writer(self,data):
         return self.construct_redis_stream_writer(data)
         
         assert(data["type"] == "STREAM")
          
         
         if self.influx_handler == None:
            self.construct_influx_handler()
            
         return Influx_Stream_Writer(self.influx_handler,data)


   def construct_redis_stream_writer(self,data):
         assert(data["type"] == "STREAM_REDIS")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Redis_Writer(self.redis_handle,data,key,self.cloud_handler)
         
     
   def construct_redis_stream_reader(self,data):
         assert(data["type"] == "STREAM_REDIS")
         
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_Redis_Reader(self.redis_handle,data,key)
   '''
   def construct_stream_writer(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Stream_List_Writer(self.redis_handle,data,key,self.cloud_handler)
  
   def construct_stream_reader(self,data):
         assert(data["type"] == "STREAM")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         retun Stream_List_Reader(self.redis_handle,data,key,self.cloud_handler)
   '''
   def construct_job_queue_client(self,data):
         assert(data["type"] == "JOB_QUEUE")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Job_Queue_Client(self.redis_handle,data,key,self.cloud_handler )
                                                                                                                                                                                                                                                                                 
   def construct_job_queue_server(self,data):
         assert(data["type"] == "JOB_QUEUE")
         key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
         return Job_Queue_Server(self.redis_handle,data,key,self.cloud_handler)

   def construct_rpc_client(self,data):
         assert(data["type"] ==  "RPC_CLIENT")
         key = self.package["namespace"]+"["+data["name"] +"]"
         return Redis_RPC_Client(self.redis_handle,data,key)

   def construct_rpc_sever(self,data):
         assert(data["type"] ==  "RPC_SERVER")
         key = self.package["namespace"]+"["+data["name"] +"]"
         return RPC_Server(self.redis_handle,data,key )
    
if __name__== "__main__":
       redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =0) # test_db
       print("starting hash test ************************************************")
       '''
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
       print("hash_delete",hash_handler.delete_all())
       print("key exists",redis_handle.exists(hash_handler.key))
       print("hash test done**********************************************")
       
       print("staring job client test********************************************************")
       
       job_queue_client = Job_Queue_Client(  redis_handle,data = {"depth":16},key = "__TEST__JOB__" , cloud_handler = None )
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
       stream_writer = Stream_List_Writer( redis_handle, {"depth":64}, key ="__STREAM__TEST__",cloud_handler = None )
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
       '''
       dict_table_1 = {"a":1,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       dict_table_2 = {"a":2,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       dict_table_3 = {"a":3,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}
       dict_table_4 = {"a":4,"b":333,"c":"test","d":b'1234', "e":[1,2,3,[4,5],6,7], "f":{"a":{"b":1} }}


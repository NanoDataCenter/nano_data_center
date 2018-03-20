
import json
import redis
import time

from .redis_stream_utilities_py3 import Redis_Stream
from .redis_rpc_client_py3 import Redis_Rpc_Client
from .redis_rpc_server_py3 import Redis_Rpc_Server

class Field_Not_Defined(Exception):
    pass       
      
class FIELD_TYPE_ERROR(Exception):
   pass
 
class RPC_Server(Redis_Rpc_Server):
    def __init__( self, redis_handle , redis_rpc_queue,depth,timeout ):
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       self.handler = {}
       self.redis_handle.delete(redis_rpc_queue)
       self.timeout_function = None
       self.timeout_value  = timeout


    def add_time_out_function(self,time_out_function):
       self.timeout_function = time_out_function
       
      

      
 
class Redis_Hash_Dictionary( object ):
 
   def __init__(self,redis_handle, name):
      self.redis_handle = redis_handle
      self.key = name

   def hset( self, field, data ):
      self.redis_handle.hset(self.key,field,json.dumps(data))      

   def hget( self, field):
      return json.loads(self.redis_handle.hget(self.key,field))

   def hgetall( self ):
      return_value = {}
      data = self.redis_handle.hgetall(self.key)
      for key, item in data.items():
         return_value[key] = json.loads(item)
      return return_value
      
   def hkeys(self):
       return self.redis_handle.hkeys(self.key)
   
   def hexists(self,field):
     return self.redis_handle.hexists(self.key,field)
   
   
   def htrim(self,fields):
     keys = self.redis_handle.keys(self.key)
     extraneous_keys = list((set(fields)-set(keys)))
     for i in extraneous_keys:
         self.redis_handle.hdel(self,key,i)     
     
class Job_Queue_Client( object ):
 
   def __init__(self,redis_handle, name, depth):
      self.redis_handle = redis_handle
      self.key = name
      self.depth = depth
      
      
   def push(self,data):
       json_data = json.dumps(data)
       self.redis_handle.lpush(self.key,json_data)
       self.redis_handle.ltrim(self.key,0,self.depth)

 
class Job_Queue_Server( object ):
 
   def __init__(self,redis_handle, name, depth):
      self.redis_handle = redis_handle
      self.key = name
      self.depth = depth
      self.redis_handle.delete(self.key)
 
   def pop(self):
       json_data = self.redis_handle.rpop(self.key)
       if json_data == None:
          return False, None
       else:
          return True, json.loads(json_data)

class  List_Handler(object):

   def __init__(self,redis_handle,name,length):
       self.redis_handle = redis_handle
       self.key = name
       self.length = length 
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
       
  
   def __init__(self,redis_handle, key, depth):
     
      self.redis_handle = redis_handle
      self.key = key
      self.depth = depth
      
      
   def push(self,data):
       json_data = json.dumps(data)
       self.redis_handle.lpush(self.key,json_data)
      
       self.redis_handle.ltrim(self.key,0,self.depth-1)
       
class Stream_List_Reader(object):
       
   def __init__(self,redis_handle, redis_key, depth):
      
      self.redis_handle = redis_handle
      self.key = redis_key
      self.depth = depth
      
      
   def range(self,start,end):
       return_value = []
       data_json_list = self.redis_handle.lrange(self.key, start, end)
       for data_json in data_json_list:
          data = json.loads(data_json)
          return_value.append(data)
       return return_value

class Stream_Writer(Redis_Stream):
       
   def __init__(self,redis_handle, redis_key, depth):
      super().__init__(redis_handle)
      self.redis_handle = redis_handle
      self.key = redis_key
      self.depth = depth
      
   def change_add_flag(self, state):
      if state == True:
          self.add_pad = ""
      else:
          self.add_pad = "~"
   
      
   def add(self,id="*", data={} ):
       store_dictionary = {}
       for i , item in data.items():
           store_dictionary[i] = json.dumps(item)
       self.xadd(key = self.key, max_len=self.depth,id=id,data_dict=store_dictionary )
       
   
      

class Stream_Reader(Redis_Stream):
       
   def __init__(self,redis_handle, redis_key, depth):
      super().__init__(redis_handle)
      self.redis_handle = redis_handle
      self.key = redis_key
      self.depth = depth
      
      
   def xrange_json(self,start_timestamp, end_timestamp , count=100):
       return_value = []
       data_json = self.xrange(self.key,start_timestamp,end_timestamp, count)
       
       for i in data_json:
          return_item = {}
          for key, item in i["data"].items():
              return_item[key] = json.loads(item)
          i["data"] = return_item
       return data_json


       
class Redis_Package_Handler(object):
   
   def __init__(self,parent,package_name  ):
       self.redis_name = parent.package_ctr_name+"[PACK:"+package_name+"]"
       self.parent = parent
       self.redis_handle = parent.redis_handle
       self.package_exists = self.redis_handle.exists(self.redis_name)
       
       
   
   def verify_package(self):
       pass
       
   def list_fields(self):
       return self.redis_handle.hgetall(self.redis_name)

   def verify_package_is_a_dictionary(self):
       if self.redis_handle.type(self.redis_name) != "hash":
           self.redis_handle.delete(self.redis_name)      
       
   def delete_package(self):
      
       data_set = self.redis_handle.hgetall(self.redis_name)
       
       for key,json_data in data_set.items():

          data = json.loads(json_data)
          self.redis_handle.delete(data["redis_key"])
      
       self.redis_handle.delete(self.redis_name)
      
   def generate_hash(self,name ):
       self.verify_package_is_a_dictionary()

       redis_key = self.redis_name+"[HASH:"+name+"]"
       data = {"type":"HASH","redis_key":redis_key}
       json_data = json.dumps(data)
       self.redis_handle.hset(self.redis_name,name,json_data)
      
       
   def generate_job_queue(self,name,depth):
       self.verify_package_is_a_dictionary()
       redis_key = self.redis_name+"[JOB_QUEUE:"+name+"]"
       data = {"type":"JOB_QUEUE","depth":depth,"redis_key":redis_key}
       json_data = json.dumps(data)
       self.redis_handle.hset(self.redis_name,name,json_data)
       
       
       
       
   def generate_rpc(self,name,depth,timeout):
       self.verify_package_is_a_dictionary()
       redis_key = self.redis_name+"[RPC:"+name+"]"
       data = {"type":"RPC","depth":depth,"redis_key":redis_key,"timeout":timeout}
       json_data = json.dumps(data)
       self.redis_handle.hset(self.redis_name,name,json_data)
 
   def  generate_stream_list(self,name,depth):
       self.verify_package_is_a_dictionary()
       redis_key = self.redis_name+"[STREAM_LIST:"+name+"]"
       data = {"type":"STREAM_LIST","depth":depth,"redis_key":redis_key}
       json_data = json.dumps(data)
       self.redis_handle.hset(self.redis_name,name,json_data) 
       
       
   def generate_stream(self,name,depth):
       self.verify_package_is_a_dictionary()
       redis_key = self.redis_name+"[STREAM:"+name+"]"
       data = {"type":"STREAM","depth":depth,"redis_key":redis_key}
       json_data = json.dumps(data)
       self.redis_handle.hset(self.redis_name,name,json_data)
 

   def generate_list(self,name,length):
       self.verify_package_is_a_dictionary()
       redis_key = self.redis_name+"[LIST:"+name+"]"
       data = {"type":"LIST","length":length,"redis_key":redis_key}
       json_data = json.dumps(data)
       self.redis_handle.hset(self.redis_name,name,json_data)
 
   
   def get_list_handler(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "LIST":
          raise FIELD_TYPE_ERROR(data["type"])
      return  List_Handler( self.redis_handle,data["redis_key"],data["length"] )
      
   def get_stream_handler(self,name):
      pass
      
   def get_hash_handler(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "HASH":
          raise FIELD_TYPE_ERROR(data["type"])
      return  Redis_Hash_Dictionary( self.redis_handle,data["redis_key"] )
 

      
   def get_job_queue_client(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "JOB_QUEUE":
          raise FIELD_TYPE_ERROR(data["type"])

      return Job_Queue_Client( self.redis_handle,data["redis_key"],data["depth"] )
 
  
      
   def get_job_queue_server(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "JOB_QUEUE":
          raise FIELD_TYPE_ERROR(data["type"])

      return Job_Queue_Server( self.redis_handle,data["redis_key"],data["depth"] )
      
      
   def get_rpc_client(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "RPC":
          raise FIELD_TYPE_ERROR(data["type"])

      return Redis_Rpc_Client(self.redis_handle,data["redis_key"] )
      
   def get_rpc_server(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "RPC":
          raise FIELD_TYPE_ERROR(data["type"])
      return RPC_Server(self.redis_handle, depth = data["depth"],redis_rpc_queue = data["redis_key"],timeout = data["timeout"])
      
   
   def get_stream_reader_list(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "STREAM_LIST":
          raise FIELD_TYPE_ERROR(data["type"])

      return Stream_List_Reader(self.redis_handle, redis_key = data["redis_key"],depth = data["depth"])
       
   def get_stream_writer_list(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "STREAM_LIST":
          raise FIELD_TYPE_ERROR(data["type"])

      return Stream_List_Writer(self.redis_handle,key =  data["redis_key"],depth = data["depth"])
       
   def get_stream_reader_stream(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "STREAM":
          raise FIELD_TYPE_ERROR(data["type"])

      return Stream_Reader(self.redis_handle, data["redis_key"],data["depth"])
      
      
   def get_stream_writer_stream(self,name):
      keys = self.redis_handle.hkeys(self.redis_name)
      if name not in keys:
           raise Field_Not_Defined(name)      
      
      data = json.loads(self.redis_handle.hget(self.redis_name,name))
      if data["type"] != "STREAM":
          raise FIELD_TYPE_ERROR(data["type"])

      return Stream_Writer(self.redis_handle, data["redis_key"],data["depth"])
           

class Redis_Package_Controller(object):
   
   def __init__(self,redis_configuration ):
       
       redis_server_ip = redis_configuration["host"]
       port            = redis_configuration["port"]
       db              = redis_configuration["redis_io_db"]
       self.redis_handle  = redis.StrictRedis( host = redis_server_ip, port = port, db =db , decode_responses=True)
  
       self.package_ctr_name = "[PACK_CTRL:]"
  
       if self.redis_handle.exists(self.package_ctr_name) :
           if self.verify_package_controller() == True:
              self.state = True
           else:
              self.state = False
              
       else:
           self.state = True
           
           
   def verify_package_controller(self):
       return_value = True
       for i in self.redis_handle.hkeys(self.package_ctr_name):
           package = Redis_Package_Handler( self, i)
           package.verify_package()
           
        
        
                   
       
   def list_packages(self):
       if self.redis_handle.exists(self.package_ctr_name) :
           return self.redis_handle.hkeys( self.package_ctr_name)
       else:
           return []       
       
       
       
       
   def delete_package(self,name):      
       if self.redis_handle.hexists(self.package_ctr_name, name)  == True:          
           package = Redis_Package_Handler( self, name )
           package.delete_package()
           self.redis_handle.hdel(self.package_ctr_name,name)
          
      
       
   def open_package(self,package_name):
       self.redis_handle.hset(self.package_ctr_name,package_name,"TBD")
       return Redis_Package_Handler( self, package_name)
 
       
       
   
      
if __name__ == "__main__":
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
    
    package_controller = Redis_Package_Controller(redis_site)
   
    x = package_controller.open_package("test_package")
    
    x.generate_hash("hash_1")
    
    x.generate_job_queue("job_1",5)
    x.generate_rpc("rpc_1",5,timeout= 15)
    x.generate_stream("stream_1",10)
    x.generate_stream_list("stream_list_1",10)
    x.generate_list("list_1",10) 
  
  
    hash_handler = x.get_hash_handler("hash_1")
    
    hash_handler.hset("field_1",1)
    hash_handler.hset("field_2",2)
    hash_handler.hset("field_3",3)
    print(hash_handler.hgetall())
    print(hash_handler.hget("field_1"))
    print(hash_handler.hget("field_2"))
    print(hash_handler.hget("field_3"))
   
    print(hash_handler.hkeys())   
    
    list_handler = x.get_list_handler("list_1")
    for i in range(0,10):
       list_handler.lset(i,i)
    for i in range(0,10):
       print(list_handler.lget(i))
    print(list_handler.lrange(0,5))

    job_queue_server = x.get_job_queue_server("job_1")
    job_queue_client = x.get_job_queue_client("job_1")
    print("testing job_queue_server")
    print("depth of job queue is only 5")
    for i in range(0,11):
        job_queue_client.push([i,i])
        
    for i in range(0,11):
       print(job_queue_server.pop())
       
    
    
    rpc_client = x.get_rpc_client("rpc_1")
    rpc_server = x.get_rpc_server("rpc_1")
    print("testing rpc structures later")
   
    stream_writer = x.get_stream_writer_stream("stream_1")
    stream_reader = x.get_stream_reader_stream("stream_1")
    print("testing stream structure")
    timestamp = time.time()*1000.
    stream_writer.change_add_flag(False)
    for i in range(0,11):
       stream_writer.add(data={"x":i,"y":i*2})
       print(i)
       time.sleep(.2)
       
    
    y = stream_reader.xrange_json(timestamp,time.time()*1000,count = 1000 ) 
    print("result length",len(y))
    print(y)
     
    stream_list_writer = x.get_stream_writer_list("stream_list_1")
    stream_list_reader = x.get_stream_reader_list("stream_list_1")
    for i in range(0,21):
       stream_list_writer.push(data={"x":i,"y":i*2})
       print(i)
       
    y = stream_list_reader.range(0,100 ) 
    print(y)
    
    #package_controller.delete_package("test_package")
    
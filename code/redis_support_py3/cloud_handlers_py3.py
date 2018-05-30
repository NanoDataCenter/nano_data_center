import base64
import redis
import msgpack
import json
from .redis_stream_utilities_py3 import Redis_Stream

class Send_Object(object):
   def __init__(self, redis_handle, transport_queue, queue_depth ):
       self.redis_handle = redis_handle
       self.transport_queue = transport_queue
       self.queue_depth = queue_depth
       
       


   def send(self,action, **kwargs):
       kwargs["ACTION"] = action
       
       
       self.redis_handle.lpush(self.transport_queue,kwargs )
       self.redis_handle.ltrim(self.transport_queue, 0,self.queue_depth)
       
   def length(self):
       return self.redis_handle.llen(self.transport_queue)
       
   def extract(self,maxlength = 20):
       length = self.redis_handle.llen(self.transport_queue)
       if length > maxlength:
         length = maxlength
       return_list = []
       for i in range(0,length):
           return_list.append(self.redis_handle.rpop(self.transport_queue))
       return_value = msgpack.packb(return_list, use_bin_type = True)
       return return_value
         
       
       

class Cloud_TX_Handler(Send_Object):

   def __init__(self, redis_handle, transport_queue = "_TRANSPORT_QUEUE_" , transport_depth = 128 ):
       Send_Object.__init__(self,redis_handle,transport_queue,transport_depth)
       self.redis_handle = redis_handle

   def check_forwarding(self, data):  # do not forward data structures unless specified in the "forward" field
       if  "forward" in data:
           if data["forward"] == True:
              return True
       return False

   def delete(self,forward_data,key):
       if self.check_forwarding(forward_data):
           self.send("DEL",key=key)
 

 
   def hset(self,forward_data,key,field,data):
       if self.check_forwarding(forward_data):
           self.send("HSET",key=key,field=field,data = data )
       
   def hdel(self,forward_dat,key,field):
       if self.check_forwarding(forward_dat):
           self.send("HDEL",key=key,field=field)
       
   def lpush(self,forward_data,depth, key, data):
       if self.check_forwarding(forward_data):
           self.send("LPUSH",key=key,depth=depth,data = data)
       
   def list_delete(self, forward_dat,key,index):
       if self.check_forwarding(forward_dat):
           self.send("LIST_DELETE",key=key,index = index)
       
   def rpop(self,forward_dat,key):
       if self.check_forwarding(forward_dat):
           self.send("RPOP",key=key)
       
   def stream_write(self,forward_dat,depth, id, key,  store_dictionary_pack ):
       if self.check_forwarding(forward_dat):
           self.send("STREAM_WRITE",id=id,key=key,depth=depth , store_dictionary = store_dictionay_pack )
       
   def stream_list_write(self, forward_dat,depth, key,data ):
       if self.check_forwarding(forward_dat):
           self.send("STREAM_LIST_WRITE", key=key,depth =depth,data = data)
       
       
class Cloud_RX_Handler(object):

   def __init__(self,redis_handle,*args):
     
      self.redis_handle = redis_handle
      self.data_handlers = {}
      self.data_handlers["DEL"] = self.delete
    
      self.data_handlers["HSET"] = self.hset
      self.data_handlers["HDEL"] = self.hdel
      self.data_handlers["LPUSH"] = self.lpush
      self.data_handlers["LIST_DELETE"] = self.list_delete
      self.data_handlers["RPOP"] = self.rpop
      self.data_handlers["STREAM_WRITE"] = self.stream_write
      self.data_handlers["STREAM_LIST_WRITE"] = self.stream_list_write
      self.redis_stream =  Redis_Stream(redis_handle, exact_flag = False)
      self.file_path = {}
      self.file_path["APP_FILES"] =  "app_data_files/"
      self.file_path["SYS_FILES"] =  "system_data_files/"
      self.file_path["LIMIT"]  = "limit_data_files/"
 
      
   def unpack_remote_data( self, list_data ):
     
      for i_json in list_data:
          
          i = json.loads(i_json)
          
          action = i["ACTION"]
         
          if action in self.data_handlers:
              self.data_handlers[action](i)
          else:
              raise ValueError("Bad Action ID")

 
   def check_for_file(self,key):
       self.file_type = None
       fields = key.split("[FILE:")
       if len(fields) > 1:
          self.file_type = fields[1].split("]")[0]
          return True
       else:
          return False

   def delete(self,key):
       self.redis_handle.delete(key)
 

   def save_raw_file(self,path,name,data): 
       f = open(self.path + name, 'w')
       f.write(data)
 
 
              
   def hset(self,data):
       self.redis_handle.hset(data["key"],data["field"],data["data"])
       if self.check_for_file(data["key"]) == True:
   
          if self.file_type in self.file_path:
               path = self.file_path[self.file_type]
               file = data["field"]
               self.save_raw_file(file_path,file,json.dumps(data["data"]))
       
   def hdel(self,data):
      self.redis_handle.hdel(data["key"],data["field"] )
       
   def lpush(self, data):
       self.redis_handle.lpush(data["key"],data["data"])
       self.redis_handle.ltrim(data["key"],0, data["depth"])

       
   def list_delete(self,data):
       if self.redis_handle.exists(data["key"]) == True:
           self.redis_handle.lset(data["key"], data["index"],"__#####__")
           self.redis_handle.lrem(data["key"], 1,"__#####__") 

       
   def rpop(self,data):
       self.redis_handle.rpop(data["key"])
       
   def stream_write(self,data ):
       self.redis_stream.xadd(key = data["key"], max_len= data["depth"],id=data["id"],data_dict=data["store_dictionary"] )
   
   
   def stream_list_write(self, data ):
       self.redis_handle.lpush(data["key"],data["data"])
       self.redis_handle.ltrim(data["key"],0,data["depth"]-1)
    

if __name__ == "__main__":
    redis_handle = redis.StrictRedis(  db=10 , decode_responses=True)
    redis_handle.flushdb()
    cloud_rx =  Cloud_RX_Handler(redis_handle)
    cloud_tx = Cloud_TX_Handler(redis_handle)
    
    data_1 = json.dumps({"data":1})   
    data_2 = json.dumps({"data":2})
    data_3 = json.dumps({"data":3})
    data_4 = json.dumps({"data":41})
    data_5 = json.dumps({"data":5})
    data_6 = json.dumps({"data":6})
    
    dict_1 = {"data":7}
    
    cloud_tx.hset("hash_test","field_1",data_1)
    cloud_tx.hset("hash_test","field_2",data_2)
    cloud_tx.hdel("hash_test","field_1")
    cloud_tx.lpush(10,"job_queue_test", data_3)
    cloud_tx.lpush( 10,"job_queue_test", data_4) 
    cloud_tx.lpush( 10,"job_queue_test", data_5) 
    cloud_tx.list_delete( "job_queue_test",1)    
    cloud_tx.rpop("job_queue_test")
    cloud_tx.stream_write(10, "*", "stream_test",  dict_1 )
    cloud_tx.stream_list_write(10,"stream_list_test", data_6 )
    #
    # Read transport list
    # 
    remote_length = redis_handle.llen("_TRANSPORT_QUEUE_")
    remote_list = []
    for i in range(0,remote_length):
        remote_list.append(redis_handle.lpop("_TRANSPORT_QUEUE_"))
        
  
    
    remote_list.reverse()
 
    cloud_rx.unpack_remote_data(remote_list)    
  
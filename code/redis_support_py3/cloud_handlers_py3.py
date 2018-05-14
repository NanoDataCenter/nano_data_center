
import redis
import msgpack
from .redis_stream_utilities_py3 import Redis_Stream


class Send_Object(object):
   def __init__(self, redis_handle, transport_queue, queue_depth ):
       self.redis_handle = redis_handle
       self.transport_queue = transport_queue
       self.queue_depth = queue_depth
       


   def send(self,action, **kwargs):
       kwargs["ACTION"] = action
       send_data = msgpack.packb(kwargs)
       self.redis_handle.lpush(self.transport_queue, send_data )
       self.redis_handle.ltrim(self.transport_queue, 0,self.queue_depth)
       


class Cloud_TX_Handler(object):

   def __init__(self, redis_handle, transport_queue = "_TRANSPORT_QUEUE_" , transport_depth = 128 ):
       self.redis_handle = redis_handle
       self.send_object = Send_Object( redis_handle,transport_queue,transport_depth)
       
   def hset(self,key,field,json_data):
       self.send_object.send("HSET",key=key,field=field,json_data = json_data)
       
   def hdel(self,key,field):
       self.send_object.send("HDEL",key=key,field=field)
       
   def lpush(self, depth, key, json_data):
       self.send_object.send("LPUSH",key=key,depth=depth,json_data = json_data)
       
   def list_delete(self, key,index):
       self.send_object.send("LIST_DELETE",key=key,index = index)
       
   def rpop(self,key):
       self.send_object.send("RPOP",key=key)
       
   def stream_write(self,depth, id, key,  store_dictionary ):
       self.send_object.send("STREAM_WRITE",id=id,key=key,depth=depth , store_dictionary = store_dictionary )
       
   def stream_list_write(self, depth, key, json_data ):
       self.send_object.send("STREAM_LIST_WRITE", key=key,depth =depth,json_data = json_data)
       
       
class Cloud_RX_Handler(object):

   def __init__(self,redis_handle):
      self.redis_handle = redis_handle
      self.data_handlers = {}
      self.data_handlers["HSET"] = self.hset
      self.data_handlers["HDEL"] = self.hdel
      self.data_handlers["LPUSH"] = self.lpush
      self.data_handlers["LIST_DELETE"] = self.list_delete
      self.data_handlers["RPOP"] = self.rpop
      self.data_handlers["STREAM_WRITE"] = self.stream_write
      self.data_handlers["STREAM_LIST_WRITE"] = self.stream_list_write
      self.redis_stream =  Redis_Stream(redis_handle, exact_flag = False)
  
      
   def unpack_remote_data( self, json_list_data ):
      list_data = json.loads(json_list_data)
      for i_json in list_data:
          i = json.loads(i_json)
          action = i["ACTION"]
          print("ACTION",action)
          if action in self.data_handlers:
              self.data_handlers[action](i)
          else:
              raise ValueError("Bad Action ID")

   def hset(self,data):
       self.redis_handle.hset(data["key"],data["field"],data["json_data"])
       
   def hdel(self,data):
       self.redis_handle.hdel(data["key"],data["field"] )
       
   def lpush(self, data):
       self.redis_handle.lpush(data["key"],data["json_data"])
       self.redis_handle.ltrim(data["key"],0, data["depth"])

       
   def list_delete(self,data):
       self.redis_handle.lset(data["key"], data["index"],"__#####__")
       self.redis_handle.lrem(data["key"], 1,"__#####__") 

       
   def rpop(self,data):
       self.redis_handle.rpop(data["key"])
       
   def stream_write(self,data ):
       self.redis_stream.xadd(key = data["key"], max_len= data["depth"],id=data["id"],data_dict=data["store_dictionary"] )
   
   
   def stream_list_write(self, data ):
       self.redis_handle.lpush(data["key"],data["json_data"])
       self.redis_handle.ltrim(data["key"],0,data["depth"]-1)
    

if __name__ == "__main__":
    redis_handle = redis.StrictRedis(  db=3 , decode_responses=True)
    cloud_rx =  Cloud_RX_Handler(redis_handle)
    cloud_tx = Cloud_TX_Handler(redis_handle)
    
    json_data_1 = json.dumps({"data":1})   
    json_data_2 = json.dumps({"data":2})
    json_data_3 = json.dumps({"data":3})
    json_data_4 = json.dumps({"data":41})
    json_data_5 = json.dumps({"data":5})
    json_data_6 = json.dumps({"data":6})
    
    dict_1 = {"data":7}
    
    cloud_tx.hset("hash_test","field_1",json_data_1)
    cloud_tx.hset("hash_test","field_2",json_data_2)
    cloud_tx.hdel("hash_test","field_1")
    cloud_tx.lpush(10,"job_queue_test", json_data_3)
    cloud_tx.lpush( 10,"job_queue_test", json_data_4) 
    cloud_tx.lpush( 10,"job_queue_test", json_data_5) 
    cloud_tx.list_delete( "job_queue_test",1)    
    cloud_tx.rpop("job_queue_test")
    cloud_tx.stream_write(10, "*", "stream_test",  dict_1 )
    cloud_tx.stream_list_write(10,"stream_list_test", json_data_6 )
    #
    # Read transport list
    # 
    remote_length = redis_handle.llen("_TRANSPORT_QUEUE_")
    remote_list = []
    for i in range(0,remote_length):
        remote_list.append(redis_handle.lpop("_TRANSPORT_QUEUE_"))
        
  
    print("len",len(remote_list))
    json_list_data = json.dumps(remote_list)
 
    cloud_rx.unpack_remote_data(json_list_data)    
  
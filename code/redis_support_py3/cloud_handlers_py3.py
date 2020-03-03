import base64
import redis
import msgpack
import json
from .redis_stream_utilities_py3 import Redis_Stream

class Job_Queue_Client( object ):
 
   def __init__(self,redis_handle,data, key,  cloud_handler):
      self.data = data
      self.redis_handle = redis_handle
      self.key = key
      self.depth =  data["depth"]
      self.cloud_handler = cloud_handler

  
   def push(self,data):
       pack_data =  msgpack.packb(data,use_bin_type = True )
       self.redis_handle.lpush(self.key,pack_data)
       self.redis_handle.ltrim(self.key,0,self.depth)



         
class Cloud_TX_Handler(object):


   def __init__(self, redis_handle, qs):
       self.site = qs.site
       self.redis_handle = redis_handle
       self.init_handler(qs)

   def init_handler(self,qs ):
      
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=qs.site )
       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"CLOUD_SERVICE_QUEUE_DATA"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)  
       self.package = package_sources[0]
     
       data_structures = self.package["data_structures"]
       self.forward_queue = self.construct_job_queue_client(data_structures["CLOUD_JOB_SERVER"])
 

          
          
   
   
          
   def construct_job_queue_client(self,data):
       self.forward_data = data
       assert(data["type"] == "JOB_QUEUE")
       key = self.package["namespace"]+"["+data["type"]+":"+data["name"] +"]"
       return Job_Queue_Client(self.redis_handle,data,key,None )
     


   def send_log(self,meta_data,input_data,local_node = None):
       data = {}
       data["local_node"] = local_node
       data["site"] = self.site
       data["name"]  = meta_data["name"]
       data["data"] = input_data
       #print("data",data)
       self.forward_queue.push(data)

       
       




   def check_forwarding(self,meta_data):  # do not forward data structures unless specified in the "forward" field
       
       if  "forward" in meta_data:
           if meta_data["forward"] == True:
             
              return True
       #print("return false")
       return False

   def delete(self,forward_data,key):
       pass
 

 
   def hset(self,forward_data,key,field,data):
       pass
       
   def hdel(self,forward_dat,key,field):
      pass
       
   def lpush(self,forward_data,depth, key, data):
       pass
       
   def list_delete(self, forward_dat,key,index):
       pass
       
   def rpop(self,forward_dat,key):
       pass
       
   def stream_write(self,meta_data, key, data,local_node = None ) :
       if self.check_forwarding(meta_data):
          self.send_log(meta_data,data,local_node)
       
       
       
   
       
       
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
      self.file_path["APP"] =  "app_data_files/"
      self.file_path["SYS"] =  "system_data_files/"
      self.file_path["LIMIT"]  = "limit_data_files/"
 
      
   def unpack_remote_data( self, i_compress ):
          
          i = msgpack.unpackb(i_compress,encoding='utf-8')
          action = i["ACTION"]
          
          #print("action",action,)
          if action in self.data_handlers:
              self.data_handlers[action](i)
          else:
              raise ValueError("Bad Action ID")

 
   def check_for_file(self,key):
       
       self.file_type = None
       fields = key.split("[FILE:")
       
       if len(fields) > 1:
          file_type = fields[1].split("]")[0]
          return True, file_type
       else:
          return False, None

   def delete(self,key):
       self.redis_handle.delete(key)
 

   def save_raw_file(self,path,name,data): 
       f = open(path + name, 'w')
       f.write(data)
 
 
              
   def hset(self,data):
       field =data["field"]
       self.redis_handle.hset(data["key"],field,data["data"])
       
       file_flag,file_type = self.check_for_file(data["key"])
       if file_flag == True:
          #print("check file true",file_type)
          if file_type in self.file_path:
              
               file_path = self.file_path[file_type]
               file = field
               temp_data = msgpack.unpackb(data["data"],encoding='utf-8')
               #print("temp_data",temp_data)
               self.save_raw_file(file_path,file,temp_data)
       
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
  
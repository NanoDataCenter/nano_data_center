import msgpack

class Job_Queue_Client( object ):
 
   def __init__(self,redis_handle,depth, key,  cloud_handler):
      
      self.redis_handle = redis_handle
      self.key = key
      self.depth =  depth
      self.cloud_handler = cloud_handler

   def delete_all( self ):
       self.redis_handle.delete(self.key)
 
      
      
   def delete(self, index ):
       if index < self.redis_handle.llen(self.key):
           self.redis_handle.lset(self.key, index,"__#####__")
           self.redis_handle.lrem(self.key, 1,"__#####__") 
 
      
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
        
 

       if pack_data == None:
          return False, None
       else:
         
          return True,msgpack.unpackb(pack_data,encoding='utf-8')     
   def push(self,data):
       pack_data =  msgpack.packb(data,use_bin_type = True )
       self.redis_handle.lpush(self.key,pack_data)
       self.redis_handle.ltrim(self.key,0,self.depth)


           
   def delete_jobs(self,data):
       for i in data:
         self.redis_handle.lset(self.key,i,"__DELETE_ME__")
       self.redis_handle.lrem(self.key,0,"__DELETE_ME__")
 

def valid_data( input_data):

   if "site" in input_data:
       if "name" in input_data:
          if "data" in input_data:
              return True
   return False              

if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    
    import json

    import os
    import copy
    #import load_files_py3
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
    import datetime


    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close() 
    redis_site = json.loads(data)
     
    #
    # Setup handle
    # open data stores instance
    
    
     
       
    qs = Query_Support( redis_site )
    

    
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"CLOUD_SERVICE_QUEUE_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list) 
    package = package_sources[0]    
    data_structures = package["data_structures"]
    generate_handlers = Generate_Handlers(package,qs)
    local_queue = generate_handlers.construct_job_queue_server(data_structures["CLOUD_JOB_SERVER"])
   
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )
    query_list = qs.add_match_relationship( query_list,relationship="CLOUD_SERVICE_HOST_INTERFACE" )
    
    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "HOST_INFORMATION" )
                                        
    host_sets, host_sources = qs.match_list(query_list) 
    
    host_source = host_sources[0]
    remote_redis_handle = redis.StrictRedis( host = host_source["host"] , port=host_source["port"], db=host_source["key_data_base"] )
    remote_client = Job_Queue_Client( remote_redis_handle,key = host_source["key"],depth=host_source["depth"],cloud_handler = None )
   
   
    while 1:
    
       print(local_queue.length())
       while local_queue.length() > 0:
           data = local_queue.pop()
           print("data",data[1])
           if valid_data(data[1]):
             
              print(remote_client.length())
              remote_client.push(data)
           else:
              print("invalid data")
       time.sleep(5)
   
   
   
   
   
   

    

else:
  pass
  










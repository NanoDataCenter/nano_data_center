
import redis
import msgpack


class Job_Queue_Server( object ):
 
   def __init__(self,redis_handle,key):
     
      self.redis_handle = redis_handle
      self.key = key 
      
     
   def delete_all( self ):
       self.redis_handle.delete(self.key)
 
 
   def length(self):
       return self.redis_handle.llen(self.key)
       
 

 
   def pop(self):
       pack_data = self.redis_handle.rpop(self.key)

       if pack_data == None:
          return False, None
       else:
         
          return True,msgpack.unpackb(pack_data,raw=False)

   def show_a_job(self,index):
       pack_data = self.redis_handle.lindex(self.key,index)
       if pack_data == None:
          return False, None
       else:
          
          return True, msgpack.unpackb(pack_data,raw=False)

          
   def show_next_job(self):
       pack_data = self.redis_handle.lindex(self.key, -1)
       if pack_data == None:
          return False, None
       else:
          
          return True, msgpack.unpackb(pack_data,raw=False)




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
    query_list = qs.add_match_relationship( query_list,relationship="CLOUD_SERVICE_HOST_INTERFACE" )
    
    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "HOST_INFORMATION" )
                                        
    host_sets, host_sources = qs.match_list(query_list) 
    
    host_source = host_sources[0]
    remote_redis_handle = redis.StrictRedis( host = host_source["host"] , port=host_source["port"], db=host_source["key_data_base"] )
    input_server = Job_Queue_Server(remote_redis_handle,key = host_source["key"])
   
    length = input_server.length()
    for i in range(0,length):
       data = input_server.show_a_job(i)

       data = data[1]
       data = data[1]
       
       print(i,valid_data(data))
       
      
    while 1:
    
       print(input_server.length())
       
       while input_server.length() > 0:
           data = input_server.show_next_job()
           if data[0] == True:
             if valid_data(data[1]) == True:
                print("input data is valid")
             else:
                print("input_data is not valid")
           quit()

       time.sleep(5)
   
   
   
   
   
   

    

else:
  pass
  










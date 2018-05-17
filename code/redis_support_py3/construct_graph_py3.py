# file build system
#
#  The purpose of this file is to load a system configuration
#  in the graphic data base
#

import json

import redis
import pickle
import gzip


class Build_Configuration(object):
   def __init__( self, redis_site ):  
       self.redis_handle = redis.StrictRedis( host = redis_site["host"] , port=redis_site["port"], db=redis_site["graph_db"] , decode_responses=True)
       self.delete_all()
 


   def delete_all(self): #tested
       self.redis_handle.flushdb()
       


   def restore_extraction(self,filename):
        file = gzip.GzipFile(filename, 'rb')
        buffer = b""
        while True:
                data = file.read()
                if data == b"":
                        break
                buffer += data
        extract = pickle.loads(buffer)
        file.close()
        keys = extract.keys()
        print("len",len(keys))
        for i,item in extract.items():
           self.redis_handle.restore(name = i,ttl=0, value = item, replace = True)
        



if __name__ == "__main__" :

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   redis_site = json.loads(data)


   bc = Build_Configuration(redis_site)
  
   bc.restore_extraction("system_data_files/extraction_file.pickle")

 
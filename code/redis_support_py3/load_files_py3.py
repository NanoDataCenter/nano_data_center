
#
# File: load_files.py
# load sys files and application files
# The data is stored in the following
#    System Files are stored in the following in json format
#    	As a dictionary with the key of FILES:SYS
#    	The key of the dictionary are the file names
#    APP Files are stored in the following in json format
#    	As a dictionary with the key of
#    	The key of the dictionary are the file names

#  import redis
#  make redis dictionary "SYS:FILES"
# store json_object to redis data "global_sensors"
import os
from os import listdir
from os.path import isfile, join
import redis
import json


app_files = "/home/pi/nano_data_center/code/app_data_files/"
sys_files = "/home/pi/nano_data_center/code/system_data_files/"


class BASIC_FILES( object ):
    def __init__(self,redis_site, redis_handle= None):
        if redis_handle == None:
            redis_handle  = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_file_db"], decode_responses=True)
        self.redis_handle = redis_handle

    def get_redis_handle(self):
        return self.redis_handle

    def file_directory(self):
        return self.redis_handle.hkeys(self.key)

    def delete_file(self, name):
        self.redis_handle.hdel(self.key, name)

    def save_file(self, name, data):
        f = open(self.path + name, 'w')
        json_data = json.dumps(data)
        f.write(json_data)
        self.redis_handle.hset(self.key, name, json_data )

    def load_file(self, name):
        
        json_data= self.redis_handle.hget(self.key, name)
        
        data = json.loads(json_data )
        return data

    def clear_all_file_data(self):
        self.redis_handle.delete(self.key)
        
    def load_all_files( self):
        files = [f for f in listdir(self.path)]
        for i in files:
            fileName, fileExtension = os.path.splitext(i)
            if fileExtension == ".json":
               f = open(self.path+i, 'r')
               data = f.read()
               
               try:
                   temp = json.loads(data) # test to ensure data has json format
                   
                   self.redis_handle.hset( self.key, i , data)
               except:
                   print("exception file: "+i)
    
    

class APP_FILES( BASIC_FILES ):
   def __init__( self, redis_site, redis_handle=None ):
       self.path = app_files
       self.key = "FILES:APP"
       BASIC_FILES.__init__(self,redis_site, redis_handle )

class SYS_FILES(BASIC_FILES):
    def __init__(self, redis_site,redis_handle=None):
        self.path = sys_files
        self.key = "FILES:SYS"
        BASIC_FILES.__init__(self,redis_site, redis_handle )
       



if __name__ == "__main__":

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   redis_site = json.loads(data)

   app_files = APP_FILES( redis_site, redis_handle=None )
   sys_files = SYS_FILES( redis_site, app_files.get_redis_handle())
   app_files.clear_all_file_data()
   sys_files.clear_all_file_data()   
   app_files.load_all_files()
   sys_files.load_all_files()   
    
   

       
else:
    pass
    
    

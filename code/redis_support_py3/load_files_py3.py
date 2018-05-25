
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
import msgpack
from  .cloud_handlers_py3 import Cloud_TX_Handler
from  .construct_data_handlers_py3 import Redis_Hash_Dictionary
app_files = "app_data_files/"
sys_files = "system_data_files/"
limit_files = "limit_data_files/"
import base64


   
class BASIC_FILES( object ):
    def __init__(self, redis_handle,path, redis_site,label):
        self.path = path
        self.redis_site = redis_site
        self.cloud_handler = Cloud_TX_Handler(redis_handle)

        self.redis_handle = redis_handle
        self.key = "[SITE:"+redis_site["site"]+"][FILE:"+label+ "]"
        self.hash_driver = Redis_Hash_Dictionary(self.redis_handle,self.key,None,self.cloud_handler)

    def file_directory(self):
        return self.hash_driver.hkeys()

    def delete_file(self, name):
        self.hash_driver.hdelete(name)

        
    def save_file(self, name, data):
        f = open(self.path + name, 'w')
        json_data = json.dumps(data)
        f.write(json_data)
        self.hash_driver.hset( name,data)

    def load_file(self, name):
        return self.hash_driver.hget(name)
 

class APP_FILES( BASIC_FILES ):
   def __init__( self, redis_handle,redis_site ):
       BASIC_FILES.__init__(self,redis_handle,app_files, redis_site,"APP" )
       

class SYS_FILES(BASIC_FILES):
    def __init__(self, redis_handle,redis_site ):
        BASIC_FILES.__init__(self,redis_handle,sys_files,redis_site,"SYS" )
    
        
class LIMIT(BASIC_FILES):
    def __init__(self, redis_handle,redis_site ):
        BASIC_FILES.__init__(self,redis_handle,limit_files,redis_site,"LIMITS" )


if __name__ == "__main__":


   def load_file( file_list,path, redis_key):
       for i in files:
           fileName, fileExtension = os.path.splitext(i)
           if fileExtension == ".json":
               f = open(path+i, 'r')
               data = f.read()
               temp = json.loads(data) # test to ensure data has json format
               pack_data = msgpack.packb(temp)
               pack_data = base64.b64encode(pack_data)
               redis_handle.hset( redis_key, i , pack_data)


 

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()

   redis_site = json.loads(data)

   redis_handle = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_file_db"], decode_responses=True)




   key = "[SITE:"+redis_site["site"]+"][FILE:"
   redis_handle.delete(key+"APP]")
   redis_handle.delete(key+"SYS]")
   redis_handle.delete(key+"LIMITS]")

   files = [f for f in listdir(app_files)]

   # load app files
   load_file( files,app_files,key+"APP]" )

  

   # load sys files

   files = [ f for f in listdir(sys_files)  ]
   load_file( files,sys_files, key+"SYS]" )

   # load limit files

   files = [ f for f in listdir(limit_files)  ]
   load_file( files,limit_files,key+"LIMITS]" )
   

else:
   pass


__TEST__= False   
if __TEST__ == True:
   app_file_handler = APP_FILES( redis_handle,redis_site )
   sys_file_handler = SYS_FILES( redis_handle,redis_site)
   print(app_file_handler.file_directory())
   directory_list = app_file_handler.file_directory()
   print(app_file_handler.load_file(directory_list[0]))
   
'''


   #
   #  the rest of this will be moved to a new manager
   #
   ####
   # INSURING THAT ETO_MANAGEMENT FLAG IS DEFINED
   ####
   temp = redis_handle.get("ETO_MANAGE_FLAG")
   if temp is None:
        # not defined
        redis_handle.set("ETO_MANAGE_FLAG", 1)

   temp = redis_handle.hget("CONTROL_VARIABLES", "ETO_MANAGE_FLAG")
   if temp is None:
        # not defined
        redis_handle.hset("CONTROL_VARIABLES", "ETO_MANAGE_FLAG", 1)

   ####
   # Construct ETO Data QUEUES
   ####

   file_data = redis_handle.hget("FILES:APP", "eto_site_setup.json")

   eto_site_data = json.loads(file_data) 

   redis_handle.delete("ETO_RESOURCE_A")
   for j in eto_site_data:
        redis_handle.hset("ETO_RESOURCE_A",
                          j["controller"] + "|" + str(j["pin"]), 0)

   keys = redis_handle.hkeys("ETO_RESOURCE")
   print("keys", keys)
   for i in keys:
        print("i", i)
        value = redis_handle.hget("ETO_RESOURCE", i)
        if redis_handle.hexists("ETO_RESOURCE_A", i):
            redis_handle.hset("ETO_RESOURCE_A", i, value)
   redis_handle.delete("ETO_RESOURCE")
   redis_handle.rename("ETO_RESOURCE_A", "ETO_RESOURCE")

   if redis_handle.hget(
        "CONTROL_VARIABLES",
            "ETO_RESOURCE_UPDATED") != "TRUE":
        redis_handle.hset("CONTROL_VARIABLES", "ETO_RESOURCE_UPDATED", "FALSE")
   #
   # delete process keys

   keys = redis_handle.hkeys("WD_DIRECTORY")
   for i in keys:
        print("i", i)
        redis_handle.hdel("WD_DIRECTORY", i)

   redis_handle.hset(
        "SYS_DICT",
        "CONTROL_VARIABLES",
        "system control and status variables")
   redis_handle.hset(
        "SYS_DICT",
        "FILES:APP",
        "dictionary of application files")
   redis_handle.hset("SYS_DICT", "FILES:SYS", "dictionary of system files")
   redis_handle.hset("SYS_DICT", "ETO_RESOURCE", "dictionary of eto resource")
   redis_handle.hset(
        "SYS_DICT",
        "SCHEDULE_COMPLETED",
        "markers to prevent multiple keying of sprinklers")
   redis_handle.hset(
        "SYS_DICT",
        "OHM_MESS",
        "ohm measurement for active measurements")
   redis_handle.hset(
        "QUEUES_DICT",
        "QUEUES:SPRINKLER:PAST_ACTIONS",
        "QUEUE OF RECENT IRRIGATION EVENTS AND THEIR STATUS")
   redis_handle.hset(
        "QUEUES_DICT",
        "QUEUES:CLOUD_ALARM_QUEUE",
        "QUEUE OF EVENTS AND ACTIONS TO THE CLOUD")
   redis_handle.hset(
        "QUEUES_DICT",
        "QUEUES:SPRINKLER:FLOW:<schedule_name>",
        "QUEUE OF PAST FLOW DATA")
   redis_handle.hset(
        "QUEUES_DICT",
        "QUEUES:SPRINKLER:CURRENT:<schedule_name>",
        "QUEUE OF PAST CURRENT DATA")
   redis_handle.hset(
        "QUEUES_DICT",
        "QUEUES:SYSTEM:PAST_ACTIONS",
        "QUEUE OF RECENT SYSTEM EVENTS AND THEIR STATUS")
'''

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
from cloud_handlers_py3 import Cloud_TX_Handler

app_files = "app_data_files/"
sys_files = "system_data_files/"


class BASIC_FILES( object ):
    def __init__(self, redis_handle,site,label):
        self.tx_handler = Cloud_TX_Handler()
        self.redis_handle = redis_handle
        self.key = "[SITE:"+site+"][FILE:"+label+ "]"
        

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


class APP_FILES( BASIC_FILES ):
   def __init__( self, redis_handle,redis_site ):
       BASIC_FILES.__init__(self,redis_handle )
       self.path = app_files
       self.key = "FILES:APP"

class SYS_FILES(BASIC_FILES):
    def __init__(self, redis_handle,redis_site ):
        BASIC_FILES.__init__(self,redis_handle )
        self.path = sys_files
        self.key = "FILES:SYS"
        



if __name__ == "__main__":


   def load_file( file_list,path, redis_key):
       for i in files:
           fileName, fileExtension = os.path.splitext(i)
           if fileExtension == ".json":
               f = open(path+i, 'r')
               data = f.read()
               temp = json.dumps(data) # test to ensure data has json format
               redis_handle.hset( redis_key, i , data)


 

   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()

   redis_site = json.loads(data)

   redis_handle = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_file_db"], decode_responses=True)





   redis_handle.delete("APP_FILES")
   redis_handle.delete("SYS_FILES")


   files = [f for f in listdir(app_files)]

   load_file( files,app_files,"FILES:APP" )

   # load app files

   # load sys files

   files = [ f for f in listdir(sys_files)  ]
   load_file( files,sys_files, "FILES:SYS" )
       



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
   #
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

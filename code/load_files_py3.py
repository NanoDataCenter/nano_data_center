
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
from redis_graph_py3 import farm_template_py3

app_files = "/home/pi/new_python/app_data_files/"
sys_files = "/home/pi/new_python/system_data_files/"


class BASIC_FILES( object ):
    def __init__(self, redis_handle):
        self.redis_handle = redis_handle

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
   def __init__( self, redis_handle ):
       BASIC_FILES.__init__(self,redis_handle )
       self.path = app_files
       self.key = "FILES:APP"

class SYS_FILES(BASIC_FILES):
    def __init__(self, redis_handle):
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





   graph_management = farm_template_py3.Graph_Management(
           "PI_1", "main_remote", "LaCima_DataStore")
   data_store_nodes = graph_management.find_data_stores()
   # find ip and port for redis data store
   data_server_ip = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   print(data_server_ip,data_server_port)

   redis_handle = redis.StrictRedis(data_server_ip, data_server_port, db=0, decode_responses=True)


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

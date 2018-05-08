#!/usr/bin/env python
import pika
import json
import base64
import time
import os

import logging
import msgpack

global connection

import msgpack
import zlib
from web_support_py3.web_access_py3 import Web_Client_Interface()
from rabbitmq_support.rabbitmq_rpc_server import Rabbitmq_RPC_Server

class Remote_Interface_server():

   def __init__(self,web_client ):
        self.web_client  = web_client
        self.redis                 = redis
        self.cmds                  = {}
        self.cmds["GET_WEB_PAGE"]  = self.get_web_page
        self.cmds["POST_WEB_PAGE"] = self.post_web_page
        self.cmds["PING"]          = self.ping

   def get_web_page( self, command_data ):
       
       results = self.web_client.get_path( command_data["path"] )
       
       return results

   def post_web_page( self, command_data ):
       results = self.web_client.post_path( path = command_data["path"], payload = command_data["data"] )
       
       return results

   def ping( self, command_data ):
      pass

          


   def process_commands( self, command_data ):
 
       try:
           
           object_data = {}
           command = command_data["command"]
           
           if  command in self.cmds:  #valid web command
               result = self.cmds[command]( command_data)
               result["results" ] = zlib.compress(msgpack.packb(result["results"]))
               
               return result
               
               
           else: # invalid web command
           
              object_data = {}
              object_data["reply"] = "BAD_COMMAND_1"
              return object_data
      
       except:  # error in processing command

           raise
           object_data = {}
           object_data["reply"] = "Exception_1"
           object_data["results"] = None
           return object data

  
if __name__ == "__main__":
   
   gm = farm_template_py3.Graph_Management("PI_1","main_remote","LaCima_DataStore")
   #
   # Now Find Data Stores
   #
   #
   #
   data_store_nodes = gm.find_data_stores()
   # find ip and port for redis data store
   data_server_ip   = data_store_nodes[0]["ip"]
   data_server_port = data_store_nodes[0]["port"]
   # find ip and port for ip server
   print( "data_server_ip",data_server_ip,data_server_port)
   redis_handle = redis.StrictRedis( host = data_server_ip, port=data_server_port, db = 0 , decode_responses=True)


   user_name = redis_handle.hget("web_gateway", "user_name" ) 

   password  = redis_handle.hget("web_gateway", "password"  ) 

   vhost     = redis_handle.hget("web_gateway", "vhost"     )

   queue     = redis_handle.hget("web_gateway", "queue"     )

   port      = int(redis_handle.hget("web_gateway", "port"  ))
   server    = redis_handle.hget("web_gateway", "server"    ) 


   web_client = Web_Client_Interface( )
   logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)
   
   
   rt = Remote_Interface_server(web_client)
   credentials = pika.PlainCredentials( user_name, password )
   parameters = pika.ConnectionParameters(server,
                                           port,  #ssl port
                                           vhost,
                                           credentials,
                                           ssl = True ,
                                          heartbeat_interval=2000 )
   connection = pika.BlockingConnection(parameters)
   channel = connection.channel()
   #connection.socket.settimeout(10000)
   #channel.queue_delete(queue=queue)
   #time.sleep(20)
   channel.queue_declare(queue=queue)
   channel.basic_qos(prefetch_count=1)
   channel.basic_consume(on_request, queue=queue)
   print (" [x] Awaiting RPC requests")
   
   channel.start_consuming()
   #   print "start consuming is ended"
   Rabbitmq_RPC_Server(user_name, password,sever,port,vhost,queue,on_request)

   
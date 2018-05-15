#!/usr/bin/env python
import pika
import uuid
import json
import msgpack
import os
import time
import redis
import rabbitmq_client





class RabbitMq_RPC_Client(object):
    def __init__(self,server,port,username,password,vhost):
         
         credentials = pika.PlainCredentials( username, password )
         parameters = pika.ConnectionParameters( server,
                                                 port,  #ssl port
                                                 vhost,
                                                 credentials,
                                                 ssl = True )
         parameters.heartbeat = 20
         self.connection = pika.BlockingConnection(parameters)        
         self.channel = self.connection.channel()
         result = self.channel.queue_declare(exclusive=True)
         self.callback_queue = result.method.queue
         self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            
            self.response = msgpack.unpackb(temp)
            
     

    def call(self,queue, data, time_out ):
      try:
        
        time_out = time_out 
        input_data = msgpack.packb(data)

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key= queue,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body= input_data)
        while self.response is None:
              self.connection.process_data_events()
              if self.response is None:
                 time_out = time_out -1
                 if time_out == 0:
                
                     data = {}
                     data["reply"] = "No Connections"
                     data["results"] = None
                     return data
                 else:
                    time.sleep(.2)
        
        return self.response
      except:
                     data = {}
                     data["reply"] = "No Connections"
                     data["results"] = None
                    
                     return data

    def close( self ):
        self.channel.close()


if __name__ == "__main__":
   
    pass
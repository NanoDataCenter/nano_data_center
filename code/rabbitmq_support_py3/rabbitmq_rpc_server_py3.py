
import pika
import msgpack

class Rabbitmq_RPC_Server(object):

   def __init__(self,user_name, password,sever,port,vhost,queue,handler):
       self.handler = handler
       credentials = pika.PlainCredentials(,user_name, password  )
       parameters = pika.ConnectionParameters(server,
                                           port,  #ssl port
                                           vhost,
                                           credentials,
                                           ssl = True ,
                                          heartbeat_interval=2000 )
       connection = pika.BlockingConnection(parameters)
       channel = connection.channel()
 
       channel.queue_declare(queue=queue)
       channel.basic_qos(prefetch_count=1)
       channel.basic_consume(self.on_request, queue=queue)
       print (" [x] Awaiting RPC requests")
       
       
   def on_request(ch, method, props, body):
    
   
    try:
       
       output_data  = self.handler( msgpack.unpackb(body))
       msgpack.packb(object_data)   
        
       
    except:
       
       output_data = {} 
       output_data["reply"] = "Rabbitmq_RPC_SERVER_ERROR"
       output_data["results"] = None
       output_data = msgpack.packb(output_data)   

    
    output_data = msgpack.packb(object_data)   
    
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                     props.correlation_id),
                     body=output_data )
    ch.basic_ack(delivery_tag = method.delivery_tag)
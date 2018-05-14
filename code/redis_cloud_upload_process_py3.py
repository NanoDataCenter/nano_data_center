

from rabbitmq_support_py3.rabbitmq_rpc_client_py3


class Redis_To_Cloud(object):
   def __init__(self, redis_handle,server,port,username,password,vhost):
       self.redis_handle = redis_handle
       self.rabbitmq_client = RabbitMq_RPC_Client(server,port,username,password,vhost)
       self.queue = queue
       
    
       
   def upload_data(self,*args):
       while self.redis_handle.llen("_TRANSPORT_QUEUE_") != 0:
            packet = self.redis_handle.rpop("_TRANSPORT_QUEUE_")
            status = self.rabbitmq_rpc_client.call(self.queue,packet,self.time_out )
            if status == False
            
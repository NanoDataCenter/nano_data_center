
import uuid
import json
import time


class Rpc_No_Communication(Exception):
   """Base class for rpc server errors"""
   pass
class Redis_Rpc_Client(object):

   def __init__( self, redis_handle , redis_rpc_queue ):
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       
       
   def send_rpc_message( self, method,parameters,timeout=30 ):
        request = {}
        request["method"] = method
        request["params"] = parameters
        request["id"]   = str(uuid.uuid1())    
        request_json = json.dumps( request )
        self.redis_handle.delete(request["id"] )
        self.redis_handle.lpush(self.redis_rpc_queue, request_json)
        data =  self.redis_handle.brpop(request["id"],timeout = timeout )
        
        self.redis_handle.delete(request["id"] )
        if data == None:
            raise Rpc_No_Communication("No Communication with Modbus Server")
        response = json.loads(data[1])
        
        return response
                
if __name__ == "__main__":
    import redis
    redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,5,decode_responses = True )
    redis_rpc_client = Redis_Rpc_Client( redis_handle, "redis_rpc_server")
    while True:
        try:
            result = redis_rpc_client.send_rpc_message("echo","echo test_message",2)
            print("result",result)
        except Rpc_No_Communication:
            print("no rpc communication")
            
import uuid
import json
import time


class Redis_Rpc_Server(object):

    def __init__( self, redis_handle , redis_rpc_queue , timeout_function=None, timeout_value=5):
       self.redis_handle = redis_handle
       self.redis_rpc_queue = redis_rpc_queue
       self.timeout_function = timeout_function
       self.timeout_value  = timeout_value
       self.handler = {}
       self.redis_handle.delete(redis_rpc_queue)
       

    def register_call_back( self, method_name, handler):
        self.handler[method_name] = handler
    
    def start( self ):
        while True:
            try:
               input = self.redis_handle.brpop(self.redis_rpc_queue,self.timeout_value)
              
               if input == None:
                    if self.timeout_function != None:
                        self.timeout_function()
               else:
                   input = json.loads(input[1])  # 0 parameter is the queue
                   self.process_message(  input )
                       
            except:
                raise
 
    def process_message( self, input):

        id      = input["id"]
        method  =  input["method"]
        params  = input["params"]
        response = self.handler[method](params)
       
        self.redis_handle.lpush( id, json.dumps(response))        
        self.redis_handle.expire(id, 30)
 
if __name__ == "__main__":
    def echo_handler(  parameters ):
        return parameters
        
    def time_out_function():
        global time_base
        print( time.time()-time_base)
        time_base = time.time()
        
        
    import redis
    time_base = time.time()
    redis_handle = redis.StrictRedis("127.0.0.1", 6379 ,5,decode_responses = True )
    redis_rpc_server = Redis_Rpc_Server( redis_handle, "redis_rpc_server", timeout_function = time_out_function)
    redis_rpc_server.register_call_back( "echo",echo_handler )
    redis_rpc_server.start()
        

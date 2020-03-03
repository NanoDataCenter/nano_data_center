from .event_listener_top_class import Event_Listner_Class_IPC
import redis
import datetime

class Get_Block_Chain_Events(object):

   def __init__(self):
       redis_handle = redis.StrictRedis( db=1 )
       ipc_socket = "/home/pi/geth.ipc"
       self.ev = Event_Listner_Class_IPC(ipc_socket,redis_handle)
       
       
   def get_all_events(self,contract_name,fromBlock=0 ,toBlock='latest'):
       self.ev.construct_loop_filter(contract_name,fromBlock,toBlock)
       return self.ev.get_all_entries(contract_name)        
   
        
if __name__ == "__main__":
   get_block_chain_events =  Get_Block_Chain_Events()
   data = get_block_chain_events.get_all_events("EventHandler")
   print("data",data)
   
   

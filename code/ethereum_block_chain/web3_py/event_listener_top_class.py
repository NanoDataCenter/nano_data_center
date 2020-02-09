import time
from .web3_top_class import Web_Class_IPC


class Event_Listner_Class_IPC(Web_Class_IPC):

   def __init__(self,ipc_socket,redis_handle,signing_key = None):
       print(ipc_socket)
       Web_Class_IPC.__init__(self,ipc_socket,redis_handle,signing_key)
       self.event_filter = {}
 
   def construct_loop_filter(self,contract_name,fromBlock=0 ,toBlock='latest' ):
       contract_object = self.get_contract(contract_name)
       block_filter=contract_object.events.Update_Event.createFilter(fromBlock=fromBlock ,toBlock=toBlock)
       self.event_filter[contract_name ] = block_filter
       
   def get_all_entries(self,contract_name):
       data = self.event_filter[contract_name].get_all_entries()
       return_value = []
       for i in data:
          temp = dict(i)
          temp["args"] = dict(i["args"])
          temp["timestamp"] = self.get_block_timestamp(i["blockNumber"])
          return_value.append(temp)
         
       return return_value

   def lastest_event_loop(self,contract_name,  event_handler,poll_interval = 1.0):
       loop_flag = True
       while loop_flag:
        for event in self.event_filter[contract_name].get_new_entries():
            loop_flag = event_handler(event)
        time.sleep(poll_interval)

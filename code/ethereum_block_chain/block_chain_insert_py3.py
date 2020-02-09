from  .web3_top_class import Web_Class_IPC
import redis
import datetime

class Save_Block_Chain_Data(object):

   def __init__(self):
       redis_handle = redis.StrictRedis( db=1 )
       signing_key = '/mnt/ssd/ethereum/dev_data/keystore/UTC--2019-12-08T20-29-05.205871190Z--75dca28623f88b105b8d0c718b4bfde0f1568688'
       ipc_socket = "/home/pi/geth.ipc"
       self.w3 = Web_Class_IPC(ipc_socket,redis_handle,signing_key)
       print(self.w3.get_block_number())
       
       
   def append_data(self,contract_name,method,*data) :
        contract_object = self.w3.get_contract(contract_name)
        receipt = self.w3.transact_contract_data(contract_object,method, *data)
        return receipt
        
if __name__ == "__main__":
   save_block_chain_data =  Save_Block_Chain_Data()
   receipt = save_block_chain_data.append_data("EventHandler","transmit_event",["event_name","event_sub_id","data"])
   print(receipt)
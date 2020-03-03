
from web3 import Web3
from web3.middleware import geth_poa_middleware
import msgpack


class Web_Class_IPC(object):

   def __init__(self,ipc_socket,redis_handle,signing_key = None):
       print(ipc_socket)
       provider = Web3.IPCProvider(ipc_socket)
       self.w3 = Web3(provider)
       self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
       assert(self.w3.isConnected())
       self.signing_key = signing_key
       self.redis_handle = redis_handle
       
       
   def send_currency(self, to_account_index, value):  # value in ether
       with open(self.signing_key) as keyfile:
           encrypted_key = keyfile.read()
           private_key = self.w3.eth.account.decrypt(encrypted_key, 'ready2go')
           signed_txn = self.w3.eth.account.signTransaction(dict(
               nonce=self.w3.eth.getTransactionCount(self.w3.eth.accounts[1]),
               gasPrice = self.w3.eth.gasPrice, 
               gas = 100000,
               to=self.w3.eth.accounts[to_account_index],
               value=self.w3.toWei(value,'ether')),
               private_key)
           rawHash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
           hexHash = self.w3.toHex(rawHash)            
           return self.w3.eth.waitForTransactionReceipt(hexHash)

   def get_block_number(self):
      return self.w3.eth.blockNumber
   
   def get_block(self,block_number):
       return self.w3.eth.getBlock(block_number)
   
   def get_block_timestamp(self,block_number):
       return self.w3.eth.getBlock(block_number).timestamp
       
       
   def get_balance(self, account_index):
       return self.w3.fromWei(self.w3.eth.getBalance(self.w3.eth.accounts[account_index]),"ether")
       
   def get_accounts(self):
      return self.w3.eth.accounts
      
   def get_contract(self,contract_name):
       address = msgpack.unpackb(self.redis_handle.hget("contract_address",contract_name),raw=False)
       abi_json = msgpack.unpackb(self.redis_handle.hget("contract_abi",contract_name),raw=False)
       
       contract_object = self.w3.eth.contract(
                                            address=address,
                                            abi=abi_json
                                          )
      
       return contract_object
       
   def read_contract_data(self,contract_object, method ,parameters=None):
       if parameters == None:
          return contract_object.__dict__["functions"][method]().call()
           
       
       if type(parameters) != list:
          parameters = [parameters]
            
       return contract_object.__dict__["functions"][method]().call(unpack(parameters))
       
   def transact_contract_data(self,contract_object, method ,parameters):
 
           
       
       if type(parameters) != list:
          parameters = [parameters]
            
       tx_hash = contract_object.__dict__["functions"][method](*parameters).transact({
              'from': self.w3.eth.accounts[0],
                  })
       tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)  
       return tx_receipt
       
   def get_transaction_events(self,contract_name,receipt):
       
       contract_object = self.get_contract(contract_name)
       rich_logs = contract_object.events.Update_Event().processReceipt(receipt)
       return_value = []
       for i in rich_logs:
          temp = dict(i)
          temp["args"] = dict(i["args"])
          return_value.append(temp)
       return return_value

    

from web3 import Web3
from web3.middleware import geth_poa_middleware
import sys
import json
import redis
import pickle
import msgpack
import os
from contract_dependencies import contract_construction_parameters

def assemble_construction_parameters(contract_name):
   return_value = []
   parameters = contract_construction_parameters[contract_name]
   for i in parameters:
     if i["type"] == "address":
        address = msgpack.unpackb(redis_handle.hget("contract_address",i["value"]),raw=False)
        valid_address = w3.toChecksumAddress(address)
        return_value.append(valid_address)
     elif i["type"] == "int":
         return_value.append(int(i["value"]))
     elif i["type"] == "string":
        return_value.append(str(i["value"]))
     else:
         raise ValueError("unsupported type")

   return return_value

redis_handle = redis.StrictRedis( db=1 )
ipc_socket = "/home/pi/geth.ipc"
provider = Web3.IPCProvider(ipc_socket)
w3 = Web3(provider)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
assert(w3.isConnected())
w3.eth.defaultAccount = w3.eth.accounts[0]



for i in  range(1,len(sys.argv),1):
   contract_name = sys.argv[i]
   construction_parameters = assemble_construction_parameters(contract_name)
   abi_file_name = "binary_data/"+contract_name+".abi"
   abi_file = open(abi_file_name,"r")
   abi_data = abi_file.read()

   abi_json = json.loads(abi_data)

   bin_file_name = "binary_data/"+contract_name+".bin"
   bin_file = open(bin_file_name,"r")
   bytecode = bin_file.read()

   contract_object = w3.eth.contract(abi=abi_json, bytecode=bytecode)
   
   
   tx_hash = contract_object.constructor(*construction_parameters).transact()
   tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
   print(tx_receipt)
   redis_handle.hset("contract_address",contract_name,msgpack.packb(tx_receipt.contractAddress, use_bin_type=True))
   redis_handle.hset("contract_abi",contract_name,msgpack.packb(abi_json, use_bin_type=True))

os.system("rm contracts/*")

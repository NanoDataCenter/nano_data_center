import time
from web3 import Web3
from web3.middleware import geth_poa_middleware

#my_provider = Web3.HTTPProvider("http://127.0.0.1:8000")
my_provider = Web3.IPCProvider("/home/pi/geth.ipc")
w3 = Web3(my_provider)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
assert(w3.isConnected())

print(w3.eth.hashrate)
print(w3.eth.accounts)
print(w3.eth.mining)
print(w3.eth.chainId)
print("made it here")
print(w3.eth.getBlock('latest'))
accounts = w3.eth.accounts
print("accounts",accounts)
block = w3.eth.blockNumber

print(w3.eth.blockNumber)
print(w3.fromWei(w3.eth.getBalance(accounts[1]),"ether"))
print(w3.fromWei(w3.eth.getBalance(accounts[2]),"ether"))
#print(w3.geth.personal.unlockAccount(accounts[0], "ready2go",10 ))
keyfile_name = '/mnt/ssd/ethereum/dev_data/keystore/UTC--2019-12-08T20-29-05.205871190Z--75dca28623f88b105b8d0c718b4bfde0f1568688'
with open(keyfile_name) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, 'ready2go')
    signed_txn = w3.eth.account.signTransaction(dict(
    nonce=w3.eth.getTransactionCount(accounts[1]),
    gasPrice = w3.eth.gasPrice, 
    gas = 100000,
    to=accounts[2],
    value=w3.toWei(10,'ether')
  ),
  private_key)
print("tx_count",w3.eth.getTransactionCount(accounts[0]))
rawHash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
hexHash = w3.toHex(rawHash)
print("hexhash",hexHash)
y = time.time()
try:
   x = w3.eth.waitForTransactionReceipt(hexHash)
except:
   raise
print(x)
print(y-time.time())
print(w3.fromWei(w3.eth.getBalance(accounts[2]),"ether"))
print(w3.fromWei(w3.eth.getBalance(accounts[1]),"ether"))
print(w3.fromWei(w3.eth.getBalance(accounts[0]),"ether"))

 

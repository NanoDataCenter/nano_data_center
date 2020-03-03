#from  utilities.web3_top_class import Web_Class_IPC
from utilities.event_listener_top_class import Event_Listner_Class_IPC
import redis
import time
import datetime
redis_handle = redis.StrictRedis( db=1 )

ipc_socket = "/home/pi/geth.ipc"






ev = Event_Listner_Class_IPC(ipc_socket,redis_handle)





print(ev.get_block_number())
ev.construct_loop_filter("EventHandler")
temp = ev.get_all_entries("EventHandler")
for event in temp:
   print(event["args"],event["blockNumber"])
def event_handler(event):
   print(dict(event["args"]),event["blockNumber"])
   if event.blockNumber > 25:
      return True
   else:
      return True

ev.lastest_event_loop("EventHandler",event_handler)


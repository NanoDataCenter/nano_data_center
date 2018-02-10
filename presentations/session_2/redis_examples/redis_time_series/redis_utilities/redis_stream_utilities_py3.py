import redis
import time

class Redis_Stream_Client(object):
   def __init__(self,redis_handle):
       self.redis_handle = redis_handle
       
   def xadd(self,key,max_len=100,id="*",data_dict = {} ):
       command_list = []
       command_list.append("XADD")
       command_list.append(str(key))
       command_list.append("MAXLEN   "+str(max_len))
       command_list.append(str(id))
       for key,data in data_dict.items():
          command_list.append(str(key)+"  "+str(data) )
       command_string = " ".join(command_list)
       #print(command_string)
       return self.redis_handle.execute_command(command_string)
       
       
   def xrange(self,key, start_time_stamp, end_time_stamp , count=100):
       command_list = []
       command_list.append("XRANGE")
       command_list.append(str(key))
       command_list.append(start_time_stamp)
       command_list.append(end_time_stamp)
       command_list.append("COUNT "+str(count))
     
       command_string = " ".join(command_list)
       #print(command_string)  
       return self.__send_and_process_range_command__(command_string)
       
     
   def xrevrange(self,key, start_time_stamp, end_time_stamp , count=100):
       command_list = []
       command_list.append("XREVRANGE")
       command_list.append(str(key))
       command_list.append(start_time_stamp)
       command_list.append(end_time_stamp)
       command_list.append("COUNT "+str(count))
       
       command_string = " ".join(command_list)
       #print(command_string)
       return self.__send_and_process_range_command__(command_string)


   def __send_and_process_range_command__(self, command_string): 
       temp = self.redis_handle.execute_command(command_string)
       return_value = []
       for i in temp:
          return_item= {}
          ids = i[0].split("-")
          
          return_item["id"] = i[0]
          return_item["timestamp"] = float(ids[0])/1000.
          return_item["sub_id"] = int(ids[1])
          data_list = i[1]
          return_data = {}
          return_item["data"] = return_data
          
          for j in range(0,len(data_list),2):
             return_data[data_list[j]] = data_list[j+1]
          return_value.append(return_item)
       return return_value

           
if __name__ == "__main__":

   redis_handle = redis.StrictRedis( host = "localhost", port = 6379, db =0, decode_responses=True)
   redis_stream = Redis_Stream_Client(redis_handle)
   key ="stream_1"
   data_dict = { "a":2,"b":3}
   for i in range(0,200):
     print(redis_stream.xadd(key,100,"*",data_dict  ))
     data_dict["a"] = i
     data_dict["b"] = i*2
   print(redis_stream.xrange(key,"-","+",count=2))
   print(time.time())
   
   print(redis_stream.xrevrange(key,"+","-",count=2))
   print(time.time())





'''
/* XRANGE/XREVRANGE actual implementation. */
/* XRANGE key start end [COUNT <n>] */
/* XREVRANGE key end start [COUNT <n>] */
* XLEN */

/* XREAD [BLOCK <milliseconds>] [COUNT <count>] [GROUP <groupname> <ttl>]
 *       [RETRY <milliseconds> <ttl>] STREAMS key_1 key_2 ... key_N
 *       ID_1 ID_2 ... ID_N */
 
 /* XADD key [MAXLEN <count>] <ID or *> [field value] [field value] ... */
 
 f you want only the last entry:
XREVRANGE mystream + - count 1

If you want only the first entry:
XRANGE mystream - + count 1
'''

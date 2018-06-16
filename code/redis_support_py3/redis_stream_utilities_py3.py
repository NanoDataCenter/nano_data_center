import redis
import time
import msgpack

class Redis_Stream(object):
   def __init__(self,redis_handle, exact_flag = False):
       self.redis_handle = redis_handle
       if exact_flag == True:
          self.add_pad = ""
       else:
          self.add_pad = "~"
          
   
   def xadd(self,key,max_len=100,id="*",data_dict = {} ):
       

       return self.redis_handle.execute_command("XADD",key,'MAXLEN','~', max_len, id, "data",data_dict["data"])
       
       
   def xrange(self,key, start_timestamp, end_timestamp , count=100):
       print(key, start_timestamp, end_timestamp , count)
       return self.__send_and_process_range_command__("XRANGE",key,start_timestamp,end_timestamp,count)
       
     
   def xrevrange(self,key, start_timestamp, end_timestamp , count=100):
       print(key, start_timestamp, end_timestamp , count)
       return self.__send_and_process_range_command__("XREVRANGE",key,start_timestamp,end_timestamp,count)

   def xdel(self,id):
       
       return self.redis_handle.execute_command("XDEL",self.key,id)
       
   def xtrim(self,key):
       pass  # future stream command

   def xlen(self,key):
        return self.redis_handle.execute_command("XLEN",key)
       
   def __send_and_process_range_command__(self, command, key, start_time,end_time,count): 
       if count != 0:
          temp = self.redis_handle.execute_command(command, key,start_time,end_time,"COUNT",count)
       else:
          temp = self.redis_handle.execute_command(command, key,start_time,end_time)

       return_value = []
       for i in temp:
          return_item= {}
          i[0] = i[0].decode()
          ids = i[0].split("-")
          
          return_item["id"] = i[0]
          return_item["timestamp"] = float(ids[0])/1000.
          return_item["sub_id"] = int(ids[1])
          packed_data = i[1][1]

          return_item["data"] = msgpack.unpackb(packed_data,encoding='utf-8')
          return_value.append(return_item)
      
       return return_value

           
if __name__ == "__main__":
    pass
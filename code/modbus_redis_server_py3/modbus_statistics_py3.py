import datetime
import time

class Hash_Logging_Object(object):

   def __init__( self, handlers,logging_key,depth):
       self.handlers = handlers
       self.logging_key = logging_key
       self.depth       = depth
       self.handler = self.handlers[logging_key]
       #self.handler.delete_all() # usefull for testing
       
   def log_value(self,key,measurement):
       if self.handler.hexists(key) == False: 
            temp = [measurement]
       else:
          temp = self.handler.hget(key)
          if isinstance(temp,list):
             temp.append(measurement)
          else:
             temp = [measurement]
       
       while len(temp) > self.depth:
             temp = temp[1:]      
       self.handler.hset(key,temp)
       
       
       
class Statistic_Handler( object ):
    
   def __init__(self,generate_handlers,data_structures,remote_units ):
       depth = 24*7*4  # one month worth of data
       self.remote_units = remote_units
       self.handlers = {}
       self.handlers["RECENT_DATA"] = generate_handlers.construct_single_element(data_structures["PLC_RECENT_DATA"] )
       self.handlers["REMOTE_DATA"] =  generate_handlers.construct_hash(data_structures["PLC_REMOTES"] )
       self.handlers["BASIC_STATUS"] =  generate_handlers.construct_hash(data_structures["PLC_BASIC_STATUS"] )
       
       self.hash_log = {}
       self.hash_log["BASIC_STATUS"] =  Hash_Logging_Object(self.handlers,"BASIC_STATUS",depth) 
       self.hash_log["REMOTE_DATA"] = Hash_Logging_Object(self.handlers,"REMOTE_DATA",depth) 
       self.initialize_logging_data()

   def initialize_logging_data( self ):
       self.start_base = time.time()

       self.basic_state = {}

       self.basic_state["HOUR"] = datetime.datetime.now().hour
       self.basic_state["MINUTE"] = datetime.datetime.now().minute
       self.basic_state["SECOND"] = datetime.datetime.now().second
       #initial basic stuff
       self.basic_state["TIME_STAMP"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
       self.basic_state["BUSY_TIME"] = 0
       self.basic_state["IDLE_TIME"] = 0
       self.basic_state["MESSAGE_COUNT"] = 0
       self.basic_state["MESSAGE_LOST"] = 0
       self.basic_state["RETRIES"]= 0
       self.basic_state["TIME_RATIO"] = 0
       self.handlers["RECENT_DATA"].set(self.basic_state)
       #initialize remotes

            
       self.remote_data = {}
       for i in self.remote_units.keys():
           item = {}
           item["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
           item["message_count"] = 0
           item["message_loss"] = 0
           item["retries"] = 0
           self.remote_data[i] = item
                 
         
   def hour_rollover( self ):
       if self.basic_state["HOUR"] !=datetime.datetime.now().hour:
           print("hour rollover")
           self.hour_basic_statistics()
           self.hour_remote_statistics()
           self.initialize_logging_data()
        
   def hour_basic_statistics( self ):
        self.update_overall_statistics()
        for i,item in self.basic_state.items():
            self.hash_log["BASIC_STATUS"].log_value(i,item)
        
   def update_overall_statistics(self):
       total_time =  self.basic_state["BUSY_TIME"] + self.basic_state["IDLE_TIME"]
       if total_time == 0 :
           self.basic_state["TIME_RATIO"] = 0   
       else:
           self.basic_state["TIME_RATIO"] = ( self.basic_state["BUSY_TIME"] *100)/total_time
       
       self.basic_state["TIME_STAMP"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
       

   def hour_remote_statistics(self):
     
       for i,item in self.remote_units.items():           
           self.hash_log["REMOTE_DATA"].log_value(i,item)
   

#
#  These are rpc handlers for statistics
#
#
   def process_start_message( self , modbus_address ): 
       self.start_base = time.time()
       
   def log_bad_message( self, modbus_address,retries ):
       self.basic_state["MESSAGE_COUNT"] +=1
       self.basic_state["MESSAGE_LOST"] += 1
       self.basic_state["RETRIES"] +=retries
       if modbus_address in self.remote_units:
           self.remote_data[modbus_address]["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
           self.remote_data[modbus_address]["message_count"] += 1
           self.remote_data[modbus_address]["message_loss"] += 1
           self.remote_data[modbus_address]["retries"] += retries

        
   def log_good_message( self, modbus_address,retries ):
       self.basic_state["MESSAGE_COUNT"] +=1
       self.basic_state["RETRIES"] +=retries
       if modbus_address in self.remote_units:
           self.remote_data[modbus_address]["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
           self.remote_data[modbus_address]["message_count"] += 1
           self.remote_data[modbus_address]["retries"] += retries

        
   def process_end_message( self ):
       self.time_base = time.time()
       delta_t = self.time_base - self.start_base
       self.basic_state["BUSY_TIME"] += delta_t
       self.update_current_state()
        
   def process_null_message( self ):
        print("null message")
        self.basic_state["MINUTE"] = datetime.datetime.now().minute
        self.basic_state["SECOND"] = datetime.datetime.now().second 
        temp = time.time()
        delta_t = temp - self.start_base
        self.start_base = temp
        self.basic_state["IDLE_TIME"] = self.basic_state["IDLE_TIME"] + delta_t
        self.hour_rollover()
        self.update_current_state()         

   def update_current_state(self):
       self.update_overall_statistics()
       temp = self.basic_state
       temp["remote_data"] = self.remote_data
       self.handlers["RECENT_DATA"].set( temp)   
       print(self.handlers["RECENT_DATA"].get())
   
   
   

class Statistic_Handler( object ):
    
   def __init__(self,handlers,redis_rpc_queue, remote_units,graph_key, rpc_queue ):

       # copy instantiation parameters
       
        self.remote_units = remote_units
  
        self.time_base = time.time()
        self.handlers = handlers
        
        
        
        
        self.queue_history_length =  1500
        self.redis_current_key = self.graph_key+":RECENT_DATA"
        self.redis_hour_key    = self.graph_key+":HOUR_DATA"
        self.redis_server_queue = self.redis_hour_key+":SERVER_QUEUE"
        self.redis_basic_queue = self.redis_hour_key+":BASIC_STATS"
        self.redis_remote_queue_header = self.redis_hour_key+":REMOTES"        
        self.redis_remote_queues = {}
        for i in remote_units:
            self.redis_remote_queues[i] = self.redis_remote_queue_header+":"+str(i)
            
            
        for i in [  self.redis_current_key,self.redis_hour_key,self.redis_basic_queue]: 
            self.verify_list(i)
        for i, item in self.redis_remote_queues.items():
            self.verify_list(i)
            
        self.initialize_logging_data()

    def process_null_message( self ):

        temp = time.time()
        delta_t = temp - self.time_base
        self.time_base = temp
        self.idle_time = self.idle_time + delta_t
        if self.hour != datetime.now().hour:
        
             self.hour_rollover()

        self.update_current_state()
        
        
        
    def process_start_message( self , modbus_address ):
       
        self.start_base = time.time()
      
        
         
    def process_end_message( self ):
        self.time_base = time.time()
        delta_t = self.time_base - self.start_base
        self.busy_time += delta_t
        if self.hour != datetime.now().hour:
             self.hour_rollover()
        self.update_current_state()
        


 
    def update_current_state(self):
        data = self.update_current_state_a()
 
        data["remotes"] = {}
        for i in self.remote_units:           
            data["remotes"][i] = self.remote_data[i]
        self.redis_handle.set(self.redis_current_key, json.dumps(data ) )       
        return data
        
    def update_current_state_a(self):
        total_time = self.busy_time + self.idle_time
        if total_time == 0 :
            time_ratio = 0   
        else:
            time_ratio = ( self.busy_time *100)/total_time
        data = {}
        data["time_ratio"] = time_ratio
        data["counts"] = self.message_count
        data["losses"] = self.message_loss 
        data["retries"] = self.retries
        data["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
       
        
        return data
 


       
    def update_list( self, key, data ):
        self.redis_handle.lpush(key,data)
        self.redis_handle.ltrim(key,0,self.queue_history_length  )
       
    def verify_list( self, item ):
            if self.redis_handle.exists(item):
                if self.redis_handle.type(item) == "list":
                    pass                   
                else:
                    self.redis_handle.delete(item)              

        
 
                
        
    def hour_rollover( self ):
        print("hour rollover")
        self.hour_basic_stuff()
        self.hour_remote_stuff()
        self.initialize_logging_data()
        
    def hour_basic_stuff( self ):
        data = self.update_current_state_a()
        self.update_list(self.redis_basic_queue, json.dumps(data ) )
 
    def hour_remote_stuff( self ):
        for i, item in self.remote_data.items():
           self.update_list(self.redis_remote_queues[i], json.dumps(item))
        


 
    def log_bad_message( self, modbus_address,retries ):
        self.message_count +=1
        self.message_loss += 1
        self.retries +=retries
        if modbus_address in self.remote_units:
            self.remote_data[modbus_address]["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
            self.remote_data[modbus_address]["message_count"] += 1
            self.remote_data[modbus_address]["message_loss"] += 1
            self.remote_data[modbus_address]["retries"] += retries

        
    def log_good_message( self, modbus_address,retries ):
        self.message_count +=1
        self.retries +=retries
        if modbus_address in self.remote_units:
            self.remote_data[modbus_address]["time_stamp"] = time.strftime( "%b %d %Y %H:%M:%S",time.localtime(time.time()))
            self.remote_data[modbus_address]["message_count"] += 1
            self.remote_data[modbus_address]["retries"] += retries

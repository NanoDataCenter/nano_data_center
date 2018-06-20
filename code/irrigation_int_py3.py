from redis_support_py3.construct_data_handlers_py3 import Stream_Writer
from redis_support_py3.construct_data_handlers_py3 import Stream_Reader
from redis_support_py3.construct_data_handlers_py3 import Redis_Hash_Dictionary
from redis_support_py3.cloud_handlers_py3 import Cloud_TX_Handler
from redis_support_py3.load_files_py3  import APP_FILES
from redis_support_py3.load_files_py3  import SYS_FILES
import redis
import json
from redis_support_py3.user_data_tables_py3 import Generate_Table_Handlers


class Irrigation_Streams(object):

   def __init__(self,generate_handlers):
        self.generate_handlers = generate_handlers
        self.redis_handle = generate_handlers.get_redis_handle()
        
   def get_stream_keys(self):
         return_value = self.redis_handle.keys("*:IRRIGATION]*")
         if return_value == None:
            return_value = []
         temp = self.redis_handle.keys("*:IRRIGATION_TIME_SERIES]*")
         if temp != None:
             return_value.extend(temp)
         temp_list = return_value
         return_value = []
         for i in temp_list:
            return_value.append(i.decode())
         return return_value
         
         
   def  parse_key(self,key):
       
       result = key.split("[STREAM:")
       if len(result) == 2:
          schedule,step = result[1].split("|")
          return schedule,step
       else:
          return None,None

        
   def get_irrigation_stream_reader(self, schedule, step ):
       return self.generate_handlers.construct_stream_reader("IRRIGATION",str(schedule)+"|"+str(step))
        
        
   def get_irrigation_stream_writer(self,schedule,step,depth =100):
       return self.generate_handlers.construct_stream_writer("IRRIGATION",str(schedule)+"|"+str(step),depth)
 
   def get_irrigation_time_series_stream_reader(self, schedule, step ):
       return self.generate_handlers.construct_stream_reader("IRRIGATION_TIME_SERIES",str(schedule)+"|"+str(step))
        
class Valve_Resistance_Data(object):
    
   def __init__(self,generate_handlers):
       self.generate_handlers = generate_handlers
       self.redis_handle = generate_handlers.get_redis_handle()
      
   def get_stream_keys(self):
         return_value =self.redis_handle.keys("*:RESISTANCE]*")
         if return_value == None:
            return_value = []
         return return_value

   def  parse_key(self,key):
       result = key.split("[STREAM_LIST:")
       if len(result) == 2:
          schedule,step = result[1].split("|")
          return schedule,step
       else:
          return None,None 
          
   def get_valve_map(self):
       return self.generate_handlers.construct_hash("RESISTANCE_TABLE","VALVE_MAP")
        
   def get_resistance_stream_reader(self, controller, pin ):
       return self.generate_handlers.construct_stream_reader("RESISTANCE",str(controller)+"|"+str(pin))
        
        
   def get_resistance_stream_writer(self,controller,pin,dept =100):
      return self.generate_handlers.construct_stream_writer("RESISTANCE",str(controller)+"|"+str(pin),depth)        	

      


class User_Data_Tables(object):

   def __init__(self, redis_site_data ):
       self.backup_db     = redis_site_data["redis_backup_db"]
       self.redis_site_data = redis_site_data
       self.table_handler = Generate_Table_Handlers( redis_site_data )
       self.redis_handle = self.table_handler.get_redis_handle()

       self.app_file_handle = APP_FILES( self.redis_handle,self.redis_site_data )
       self.sys_filie_handle = SYS_FILES( self.redis_handle,self.redis_site_data)
       
       self.valve_resistance_data = Valve_Resistance_Data(self.table_handler)
       
      
       self.irrigation_streams = Irrigation_Streams(self.table_handler)

   def get_redis_handle(self):
      return self.redis_handle   
       
   def initialize(self):
       
       self.initialize_irrigation_streams()
       self.initialize_valve_resistance_streams()
 
   def initialize_irrigation_streams(self):    
       schedule_dictionary = {}

       sprinkler_ctrl = self.app_file_handle.load_file("sprinkler_ctrl.json")

       for j in sprinkler_ctrl:
           schedule = j["name"]
          
           json_data  =self.app_file_handle.load_file(j["link"]) 
           schedule_dictionary[schedule] = len(json_data)

                   
           
       #
       #  Now remove irrigation streams which do are not defined
       #
       #
       #
       return
       #### work on this later
       ref_keys = self.irrigation_streams.get_stream_keys()
       if ref_keys == None:
          ref_keys = []
       for i in ref_keys:
          schedule,step = self.irrigation_streams.parse_key(i)
          if (schedule==None) or (step==None):
             self.redis_handle.move(i,self.backup_db)
          if schedule not in schedule_dictionary:
              self.redis_handle.move(i,self.backup_db)
              continue
          if step >= schedule_dictionary[schedule]:
              self.redis_handle.move(i,self.backup_db)     
              
   def initialize_valve_resistance_streams(self):
   
       valve_map = self.valve_resistance_data.get_valve_map()
       valve_map.delete_all()
       
       
       
      
       controller_dictionary = {}

       sprinkler_ctrl = self.app_file_handle.load_file("sprinkler_ctrl.json")

       for j in sprinkler_ctrl:
           schedule = j["name"]
           json_data  =self.app_file_handle.load_file(j["link"]) 
           for i in json_data["schedule"]:
             for k in i:
                remote = k[0]
                pin    = str(k[1][0])
                if remote not in controller_dictionary:
                     controller_dictionary[remote] = set()
                     
                if pin not in controller_dictionary[remote]:
                   controller_dictionary[remote].add(pin) 
                   
       for i, item in controller_dictionary.items():   
           valve_map.hset(i,list(item)) 
           
       #
       #  Now remove resistance streams which do are not defined
       #
       #
       #
       ref_keys = self.valve_resistance_data.get_stream_keys()
       
       for i in ref_keys:
          controller,pin = self.valve_resistance.parse_key()
          if (controller==None) or (pin==None):
             self.redis_handle.move(i,self.backup_db)

          if controller not in controller_dictionary:
              self.redis_handle.move(i,self.backup_db)
              continue
          if pin not in controller_dictionary[controller]:
              self.redis_handle.move(i,self.backup_db)
               
              
if __name__ == "__main__":

    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site_data = json.loads(data)
    user_data = User_Data_Tables(redis_site_data)
    user_data.initialize()    
             
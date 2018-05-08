



from .construct_data_handlers_py3 import Stream_Writer
from .construct_data_handlers_py3 import Stream_Reader
from .construct_data_handlers_py3 import Stream_List_Reader
from .construct_data_handlers_py3 import Stream_List_Writer
from .construct_data_handlers_py3 import Redis_Hash_Dictionary
from .cloud_handlers_py3 import Cloud_TX_Handler
from .load_files_py3  import APP_FILES
from .load_files_py3  import SYS_FILES
import redis
import json


class Generate_Table_Handlers(object):

   def __init__(self,site_data):
       self.site_data = site_data   
      
       self.redis_handle = redis.StrictRedis( host = site_data["host"] , port=site_data["port"], db=site_data["redis_table_db"] , decode_responses=True)
       self.prefix = "[SITE:"+site_data["site"]+"][TABLE_DATA:"
       self.cloud_handler = Cloud_TX_Handler(self.redis_handle) 
       
   def get_redis_handle(self):
       return self.redis_handle   


         
   def construct_hash(self,table_name,hash_name):
         data = {}
         key = self.prefix + table_name+"][HASH:"+hash_name+"]"
         return  Redis_Hash_Dictionary( self.redis_handle,key,data,self.cloud_handler )


   def construct_stream_writer(self,table_name,stream_name,depth):
         data = { "depth":depth}
         key = self.prefix + table_name+"][STREAM:"+stream_name+"]"
         return Stream_Writer(self.redis_handle,key,data,self.cloud_handler)
         
   def construct_stream_reader(self,table_name,stream_name):
         
         key = self.prefix + table_name+"][STREAM:"+stream_name+"]"
         return Stream_Reader(self.redis_handle,key)

   def construct_stream_list_writer(self,table_name,stream_name,depth):
         data = { "depth":depth}
         key = self.prefix + table_name+"][STREAM_LIST:"+stream_name+"]"
         return Stream_List_Writer(self.redis_handle,key,data,self.cloud_handler)


   def construct_stream_list_reader(self,table_name,stream_name):
      
        key = self.prefix + table_name+"][STREAM_LIST:"+stream_name+"]"
        return Stream_List_Reader(self.redis_handle,key)
  

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
        
        

class ETO_Data(object):

   def __init__(self,generate_handlers):
        self.generate_handlers = generate_handlers
        self.redis_handle = generate_handlers.get_redis_handle()

   def get_hash_table(self):
       return  self.generate_handlers.construct_hash("ETO","ETO_TABLE")

        
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
  
class Irrigation_Scheduling(object):

   def __init__(self,generate_handlers):
        self.generate_handlers = generate_handlers
        self.redis_handle = generate_handlers.get_redis_handle()

   def get_hash_table(self):
       return  self.generate_handlers.construct_hash("IRRIGATION_SCHEDULING","SCHEDULE_COMPLETED")

class System_Scheduling(object):

   def __init__(self,generate_handlers):
        self.generate_handlers = generate_handlers
        self.redis_handle = generate_handlers.get_redis_handle()

   def get_hash_table(self):
       return  self.generate_handlers.construct_hash("SYSTEM_SCHEDULING","SYSTEM_COMPLETED")
       
  
class User_Data_Tables(object):

   def __init__(self, redis_site_data ):
       self.backup_db     = redis_site_data["redis_backup_db"]
       self.redis_site_data = redis_site_data
       self.app_file_handle = APP_FILES( redis_site_data )
       self.sys_filie_handle = SYS_FILES(redis_site_data,self.app_file_handle.get_redis_handle())
       self.table_handler = Generate_Table_Handlers( redis_site_data )
       self.redis_handle = self.table_handler.get_redis_handle()
       self.valve_resistance_data = Valve_Resistance_Data(self.table_handler)
       self.system_scheduling = System_Scheduling(self.table_handler)
       self.irrigation_scheduling = Irrigation_Scheduling(self.table_handler)
       self.eto_data = ETO_Data( self.table_handler )
       self.irrigation_streams = Irrigation_Streams(self.table_handler)
   
       
   def initialize(self):
       self.initialize_eto_tables()
       self.initialize_irrigation_streams()
       self.initialize_valve_resistance_streams()
      
   def initialize_eto_tables(self):
       eto_file_data = self.app_file_handle.load_file("eto_site_setup.json")
       eto_redis_hash_table = self.eto_data.get_hash_table()
       eto_redis_hash_data = eto_redis_hash_table.hgetall()
       if eto_redis_hash_data == None:
          eto_redis_hash_data = {}
       new_data = {}
       
       #
       # Step 1  Populate file
       #
       for j in eto_file_data:
           new_data[ j["controller"] + "|" + str(j["pin"])] = 0
       #
       # populate from redis hash table
       #
       #
       eto_redis_hash_table.delete()
       for i in new_data.keys():
           data = new_data[i]
           if i in eto_redis_hash_data:
              data = eto_redis_hash_data[i]
           eto_redis_hash_table.hset(i,data )  
           
   def initialize_valve_resistance_streams(self):
   
       valve_map = self.valve_resistance_data.get_valve_map()
       valve_map.delete()
       
       
       
      
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
       
       ref_keys = self.irrigation_streams.get_stream_keys()
       if ref_keys == None:
          ref_keys = []
       for i in ref_keys:
          schedule,step = self.irrigation_streams.parse_key()
          if (schedule==None) or (step==None):
             self.redis_handle.move(i,self.backup_db)
          if schedule not in schedule_dictionary:
              self.redis_handle.move(i,self.backup_db)
              continue
          if step >= schedule_dictionary[schedule]:
              self.redis_handle.move(i,self.backup_db)      
                
if __name__ == "__main__":

    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site_data = json.loads(data)
    user_data = User_Data_Tables(redis_site_data)
    user_data.initialize()    

import json
import redis

import redis_graph_py3
from .  import redis_graph_functions
from   .redis_graph_functions  import Build_Configuration
from    .redis_graph_functions  import Query_Configuration



class Construct_System(Build_Configuration):

   def __init__( self, db = 14 ):
         print("db",db)
         redis_handle  = redis.StrictRedis( host = "localhost", port=6379, db=db , decode_responses=True)
      
         super().__init__(redis_handle )
    

   def construct_system( self,name,properties={}):
   
       self.construct_node( push_namespace = True,  relationship="SYSTEM", label = name,  
          properties=properties)
       
   def end_system( self):
       self.pop_namespace()

   def construct_site( self,name, address, properties={}):

       properties["address"] = address
       self.construct_node(  push_namespace=True,relationship="SITE", label=name,  
               properties =properties)

   def end_site( self ):
      self.pop_namespace()

   def add_redis_data_store( self, name, ip, port=6379, properties = {} ):
       
       properties["ip"] = ip
       properties["port"] = port
       self.construct_node( push_namespace=True,relationship="DATA_STORE", label=name,
                               properties= properties )
   def start_moisture_store( self ):
       self.construct_node( push_namespace=True,relationship="MOISTURE_STORE", label="MOISTURE_STORE",
                               properties= {} )

   def end_moisture_store( self ):
      self.pop_namespace()

      
   def add_moisture_sensor_store( self, name, description, description_map, depth_map, update_time ):
       properties = {}
       properties["description"] = description
       properties["description_map"] = json.dumps(description_map)
       properties["update_time"] = update_time
       properties["depth_map"] = json.dumps(depth_map)
       self.construct_node( push_namespace=True,relationship="MOISTURE_DATA", label=name,
                               properties= properties )
   
   def add_status_store( self, name, queue_name):
       properties = {}
       properties["queue_name"] = queue_name
       self.construct_node( push_namespace=True,relationship="STATUS_STORE", label=name,
                               properties= properties )

   def start_info_store( self ):
       self.construct_node( push_namespace=True,relationship="INFO_STORE", label="INFO_STORE",
                               properties= {} )

  
   def add_eto_store(self ):
       self.construct_node( push_namespace=False,relationship="ETO_STORE", label="ETO_STORE",
                               properties= {} )


   def add_air_temperature_humidity_store(self):
       self.construct_node( push_namespace=False,relationship="TEMP_HUMIDITY", label="TEMP_HUMIDITY",
                               properties= {} )

   def add_air_temperature_humidity_daily_log(self):
       self.construct_node( push_namespace=False,relationship="TEMP_HUMIDITY_DAILY", label="TEMP_HUMIDITY_DAILY",
                               properties= {} )
       self.construct_node( push_namespace=False,relationship="TEMP_HUMIDITY_DAILY_ETO", label="TEMP_HUMIDITY_DAILY_ETO",
                               properties= {} )


   def end_info_store(self):   
       self.pop_namespace()



   def end_redis_data_store( self):
       self.pop_namespace()

   def add_udp_io_sever(self, name, ip,remote_type, port, properties={} ):

       properties["ip"] = ip
       properties["remote_type"] = remote_type
       properties["port"] = port
       return self.construct_node(  push_namespace=True,relationship="UDP_IO_SERVER", 
               label=name, properties = properties )


   def end_udp_io_server(self ):
       self.pop_namespace()


   def add_rtu_interface(self, name ,protocol, baud_rate, properties={} ):

       properties["protocol"]= protocol
       properties["baud_rate"] = baud_rate
       return self.construct_node(  push_namespace=True,relationship="RTU_INTERFACE", 
                 label=name,properties = properties)

   def end_rtu_interface( self ):
       self.pop_namespace()



   def add_remote( self, name,modbus_address,type, function, properties = {}):

 
       properties["modbus_address"] = modbus_address
       properties["type"]           = type
       properties["function"]       = function
       self.construct_node(  push_namespace=True,relationship="REMOTE", label=name, 
               properties = properties )


   def construct_controller( self,name, ip,type,properties={} ):
       properties["name"] = name
       properties["ip"]   = ip
       self.construct_node(  push_namespace=True,relationship="CONTROLLER", label=name, 
               properties = properties)


   def end_controller( self ):
       self.pop_namespace()

   def start_service( self, properties = {} ):
       self.construct_node(  push_namespace=TRUE,relationship="SERVICES", label=name, 
               properties = properties)


   def construct_web_server( self, name,url,properties = {} ):

       properties["url"]   = url
       self.construct_node(  push_namespace=False,relationship="WEB_SERVER", label=name, 
               properties = properties)

   def add_rabbitmq_command_rpc_queue( self,name, properties = {} ):

       
       self.construct_node(  push_namespace=False,relationship="COMMAND_RPC_QUEUE", label=name, 
                                properties = properties)

   def add_rabbitmq_web_rpc_queue( self,name, properties = {} ):
 
       
       self.construct_node(  push_namespace=False,relationship="WEB_RPC_QUEUE", label=name, 
                                properties = properties)

   def add_rabbitmq_event_queue( self,name, properties = {} ):

       
       self.construct_node(  push_namespace=False,relationship="RABBITMQ_EVENT_QUEUE", label=name, 
                                 properties = properties)



   def add_rabbitmq_status_queue( self,name,vhost,queue,port,server  ):
       properties          = {}
  
       properties["vhost"]    = vhost
       properties["queue"]    = queue
       properties["port"]     = port
       properties["server"]   = server
       
       self.construct_node(  push_namespace=False,relationship="RABBITMQ_STATUS_QUEUE", label=name, 
                                 properties = properties)


   def add_ntpd_server( self,name, properties = {} ):
       
       self.construct_node(  push_namespace=False,relationship="NTPD_SERVER", label=name, 
                                properties = properties)


   def start_eto_server( self,name, properties = {} ):
 
       self.construct_node(  push_namespace=False,relationship="ETO_SERVER", label=name, properties = properties)

   def add_eto_setup_code( self, access_codes, altitude , properties = {} ):

       properties["messo_eto"]     = json.dumps( access_codes["messo_eto"] )
       properties["messo_precp"]   = json.dumps( access_codes["messo_precp"] )
       properties["cimis_eto"]     = json.dumps( access_codes["cimis_eto"] )
       properties["cimis_spatial"] = json.dumps( access_codes["cimis_spatial"])
       properties["altitude"]      = altitude
       
       self.construct_node(  push_namespace=False,relationship="ETO_SETUP_DATA", label="ETO_SETUP_DATA", 
                                 properties = properties)


   def end_eto_server(self):
         self.pop_namespace()
   

   def add_linux_server_monitor( self, name,properties = {} ):
       properties["name"]  = "Linux Server Monitor"
       
       self.construct_node(  push_namespace=False,relationship="LINUX_SERVER_MONITOR", label=name, properties = properties)

   def add_schedule_monitoring( self, name,properties = {} ):

       
       self.construct_node(  push_namespace=False,relationship="NTPD_SERVER", label=name, properties = properties)



   def add_moisture_monitoring( self, name, properties = {} ):

       
       self.construct_node(  push_namespace=False,relationship="NTPD_SERVER", label=name, properties = properties)

   def irrigation_monitoring( self, name,properties = {} ):

       
       self.construct_node(  push_namespace=False,relationship="IRRIGATION_MONITOR", label=name, properties = properties)

   def add_device_monitoring( self, name, properties = {} ):
 
       
       self.construct_node(  push_namespace=False,relationship="DEVICE_MONITOR", label=name, properties = properties)

   def add_process_monitoring( self,name, properties = {}  ):      
       self.construct_node(  push_namespace=False,relationship="PROCESS_MONITOR", label=name, properties = properties)


   def add_watch_dog_monitoring( self,name, properties = {}  ):

       
       self.construct_node(  push_namespace=False,relationship="WATCH_DOG_MONITORING", label=name, properties = properties)


   def add_io_collection( self, name, properties = {} ):

       
       self.construct_node(  push_namespace=False,relationship="PROCESS_MONITOR", label=name, properties = properties)

   def add_local_ai( self, name, properties = {} ):       
       self.construct_node(  push_namespace=False,relationship="PROCESS_MONITOR", label=name, properties = properties)

   
class Graph_Management(Query_Configuration):

   def __init__( self , controller_name , io_server_name, data_store_name,db = 14 ):
      self.redis_handle  = redis.StrictRedis( host = "localhost", port=6379, db =db , decode_responses=True)
   
      super().__init__( self.redis_handle)
      
      self.controller_name = controller_name
      self.io_server_name  = io_server_name
      self.data_store_name = data_store_name
      self.initialize_cb_handlers()


   def find_remotes( self  ):
      data = self.match_terminal_relationship( "REMOTE_UNIT", label= None , starting_set = None )
 
      return data



   def find_data_stores( self ):

       data = self.match_terminal_relationship( "DATA_STORE", label= None , starting_set = None )

       return data

   def find_io_servers( self ):
      data = self.match_terminal_relationship( "UDP_IO_SERVER", label= None , starting_set = None )
      return data

   


   def initialize_cb_handlers( self ):
       self.cb_handlers = {}

   def add_cb_handler( self, tag, function ):
       self.cb_handlers[ tag ] = function

   def verify_handler( self, tag ):
       try:
           return tag in self.cb_handlers
       except:
          #print "handlers:", type(self.cb_handlers)
          #print "tag", tag
          raise        

   def execute_cb_handlers( self, tag, value, parameters ):  # parameters is a list
       function = self.cb_handlers[tag]
       return function( tag, value , parameters )  


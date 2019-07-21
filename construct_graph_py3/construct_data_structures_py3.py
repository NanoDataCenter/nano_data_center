

class Construct_Data_Structures(object):

   def __init__(self,site,bc):
       self.bc   = bc
       self.site = site
       self.header_node = "[PACK_CTRL:" +site+ "]"
       self.current_package = None
      
       
       
   def construct_package(self,package_name):
        assert(self.current_package == None)
        self.name = package_name
        self.current_package = self.header_node+"[PACK:"+package_name+"]"
        self.properties = {}
        self.properties["data_structures"]  = {}
        
        
      
   def close_package_contruction(self):
        self.current_package = None
        self.bc.add_info_node("PACKAGE",self.name,self.properties)
        
        
   def add_managed_hash(self,name,fields,forward=False):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["type"]  = "MANAGED_HASH"
       properties["forward"] =forward
       properties["fields"] = fields
       self.properties["data_structures"][name] = properties 

      
   def add_hash(self,name,forward=False):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["type"]  = "HASH"
       properties["forward"] =forward
       self.properties["data_structures"][name] = properties 
        
      
   def add_stream(self,measurement, index = 0 ,forward=False):

       assert(measurement not in self.properties )
       properties = {}
       properties["site"] = self.site
       properties["type"]  = "STREAM"
       properties["measurement"] = measurement
       properties["index"] = index
       properties["forward"] =forward
       self.properties["data_structures"][measurement] = properties 

   def add_redis_stream(self,name,depth=256,forward=False):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["type"]  = "STREAM_REDIS"
       properties["depth"]  =depth
       properties["forward"] =forward
       self.properties["data_structures"][name] = properties 

       
   def add_stream_list(self,name,depth,forward=False):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["type"]  = "STREAM_LIST"
       properties["depth"]  =depth
       properties["forward"] =forward
       self.properties["data_structures"][name] = properties 
       
   def add_job_queue(self,name,depth,forward=False):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["depth"] = depth
       properties["type"]  = "JOB_QUEUE"
       properties["forward"] =forward
       self.properties["data_structures"][name] = properties 
      
      
   def add_rpc_server(self,name,depth):
       assert(name not in self.properties )
       properties = {}
       properties["namde"] = name
       properties["depth"] = depth
       properties["type"]  = "RPC"
       self.properties["data_structures"][name] = properties 
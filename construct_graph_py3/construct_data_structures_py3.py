

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
        
   def add_single_element(self,name,forward=False):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["type"]  = "SINGLE_ELEMENT"
       self.properties["data_structures"][name] = properties 
       
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
        
      


   def add_redis_stream(self,name,depth=1024,forward=False):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["type"]  = "STREAM_REDIS"
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
      
      
   def add_rpc_server(self,name,properties = {}):
       assert(name not in self.properties )
      
       properties["name"] = name
       
       properties["type"]  = "RPC_SERVER"
       self.properties["data_structures"][name] = properties 
      
   def add_rpc_client(self,name):
       assert(name not in self.properties )
       properties = {}
       properties["name"] = name
       properties["type"]  = "RPC_CLIENT"
       self.properties["data_structures"][name] = properties
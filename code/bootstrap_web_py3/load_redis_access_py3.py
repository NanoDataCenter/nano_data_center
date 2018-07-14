#
#
#  File: load_redis_access_py3.py
#
#
#
import json




class Web_Redis_Hash_Dictionary(object):

   def __init__(self):
       self.operation_table = {}
       self.operation_table["delete_all" ] = self.delete_all
       self.operation_table["hset" ] = self.hset
       self.operation_table["hmset" ] = self.hmset
       self.operation_table["hget" ] = self.hget 
       self.operation_table["hgetall" ] = self.hgetall
       self.operation_table["hkeys"] = self.hkeys
       self.operation_table[ "hexists"] = self.hexists
       self.operation_table["hdelete" ] = self.hdelete

   def process_request(handler,operation_type):
       if operation_type in self.operation_table:
          return self.operation_table[operation_type](handler,param)   
       else:
          raise ValueError("unsupported_operation")       
   
   def delete_all( self,handler,param ):
       handler.delete_all()
       return json.dumps("SUCCESS")
      

   def hset(self,handler,param):
       handler.hset(param["field"],param["data"])  
       return json.dumps("SUCCESS")       

   def hmset(self,handler,param):
      
       handler.hmset(param["dictionary_table"])
       return json.dumps("SUCCESS")
        
   def hget(self,handler,param):
       return json.dumps(handler.hget(param["field"]))   
      
   def hgetall(self,handler,param):
       
       return json.dumps(handler.hgetall(  ))
      
   def hkeys(self,handler,param) :
       return json.dumps( handler.hkeys() )
   
   def hexists(self,handler,param):
       return json.dumps(handler.hexists(param["field"]))
    
   def hdelete(self,handler,param):
       handler.hdelete(param["field"])
       return json.dumps("SUCCESS")
       
          
class Web_Job_Queue_Client( object ):
 
   def __init__(self):
       self.operation_table = {}
       self.operation_table["delete_all" ] = self.delete_all
       self.operation_table["delete" ] = self.delete
       self.operation_table["length" ] = self.length
       self.operation_table["push" ] = self.push 

   def process_request(handler,operation_type):
       if operation_type in self.operation_table:
          return self.operation_table[operation_type](handler,param)   
       else:
          raise ValueError("unsupported_operation")       
  
   def delete_all( self,handler,param ):
        handler.delete_all()
        return json.dumps("SUCCESS")
     
   def delete( self,handler,param ):   
       handler.delete(self, index )
       return json.dumps("SUCCESS")      
       
   def length( self,handler,param ):   
       return json.dumps(handler.length())
       
   
   def push( self,handler,param ):   
       handler.push(param["data"])
       return json.dumps("SUCCESS")
        

        
class Web_Stream_Reader(object):
       
   def __init__(self):
       self.operation_table = {}
       self.operation_table["delete_all" ] = self.delete_all
       self.operation_table["range" ] = self.range
       self.operation_table["revrange" ] = self.revrange
  
   
   def delete_all( self,handler,param ):
        handler.delete_all()
        return json.dumps("SUCCESS")
     
     
     
   def range(self,handler,param ):     
       json.dumps(handler.range(param["start_timestamp"], param["end_timestamp"] , param["count"] ))
 
   def revrange(self,handler,param ):
       json.dumps(handler.revrange(param["start_timestamp"], param["end_timestamp"] , param["count"] ))



class Load_Redis_Access(object):

   def __init__( self, app, auth, request ):
       self.app           = app
       self.auth          = auth
       self.request      = request
       self.access_handlers = {}
       self.operations = {}
       self.operations["Redis_Hash_Dictionary"] = Web_Redis_Hash_Dictionary()
       self.operations["Job_Queue_Client"]   = Web_Job_Queue_Client()
       self.operations["Stream_Reader"] = Web_Stream_Reader()      
       a1 = auth.login_required( self.redis_access )
       app.add_url_rule('/ajax/redis_access',"redis_access",a1,methods=["POST"])


   def add_access_handlers(self,name,handler,type):
       if type in self.operations:
           if name not in self.access_handlers:
               self.access_handlers[name] = {"handler":handler,"type":type}
           else:
              raise ValueError("duplicate key")
       else:
          raise ValueError("invalid handler")
       
       
   def redis_access( self ):
       param = self.request.get_json()
       name = param["name"]
       type = param["type"]
       operation = param["operation"]
       print("**********************************************param",param)
       print("**********************************************keys",self.access_handlers.keys())
       if name in self.access_handlers.keys():
           
           handler = self.access_handlers[name]["handler"]
       else:
           raise ValueError("Non existant handler")
       if type in self.operations:
           access_function = self.operations[type].operation_table[operation]
           return access_function(handler,param)
       
       else:
          raise ValueError("Bad operation type")
      
       

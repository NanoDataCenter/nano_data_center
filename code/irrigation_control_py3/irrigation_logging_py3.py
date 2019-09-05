import json
import base64
import time

class Hash_Logging_Object(object):

   def __init__( self, handlers,logging_key,depth):
       self.handlers = handlers
       self.logging_key = logging_key
       self.depth       = depth
       self.handler = self.handlers[logging_key]
       self.handler.delete_all()
       
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
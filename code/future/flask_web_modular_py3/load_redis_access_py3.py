#
#
#  File: load_redis_access_py3.py
#
#
#
import json






class Load_Redis_Access(object):

   def __init__( self, app, auth, request, redis_handle ):
       self.app           = app
       self.auth          = auth
       self.request      = request
       self.redis_handle  = redis_handle
    
       #
       # Redis simple values
       #
       self.rules = [ # simple key, values
                      [ "redis_keys",            self.redis_keys],
                      [ "redis_get",             self.redis_get],
                      [ "redis_set",             self.redis_set],
                      [ "redis_del",             self.redis_del],
                      # list operations
                      ["redis_llen"      , self.redis_llen    ],
                      ["redis_rpush"     , self.redis_rpush   ],
                      ["redis_rpop"       , self.redis_rpop     ],
                      ["redis_lpush"     , self.redis_lpush   ],
                      ["redis_lpop"       , self.redis_lpop    ],
                      ["redis_lget"      , self.redis_lget    ],
                      ["redis_lset"      , self.redis_lset    ],
                      ["redis_ldelete"   , self.redis_ldelete ],
                      ["redis_lrange"     , self.redis_lrange  ],
                      ["redis_ltrim"      , self.redis_ltrim    ],
                      # hash operations
                      [ "redis_hset",               self.redis_hset    ],
                      [ "redis_hkeys",              self.redis_hkeys   ],
                      [ "redis_hget",               self.redis_hget    ],
                      [ "redis_hgetall",            self.redis_hgetall ],
                      [ "redis_hexist",             self.redis_hexist  ],
                      [ "redis_hdel",               self.redis_hdel    ]]

                      
       for i in self.rules:
          a1 = auth.login_required( i[1] )
          app.add_url_rule('/ajax/'+i[0],i[0],a1,methods=["POST"])

   #
   # Functions
   #
   #

   #
   #  Redis Key Value Functions
   #
   #

   def redis_keys( self ):
       parm = self.request.get_json()
       return_value = []
       for i in parm:
           return_value.extend(self.redis_handle.keys(i))
       return return_value
       

   def redis_get(self):
       return_value = {}
       param = self.request.get_json()
       for i in param:     
           temp = self.redis_handle.get( i )
           return_value[i] = temp
       return json.dumps( return_value )
  
   def redis_set(self):
       return_value = []
       param = self.request.get_json()
       for i,item in param.items():
           self.redis_handle.set( i,item )
       return json.dumps('SUCCESS')

   def redis_del(self):
       return_value = []
       param = self.request.get_json()
       for i in param.keys():
           self.redis_handle.delete( i )
       return json.dumps('SUCCESS')
    

   #
   #
   # list functions llen rpush, rop, lpush,lpop,  lrange ,ltrim, lset,ldelete
   # list insert is not implemented right now
   #
   #

   def redis_llen( self ):
       return_value = {}
       param = self.request.get_json()
       for i in param:     
           temp = self.redis_handle.llen( i )
           return_value[i] = temp
       return json.dumps( return_value )

   def redis_rpush( self ):
       return_value = []
       param = self.request.get_json()
       for i,item in param.items():
           self.redis_handle.rpush( i,item )
       return json.dumps('SUCCESS')

   def redis_rpop( self ):
       return_value = {}
       param = self.request.get_json()
       for i in param:     
           temp = self.redis_handle.rpop( i )
           return_value[i] = temp
       return json.dumps( return_value )

   def redis_lpush( self ):
       return_value = []
       param = self.request.get_json()
       for i,item in param.items():
           self.redis_handle.lpush( i,item )
       return json.dumps('SUCCESS')
  
   def redis_lpop(self ):
       return_value = {}
       param = self.request.get_json()
       for i in param:     
           temp = self.redis_handle.rpop( i )
           return_value[i] = temp
       return json.dumps( return_value )


   def redis_lget( self ):
       return_value = {}
       param = self.request.get_json()
       for i in params:     
           temp = self.redis_handle.lget( i, items["index"] )
           return_value[i] = { index: items["index"], "value": temp }
       return json.dumps( return_value )

   def redis_lset( self ):
       return_value = []
       param = self.request.get_json()
       for i,items in param.items():
           self.redis_handle.set( i,items["index"],items["value"] )
       return json.dumps('SUCCESS')

   def redis_ldelete(self ):
       param = self.request.get_json()
       token = "------------~~~~~~~~~~~~~~~~~~-----------------"
       key = param["key"]
       list_indexes = param["list_indexes"]
       for i in list_indexes:
           
           self.redis_handle.lset( key, i, token)
       self.redis_handle.lrem(key,0,token)
       return json.dumps('SUCCESS')

   def redis_lrange( self ):
       return_value = []
       param    = self.request.get_json()
       key      = param["key"]
       start    = param["start"]
       end      = param["end"]
       temp  = self.redis_handle.lrange(key,start,end) 
       for i in temp:
          return_value.append(i)
       return json.dumps(return_value)

   def redis_ltrim( self ):
       param    = self.request.get_json()
       key      = param["key"]
       start    = param["start"]
       end      = param["end"]
       self.redis_handle.ltrim(key,start,end)
       return json.dumps('SUCCESS')



   #
   #
   # Hash functions
   #
   #
   #

   def redis_hset(self ):
       return_value = []
       param = self.request.get_json()

       for j in param:
           self.redis_handle.hset( j["redis_key"],j["hash"],j["value"] )
       return json.dumps('SUCCESS')


   def redis_hkeys(self ):
       return_value = {}
       param = self.request.get_json()
       
       for i in params:     
           temp = self.redis_handle.hkeys( i )
           return_value[i] = { "keys":temp }
       return json.dumps( return_value )

   def redis_hget(self ):  # tested
       return_value = {}
       param = self.request.get_json()
       for i in param["key_list"]:             
           temp = self.redis_handle.hget( param["hash_name"], i )
           #print("***********",param["hash_name"],i,temp)
           return_value[i] = temp
       return json.dumps( return_value )

   def redis_hgetall(self ): #tested
       return_value = {}
       param = self.request.get_json()
       temp = self.redis_handle.hgetall(param)
       for i,item in temp.items():
           return_value[i] = item
       return json.dumps( return_value )

   def redis_hexist(self ):
       return_value = {}
       param = self.request.get_json()
       for i in params:     
           temp = self.redis_handle.hexit( i, items["key"] )
           return_value[i] = temp
       return json.dumps( return_value )

   def redis_hdel(self ):
       return_value = []
       param = self.request.get_json()
       for i,items in param.items():
           self.redis_handle.set( i,items["key"] )
       return json.dumps('SUCCESS')


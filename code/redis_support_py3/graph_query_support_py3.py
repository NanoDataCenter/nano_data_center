
import json
import redis

class Query_Support(object):

   
   def __init__( self , redis_server_ip , redis_server_port=6379, db = 3 ):
      self.redis_handle  = redis.StrictRedis( host = redis_server_ip, port = redis_server_port, db =db , decode_responses=True)
      self.sep       = "["
      self.rel_sep   = ":"
      self.label_sep = "]"
      self.namespace     = []


   def add_match_terminal( self, query_list, relationship, label=None , property_mask = None ):
       temp = {}
       temp["relationship"] = relationship
       temp["label"]        = label
       temp["property_mask"] = property_mask
       temp["type"] = "MATCH_TERMINAL"
       query_list.append(temp)
       return query_list

   def add_match_relationship( self, query_list, relationship, label=None , property_mask=None ):
       temp = {}
       temp["relationship"] = relationship
       temp["label"]        = label
       temp["property_mask"] = property_mask
       temp["type"] = "MATCH_RELATIONSHIP"
       query_list.append(temp)
       return query_list


       

   def match_list( self,  match_list, starting_set = None  ):
       if starting_set == None:
           starting_set = self.redis_handle.smembers("@GRAPH_KEYS")
       
       for i in match_list:
           if i["type"] == "MATCH_TERMINAL":
               starting_set = self.match_terminal_relationship( i["relationship"], i["label"] , starting_set, i["property_mask"])
               if starting_set == None:
                   return set([]), []

           elif i["type"] == "MATCH_RELATIONSHIP":
               starting_set = self.match_relationship( i["relationship"], i["label"] , starting_set )
               if starting_set == None:
                   return set([]), []
          
         
       return starting_set, self.return_data( starting_set)
       
            


   def match_terminal_relationship( self, relationship, label= None , starting_set = None,property_values = None ):
       return_value = None
       
       if label == None:
          
          if self.redis_handle.sismember( "@TERMINALS", relationship) == True:
             
              return_value = set(self.redis_handle.smembers("&"+relationship))
              return_value = return_value.intersection(starting_set)
              
       
       else:
          if self.redis_handle.sismember( "@TERMINALS", relationship) == True:
               if self.redis_handle.exists("$"+relationship+self.rel_sep+label) == True:
                   return_value = self.redis_handle.smembers("$"+relationship+self.rel_sep+label)
                   return_value = return_value.intersection(starting_set)

       if (property_values != None) and (return_value != None):
          return_value = self.match_properties( return_value , property_values )
       return return_value

   def match_relationship( self, relationship, label= None , starting_set = None ):
       return_value = None
       
       if label == None:
          
          if self.redis_handle.sismember(  "@RELATIONSHIPS", relationship) == True:
             
              return_value = set(self.redis_handle.smembers("%"+relationship))
              return_value = return_value.intersection(starting_set)
              
       
       else:
          
          if self.redis_handle.sismember( "@RELATIONSHIPS", relationship) == True:
               
               if self.redis_handle.exists("#"+relationship+self.rel_sep+label) == True:
                   
                   return_value = self.redis_handle.smembers("#"+relationship+self.rel_sep+label)
                   
                   return_value = return_value.intersection(starting_set)
       return return_value


      

   def match_properties( self, starting_set , property_values ):
       return_value = []
       for i in list(starting_set):
           flag = True
           
           for j , value in property_values.items(): 
               
               data = self.redis_handle.hget(i,j)
               if data == None:
                   flag = False
                   break
               
               if json.loads(data) != value:
                   flag = False
                   break
 
           if flag == True:
               return_value.append( i)
       return return_value


   def return_data( self, key_set ):
       return_value = []
       for i in key_set:
           data = self.redis_handle.hgetall(i)
           
           temp = {}
           for j in data.keys():

               try:
                   temp[j] = json.loads(data[j] )
               except:
                   #print("exception")
                   temp[j] = data[j]
           return_value.append(temp)
       return return_value



if __name__ == "__main__":
   qs = Query_Support("localhost")
   query_list = []
   query_list = qs.add_match_relationship(query_list,relationship="SITE",label="LaCima" )
   query_list = qs.add_match_terminal( query_list, 
                                      relationship = "ETO_ENTRY" ,
                                      label = "ETO_CIMIS_SATELLITE",
                                      property_mask= {'measurement_tag': 'CIMIS_SATELLITE_ETO'}  )
   print( qs.match_list(query_list))



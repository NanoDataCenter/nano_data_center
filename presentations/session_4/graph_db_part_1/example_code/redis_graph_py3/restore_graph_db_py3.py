import redis
import json
class Dictionary_to_Graph:

   def __init__( self, graph_db= 14 ):
       self.redis_handle = redis.StrictRedis( host = "localhost", port=6379, graph = 14 , decode_responses=True)
 
      

   def dictionary_to_graph( self ):
       self.node_list = []
       self.graph_members = set()
       self.
       self.node_set  = self.redis_handle.smembers("@GRAPH_KEYS")
       self.node_list = list( self.node_set )
       self.graph_dict = {}
       self.list_data  = []

       for i in self.node_list:
           self.list_data.append(self._parse_string_data(str(i)))
       
       for i in self.list_data:
           temp1 = self.graph_dict
           while len(i ) > 0 :
               a = i.pop(0)
               for j in a:
                  if j not in temp1:
                     temp1[j] = {}
                  temp1 = temp1[j]


   def get_graph_dictionary( self):
       if self.graph_dict == None:
           self.graph_to_dictionary()
       return self.graph_dict

   def get_node_set( self ):
       if self.node_set == None:
           self.graph_to_dictionary()
       return self.node_set

   def pretty_print( self, tabs = "->" ):
       data = self.get_graph_dictionary()
       return json.dumps(data, indent=tabs, sort_keys=True)

   def _parse_string_data( self, string_input ):
       temp_string = string_input[1:-2] # remove [   and ending ]
       temp_list = temp_string.split("][")
       return_value = []
       for i in temp_list:
          temp_pair = i.split(":")
          return_value.append(temp_pair)
       return return_value

        
if __name__ == "__main__":
   
   gd = Graph_To_Dictionary()
   gd.graph_to_dictionary()
   print(gd.pretty_print())
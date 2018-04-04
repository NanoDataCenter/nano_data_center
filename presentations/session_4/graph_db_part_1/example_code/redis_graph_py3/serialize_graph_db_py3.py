import redis
import pickle
class Serialize_Graph:

   def __init__( self, graph_db= 14 ):
       self.redis_handle = redis.StrictRedis( host = "localhost", port=6379, db= graph_db , decode_responses=True)
 
      

   def serialize_graph( self, out_file = "graph_db.pickle" ):
       self.key_list = self.redis_handle.keys()
       self.ser_obj = {}
       for i in self.key_list:
           self.ser_obj[i] = self.redis_handle.dump(i)
       file_object = open(out_file, mode='wb')
       print(pickle.dumps(self.ser_obj))
       pickle.dump(self.ser_obj, file_object)
       file_object.close()  
          

        
if __name__ == "__main__":
   
   sg = Serialize_Graph()
   sg.serialize_graph()
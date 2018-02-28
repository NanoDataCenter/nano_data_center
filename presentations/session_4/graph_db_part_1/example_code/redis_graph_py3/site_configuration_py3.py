import json
class Retrieve_Site_ID( object ):

   def __init__(self,path=""):
       self.path = path
       
   def read_configuration(self):
       file = open(self.path+"/site_configuration.json","r")
       config_data =  json.load(file)
       return config_data
       
       
       
if __name__ == "__main__":
   retrive_class = Retrieve_Site_ID("redis_graph_py3")
   print( retrive_class.read_configuration())
   
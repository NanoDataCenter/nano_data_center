#
#  The logging object was broken out as a class
#  for testability considerations 
#

import time
import math
import numpy as np
from scipy.optimize import curve_fit



class Logging_Object(object):

   def __init__( self, data_offset = 4 ):
       self.offset = data_offset

   def initialize_object( self, name,schedule_name,step ):
       obj                 = {}
       obj["name"]         = name
       obj["time"]         = time.time()
       obj["schedule_name"] = schedule_name
       obj["step"]          = step
       obj["fields"]        = {}
       return obj



   def initialize_field( self, obj ,field):
       if field not in obj["fields"]:
           obj["fields"][field]            = {}
           obj["fields"][field]["data"]    = []

   def log_element( self, obj,key, value ):
       try:
           value = float( value )
       except:
           value = 0
       if key not in obj["fields"]:
           self.initialize_field( obj, key) 
       temp = obj["fields"][key]
       temp["data"].append(value)
  
   
   def curve_fit_function( self, x, a,b,c):
       return (a*x*x)+(b*x)+c


   def compute_object_statistics( self, obj ):
     
       for j, item in obj["fields"].items():
           temp_list = item["data"][self.offset:]
           if len( temp_list ) > 0:
               item["count"]    = len(temp_list)
               np_array        = np.array(temp_list)
               item["total"]   = np.sum(np_array)
               item["average"] = np.mean(np_array)
               item["std"]    = np.std(np_array)
               item["max"]    = np.max(np_array)
               item["min"]    = np.min(np_array)
               item["median"] = np.median(np_array)
               self.curve_fit_data(item, np_array)
           else:  
               item["total"]  = 0
               item["average"] = 0
               item["std"]    = 0
               item["max"]    = 0
               item["min"]    = 0
               item["median"] = 0
               item["curve_fit"] = None
 

   def curve_fit_data(self, obj_dict, np_array):
       x_range = range(self.offset, self.offset+obj_dict["count"])
       x_data_np = np.array(x_range)
       
       curve_parameters,error_matrix    = curve_fit(self.curve_fit_function, x_data_np, np_array )
 
       obj_dict["curve_fit"] = {}
       obj_dict["curve_fit"]["a"] = curve_parameters[0]
       obj_dict["curve_fit"]["b"] = curve_parameters[1]
       obj_dict["curve_fit"]["c"] = curve_parameters[2]
       raw_error = self.compute_raw_error( curve_parameters, x_data_np, np_array )
       obj_dict["abs_error"] = raw_error
    
      

   def compute_raw_error( self, curve , x_data, y_data):
       error = 0
       for i in range(len(x_data)):
           j = x_data[i]
           data = self.curve_fit_function(j,curve[0],curve[1],curve[2] )
           error  += math.fabs( y_data[i] -data )
       return error
 
if __name__ == "__main__":
   log_obj =  Logging_Object()
   obj     =  log_obj.initialize_object( "test","test_schedule","1" )
   #log_obj.initialize_field( obj ,"test1")
   #log_obj.initialize_field( obj, "test2")
   #log_obj.initialize_field( obj, "test1")
   for i in range(0,51):
       log_obj.log_element(obj,"test3",i )
   log_obj.compute_object_statistics(obj )
   print(obj)

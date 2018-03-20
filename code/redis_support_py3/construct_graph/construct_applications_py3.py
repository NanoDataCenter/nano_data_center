import redis
import json

#from .construct_weather_stations_py3 import Construct_Weather_Stations


class Construct_Applications(object):

   def __init__(self,bc,cd):  # bc is build configuration class cd is construct data structures
       bc.add_header_node("APPLICATION_SUPPORT")
       #Construct_Weather_Stations(bc,cd)
       #Construct_Irrigation_Support(bc,cd)
       #Construct_Data_Acquisition(bc,cd)
       bf.end_header_node("APPLICATION_SUPPORT")
       
       


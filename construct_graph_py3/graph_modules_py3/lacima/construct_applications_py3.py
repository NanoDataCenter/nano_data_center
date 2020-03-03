import redis
import json

from .application_modules_py3.construct_weather_stations_py3 import Construct_Weather_Stations
from .application_modules_py3.construct_irrigation_scheduling_py3 import Construct_Irrigation_Scheduling_Control


class Construct_Lacima_Applications(object):

   def __init__(self,bc,cd):  # bc is build configuration class cd is construct data structures
       bc.add_header_node("APPLICATION_SUPPORT")
       Construct_Weather_Stations(bc,cd)       
       Construct_Irrigation_Scheduling_Control(bc,cd)
       bc.end_header_node("APPLICATION_SUPPORT")
       
       


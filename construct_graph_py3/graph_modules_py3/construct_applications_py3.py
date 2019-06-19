import redis
import json

from .application_modules_py3.construct_weather_stations_py3 import Construct_Weather_Stations
from .application_modules_py3.construct_irrigation_scheduling_py3 import Construct_Irrigation_Scheduling_Control

from .application_modules_py3.construct_mqtt_handlers_py3 import Construct_MQTT_Handlers
class Construct_Applications(object):

   def __init__(self,bc,cd):  # bc is build configuration class cd is construct data structures
       bc.add_header_node("APPLICATION_SUPPORT")
       Construct_Weather_Stations(bc,cd)
       Construct_MQTT_Handlers(bc,cd)
       Construct_Irrigation_Scheduling_Control(bc,cd)
       #Construct_Irrigation(bc,cd)
       #Construct_Data_Acquisition(bc,cd)
       bc.end_header_node("APPLICATION_SUPPORT")
       
       


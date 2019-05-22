import redis
import json

from .application_modules_py3.construct_weather_stations_py3 import Construct_Weather_Stations
from .application_modules_py3.construct_scheduling_py3 import Construct_Scheduling
from .application_modules_py3.construct_irrigation_py3 import Construct_Irrigation
from .application_modules_py3.construct_mqtt_handlers_py3 import Construct_MQTT_HANDLERS
class Construct_Applications(object):

   def __init__(self,bc,cd):  # bc is build configuration class cd is construct data structures
       bc.add_header_node("APPLICATION_SUPPORT")
       Construct_Weather_Stations(bc,cd)
       Construct_MQTT_HANDLERS(bc,cd)
       #Construct_Scheduling(bc,cd)
       #Construct_Irrigation(bc,cd)
       #Construct_Data_Acquisition(bc,cd)
       bc.end_header_node("APPLICATION_SUPPORT")
       
       


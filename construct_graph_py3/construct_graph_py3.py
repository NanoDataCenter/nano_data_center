# file build system
#
#  The purpose of this file is to load a system configuration
#  in the graphic data base
#

import json

import redis
from  build_configuration_py3 import Build_Configuration
from  construct_data_structures_py3 import Construct_Data_Structures
from  graph_modules_py3.lacima.construct_applications_py3 import Construct_Lacima_Applications
from  graph_modules_py3.lacima.construct_controller_py3 import Construct_Lacima_Controllers
from  graph_modules_py3.lacima.construct_redis_monitor_py3 import Construct_Lacima_Redis_Monitoring
from  graph_modules_py3.lacima.construct_mqtt_devices_py3  import  Construct_Lacima_MQTT_Devices
from  graph_modules_py3.lacima.construct_plc_devices_py3   import  Construct_Lacima_PLC_Devices
from  graph_modules_py3.lacima.construct_cloud_interface_py3 import Construct_Lacima_Cloud_Service
from  graph_modules_py3.lacima.plc_measurements_py3 import Construct_Lacima_PLC_Measurements

from  graph_modules_py3.cloud_site.construct_applications_py3 import Construct_Cloud_Applications
from  graph_modules_py3.cloud_site.construct_controller_py3 import Construct_Cloud_Controllers
from  graph_modules_py3.cloud_site.construct_redis_monitor_py3 import Construct_Cloud_Redis_Monitoring

if __name__ == "__main__" :

   file_handle = open("../code/system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   redis_site = json.loads(data)


   bc = Build_Configuration(redis_site)
   cd = Construct_Data_Structures(redis_site["site"],bc)
   
   #
   #
   # Construct Systems
   #
   #
   bc.add_header_node( "SYSTEM","main_operations" )
   #
   #
   #  Construct Master Site
   #
   #
   
   bc.add_header_node( "SITE","CLOUD_SITE",  properties = {"address":"21005 Paseo Montana Murrieta, Ca 92562" } )
                                                  
   Construct_Cloud_Applications(bc,cd)
   Construct_Cloud_Controllers(bc,cd)
   Construct_Cloud_Redis_Monitoring(bc,cd)

   bc.end_header_node("SITE")                                                  
   
   #
   #
   # Construction Sites for LaCima
   #
   #
 
   bc.add_header_node( "SITE","LaCima",  properties = {"address":"21005 Paseo Montana Murrieta, Ca 92562" } )
                                                  

   Construct_Lacima_Applications(bc,cd)
   Construct_Lacima_Controllers(bc,cd)
   Construct_Lacima_Redis_Monitoring(bc,cd)
   Construct_Lacima_MQTT_Devices(bc,cd)
   Construct_Lacima_PLC_Devices(bc,cd) 
   Construct_Lacima_Cloud_Service(bc,cd)
   Construct_Lacima_PLC_Measurements(bc,cd)

   bc.end_header_node("SITE")
   bc.end_header_node("SYSTEM")
   bc.check_namespace()
   bc.store_keys()
   bc.extract_db()
   bc.save_extraction("../code/system_data_files/extraction_file.pickle")
   bc.delete_all()
   #bc.restore_extraction("extraction_file.pickle")
   #bc.delete_all()


 
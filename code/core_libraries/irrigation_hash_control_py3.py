

import time
import redis
import json
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from redis_support_py3.graph_query_support_py3 import  Query_Support

 


def generate_irrigation_control(redis_site_data):
       qs = Query_Support( redis_server_ip = redis_site_data["host"], redis_server_port=redis_site_data["port"] )
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site_data["site"] )

       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGATION_CONTROL_MANAGEMENT"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       
       generate_handlers = Generate_Handlers(package,redis_site_data)
    
       return generate_handlers.construct_managed_hash(data_structures["IRRIGATION_CONTROL"])
       
def generate_sensor_minute_status(redis_site_data):
       qs = Query_Support( redis_server_ip = redis_site_data["host"], redis_server_port=redis_site_data["port"] )
       query_list = []
       query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site_data["site"] )

       query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"MQTT_DEVICES_DATA"} )
                                           
       package_sets, package_sources = qs.match_list(query_list)  
     
       package = package_sources[0] 
       data_structures = package["data_structures"]
       
       generate_handlers = Generate_Handlers(package,redis_site_data)
    
       return generate_handlers.construct_hash(data_structures["MQTT_SENSOR_STATUS"])

   

   
if __name__ == "__main__":
      #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
    x = generate_irrigation_control(redis_site)
    #
    # Binary Test
    #
    print(x.hget("RAIN_FLAG"))
    x.hset("RAIN_FLAG",x.hget("RAIN_FLAG"))
    print(x.hget("RAIN_FLAG"))
    x.hset("RAIN_FLAG",1)
    print(x.hget("RAIN_FLAG"))
    x.hset("RAIN_FLAG",0)
    print(x.hget("RAIN_FLAG"))
    #
    # Float Test
    #
    temp = x.hget("FLOW_CUT_OFF")
    print(temp)
    x.hset("FLOW_CUT_OFF",35)
    print(x.hget("FLOW_CUT_OFF"))
    x.hset("FLOW_CUT_OFF",temp)
    print(x.hget("FLOW_CUT_OFF"))
    #
    # string test
    #
    temp = x.hget("SCHEDULE_NAME")
    print(temp)
    x.hset("SCHEDULE_NAME","TEMP")
    print(x.hget("SCHEDULE_NAME"))
    x.hset("SCHEDULE_NAME",temp)
    print(x.hget("SCHEDULE_NAME"))
    #
    # dictionary test
    #
    temp = x.hget("SLAVE_MAX_CURRENT")
    print(temp)
    x.hset("SLAVE_MAX_CURRENT",temp)
    temp_1 = x.hget("SLAVE_MAX_CURRENT")
    print(temp,temp_1)
    temp = x.hget_all()
    print(temp)
    

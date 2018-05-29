#
#
# File: eto.py
#
#
from eto_py3.wunderground_personal_weather_station_py3 import Wunder_Personal
from eto_py3.messo_handlers_py3 import Messo_ETO
from eto_py3.messo_handlers_py3 import Messo_Precp
from eto_py3.cimis_spatial_py3 import CIMIS_SPATIAL
from eto_py3.cimis_handlers_py3 import CIMIS_ETO
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers




ONE_DAY = 24 * 3600


class Eto_Management(object):
    def __init__(self,  eto_sources, package,site_data,eto_hash_table ):

        self.eto_sources = eto_sources
        self.package  = package
        self.site_data = site_data
        self.eto_hash_table = eto_hash_table
       
        self.generate_redis_handlers()
        self.initialize_values()
        self.generate_calculators()
       

                               
    def generate_redis_handlers(self):
        self.handlers = {}
        data_structures = self.package["data_structures"]
        generate_handlers = Generate_Handlers(self.package,self.site_data)
        self.ds_handlers = {}
        self.ds_handlers["EXCEPTION_VALUES"] = generate_handlers.construct_hash(data_structures["EXCEPTION_VALUES"])
        self.ds_handlers["ETO_VALUES"] = generate_handlers.construct_hash(data_structures["ETO_VALUES"])
        self.ds_handlers["RAIN_VALUES"] = generate_handlers.construct_hash(data_structures["RAIN_VALUES"])
        self.ds_handlers["ETO_CONTROL"] = generate_handlers.construct_hash(data_structures["ETO_CONTROL"])
        self.ds_handlers["ETO_HISTORY"] = generate_handlers.construct_stream_writer(data_structures["ETO_HISTORY"])
        self.ds_handlers["RAIN_HISTORY"] = generate_handlers.construct_stream_writer(data_structures["RAIN_HISTORY"] )
        self.ds_handlers["EXCEPTION_LOG"] = generate_handlers.construct_stream_writer(data_structures["EXCEPTION_LOG"] )
      

    def initialize_values(self):
         if self.ds_handlers["ETO_CONTROL"].hget("ETO_UPDATE_FLAG") == None:
             self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_FLAG",0)
         if self.ds_handlers["ETO_CONTROL"].hget("ETO_LOG_FLAG") == None:
             self.ds_handlers["ETO_CONTROL"].hset("ETO_LOG_FLAG",0)

     

        
    def generate_calculators(self):
        for data in self.eto_sources:
            print(data["type"])
            if data["type"] == "WUNDERGROUND":
               data["calculator"] = Wunder_Personal(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "CIMIS_SAT":
               data["calculator"] = CIMIS_SPATIAL(data, self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "CIMIS":
               data["calculator"] = CIMIS_ETO(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "MESSO_ETO":
               data["calculator"] = Messo_ETO(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            if data["type"] == "MESSO_RAIN":
               data["calculator"] = Messo_Precp(data,self.ds_handlers["ETO_VALUES"],self.ds_handlers["RAIN_VALUES"])
               continue
            assert(0,"data type is not recognized",data["type"] )
       

    def new_day_rollover( self, *parameters ):
         
         self.ds_handlers["EXCEPTION_VALUES"].delete()
         self.ds_handlers["ETO_VALUES"].delete()
         self.ds_handlers["RAIN_VALUES"].delete()
         self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_FLAG",0)
         self.ds_handlers["ETO_CONTROL"].hset("ETO_LOG_FLAG",0)
         return "DISABLE"

    def make_measurement(self, *parameters):
    
        for source in self.eto_sources:
            
            if "calculator" in source:
                try:
                    source["calculator"].compute_previous_day()
                except:
                   
                   print("exception",source["name"])
                   self.ds_handlers["EXCEPTION_VALUES"].hset(source["name"],"EXCEPTION")
       
             

    def update_eto_bins(self, *parameters):
        if int(self.ds_handlers["ETO_CONTROL"].hget("ETO_UPDATE_FLAG")) == 1:
            return True
        self.ds_handlers["ETO_CONTROL"].hset("ETO_UPDATE_FLAG",1) 
        # find eto with lowest priority
        eto = self.find_eto()
        if eto ==  None:
           return False
        self.reference_eto = eto
        rain = self.find_rain()
        self.reference_rain = self.find_rain()
        print("reference_eto",eto)
        for i in self.eto_hash_table.hkeys():
           
           new_value = float(self.eto_hash_table.hget(i)) + float(eto)
           print("eto_update",i,new_value)
           self.eto_hash_table.hset(i,new_value)
        


    def log_sprinkler_data(self,*parameters):
       if int(self.ds_handlers["ETO_CONTROL"].hget("ETO_LOG_FLAG")) == 1:
            return
       self.ds_handlers["ETO_CONTROL"].hset("ETO_LOG_FLAG",1) 
    
       eto_data = self.assemble_data("eto",self.ds_handlers["ETO_VALUES"])
       
       
       self.ds_handlers["ETO_HISTORY"].add_json(data = eto_data) 
       rain_data = self.assemble_data("rain",self.ds_handlers["RAIN_VALUES"])
       
       self.ds_handlers["RAIN_HISTORY"].add_json(data = rain_data) 
       exception_data = self.ds_handlers["EXCEPTION_VALUES"].hgetall()
       self.ds_handlers["EXCEPTION_LOG"].add_json(data=exception_data)

    def find_eto(self):
       eto_data = self.ds_handlers["ETO_VALUES"].hgetall()
       
       ref_priority = 1000000 # large starting number
       eto_value = None
       for i ,data in eto_data.items():
          
           if data["priority"] < ref_priority:
               ref_priority = int(data["priority"])
               eto_value = float(data["eto"])
               
               
       
       return eto_value

    def find_rain(self):
       rain_data = self.ds_handlers["RAIN_VALUES"].hgetall()
       
       ref_priority = 1000000 # large starting number
       for i ,data in rain_data.items():
          
           if data["priority"] < ref_priority:
               ref_priority = int(data["priority"])
               rain_data = float(data["rain"])
       
       return rain_data       
       
 
    def assemble_data(self,field_key,hash_handler):
       data = hash_handler.hgetall()
       return_value = {}
       for key , item in data.items():
          return_value[key] = item[field_key]
       return return_value
      
       
       
def replace_keys( redis_site_data,elements ):
   redis_handle = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_password_db"], decode_responses=True)
   for i in elements:
      
       temp = i["access_key"]
       api_key = redis_handle.hget("eto",temp)
      
       i["access_key"] = api_key



def construct_eto_instance(qs, site_data,user_table ):

    #
    #
    # find nodes associated with WEATHER_STATIONS
    #
    #
    
    #
    #  Find "WS_STATION" nodes
    #
    #
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "WS_STATION" )
                                        
    eto_sets, eto_sources = qs.match_list(query_list)                                    
    
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"WEATHER_STATION_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)  
     
    

    print(package_sets)
    #
    # Replace symbolic keys with actual api keys
    #
    replace_keys(site_data, eto_sources)
    
   
    eto_hash_table = user_table.eto_data.get_hash_table()
    
    eto = Eto_Management(eto_sources, package_sources[0],site_data ,eto_hash_table )
    
    
    
  

    return eto


def add_eto_chains(eto, cf):

    cf.define_chain("eto_time_window", True)
    cf.insert.wait_event_count( event = "DAY_TICK" )
    cf.insert.log("Got Day Tick")
    cf.insert.one_step(eto.new_day_rollover)
    cf.insert.reset()

    cf.define_chain("enable_measurement", True)
    cf.insert.log("starting enable_measurement")
    cf.insert.wait_tod_ge( hour =  1 )
    cf.insert.enable_chains(["eto_make_measurements"])
    cf.insert.log("enabling making_measurement")
    cf.insert.wait_tod_ge(hour=8)
    cf.insert.enable_chains(["update_eto_bins"])
    cf.insert.wait_tod_ge( hour =  12 )
    cf.insert.disable_chains(["eto_make_measurements","update_eto_bins","log_sprinkler_data"])
    cf.insert.enable_chains(["log_sprinkler_data"])
    cf.insert.wait_event_count( event = "DAY_TICK" )
    cf.insert.reset()

    cf.define_chain("update_eto_bins", False)
    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 5)
    cf.insert.log("updating eto bins")
    cf.insert.wait_function( eto.update_eto_bins )
    cf.insert.terminate()
    
    cf.define_chain("log_sprinkler_data", False)
    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 2)
    cf.insert.log("logging sprinkler data")
    cf.insert.one_step( eto.log_sprinkler_data )
    cf.insert.terminate()
    
    
    cf.define_chain("eto_make_measurements", False)
    cf.insert.log("starting make measurement")
    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 2)
    cf.insert.one_step( eto.make_measurement )
    
    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 8)
    cf.insert.log("Receiving 8 minute tick")
    
    cf.insert.reset()

    cf.define_chain("test_generator",False)

    cf.insert.terminate()


if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json

    import os
    import copy
    #import load_files_py3
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    import datetime
    from redis_support_py3.user_data_tables_py3 import User_Data_Tables

    from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter

    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
 
    #
    # Setup handle
    # open data stores instance
    user_table = User_Data_Tables(redis_site)
    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
    
    eto = construct_eto_instance(qs, redis_site,user_table )
    #
    # Adding chains
    #
    cf = CF_Base_Interpreter()
    add_eto_chains(eto, cf)
    #
    # Executing chains
    #
    
    cf.execute()

else:
  pass
  

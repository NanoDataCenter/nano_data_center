#
#
# File: eto.py
#
#
# redis_handle
#




ONE_DAY = 24 * 3600


class Eto_Management(object):
    def __init__(self, redis_handle, eto_sources, rain_sources):

        self.eto_sources = eto_sources
        self.rain_sources = rain_sources
        self.redis_handle = redis_handle
        self.redis_old = redis.StrictRedis(
            host='192.168.1.84', port=6379, db=0 , decode_responses=True)
        self.alarm_queue = AlarmQueue(self.redis_old)
        try:
             eto_update_flag = int(
                  self.redis_handle.hget(
                  "ETO_VARIABLES",
                   "ETO_UPDATE_FLAG"))
        except:
            self.redis_handle.hset("ETO_VARIABLES", "ETO_UPDATE_FLAG", 0)
            eto_update_flag = 0
        if eto_update_flag is None:

            self.redis_handle.hset("ETO_VARIABLES", "ETO_UPDATE_FLAG", 0)
        self.initialize_data_lists()

    def check_for_eto_update(
            self,
            chainFlowHandle,
            chainObj,
            parameters,
            event):
        #print( "check_for_eto_update")
        return
        eto_update_flag = int(
            self.redis_handle.hget(
                "ETO_VARIABLES",
                "ETO_UPDATE_FLAG"))

        if eto_update_flag == 0:
            self.update_all_bins(self.get_eto_integration_data())

        return "DISABLE"

    def initialize_data_lists(self):
        
        for i in self.eto_sources:
            try:
                data_store = i["measurement"]
                #print "eto_data_store", data_store
                length = self*_handle.llen(data_store)
                
                if length == 0:
                    self.redis_handle.lpush(data_store, "EMPTY")
                    length = self.redis_handle.llen(data_store)
                    

            except BaseException:
                self.redis_handle.lpush(data_store, "EMPTY")

        for i in self.rain_sources:
            try:
                data_store = i["measurement"]
                
                length = self.redis_handle.llen(data_store)
                
                if length == 0:
                    self.redis_handle.lpush(data_store, "EMPTY")
            except BaseException:
                self.redis_handle.lpush(data_store, "EMPTY")

    def generate_new_sources(
            self,
            chainFlowHandle,
            chainObj,
            parameters,
            event):
        #print "generate_new_sources", event
        self.redis_handle.hset(
            "ETO_VARIABLES",
            "NEW_SOURCES",
            time.strftime("%c"))
        for i in self.eto_sources:
            data_store = i["measurement"]
            # print "data_store",data_store
            self.redis_handle.lpush(data_store, "EMPTY")
            list_length = i["list_length"]
            #print "list_length", list_length
            self.redis_handle.ltrim(data_store, 0, list_length)

        for i in self.rain_sources:
            data_store = i["measurement"]
            self.redis_handle.lpush(data_store, "EMPTY")
            list_length = i["list_length"]
            self.redis_handle.ltrim(data_store, 0, list_length)
        self.redis_handle.hset("ETO_VARIABLES", "ETO_UPDATE_FLAG", 0)

        return "DISABLE"

    def make_measurement(self, chainFlowHandle, chainOjb, parameters, event):
        print("make measurement")
        if event["name"] == "INIT":
            return "CONTINUE"
        if int(self.redis_handle.hget("ETO_VARIABLES", "ETO_UPDATE_FLAG")) == 1:
            print("ETO_UPDATE_FLAG is one")
            return
        #print( "make measurements", self.eto_sources)
        return_value = True
        self.start_sensor_integration()
        for i in self.eto_sources:
            #print( i["measurement_tag"])
            data_store = i["measurement"]

            data_value = self.redis_handle.lindex(data_store, 0)
            flag, data = self.eto_calculators.eto_calc(i)
            if flag:
                temp = data
                #self.redis_handle.lset(data_store, 0, temp)
                self.update_integrated_eto_value(i, temp)

        for i in self.rain_sources:
            data_store = i["measurement"]
            data_value = self.redis_handle.lindex(data_store, 0)
            flag, data = self.eto_calculators.rain_calc(i)
            if flag:
                temp = data
                #self.redis_handle.lset(data_store, 0, temp)
                self.update_rain_value(i, temp)

        self.store_integrated_data()
        self.redis_handle.hset(
            "ETO_VARIABLES",
            "INTEGRATED_FLAG",
            self.integrated_eto_flag())

        if self.integrated_eto_flag():
            eto_data = self.get_eto_integration_data()
            #print  # *************** update_flag ***************, self.eto_update_flag

            eto_update_flag = int(
                self.redis_handle.hget(
                    "ETO_VARIABLES",
                    "ETO_UPDATE_FLAG"))
            if eto_update_flag == 0:
                #print "made it here --------------"
                #self.store_cloud_data()
                self.update_all_bins(eto_data)

            return_value = True
        #print "return_value", return_value

        return return_value

    def update_all_bins(self, eto_data):
        self.alarm_queue.store_past_action_queue( "ETO_UPDATE", "GREEN" ,data = eto_data)
        eto_update_flag = int(
            self.redis_handle.hget(
                "ETO_VARIABLES",
                "ETO_UPDATE_FLAG"))
        assert (eto_update_flag == 0), "Bad logic"
        if eto_update_flag == 1:
            return  # protection for production code

        self.redis_handle.hset("ETO_VARIABLES", "ETO_UPDATE_FLAG", 1)
        self.update_eto_bins_new(eto_data)
        self.update_sprinklers_time_bins_old(eto_data)

    def update_eto_bins_new(self, eto_data):
        pass

    def update_sprinklers_time_bins_old(self, eto_data):
        keys = self.redis_old.hkeys("ETO_RESOURCE")
        #print "keys", keys
        for j in keys:
            try:
                temp = self.redis_old.hget("ETO_RESOURCE", j)
                temp = float(temp)
            except BaseException:
                #print "exception"
                temp = 0
            temp = temp + float(eto_data)
            #print "j===========", j, temp
            self.redis_old.hset("ETO_RESOURCE", j, temp)

    #
    #  Sensor Integration
    #
    #
    #
    #

    def start_sensor_integration(self):

        self.mv_eto_sensors = {}
        self.eto_sensors = {}
        self.rain_sensors = {}

    def update_integrated_eto_value(self, eto_source, data_value):
 
        
        # eto_value",eto_source["name"],eto_source["majority_vote_flag"],data_value
        self.eto_sensors[eto_source["name"]] = data_value
        if eto_source["majority_vote_flag"]:
            self.mv_eto_sensors[eto_source["name"]] = data_value

    def update_rain_value(self, rain_source, data_value):
        self.rain_sensors[rain_source["name"]] = data_value

    def store_integrated_data(self):
        #print "integrating data"
        #print json.dumps(self.mv_eto_sensors)
        #print( self.rain_sensors, self.eto_sensors) 
        temp_eto_json = json.dumps(self.eto_sensors)
        temp_eto = json.loads(temp_eto_json)
        temp_eto["timestamp"] = time.time()
        temp_eto["date"] = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        temp_rain_json = json.dumps(self.rain_sensors)
        temp_rain = json.loads(temp_rain_json)
        temp_rain["timestamp"] = time.time()
        temp_rain["date"] = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        self.redis_handle.set(
            self.eto_integrated_measurement,json.dumps(self.mv_eto_sensors))
        self.redis_handle.set(
            self.eto_measurement, json.dumps(
                temp_eto))
        self.redis_handle.set(
            self.rain_measurement, json.dumps(
                temp_rain))
        del temp_eto["date"]          
        self.redis_handle.lpush(self.eto_queue["name"], json.dumps(temp_eto))
        self.redis_handle.ltrim(self.eto_queue["name"], 0, self.eto_queue["list_length"] )
        del temp_rain["date"]          
        self.redis_handle.lpush(self.rain_queue["name"], json.dumps(temp_rain))
        self.redis_handle.ltrim(self.rain_queue["name"], 0, self.rain_queue["list_length"] )
                 
                
    def get_eto_integration_data(self):
        #print "get_eto_integration_data"
        try:
           key_length = len(self.mv_eto_sensors.keys())
           if key_length > 0:
               return_value = 0
               for key, value in self.mv_eto_sensors.items():
                  if return_value < value:
                       return_value = value
           else:
              return_value = self.eto_default
              # send alert error message
        except:
           return_value = self.eto_default
        #print ("eto_integration", return_value)
        return return_value

    def integrated_eto_flag(self):
        #print "integrated eto flag"
        if ((self.redis_old.llen("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE") != 0) or
                (self.redis_old.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE") != 0)):
            return False  # items are still in sprinkler queue

        key_length = len(self.mv_eto_sensors.keys())

        if key_length >= self.mv_threshold_number:
            return_value = True
        else:
            return_value = False
        #print "return_Value", return_value
        return return_value

    def get_max_data(self, json_data):
        #print("json_data",json_data)
        data = json.loads(json_data)
        #print "get_max_data", data
        key_length = len(data.keys())
        if key_length > 0:
            return_value = 0
            for key, value in data.items():
                if return_value < value:
                    return_value = value
        else:
            return_value = 0.0

        return return_value
    '''
    def store_cloud_data(self):
        return
        data = {}
        data["namespace"] = self.cloud_namespace
        data["eto"] = self.get_max_data(
            self.redis_handle.get(
                self.eto_integrated_measurement))
        data["rain"] = self.get_max_data(
            self.redis_handle.get(
                self.rain_measurement))
        data["time_stamp"] = time.strftime(
            "%b %d %Y %H:%M:%S", time.localtime(
                time.time() - 24 * 3600))  # time stamp is a day earlier
        #print "data", data
        self.status_queue_class.queue_message("eto_measurement", data)
    '''
    #
    #
    #   Test support routines
    #
    def print_result_1(self, chainFlowHandle, chainOjb, parameters, event):

        #print "reading data store"
        return_value = "CONTINE"

        for i in self.eto_sources:
            data_store = i["measurement"]
            data_value = self.redis_handle.lindex(data_store, 0)
            #print i["name"], data_store, data_value
            #print self.redis_handle.llen(data_store)
            self.redis_handle.lpop(data_store)
            self.redis_handle.delete(data_store)

        for i in self.rain_sources:
            data_store = i["measurement"]
            data_value = self.redis_handle.lindex(data_store, 0)
            #print i["name"], data_store, data_value
            #print self.redis_handle.llen(data_store)
            self.redis_handle.lpop(data_store)
            self.redis_handle.delete(data_store)


class ETO_Calculators(object):

    def __init__(self, redis_handle):

        self.redis_handle = redis_handle
        self.eto_handlers = {}
        self.eto_handlers["CIMIS_SATELLITE_ETO"] = self.cimis_satellite
        self.eto_handlers["CIMIS_ETO"] = self.cimis_eto
        self.eto_handlers["SRUC1_ETO"] = self.sruc1_eto
        self.eto_handlers["HYBRID_SITE"] = self.hybrid_eto

        self.rain_handlers = {}
        self.rain_handlers["CIMIS_RAIN"] = self.cimis_rain
        self.rain_handlers["SRUC1_RAIN"] = self.sruc1_rain

    def eto_calc(self, eto_source):
        #print( "made it eto_calc",eto_source["measurement_tag"])

        try:

            if eto_source["measurement_tag"] in self.eto_handlers:

                result = self.eto_handlers[eto_source["measurement_tag"]](
                    eto_source)
                #print( "eto_calc", eto_source["measurement_tag"])
                return True, result
            else:
                print( "handler is bad")
                #raise ValueError("non existance handler")
        except BaseException:
            #raise
            #print( "problem with handler " + eto_source["measurement_tag"])
            return False, 0.0

        return False, 0

    def rain_calc(self, rain_source):
        try:
            if rain_source["measurement_tag"] in self.rain_handlers:
                result = self.rain_handlers[rain_source["measurement_tag"]](
                    rain_source)
                #print "rain_calc", result
                return True, result
            else:
                raise ValueError("non existance handler")
        except BaseException:
            print( "problem with handler " + rain_source["measurement_tag"])
            #raise
            return False, 0.0
    #
    #  ETO Calculation handlers
    #

    def cimis_satellite(self, eto_data):
        spatial = CIMIS_SPATIAL(eto_data)
        result = spatial.get_eto(time=time.time() - 24 * 3600)
        return result

    def cimis_eto(self, eto_data):
        #print( "eto_data",eto_data)
        cimis_eto = CIMIS_ETO(eto_data)
        cimis_results = cimis_eto.get_eto(time=time.time() - 24 * 3600)
        #print("cimis_results",cimis_results)
        result = cimis_results["eto"]
        return result

    def sruc1_eto(self, eto_data):

        messo_eto = Messo_ETO(eto_data)
        messo_results = messo_eto.get_daily_data(time=time.time())
        result = self.calculate_eto(eto_data["altitude"], messo_results)
        
        return result

    def hybrid_eto(self, eto_data):
        messo_eto = Messo_ETO(eto_data)
        messo_results = messo_eto.get_daily_data(time=time.time())
        redis_key = eto_data["rollover"]
        # print redis_key
        redis_data_json = self.redis_handle.lrange(redis_key, 0, 24)
        # for i in range(0,24):
        #    print i, messo_results[i]
        if len(redis_data_json) < 24:
            # print redis_data_json
            raise BaseException("bad data")
        # print messo_results[0]
        # print json.loads(redis_data_json[0])

        for i in range(0, 24):
            temp = messo_results[i]
            data = json.loads(redis_data_json[i])
            temp["Humidity"] = data["air_humidity"]
            temp["TC"] = self.convert_to_C(data["air_temperature"])
        # print messo_results[0]
        result = self.calculate_eto(eto_data["altitude"], messo_results)
        #print "hybrid result", result
        return result

    def cimis_rain(self, eto_data):
        cimis_eto = CIMIS_ETO(eto_data)
        cimis_results = cimis_eto.get_eto(time=time.time() - 24 * 3600)
        result = cimis_results["rain"]
        return result

    def sruc1_rain(self, eto_data):
        
        messo_precp = Messo_Precp(eto_data)
       
        result = messo_precp.get_daily_data(time=time.time())
        print("result",result)
        return result


def replace_keys( qs,elements ):
   redis_handle = qs.redis_handle
   for i in elements:
      
      temp = i["api-key"]
      api_key = redis_handle.hget("eto",temp)
      
      i["api-key"] = api_key



def construct_eto_instance(qs, site_data ):

    #
    #
    # find eto sources
    #
    #
    print(site_data['site'])
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=site_data["site"] )
    query_list = qs.add_match_terminal( query_list, 
                                      relationship = "ETO_ENTRY" )
                                      
    

    eto_sets, eto_sources = qs.match_list(query_list)


    print("eto_sets",eto_sets)
    exit()

    replace_keys(qs, eto_sources,redis_host)
    # construct package interfaces

    #
    # find rain sources
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label="LaCima" )
    query_list = qs.add_match_terminal( query_list, 
                                      relationship = "RAIN_ENTRY" )
    rain_sets, rain_sources = qs.match_list(query_list)
    replace_keys(qs,rain_sources)
    # construct package interfaces

    eto = Eto_Management(redis_handle, eto_sources, rain_sources)

    eto.eto_calculators = ETO_Calculators(redis_handle)
    #
    # find eto data stores
    eto.data_stores = gm.match_relationship_list([["ETO_STORE",None]])
    #
    #  Make sure that there is a data store for every eto_source
    #
    #
    eto_source_temp_list = gm.form_key_list("measurement", eto.eto_sources)
    eto_store_temp_list = gm.form_key_list("name", eto.data_stores)
    assert len(set(eto_source_temp_list) ^ set(
        eto_store_temp_list)) == 0, "graphical data base error"

    #
    # find rain stores
    #
    eto.rain_data_stores = gm.match_relationship_list([["RAIN_STORE",None]])

    rain_source_temp_list = gm.form_key_list("measurement", eto.rain_sources)
    rain_store_temp_list = gm.form_key_list("name", eto.rain_data_stores)
    
    eto.rain_queue = gm.match_terminal_relationship("RAIN_QUEUE")[0]
    eto.eto_queue = gm.match_terminal_relationship("ETO_QUEUE")[0]
    
    
    
    assert len(set(rain_source_temp_list) ^ set(
        rain_store_temp_list)) == 0, "graphical data base error"

    #
    #
    #
    #status_stores = gm.match_terminal_relationship("CLOUD_STATUS_STORE")

    # cloud publish will be redesigned
    temp = gm.match_terminal_relationship("ETO_SITES")
    #cloud_namespace = temp[0]["namespace"]
    #eto.cloud_namespace = cloud_namespace
    eto.eto_integrated_measurement = temp[0]["integrated_measurement"]
    eto.eto_measurement = temp[0]["measurement"]
    eto.mv_threshold_number = temp[0]["mv_threshold_number"]
    temp = gm.match_terminal_relationship("RAIN_SOURCES")
    eto.rain_measurement = temp[0]["measurement"]

    #queue_name = status_stores[0]["queue_name"]

    #eto.status_queue_class = rabbit_cloud_status_publish_py3.Status_Queue(
    #   redis_handle, queue_name)

    #eto.eto_default = .20

    return eto


def add_eto_chains(eto, cf):

    cf.define_chain("eto_time_window", True)
    cf.insert.wait_event_count( event = "DAY_TICK" )
    cf.insert.log("Got Day Tick")
    cf.insert.one_step(eto.generate_new_sources)
    cf.insert.reset()

    cf.define_chain("enable_measurement", True)
    cf.insert.log("starting enable_measurement")
    cf.insert.wait_tod_ge( hour =  7 )
    cf.insert.enable_chains(["eto_make_measurements"])
    cf.insert.log("enabling making_measurement")
    cf.insert.wait_tod_ge( hour =  18 )
    #cf.insert.one_step(eto.check_for_eto_update])
    cf.insert.disable_chains(["eto_make_measurements"])
    cf.insert.wait_event_count( event = "HOUR_TICK" )
    cf.insert.reset()

    cf.define_chain("eto_make_measurements", False)
    cf.insert.log("starting make measurement")
    cf.insert.one_step( eto.make_measurement )
    cf.insert.wait_event_count( event = "MINUTE_TICK",count = 15 )
    cf.insert.log("Receiving Hour tick")
    cf.insert.reset()

    cf.define_chain("test_generator",False)
    cf.insert.send_event("DAY_TICK", 0)
    cf.insert.log("Sending Day Tick")
    cf.insert.wait_event_count( event = "TIME_TICK" ,count = 1)
    cf.insert.enable_chains(["eto_make_measurements"])
    cf.insert.log("Enabling chain")
    cf.insert.send_event("HOUR_TICK", 0)
    cf.insert.wait_event_count( event = "TIME_TICK" ,count = 2)
    cf.insert.log("TIME TICK DONE")
    cf.insert.disable_chains( ["eto_make_measurements"] )
    cf.insert.log("DISABLE CHAIN DONE")
    cf.insert.one_step(eto.print_result_1)
    cf.insert.log("DISABLE CHAIN DONE")
    cf.insert.send_event("HOUR_TICK", 0)
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
    import load_files_py3
    from redis_interfaces_py3.graph_query_support_py3 import  Query_Support
    import datetime

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

    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
    
    eto = construct_eto_instance(qs, redis_site )
    #
    # Adding chains
    #
    cf = CF_Base_Interpreter()
    add_eto_chains(eto, cf)
    #
    # Executing chains
    #
    
    cf.execute()

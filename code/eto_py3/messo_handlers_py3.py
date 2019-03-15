import urllib.request
import time
import datetime
import json
ONE_DAY = 3600*24
from .calculate_eto_py3 import Calculate_ETO

class Messo_ETO(object):
    def __init__(self, access_data,eto_dict, rain_dict):
        self.calculate_eto = Calculate_ETO()
        self.eto_dict = eto_dict
        self.messo_data = access_data
        self.alt = access_data["altitude"]
        self.lat = access_data["latitude"]
        self.priority = access_data["priority"]
        self.app_key = self.messo_data["access_key"]
        self.url = self.messo_data["url"]
        self.station = self.messo_data["station"]
        self.token = "&token=" + self.app_key

    def compute_previous_day(self):
        if self.eto_dict.hget("messo:"+self.station+":normal_eto" ) != None:
           print("****************** messo eto returning")
           return
        ts = time.time()
        date_1 = datetime.datetime.fromtimestamp(
            ts - 1 * ONE_DAY).strftime('%Y%m%d')
        date_2 = datetime.datetime.fromtimestamp(
            ts - 0 * ONE_DAY).strftime('%Y%m%d')
        start_time = "&start=" + date_1 + "0800"
        end_time = "&end=" + date_2 + "0900"

        url = self.url + "stid=" + self.station + self.token + start_time + end_time + \
            "&vars=relative_humidity,air_temp,solar_radiation,peak_wind_speed,wind_speed&obtimezone=local"

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        temp = response.read()
        data = json.loads(temp.decode())

        station = data["STATION"]

        # print data.keys()
        # print data["UNITS"]
        station = station[0]
        station_data = station["OBSERVATIONS"]

        keys = station_data.keys()
        # print "keys",keys
        return_value_normal = []
        return_value_gust = []
        
        for i in range(0, 24):
            temp = {}
            temp["delta_timestamp"] = 1./24.
            temp["wind_speed"] = station_data["wind_speed_set_1"][i]
            temp["HUM"] = station_data["relative_humidity_set_1"][i]
            temp["SolarRadiationWatts/m^2"] = station_data["solar_radiation_set_1"][i]
            temp["TC"] = station_data["air_temp_set_1"][i]
            return_value_normal.append(temp)
            temp = {}
            temp["delta_timestamp"] = 1./24.
            temp["wind_speed"] = station_data["peak_wind_speed_set_1"][i]
            temp["HUM"] = station_data["relative_humidity_set_1"][i]
            temp["SolarRadiationWatts/m^2"] = station_data["solar_radiation_set_1"][i]
            temp["TC"] = station_data["air_temp_set_1"][i]
            return_value_gust.append(temp)
            
        
        print("messo calculation")
        self.eto_dict.hset("messo:"+self.station+":normal_eto",
                           { "eto":self.calculate_eto.__calculate_eto__( results  =  return_value_normal, alt = self.alt,lat = self.lat ), 
                           "priority":self.priority,"status":"OK" })
        self.eto_dict.hset("messo:"+self.station+":gust_eto",
                           { "eto":self.calculate_eto.__calculate_eto__( return_value_gust, self.alt,self.lat ), "priority":100,"status":"OK" })

        


class Messo_Precp(object):
    def __init__(self, data,eto_dict,rain_dict):
        self.rain_dict = rain_dict
        self.messo_data = data
        self.app_key = self.messo_data["access_key"]
        self.url = self.messo_data["url"]
        self.station = self.messo_data["station"]
        self.token = "&token=" + self.app_key

    def compute_previous_day(self):
        
        if self.rain_dict.hget("messo:"+self.station) != None:
            print("*********************","am returning messo precp")
            return

        ts = time.time()
        date_1 = datetime.datetime.fromtimestamp(
            ts - 1 * ONE_DAY).strftime('%Y%m%d')
        date_2 = datetime.datetime.fromtimestamp(
            ts - 0 * ONE_DAY).strftime('%Y%m%d')
        start_time = "&start=" + date_1 + "0800"
        end_time = "&end=" + date_2 + "0900"

        url = self.url + "stid=" + self.station + self.token + \
            start_time + end_time + "&obtimezone=local"
        
        req = urllib.request.Request(url)
       
        response = urllib.request.urlopen(req)
        temp = response.read()
        data = json.loads(temp.decode())
        
        
        station = data["STATION"]
        station = station[0]
        station_data = station["OBSERVATIONS"]
        
        rain = float(station_data["total_precip_value_1"]) / 25.4
        self.rain_dict.hset( "messo:"+self.station,  {"rain":rain,"priority":self.messo_data["priority"],"status":"OK"} )
        
       


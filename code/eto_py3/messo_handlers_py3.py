import urllib.request
import time
import datetime
import json
ONE_DAY = 3600*24


class Messo_ETO(object):
    def __init__(self, access_data,calculate_eto):
        self.calculate_eto = calculate_eto
        self.messo_data = access_data
        self.alt = access_data["alt"]
        self.lat = access_data["lat"]

        self.app_key = self.messo_data["api-key"]
        self.url = self.messo_data["url"]
        self.station = self.messo_data["station"]
        self.token = "&token=" + self.app_key

    def get_daily_data(self, time=time.time()):
        date_1 = datetime.datetime.fromtimestamp(
            time - 1 * ONE_DAY).strftime('%Y%m%d')
        date_2 = datetime.datetime.fromtimestamp(
            time - 0 * ONE_DAY).strftime('%Y%m%d')
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
        print("return_value",return_value_normal)
        return_value = {"normal_eto":self.calculate_eto.__calculate_eto__( return_value_normal, self.alt,self.lat ),
                        "gust_eto":self.calculate_eto.__calculate_eto__(return_value_gust,self.alt,self.lat) }
        return return_value


class Messo_Precp(object):
    def __init__(self, access_data):
        self.messo_data = access_data
        self.app_key = self.messo_data["api-key"]
        self.url = self.messo_data["url"]
        self.station = self.messo_data["station"]
        self.token = "&token=" + self.app_key

    def get_daily_data(self, time=time.time()):

        date_1 = datetime.datetime.fromtimestamp(
            time - 1 * ONE_DAY).strftime('%Y%m%d')
        date_2 = datetime.datetime.fromtimestamp(
            time - 0 * ONE_DAY).strftime('%Y%m%d')
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
        return rain

if __name__ == "__main__":
    from .calculate_eto_py3 import Calculate_ETO
    calculate_ETO = Calculate_ETO()
    access_data = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/timeseries?" ,  "station":"SRUC1","alt":2400,"lat":33.2 }
    eto =  Messo_ETO(access_data,calculate_ETO )
    print("eto",eto.get_daily_data())
    
    access_data = {"api-key":"8b165ee73a734f379a8c91460afc98a1"  ,"url":"http://api.mesowest.net/v2/stations/precip?" ,  "station":"SRUC1" }
    rain =  Messo_Precp(access_data)
    print("rain",rain.get_daily_data())

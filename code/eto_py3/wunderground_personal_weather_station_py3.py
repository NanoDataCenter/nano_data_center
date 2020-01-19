#
#
#
#
#
#
import datetime
import time
import json
from urllib.request import urlopen
import math

from .calculate_eto_py3 import Calculate_ETO
DAY = 24*3600

class Wunder_Personal( object ):

   def __init__(self,data,eto_sources,rain_sources):
    
     self.access_key = data["access_key"]
     self.pws = data["pws"]
     self.alt  = data["alt"]
     self.lat  = data["lat"]
     self.priority = data["priority"]
     self.calculate_eto = Calculate_ETO()
     self.eto_sources = eto_sources
     self.rain_sources = rain_sources
     
   #https://api.weather.com/v2/pws/observations/hourly/7day?stationId=KCAMURRI101&format=json&units=e&apiKey=dc0b888f054d45a88b888f054db5a83b  
     
   def compute_previous_day( self):
       
       if self.eto_sources.hget("wunder:"+self.pws+":Normal") != None:
          print("*********************","am returning wunder")
          return
       dt = datetime.datetime.now() + datetime.timedelta(days=-1)
       year = str(dt.year).zfill(4)
       month = str(dt.month).zfill(2)
       day = str(dt.day).zfill(2)
       
       url = 'https://api.weather.com/v2/pws/observations/hourly/7day?stationId='+self.pws+'&format=json&units=e&apiKey='+self.access_key 
       print("-------------url----------------",url)
       response = self.__load_web_page__(url)
       
       if response[0] == True:
          
          return True, self.__parse_data__(response[1])
       else:
          return False, None


   def __load_web_page__( self, url ):
       
       f = urlopen(url)
       json_data = f.read()
       f.close()
       data = json.loads(json_data.decode())
       return True, data
       #'stationID', 'winddirAvg', 'qcStatus', 'obsTimeUtc', 'obsTimeLocal', 'solarRadiationHigh', 'epoch', 'tz', 'uvHigh', 'imperial', 'lat', 'humidityLow', 'humidityAvg', 'lon', 'humidityHigh'])

   def __parse_data__(self,observations):
       data = observations["observations"]
       #print("data",data)
      
       valid_data = []
       self.determing_observation_window()
       for i in data:
          
          if self.match_time(i) == True:
            valid_data.append(i)

           
       
       
       
       results_normal = []
       results_max  = []
        
       for i in valid_data:
           #print(i['imperial'].keys())
           delta_timestamp = 1./24.
      
           
           results_normal.append({
                            "delta_timestamp": 1./24,
                            "TC":self.__convert_to_C__(i['imperial']['tempAvg']),
                            "HUM":float(i['humidityAvg']),
                            "wind_speed":float(i['imperial'][ 'windspeedAvg'])*0.44704,
                            "SolarRadiationWatts/m^2":float(i['solarRadiationHigh']) })  #i["wgusti"] )
           results_max.append({
                            "delta_timestamp": 1./24,
                            "TC":self.__convert_to_C__(float(i['imperial']['tempAvg'])+2),
                            "HUM":float(i['humidityAvg'])*.95,
                            "wind_speed":float(i['imperial']['windspeedAvg'])*1.1*0.44704,
                            "SolarRadiationWatts/m^2":float(i['solarRadiationHigh'])*1.15 })  #i["wgusti"] )
                         

       
       
       self.eto_sources.hset("wunder:"+self.pws+":Normal", { "eto":self.calculate_eto.__calculate_eto__(results_normal,self.alt,self.lat),
                                                            "priority":self.priority,"status":"OK" ,"time":str(datetime.datetime.now())}       ) 
                                                            ### These sources are for information only                                                          
       
       self.eto_sources.hset("wunder:"+self.pws+":Max",   { "eto":self.calculate_eto.__calculate_eto__(results_max,self.alt,self.lat),
                                                            "priority":100,"status":"OK" ,"time":str(datetime.datetime.now())}       )                                                       
                                                            
       self.rain_sources.hset("wunder:"+self.pws ,{"rain":valid_data[-1]['imperial']['precipTotal'],"priority":self.priority,"time":str(datetime.datetime.now())})


   def __convert_to_C__(self, deg_f):
        deg_f = float(deg_f)
        return ((deg_f - 32) * 5.0) / 9.0     
    

   def determing_observation_window(self):
       current_time = time.time()
       reference_time = current_time-24*3600
       ref_datetime = datetime.datetime.fromtimestamp(reference_time)
       self.ref_month = ref_datetime.month
       self.ref_day  = ref_datetime.day
       #print(self.ref_month,self.ref_day)
 
   def match_time(self,input):
       
       temp = input["obsTimeLocal"].split(" ")
       date_list = temp[0].split("-")
       
       if (int(date_list[1]) == self.ref_month) and (int(date_list[2]) == self.ref_day):
         return True
       else:
         return False
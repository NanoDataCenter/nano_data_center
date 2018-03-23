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
     
     
   def compute_previous_day( self):
       if self.eto_sources.hget("wunder:"+self.pws+":Normal") != None:
          print("*********************","am returning wunder")
          return
       dt = datetime.datetime.now() + datetime.timedelta(days=-1)
       year = str(dt.year).zfill(4)
       month = str(dt.month).zfill(2)
       day = str(dt.day).zfill(2)
       url = 'http://api.wunderground.com/api/'+self.access_key+'/history_'+year+month+day+'/q/pws:'+self.pws+'.json'
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
       if "error" in data["response"] :
          return [ False, data ]
       else:
          return [ True, data ]

   def __parse_data__(self,data):
       list_data = data["history"]["observations"]
       start_data = list_data.pop(0)
       j =  start_data["utcdate"]
       dt =  datetime.datetime(int(j["year"]),int(j["mon"]), int(j["mday"]), int(j["hour"]), int(j["min"]), 0)
       starting_timestamp = int((time.mktime(dt.timetuple()) ))
       total = 0
       results_normal = []
       results_gust  = []
       results_max = []
       for i in list_data:
           j = i["utcdate"]
           dt =  datetime.datetime(int(j["year"]),int(j["mon"]), int(j["mday"]), int(j["hour"]), int(j["min"]), 0)
           timestamp = int((time.mktime(dt.timetuple()) ))
           delta_timestamp = (timestamp - starting_timestamp)/DAY
           starting_timestamp = timestamp
           
           results_normal.append({
                            "delta_timestamp":delta_timestamp, 
                            "TC":self.__convert_to_C__(i['tempi']),
                            "HUM":float(i["hum"]),
                            "wind_speed":float(i["wspdi"])*0.44704,
                            "SolarRadiationWatts/m^2":float(i["solarradiation"]) })  #i["wgusti"] )
           results_max.append({
                            "delta_timestamp":delta_timestamp, 
                            "TC":self.__convert_to_C__(float(i['tempi'])+2),
                            "HUM":float(i["hum"])*.95,
                            "wind_speed":float(i["wspdi"])*1.1*0.44704,
                            "SolarRadiationWatts/m^2":float(i["solarradiation"])*1.15 })  #i["wgusti"] )
                         
           results_gust.append({"delta_timestamp":delta_timestamp, 
                            "TC":self.__convert_to_C__(i['tempi']),
                            "HUM":float(i["hum"]),
                            "wind_speed":float(i["wgusti"])*0.44704,
                            "SolarRadiationWatts/m^2":float(i["solarradiation"]) })  #i["wgusti"] )
       
       
       self.eto_sources.hset("wunder:"+self.pws+":Normal", { "eto":self.calculate_eto.__calculate_eto__(results_normal,self.alt,self.lat),
                                                            "priority":self.priority,"status":"OK" }       ) 
                                                            ### These sources are for information only                                                          
       self.eto_sources.hset("wunder:"+self.pws+":Gusts" ,  { "eto":self.calculate_eto.__calculate_eto__(results_gust,self.alt,self.lat),
                                                            "priority":100,"status":"OK" }       )  
       self.eto_sources.hset("wunder:"+self.pws+":Max",   { "eto":self.calculate_eto.__calculate_eto__(results_max,self.alt,self.lat),
                                                            "priority":100,"status":"OK" }       )                                                       
                                                            
       self.rain_sources.hset("wunder:"+self.pws ,{"rain":list_data[-1]["precip_totali"],"priority":self.priority})


   def __convert_to_C__(self, deg_f):
        deg_f = float(deg_f)
        return ((deg_f - 32) * 5.0) / 9.0     
    


 

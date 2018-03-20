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

#from .eto_calculation import eto_calculation
DAY = 24*3600

class Wunder_Personal( object ):

   def __init__(self,key,pws,alt, lat,calculate_eto):
     self.key = key
     self.pws = pws
     self.alt  = alt
     self.lat  = lat
     self.calculate_eto = calculate_eto
     
     
   def compute_previous_day( self):
    
       dt = datetime.datetime.now() + datetime.timedelta(days=-1)
       year = str(dt.year).zfill(4)
       month = str(dt.month).zfill(2)
       day = str(dt.day).zfill(2)
       url = 'http://api.wunderground.com/api/'+self.key+'/history_'+year+month+day+'/q/pws:'+self.pws+'.json'
       response = self.__load_web_page__(url)
       if response[0] == True:
          return True, self.__parse_data__(response[1])
       else:
          return False, None


   def __load_web_page__( self, url ):
       print("url",url)
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
           print(i["solarradiation"])
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
       
       return { "eto_normal":self.calculate_eto.__calculate_eto__(results_normal,self.alt,self.lat),
                "eto_max":self.calculate_eto.__calculate_eto__(results_max,self.alt,self.lat),
                "eto_gusts":self.calculate_eto.__calculate_eto__(results_gust,self.alt,self.lat ),
                "rain":list_data[-1]["precip_totali"] }


   def __convert_to_C__(self, deg_f):
        deg_f = float(deg_f)
        return ((deg_f - 32) * 5.0) / 9.0     
    
if __name__ == "__main__":
   from .calculate_eto_py3 import Calculate_ETO
   calculate_ETO = Calculate_ETO()

   wunder_personal = Wunder_Personal( key = 'a39d1fe3f2f42a9e', pws = 'KCAMURRI101',lat = 33.2, alt = 2400,calculate_eto=calculate_ETO )
   print(wunder_personal.compute_previous_day())


 

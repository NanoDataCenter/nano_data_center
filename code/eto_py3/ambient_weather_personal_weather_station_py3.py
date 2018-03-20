#
#
#
#
#
#
import datetime
from datetime import timezone
import time
import json
from urllib.request import urlopen
import math

#from .eto_calculation import eto_calculation
DAY = 24*3600


"""	
Larry Rosenman	9:42pm Mar 5
https://api.ambientweather.net/v1/devices/<macaddress>?applicationKey=<your application key>&apiKey=<your apikey>&endTime='YYYY-MM-DD 23:59:59'&limit=288
"""
class Ambient_Weather_Station( object ):

   def __init__(self,mac,application_key,api_key,alt, lat,calculate_eto):
     self.mac = mac
     self.application_key = application_key
     self.api_key = api_key
     self.lat  = lat
     self.calculate_eto = calculate_eto
     
     
   def compute_previous_day( self):
       master_response = []
       dt1 = datetime.datetime.now() + datetime.timedelta(days=-1)
       year = str(dt1.year).zfill(4)
       month = str(dt1.month).zfill(2)
       day = str(dt1.day).zfill(2)
       dt1 = datetime.datetime( int(year),int(month),int(day),0,0,0)
       url = 'https://api.ambientweather.net/v1/devices/'+self.mac
       url += "?applicationKey="+self.application_key+"&apiKey="+self.api_key
       url += "&endTime="+year+"-"+month +"-"+day +'%%20'+"23:59:59&limit=1000"
       response = self.__load_web_page__(url)
       
       master_response = response
       dt2 = datetime.datetime.now() + datetime.timedelta(days=0)
       year = str(dt2.year).zfill(4)
       month = str(dt2.month).zfill(2)
       day = str(dt2.day).zfill(2)
       dt2 = datetime.datetime(int(year),int(month),int(day),0,0,0)
       url = 'https://api.ambientweather.net/v1/devices/'+self.mac
       url += "?applicationKey="+self.application_key+"&apiKey="+self.api_key
       url += "&endTime="+year+"-"+month +"-"+day +'%%20'+"23:59:59&limit=1000"
       response = self.__load_web_page__(url)
       master_response.extend(response)
       self.__parse_data__(master_response,dt1,dt2)

   def __load_web_page__( self, url ):
       print("url",url)
       f = urlopen(url)
       json_data = f.read()
       f.close()
       #print(json_data)
       data = json.loads(json_data.decode())
       return data

   def __parse_data__(self,data,dt1,dt2):
       utc1 = dt1.replace(tzinfo=timezone.utc).timestamp()
       utc2 = dt2.replace(tzinfo=timezone.utc).timestamp()
       for i in data:
          print(float(i["dateutc"]/1000))
       print(dt1.timestamp(),utc1,dt2.timestamp(),utc2)
       print(dt1.timestamp()-utc1,dt2.timestamp()-utc2)
       quit()
       
       print("length of data is",len(data))
       print("keys of data",data[0].keys())
       data.reverse()
       return_value = []
       for i in data:
           temp = float(i["dateutc"])
           print(temp)
           if( (temp>utc1) and (temp<utc2 )):
              print("************",temp,utc1,utc2)
           
          
       print( return_value)
       print(len(return_value))
       print(utc1,utc2)
       quit()
       return return_Value

   '''
'humidity'
'tempf'
'windspeedmph': 4.3
'dateutc': 1520372400000
'solarradiation': 663.18
'dailyrainin': 0
'windgustmph': 4.5

   def __parse_data__(self,data):
       list_data = data["history"]["observations"]
       start_data = list_data.pop(0)
       j =  start_data["utcdate"]
       dt =  datetime.datetime(int(j["year"]),int(j["mon"]), int(j["mday"]), int(j["hour"]), int(j["min"]), 0)
       starting_timestamp = int((time.mktime(dt.timetuple()) ))
       total = 0
       results_normal = []
       results_gust  = []
       for i in list_data:
           j = i["utcdate"]
           dt =  datetime.datetime(int(j["year"]),int(j["mon"]), int(j["mday"]), int(j["hour"]), int(j["min"]), 0)
           timestamp = int((time.mktime(dt.timetuple()) ))
           delta_timestamp = (timestamp - starting_timestamp)/DAY
           starting_timestamp = timestamp
          
           results_normal.append({"delta_timestamp":delta_timestamp, 
                            "TC":self.__convert_to_C__(i['tempi']),
                            "HUM":float(i["hum"]),
                            "wind_speed":float(i["wspdi"])*0.44704,
                            "SolarRadiationWatts/m^2":float(i["solarradiation"]) })  #i["wgusti"] )
           results_gust.append({"delta_timestamp":delta_timestamp, 
                            "TC":self.__convert_to_C__(i['tempi']),
                            "HUM":float(i["hum"]),
                            "wind_speed":float(i["wgusti"])*0.44704,
                            "SolarRadiationWatts/m^2":float(i["solarradiation"]) })  #i["wgusti"] )
       return { "eto_normal":self.calculate_eto.__calculate_eto__(results_normal,self.alt,self.lat),
                "eto_gusts":self.calculate_eto.__calculate_eto__(results_gust,self.alt,self.lat ),
                "rain":list_data[-1]["precip_totali"] }
   '''

   def __convert_to_C__(self, deg_f):
        deg_f = float(deg_f)
        return ((deg_f - 32) * 5.0) / 9.0     
    
if __name__ == "__main__":
   from .calculate_eto_py3 import Calculate_ETO
   calculate_ETO = Calculate_ETO()

   ambient_station = Ambient_Weather_Station( mac = 'EC:FA:BC:07:F3:A1', application_key = '65ec33b793e54c80909be5abe7a1998764b042e4ccbf4100a8778860064aec07',
                                              api_key = 'b84fe5d75ec74ee99ee9881d5e115f42218326f377e6459c9383000014f3c3e4',
                                              lat = 33.2, alt = 2400,calculate_eto=calculate_ETO )
   print(ambient_station.compute_previous_day())

   #

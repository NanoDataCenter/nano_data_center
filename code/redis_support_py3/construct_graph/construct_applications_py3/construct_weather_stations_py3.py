class Construct_Weather_Stations(object):

   def __init__(self,bc,cd):
      self.bc = bc
      self.cd = cd
      bc.add_header_note("WEATHER_STATIONS")
      cd.construct_package("WEATHER_STATION_DATA")
      cd.add_stream("ETO_HISTORY",360)
      cd.add_stream("RAIN_HISTORY",360)
      cd.close_package_contruction()
      self.add_station_wunderground()
      self.add_station_cimis_satellite()
      self.add_station_cimis()
      self.add_station_messo_west_sruc1()
      bc.end_header_node("WEATHER_STATIONS")

   def add_station_wunderground(self):
       properties = {"access_key":"WUNDERGROUND","pws":'KCAMURRI101','lat':33.2,"alt":2400, "priority":1}
       bc.add_info_node( "WS_STATION",'KCAMURRI101',properties=properties) 
       
      
   def add_station_cimis_satellite(self):
       properties = { "access_key":"ETO_CIMIS_SATELLITE"  , 
                      "url":"http://et.water.ca.gov/api/data", 
                      "longitude":  -117.299459  ,
                      "latitude":33.578156 ,
                      "priority":5 } 
                  
       cf.add_info_node( "WS_STATION","ETO_CIMIS_SATELLITE",properties=properties)
       
   def add_station_cimis(self):
       properties = { "access_key":"ETO_CIMIS"  , 
                      "url":"http://et.water.ca.gov/api/data", 
                      "station":62, 
                      "altitude":2400
                      "priority":4 }
       cf.add_info_node( "WS_STATION","Station_62",properties=properties) 

   def add_station_messo_west_sruc1(self):
       properties = {"access_key":"MESSOWEST"  ,
                     "url":"http://api.mesowest.net/v2/stations/timeseries?" ,  
                     "station":"SRUC1", 
                     "altitude":2400
                     "priority":2 }
  
       cf.add_info_node( "WS_STATION","SRUC1",properties=properties)


   def add_station_messo_west_sruc1(self):
       properties = {"access_key":"MESSOWEST"  ,
                     "url":"url":"http://api.mesowest.net/v2/stations/precip?" ,  
                     "station":"SRUC1",
                     "priority":2}
 
  
       cf.add_info_node( "WS_STATION","SRUC1_RAIN",properties=properties)

              
       
       

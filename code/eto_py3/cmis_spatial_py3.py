
import urllib.request
import time
import datetime
import json
ONE_DAY = 3600*24

class CIMIS_SPATIAL(object):
    # fetch from cimis site
    def __init__(self, access_data):
        self.cimis_data = access_data
        self.app_key = "appKey=" + self.cimis_data["api-key"]
        self.cimis_url = self.cimis_data["url"]
        self.latitude = self.cimis_data["latitude"]
        self.longitude = self.cimis_data["longitude"]

    def get_eto(self, time=time.time() - 1 * ONE_DAY):  # time is in seconds for desired day

        date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
        lat_long = "lat=" + str(self.latitude) + ",lng=" + str(self.longitude)
        url = self.cimis_url + "?" + self.app_key + "&targets=" + \
            lat_long + "&startDate=" + date + "&endDate=" + date

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        temp = response.read()
       
        data = json.loads(temp.decode())
       
        temp = float(data["Data"]["Providers"][0]
                     ["Records"][0]['DayAsceEto']["Value"])

        return temp


if __name__ == "__main__":
   access_data  = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "longitude":  -117.299459  ,"latitude":33.578156  }
   x =  CIMIS_SPATIAL(access_data)
   print(x.get_eto())

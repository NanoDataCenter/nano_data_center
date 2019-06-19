
import urllib.request
import time
import datetime
import json
import datetime
ONE_DAY = 3600*24

class CIMIS_SPATIAL(object):
    # fetch from cimis site
    def __init__(self, access_data,eto_sources,rain_sources):
        self.eto_sources = eto_sources
        self.cimis_data = access_data
        self.app_key = "appKey=" + self.cimis_data["access_key"]
        self.cimis_url = self.cimis_data["url"]
        self.latitude = self.cimis_data["latitude"]
        self.longitude = self.cimis_data["longitude"]
        self.priority = access_data["priority"]

    def  compute_previous_day(self):
        if self.eto_sources.hget("CIMIS_SAT:"+str(self.longitude)) != None:
            print("*********************","am returning cimis_spatial")
            return
         
        ts=time.time() - 1 * ONE_DAY  # time is in seconds for desired day

        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        lat_long = "lat=" + str(self.latitude) + ",lng=" + str(self.longitude)
        url = self.cimis_url + "?" + self.app_key + "&targets=" + \
            lat_long + "&startDate=" + date + "&endDate=" + date

        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        temp = response.read()
       
        data = json.loads(temp.decode())
       
        temp = float(data["Data"]["Providers"][0]
                     ["Records"][0]['DayAsceEto']["Value"])
        date_string = str(datetime.datetime.now())
        self.eto_sources.hset("CIMIS_SAT:"+str(self.longitude), 
           { "eto":temp,"priority":self.priority,"status":"OK","time": date_string})



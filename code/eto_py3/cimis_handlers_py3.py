import urllib.request
import time
import datetime
import json
ONE_DAY = 3600*24
class CIMIS_ETO(object):
    # fetch from cimis site
    def __init__(self, access_data,eto_data, rain_data ):
        self.eto_data = eto_data
        self.rain_data = rain_data
        self.cimis_data = access_data
        self.app_key = "appKey=" + self.cimis_data["access_key"]
        self.cimis_url = self.cimis_data["url"]
        self.station = self.cimis_data["station"]

    def compute_previous_day( self):
        
        if self.eto_data.hget("CIMIS:"+str(self.station) ) != None:
           print("***************** cimis eto returning")
           return
 
        ts=time.time() - 1 * ONE_DAY # time is in seconds for desired day
       
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

        url = self.cimis_url + "?" + self.app_key + "&targets=" + \
            str(self.station) + "&startDate=" + date + "&endDate=" + date
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        temp = response.read()
        #print("temp",temp)
        data = json.loads(temp.decode())
        print("made it here")
        self.eto_data.hset("CIMIS:"+str(self.station), {"eto":float(
                data["Data"]["Providers"][0]["Records"][0]['DayAsceEto']["Value"]),
                "priority":self.cimis_data["priority"],"status":"OK" })
        self.rain_data.hset("CIMIS:"+str(self.station), {"rain":float(
                data["Data"]["Providers"][0]["Records"][0]['DayPrecip']["Value"]),
                "priority":self.cimis_data["priority"],"status":"OK" })

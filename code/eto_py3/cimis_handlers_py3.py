import urllib.request
import time
import datetime
import json
ONE_DAY = 3600*24
class CIMIS_ETO(object):
    # fetch from cimis site
    def __init__(self, access_data):

        self.cimis_data = access_data
        self.app_key = "appKey=" + self.cimis_data["api-key"]
        self.cimis_url = self.cimis_data["url"]
        self.station = self.cimis_data["station"]

    def get_eto(self, time=time.time() - 1 * ONE_DAY):  # time is in seconds for desired day
        #print("made it here")
        date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')

        url = self.cimis_url + "?" + self.app_key + "&targets=" + \
            str(self.station) + "&startDate=" + date + "&endDate=" + date
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        temp = response.read()
        #print("temp",temp)
        data = json.loads(temp.decode())
        #print("data",data)
        return {
            "eto": float(
                data["Data"]["Providers"][0]["Records"][0]['DayAsceEto']["Value"]),
            "rain": float(
                data["Data"]["Providers"][0]["Records"][0]['DayPrecip']["Value"])}



if __name__ == "__main__":
   access_data = { "api-key":"e1d03467-5c0d-4a9b-978d-7da2c32d95de"  , "url":"http://et.water.ca.gov/api/data"     , "station":62 }
   x =  CIMIS_ETO(access_data)
   print(x.get_eto())

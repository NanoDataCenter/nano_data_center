import json
import time
import datetime

import urllib3
from influxdb import InfluxDBClient


'''
Results sets notes
Filtering by measurement
Using rs.get_points('cpu') will return a generator for all the points that are in a series with measurement name cpu, no matter the tags.

rs = cli.query("SELECT * from cpu")
cpu_points = list(rs.get_points(measurement='cpu'))
Filtering by tags
Using rs.get_points(tags={'host_name': 'influxdb.com'}) will return a generator for all the points that are tagged with the specified tags, no matter the measurement name.

rs = cli.query("SELECT * from cpu")
cpu_influxdb_com_points = list(rs.get_points(tags={"host_name": "influxdb.com"}))
Filtering by measurement and tags
Using measurement name and tags will return a generator for all the points that are in a series with the specified measurement name AND whose tags match the given tags.

rs = cli.query("SELECT * from cpu")
points = list(rs.get_points(measurement='cpu', tags={'host_name': 'influxdb.com'}))

select format
SELECT * FROM "db.retention.measurement" WHERE "planet" = 'Saturn' AND time > '2015-04-16 12:00:01'
'''


class Influx_Handler(object):

   def __init__(self,host,username,password,database,retention):
       self.client = InfluxDBClient( host = host, username=username,password=password,ssl=True,verify_ssl=False)
       urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
       self.database = database
       self.retention = retention
      
   
   #data base stuff   
   def create_database(self,data_base):
       return self.client.create_database(data_base)
       
   
   def drop_database(self,data_base):
       return self.client.drop_database(data_base)
       
   def switch_database(self,data_base):
       self.client.switch_database(data_base)
       
       
   def list_databases(self):
       return self.client.get_list_database()

   def write_point(self,data,tags= {}):
       
       temp = datetime.datetime.utcnow().isoformat(sep='T')
       data["time"] = temp
       data["tags"] = tags
      
       final_data = [data]
       
       return  self.client.write_points(points = final_data,database = self.database,retention_policy = self.retention)   
   
   def insert_point(self,measurement="",tags={},fields={},db = None,retention = None):
       
       data = {}
       data["measurement"] = measurement
       data["tags"] = tags
       data["fields"] = fields
       
       temp = datetime.datetime.utcnow().isoformat(sep='T')
       data["time"] = temp
       final_data = [data]
       
       return  self.client.write_points(points = final_data,database = db, tags = tags,retention_policy = retention)
 
   # point maintainence
   def delete_series(measurement,tags= None,db = None):
      return self.client.delete_point_series(measurement,tags,db)
   
   def delete_measurement(self,measurement):
      return self.client.drop_measurement(measurement)
   
   def list_measurements(self):
       return self.client.get_list_measurements()


   # query stuff -- returns results set see notes at top
   def query(self,query_string):
       self.results = self.client.query(query_string)
       return self.results
       


   # retention policy must be >= 1hr
   def setup_retention(self,name,duration,database=None,default = False):
       self.client.create_retention_policy(name, duration, 1, database, default=False,shard_duration=duration)
       
   def alter_retention(self,name,duration,database= None,default = False):
      self.client.alter_retention_policy(name, database, duration, replication=None, default=default,shard_duration=duration)
   
   def drop_retention(self,name,database=None):
      self.client.drop_retention_policy(name, database)    
   
   def list_retention(self,database=None):
       return self.client.get_list_retention_policies(database)
   
  
   
  
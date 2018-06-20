# 
#
# File: utilities.py
#
#
#
#





#
#
#  This Class Deletes Legacy cimis emails sent to lacima ranch
#  Emails are not used as an api key now is used to access data
#
#
#

import msgpack


class Irrigation_Scheduling(object):

   def __init__(self,generate_handlers):
        self.generate_handlers = generate_handlers
        self.redis_handle = generate_handlers.get_redis_handle()

   def get_hash_table(self):
       return  self.generate_handlers.construct_hash("IRRIGATION_SCHEDULING","SCHEDULE_COMPLETED")

class System_Scheduling(object):

   def __init__(self,generate_handlers):
        self.generate_handlers = generate_handlers
        self.redis_handle = generate_handlers.get_redis_handle()

   def get_hash_table(self):
       return  self.generate_handlers.construct_hash("SYSTEM_SCHEDULING","SYSTEM_COMPLETED")
       
  
class User_Data_Tables(object):

   def __init__(self, redis_site_data ):
       self.backup_db     = redis_site_data["redis_backup_db"]
       self.redis_site_data = redis_site_data
       self.table_handler = Generate_Table_Handlers( redis_site_data )
       self.redis_handle = self.table_handler.get_redis_handle()

       self.app_file_handle = APP_FILES( self.redis_handle,self.redis_site_data )
       self.sys_filie_handle = SYS_FILES( self.redis_handle,self.redis_site_data)
       
       self.system_scheduling = System_Scheduling(self.table_handler)
       self.irrigation_scheduling = Irrigation_Scheduling(self.table_handler)
       
   def get_redis_handle(self):
      return self.redis_handle   

 
class Delete_Cimis_Email():

   def __init__(self,  app_files,user_table,qs  ):
        redis_handle = redis.StrictRedis(redis_site["host"], redis_site["port"], db=redis_site["redis_password_db"], decode_responses=True)
        self.email_data = redis_handle.hgetall("CIMIS_EMAIL")
      

 


   def delete_email_files( self,chainFlowHandle, chainOjb, parameters, event ):  
       print( "make it here" )
       if self.email_data != None: 
           IMAP_SERVER = 'imap.gmail.com'
           IMAP_PORT = '993'
           
           imap_username = self.email_data["imap_username"] 
           imap_password = self.email_data["imap_password"] 
           self.imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
           self.imap.login(imap_username, imap_password)
           self.imap.select('Inbox')
           status, data = self.imap.search(None, 'ALL')
           count = sum(1 for num in data[0].split())
           print ("count",count)
           if count > 0 :
              self.imap.select('Inbox')
              status, data = self.imap.search(None, 'ALL')
              for num in data[0].split():
                  self.imap.store(num, '+FLAGS', r'\Deleted')
              self.imap.expunge()


class Monitoring_Base(object):

   def __init__(self,app_file,file_name,completion_dictionary,generate_handler,data_structures,active_function=None):
       self.app_file = app_file
       self.file_name = file_name
       self.completion_dictionary = completion_dictionary
       self.job_queue = self.find_job_queue(generate_handler,data_structures)
       self.active_function = active_function

   def find_job_queue(self,generate_handler,data_structures):
       return generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_ACTIONS"])

       
   def clear_done_flag( self, *arg ):
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      item_control = self.app_file.load_file(self.file_name)
      for  j in  item_control:
           name = j["name"]
           if self.determine_start_time( j["start_time"],j["end_time"]) == False: 
               temp_1 = json.dumps( [0,-1] )
               temp_check = self.completion_dictionary.hget(name)
               if temp_1 != temp_check:
                  self.completion_dictionary.hset(name,temp_1)
    



       
   def check_flag( self,item ):
      try:
         data = self.completion_dictionary.hget( item )
 
         print("data check flag",data)
         data = json.loads( data)

      except:
         print("exception check_flag")
         data = [ 0 , -3 ]
      
      if int(data[0]) == 0 :
         return_value = True
      else:
         return_value = False
       
      
      return return_value
  

   def match_time( self, compare, value ):
     return_value = False
     if compare[0] < value[0]:
       return_value = True
     if (compare[0] ==  value[0]) and ( compare[1] <= value[1] ):
       return_value = True
     return return_value

   def determine_start_time( self, start_time,end_time ):
       return_value = False
       temp = datetime.datetime.today()
       st_array = [ temp.hour, temp.minute ]
       if self.match_time( start_time,end_time ) == True:
	           if ( self.match_time( start_time, st_array) and 
	                self.match_time( st_array, end_time )) == True:
	              return_value = True
       else: 
	         # this is a wrap around case
          if   self.match_time( start_time,st_array) :
               return_value = True
          if  self.match_time(st_array,end_time):
                return_value = True
       return return_value
     



  




              
class System_Monitoring(Monitoring_Base): 
   
   def __init__(self, app_files,user_tables,qs,generate_handler,data_structures):
       completion_dictionary = user_tables.system_scheduling.get_hash_table()
       Monitoring_Base.__init__(self,app_files,"system_actions.json",completion_dictionary,generate_handler,data_structures)

   def check_for_active_activity( self, *args):
      if self.active_function != None:
         if self.active_function() == False:
            return  # something like rain day has occurred
            
      temp = datetime.datetime.today()
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      st_array = [temp.hour,temp.minute]
      item_control = self.app_file.load_file(self.file_name)
      for j in item_control:
          print("j",j.keys())
          name     = j["name"]
          command  = j['command_string']
          
          if j["dow"][dow] != 0 :
            
            start_time = j["start_time"]
            end_time   = j["end_time"]
    
            if self.determine_start_time( start_time,end_time ):
                 if self.check_flag( name ):
                     print( "queue in schedule ",name )
                     temp = {}
                     temp["command"]        = command
                     temp["schedule_name"]  = name
                     temp["step"]           = 0
                     temp["run_time"]       = 0
                     self.job_queue.push(json.dumps(temp ))
                     temp = [1,time.time()+60*3600 ]  # +hour prevents a race condition
                     self.completion_dictionary.hset( name,json.dumps(temp) ) 
                  
  
class Schedule_Monitoring(Monitoring_Base):
   def __init__(self, app_files,user_tables,qs,generate_handler,data_structures ):
       completion_dictionary = user_tables.system_scheduling.get_hash_table()
       Monitoring_Base.__init__(self,app_files,"sprinkler_ctrl.json",completion_dictionary,generate_handler,data_structures,self.rain_check)
       self.find_rain_structure( generate_handler,data_structures )
       
       
   def find_rain_structure(self,generate_handler,data_structures):
        
        self.irrigation_control = generate_handlers.construct_hash(data_structures["IRRIGATION_CONTROL"])
        self.rain_field  = "RAIN_FLAG"
   
   def rain_check(self):
       print("rain_check")
       try:
          
          rain_day = self.irrigation_control.hget(self.rain_field)
          
         
          rain_day = int( rain_day )
       except:
          
          rain_day = int(0)
          self.irrigation_control.hset(self.rain_field,0  )
          
          print("exception")
       

       if rain_day == 0:
          return True
       else:
          return False

   def check_for_active_activity( self, *args):
      if self.active_function != None:
         if self.active_function() == False:
            return  # something like rain day has occurred
            
      temp = datetime.datetime.today()
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      st_array = [temp.hour,temp.minute]
      item_control = self.app_file.load_file(self.file_name)
      for j in item_control:
          name = j["name"]
          print( "checking schedule",name )
          
          if j["dow"][dow] != 0 :
	    
            start_time = j["start_time"]
            end_time   = j["end_time"]
        
            if self.determine_start_time( start_time,end_time ):
                 print( "made it past start time",start_time,end_time )
                 if self.check_flag( name ):
                     print( "queue in schedule ",name )
                     temp = {}
                     temp["command"] =  "QUEUE_SCHEDULE"
                     temp["schedule_name"]  = name
                     temp["step"]           = 0
                     temp["run_time"]       = 0
                     self.job_queue.push( json.dumps(temp) )
                     temp = [1,time.time()+60*3600 ]  # +hour prevents a race condition
                     self.completion_dictionary.hset( name,json.dumps(temp) ) 
 

class Ntpd():
   def __init__( self ):
     pass

   def get_time( self, chainFlowHandle, chainObj, parameters, event ):
     os.system("ntpdate -b -s -u pool.ntp.org")


     
if __name__ == "__main__":
   import datetime
   import time
   import string

   import math
   import redis
   
   import json

   import os
   import copy
   import imaplib
   
   from redis_support_py3.load_files_py3  import  APP_FILES

   
   from redis_support_py3.graph_query_support_py3 import Query_Support
   from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter
   from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
   from redis_support_py3.user_data_tables_py3 import Generate_Table_Handlers
   from redis_support_py3.load_files_py3  import APP_FILES
   from redis_support_py3.load_files_py3  import SYS_FILES



   file_handle = open("system_data_files/redis_server.json",'r')
   data = file_handle.read()
   file_handle.close()
   redis_site = json.loads(data)

   
   
 
   user_table = User_Data_Tables(redis_site)
   redis_handle = user_table.get_redis_handle()
   app_files = APP_FILES(redis_handle,redis_site)
   qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
   
   
   delete_cimis_email = Delete_Cimis_Email(app_files,user_table,qs)
   
   query_list = []
   query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

   query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGATION_DATA"} )
                                           
   package_sets, package_sources = qs.match_list(query_list) 
   package = package_sources[0]
   generate_handlers = Generate_Handlers(package,redis_site)
   data_structures = package["data_structures"]
   action       = System_Monitoring( app_files,user_table,qs,generate_handlers,data_structures)
   sched        = Schedule_Monitoring( app_files,user_table,qs,generate_handlers,data_structures )
 
   ntpd = Ntpd()
   
   
   #
   #
   #  Adding Chains
   #
   #
   
   cf = CF_Base_Interpreter()



   cf.define_chain("delete_cimis_email_data",False)
   cf.insert.wait_tod( hour=9 )
   cf.insert.one_step( delete_cimis_email.delete_email_files)
   cf.insert.wait_tod_ge( hour=10 )
   cf.insert.reset()

   cf.define_chain( "plc_auto_mode", True )
   cf.insert.one_step( action.check_for_active_activity  )
   cf.insert.one_step( sched.check_for_active_activity  )
   cf.insert.wait_event_count( event =  "MINUTE_TICK"  )
   cf.insert.reset()
    
   cf.define_chain("clear_done_flag",True)
   cf.insert.one_step(action.clear_done_flag )
   cf.insert.one_step(sched.clear_done_flag )
   cf.insert.wait_event_count( event =  "MINUTE_TICK"  )
   cf.insert.reset()

   #
   #
   # internet time update
   #
   #
  
   cf.define_chain("ntpd",False)
   cf.insert.log("ntpd")
   cf.insert.one_step(ntpd.get_time )
   cf.insert.log("got time" )
   cf.insert.wait_event_count( event =  "HOUR_TICK"  )
   cf.insert.reset()

 
   cf.execute()   

else:
  pass
  
  
'''

'''
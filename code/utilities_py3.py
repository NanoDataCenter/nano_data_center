# 
#
# File: utilities.py
#
#
#
#





import msgpack
from redis_support_py3.load_files_py3  import APP_FILES
from redis_support_py3.load_files_py3  import SYS_FILES
from redis_support_py3.construct_data_handlers_py3 import Generate_Handlers
from core_libraries.irrigation_hash_control_py3 import generate_irrigation_control




class Monitoring_Base(object):

   def __init__(self,app_file,file_name,completion_dictionary,job_queue,active_function=None):
       self.app_file = app_file
       
       self.file_name = file_name
       self.completion_dictionary = completion_dictionary
       self.job_queue = job_queue
       self.active_function = active_function


       
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
 
         #print("data check flag",data)
         data = json.loads( data)

      except:
         #print("exception check_flag")
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
       #print("start_time",start_time,end_time)
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
       #print("return_value",return_value)
       return return_value
     
   def check_for_schedule_activity( self, *args):
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
          #print( "checking schedule",name )
          
          if j["dow"][dow] != 0 :
	    
            start_time = j["start_time"]
            end_time   = j["end_time"]
            #print("made it here")
            if self.determine_start_time( start_time,end_time )  == True:
                 #print( "made it past start time",start_time,end_time )
                 if self.check_flag( name ):
                     #print( "queue in schedule ",name )
                     temp = {}
                     temp["command"] =  "QUEUE_SCHEDULE"
                     temp["schedule_name"]  = name
                     temp["step"]           = 0
                     temp["run_time"]       = 0
                     self.job_queue.push( temp )
                     temp = [1,time.time()+60*60 ]  # +hour prevents a race condition
                     self.completion_dictionary.hset( name,json.dumps(temp) ) 



   def check_for_system_activity( self, *args):

      temp = datetime.datetime.today()
      dow_array = [ 1,2,3,4,5,6,0]
      dow = datetime.datetime.today().weekday()
      dow = dow_array[dow]
      st_array = [temp.hour,temp.minute]
      sprinkler_ctrl = self.app_file.load_file("system_actions.json")
      for j in sprinkler_ctrl:
          
          name     = j["name"]
          command  = j["command_string"]
          #print( "checking schedule",name)
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
                     self.job_queue.push( temp )
                     temp = [1,time.time()+60*60 ]  # +hour prevents a race condition
                     self.completion_dictionary.hset( name,json.dumps(temp) ) 


         
class System_Monitoring(Monitoring_Base): 
   
   def __init__(self, app_files,completion_dictionary,job_queue):
       
       Monitoring_Base.__init__(self,app_files,"system_actions.json",completion_dictionary,job_queue)
 
       
   '''    


   '''               
  
class Irrigation_Schedule_Monitoring(Monitoring_Base):
   def __init__(self, app_files,completion_dictionary,job_queue,irrigation_control ):
       Monitoring_Base.__init__(self,app_files,"sprinkler_ctrl.json",completion_dictionary,job_queue,self.rain_check)
       self.irrigation_control = irrigation_control
       
       

          
   def rain_check(self):
       return self.irrigation_control.hget("RAIN_FLAG")


   
 

class Ntpd():
   def __init__( self ):
     pass

   def get_time( self, chainFlowHandle, chainObj, parameters, event ):
     os.system("ntpdate -b -s -u pool.ntp.org")


def add_chains(cf,sched,action,ntpd):


   cf.define_chain( "irrigation_scheduling", True )
   cf.insert.one_step( action.check_for_system_activity  )
   cf.insert.one_step( sched.check_for_schedule_activity  )
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

if __name__ == "__main__":

    import datetime
    import time
    import string
    import urllib.request
    import math
    import redis
    import base64
    import json

    import os
    import copy
    #import load_files_py3
    from redis_support_py3.graph_query_support_py3 import  Query_Support
    import datetime
    

    from py_cf_new_py3.chain_flow_py3 import CF_Base_Interpreter

    #
    #
    # Read Boot File
    # expand json file
    # 
    file_handle = open("system_data_files/redis_server.json",'r')
    data = file_handle.read()
    file_handle.close()
    redis_site = json.loads(data)
     
    #
    # Setup handle
    # open data stores instance

    qs = Query_Support( redis_server_ip = redis_site["host"], redis_server_port=redis_site["port"] )
    query_list = []
    query_list = qs.add_match_relationship( query_list,relationship="SITE",label=redis_site["site"] )

    query_list = qs.add_match_terminal( query_list, 
                                        relationship = "PACKAGE", property_mask={"name":"IRRIGIGATION_SCHEDULING_CONTROL_DATA"} )
                                           
    package_sets, package_sources = qs.match_list(query_list)  
 
    package = package_sources[0]
    
    #
    #  do verifications of data package
    #
    #
    #
    data_structures = package["data_structures"]
    redis_handle =  redis.StrictRedis( host = redis_site["host"] , port=redis_site["port"], db=redis_site["redis_io_db"] ) 
    generate_handlers = Generate_Handlers( package, redis_handle )
    
    
    
    app_files = APP_FILES(redis_handle,redis_site)
    data_structures = package["data_structures"]
    job_queue = generate_handlers.construct_job_queue_client(data_structures["IRRIGATION_JOB_SCHEDULING"])
  
    completion_dictionary        = generate_handlers.construct_hash(data_structures["SYSTEM_COMPLETION_DICTIONARY"])
    
 

    irrigation_control        = generate_irrigation_control(redis_site,redis_handle,qs)
    sched        = Irrigation_Schedule_Monitoring( app_files,completion_dictionary,job_queue,irrigation_control )
    action       = System_Monitoring(app_files,completion_dictionary,job_queue)

    ntpd = Ntpd()
    #
    # Adding chains
    #

    cf = CF_Base_Interpreter()
    add_chains(cf,sched,action,ntpd)
    #
    # Executing chains
    #
    
    #cf.execute()

else:
  pass
 
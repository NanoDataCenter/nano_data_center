import time   
import json
from  .main_valve_control_py3 import Main_Valve


from .valve_resistance_check_py3  import   Valve_Resistance_Check
from .clean_filter_py3            import   Clean_Filter
from .check_off_py3               import   Check_Off
#from .irrigation_control_py3      import   Irrigation_Control
from .irrigation_control_basic_py3      import   Irrigation_Control_Basic   
from .manage_eto_py3                    import   Manage_Eto
from  .irrigation_logging_py3   import Irrigation_Logging



class Irrigation_Queue_Management(object):

   def __init__( self, cluster_id, cf,cluster_control, 
                       irrigation_io, redis_handle,redis_new_handle, gm,
                       alarm_queue, app_files, sys_files):
       self.cf = cf
       self.cluster_ctrl  = cluster_control
       self.irrigation_io = irrigation_io
       self.redis_handle  = redis_handle
       self.cluster_id    = cluster_id
       self.alarm_queue   = alarm_queue
       self.check_off     = Check_Off(cf,cluster_control,irrigation_io, redis_handle, alarm_queue ) 
       self.measure_valve_resistance = Valve_Resistance_Check(cf,cluster_control,irrigation_io, 
                                               redis_handle, alarm_queue, app_files, sys_files)
       self.clean_filter = Clean_Filter(cf,cluster_control,irrigation_io, redis_handle, alarm_queue)

       self.manage_eto   =  Manage_Eto( redis_handle, alarm_queue, app_files )

                        
       hooks_15    = [] 
       hooks_60    = [self.manage_eto.minute_update]
       hooks_start = [self.manage_eto.setup_sprinkler]
       hooks_term  = []
       logging_obj = Irrigation_Logging(redis_handle, redis_new_handle,gm,alarm_queue )
       user_data = None

       self.irrigation_control  =  Irrigation_Control_Basic(cf,cluster_control,irrigation_io, 
                                    redis_handle, alarm_queue,app_files, sys_files,
                                    hooks_15, hooks_60, hooks_start, hooks_term,
                                    logging_obj,user_data)
  
       #
       # This chain strobes the plc watchdog timers
       #
       cf.define_chain("plc_watch_dog", True ) 
       cf.insert.one_step( irrigation_io.read_wd_flag   )
       cf.insert.one_step( irrigation_io.write_wd_flag )
       cf.insert.wait_event_count( count = 30 ) # wait 30 second
       cf.insert.reset()

       cf.define_chain("controller_time_stamp",True)
       cf.insert.one_step( self.update_time_stamp)
       cf.insert.wait_event_count( count = 10 )
       cf.insert.reset()      

       cf.define_chain("QC_Startup", True )
       cf.insert.one_step(cluster_control.disable_cluster, cluster_id )
       cf.insert.one_step(irrigation_io.disable_all_sprinklers )
       #
       # verify plc's are on line
       #
       cf.insert.one_step( irrigation_io.read_mode_switch)
       #
       #
       #
       cf.insert.one_step( self.check_for_unfinished_job )
       cf.insert.terminate()

        
 
       cf.define_chain("QC_Finish_Job", False )
       cf.insert.log( "Finishing Job" )
       cf.insert.one_step( self.start_unfinished_job )
       cf.insert.wait_event_count( event = "RELEASE_IRRIGATION_CONTROL" ,count = 1)
       cf.insert.one_step( self.irrigation_control.clean_up_irrigation_cell)
       cf.insert.log("RELEASE_IRRIGATION_CONTROL event received")
       cf.insert.enable_chains( ["QC_Check_Irrigation_Queue"])
       cf.insert.terminate()







       cf.define_chain("QC_Check_Irrigation_Queue", False )
       cf.insert.one_step(cluster_control.disable_cluster, cluster_id )
       cf.insert.one_step(irrigation_io.disable_all_sprinklers )
       cf.insert.log( "Checking Irrigation Queue" )
       cf.insert.wait_function( self.check_queue)
       cf.insert.one_step( self.dispatch_entry )
       cf.insert.wait_event_count( event = "RELEASE_IRRIGATION_CONTROL" ,count = 1)
       cf.insert.one_step( self.irrigation_control.clean_up_irrigation_cell)
       cf.insert.wait_event_count( count = 1 )
       cf.insert.log("RELEASE_IRRIGATION_CONTROL event received")
       cf.insert.reset()


       self.chain_list    = []
       self.chain_list.extend(self.check_off.construct_chains(cf))
       self.chain_list.extend(self.measure_valve_resistance.construct_chains(cf))
       self.chain_list.extend(self.clean_filter.construct_chains(cf))
       #self.chain_list.extend(self.irrigation_control.construct_chains(cf))
       self.chain_list.extend(self.irrigation_control.construct_chains(cf))

       cluster_control.define_cluster( cluster_id, self.chain_list, [])
       self.check_off.construct_clusters( cluster_control, cluster_id,"CHECK_OFF" )
       self.measure_valve_resistance.construct_clusters(cluster_control, 
                                                     cluster_id,"MEASURE_RESISTANCE" )
       self.clean_filter.construct_clusters( cluster_control, cluster_id,"CLEAN_FILTER" )
       #self.irrigation_control   =  Irrigation_Control(io_control, redis_handle, alarm_queue)
       self.irrigation_control.construct_clusters( cluster_control, cluster_id,"DIAGNOSITIC_CONTROL" )



 

   def terminate_operation( self):
       self.clear_redis_irrigate_queue()
       self.cf.disable_chain_base(["QC_Check_Irrigation_Queue"] )
       self.cluster_ctrl.disable_cluster_rt( self.cf,self.cluster_id)

   def suspend_operation( self ,*args):
       self.cf.suspend_chain_code(["QC_Check_Irrigation_Queue"])
       self.cluster_ctrl.suspend_cluster_rt(self.cf , self.cluster_id)

   def resume_operation( self, *args ):
       self.cf.resume_chain_code(["QC_Check_Irrigation_Queue"])
       self.cluster_ctrl.resume_cluster_rt( self.cf,self.cluster_id)

   def restart_operation( self,*args):
       self.cf.enable_chain_code(["QC_Check_Irrigation_Queue"])
       self.cluster_ctrl.disable_cluster_rt( self.cf,self.cluster_id)

   def skip_operation( self,*args ):
       self.cf.send_event("RELEASE_IRRIGATION_CONTROL",None)       
      
   #
   # This function takes data from the IRRIGATION QUEUE And Transferrs it to the IRRIGATION_CELL_QUEUE
   # IRRIGATION_CELL_QUEUE only has one element in it
   #

   def start_unfinished_job( self, cf_handle, chainObj, parameters, event):
       json_string = self.redis_handle.lindex( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE",0 )
       json_object = json.loads(json_string)
       json_object["restart"] =  True
       if "elasped_time" not in json_object:
           json_object["elasped_time"] = 0 # this should not happen
       json_string = json.dumps( json_object )
       self.redis_handle.lset("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE",0,json_string)
       self.cluster_ctrl.enable_cluster_reset_rt( cf_handle, self.cluster_id,"DIAGNOSITIC_CONTROL" )

   def check_for_unfinished_job ( self,cf_handle, chainObj, parameters, event):

       if self.redis_handle.llen( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE" ) == 0:
           cf_handle.enable_chain_base(["QC_Check_Irrigation_Queue"] )
       else:
           cf_handle.enable_chain_base(["QC_Finish_Job"] )

      


   def check_queue( self, cf_handle, chainObj, parameters, event):
       if event["name"] == "INIT":
          return False

       length =   self.redis_handle.llen("QUEUES:SPRINKLER:IRRIGATION_QUEUE"  );
       #print("length",length)
       
       if int(length) > 0:
           return_value = True
       else:
           return_value = False
       
       return return_value 
            
   def dispatch_entry(self , cf_handle, chainObj, parameters, event ): 
 
       if event["name"] == "INIT":
          return

       binary_string = self.redis_handle.rpop(  "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       json_string = binary_string
       json_object = json.loads(json_string)
       print("json_object",json_object)
       if json_object["type"] == "CHECK_OFF":
           self.cluster_ctrl.enable_cluster_reset_rt( cf_handle, self.cluster_id, "CHECK_OFF" )
           return
       
       if json_object["type"] == "RESISTANCE_CHECK":
           print("made it here")
           self.cluster_ctrl.enable_cluster_reset_rt( cf_handle, self.cluster_id,"MEASURE_RESISTANCE" )
           return
       
 

       if json_object["type"] == "CLEAN_FILTER":
           self.cluster_ctrl.enable_cluster_reset_rt( cf_handle, self.cluster_id,"CLEAN_FILTER" )
           return
       if json_object["type"] == "IRRIGATION_STEP":
          json_object["restart"] =  False
          json_object["elasped_time"] = 0 
          json_string = json.dumps(json_object)
          print("basic irrigation control")
          self.redis_handle.delete("QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")
          self.redis_handle.lpush( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE", json_string)
          self.cluster_ctrl.enable_cluster_reset_rt( cf_handle, self.cluster_id,"DIAGNOSITIC_CONTROL" )
   
       if json_object["type"] == "START_SCHEDULE" :
          self.alarm_queue.store_event_queue( "irrigation_schedule_start", json_object )
  
       if json_object["type"] == "END_SCHEDULE" :
           self.alarm_queue.store_event_queue( "irrigation_schedule_stop", json_object )
       
       return "DISABLE"

   def clear_redis_irrigate_queue( self,*args ):
       #print "clearing irrigate queue"
       self.redis_handle.delete( "QUEUES:SPRINKLER:IRRIGATION_QUEUE" )
       self.redis_handle.delete( "QUEUES:SPRINKLER:IRRIGATION_CELL_QUEUE")

   def read_wd_flag( self,*arg ):
       irrigation_io.read_wd_flag()     

   def write_wd_flag( self,value,*arg ):
       irrigation_io.write_wd_flag()  

   def update_time_stamp( self, *args ):
       self.redis_handle.hset( "CONTROL_VARIABLES", "sprinkler_time_stamp", time.time() )


if __name__ == "__main__":
   pass

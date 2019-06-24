import json
import base64
import time

class Valve_Resistance_Check(object):

   def __init__( self, cf, cluster_control,io_control, redis_handle,
                alarm_queue, app_files, sys_files):
       self.redis_handle = redis_handle
       self.sys_files    = sys_files
       self.app_files    = app_files
       self.cf           = cf
       self.cluster_control = cluster_control
       self.io_control      = io_control
       self.alarm_queue     = alarm_queue
       


   def construct_chains( self, cf):

       cf.define_chain("resistance_check",False)        
       cf.insert.send_event("IRI_MASTER_VALVE_SUSPEND",None)
       cf.insert.one_step( self.assemble_relevant_valves )
       cf.insert.enable_chains(["test_each_valve"])
       cf.insert.wait_event_count( event = "IR_V_Valve_Check_Done" )
       cf.insert.log("event IR_V_Valve_Check_Done")
       cf.insert.send_event("RELEASE_IRRIGATION_CONTROL" ) 
       cf.insert.send_event("IRI_MASTER_VALVE_RESUME",None)
       cf.insert.terminate() 

       cf.define_chain("test_each_valve",False,init_function= self.check_queue_a)
       cf.insert.wait_event_count( count = 1 )
       cf.insert.one_step(self.valve_setup)
       cf.insert.wait_event_count(count =2)
       cf.insert.one_step( self.valve_measurement)
       cf.insert.verify_function_terminate(  reset_event = "IR_V_Valve_Check_Done",
                                             reset_event_data=None,
                                             function = self.check_queue) 

       cf.insert.reset()

       return  ["resistance_check","test_each_valve"]

 



   def construct_clusters( self, cluster, cluster_id, state_id ):
       cluster.define_state( cluster_id, state_id, ["resistance_check"]  )


   def assemble_relevant_valves(self, *args):
       remote_dictionary = set()
       pin_dictionary    = set()
       dictionary        = {}
       
       
       
       self.redis_handle.delete(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" )
       sprinkler_ctrl = self.app_files.load_file("sprinkler_ctrl.json")

       for j in sprinkler_ctrl:
           schedule = j["name"]
           json_data  =self.app_files.load_file(j["link"]) 
           for i in json_data["schedule"]:
             for k in i:
                remote = k[0]
                pin    = str(k[1][0])
                self.update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )

       master_valve = self.sys_files.load_file("master_valve_setup.json")

       for j in master_valve:
          remote = j[0]
          pin    = str(j[1][0])
          self.update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )         
          remote = j[2]
          pin    = str(j[3][0])
          self.update_entry( remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary )  
          json_string = json.dumps(dictionary)         
          queue_object = base64.b64encode(json_string.encode())
          self.redis_handle.set(  "SPRINKLER_RESISTANCE_DICTIONARY",queue_object)
               
   def add_resistance_entry( self, remote_dictionary,  pin_dictionary, remote, pin ):
       if ( remote not in remote_dictionary ) or ( pin not in pin_dictionary ):
               remote_dictionary.union( remote)
               pin_dictionary.union(pin)
               json_object = [ remote,pin]
               json_string = json.dumps(json_object)
               #print( "json_string",json_string )
               self.redis_handle.lpush(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE",json_string )


   def update_entry( self,remote_dictionary, pin_dictionary, remote,pin, schedule ,  dictionary ):
       
       if remote not in dictionary :
           dictionary[remote] = {}
       
       if pin not in  dictionary[remote]:
           dictionary[remote][pin] = list(set())
       dictionary[remote][pin] = set( dictionary[remote][pin])
       dictionary[remote][pin].union(schedule) 
       dictionary[remote][pin] = list( dictionary[remote][pin])
       self.add_resistance_entry( remote_dictionary, pin_dictionary, remote, pin )

   def check_queue(self,cf_handle, chainObj, parameters, event ):
       if event["name"] == "INIT":
          return True
       else:
          return self.check_queue_a()
          
       

   def check_queue_a( self,*args ):
       length = self.redis_handle.llen(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" )
       print("check_queue",length)
       if length > 0:
           return_value = True
       else:
           self.alarm_queue.store_past_action_queue("Valve_Resistance_Check_Done","Green" )
           return_value = False
       print("return_value",return_value)
       return return_value

   def valve_setup(self, *args ):
       print("setup step")
       json_string = self.redis_handle.rpop(  "QUEUES:SPRINKLER:RESISTANCE_CHECK_QUEUE" )
       json_object = json.loads(json_string)
       print( "json object",json_object )
       self.io_control.disable_all_sprinklers()
       self.io_control.load_duration_counters( 1  ) #  2 minute
       self.io_control.turn_on_valve(  [{"remote": json_object[0], "bits":[int(json_object[1])]}] ) #  {"remote":xxxx,"bits":[] } 
       self.remote = json_object[0]
       self.output = json_object[1]
 

           
   def valve_measurement(self, *args ):
       print("measurement step")
       coil_current = self.io_control.measure_valve_current()
       print( "coil current",coil_current )
       queue = "log_data:resistance_log:"+str(self.remote)+":"+str(self.output)
       self.redis_handle.lpush(queue, coil_current )  # necessary for web server
       self.redis_handle.ltrim(queue,0,30)
       queue = "log_data:resistance_log_cloud:"+str(self.remote)+":"+str(self.output)
       self.redis_handle.lpush(queue, 
              json.dumps( { "current": coil_current, "time":time.time()} ))  #necessary for cloud
       self.redis_handle.ltrim(queue,0,30)
       self.io_control.disable_all_sprinklers()
               



if __name__ == "__main__":
   pass

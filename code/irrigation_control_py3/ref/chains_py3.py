#
# Adding chains
#
   cf = py_cf.CF_Interpreter()

   cf.define_chain("reboot_message", True)  #tested
   cf.insert_link( "link_1",  "One_Step", [  clear_redis_set_keys ] )
   cf.insert_link( "link_2",  "One_Step", [ clear_redis_clear_keys ] )
   cf.insert_link( "link_2",  "One_Step",   [ plc_watch_dog.read_mode ] )
   cf.insert_link( "link_3",  "One_Step",   [ plc_watch_dog.read_mode_switch ] ) 
   cf.insert_link( "link_3",  "One_Step", [ irrigation_io_control.disable_all_sprinklers ] )
   cf.insert_link( "link_4",  "One_Step" ,[ check_for_uncompleted_sprinkler_element ] )
   cf.insert_link( "link_5",  "Terminate",  [] )




   cf.define_chain("update_time_stamp", True) #tested
   cf.insert_link( "link_1",  "WaitTime",    [10,0,0,0] )
   cf.insert_link( "link_3",  "One_Step",    [ monitor.update_time_stamp ] )
   cf.insert_link( "link_4",  "Reset",       [] )
   
 
  


        
   cf.define_chain("manual_master_valve_on_chain",False) #tested
   #cf.insert_link( "link_1",    "Log",                  ["manual master"] )
   cf.insert_link( "link_2",    "Code",                 [ monitor.verify_resume ])
   cf.insert_link( "link_3",    "One_Step",             [ irrigation_io_control.turn_on_master_valves ] )
   cf.insert_link( "link_4",    "One_Step",             [ irrigation_io_control.turn_off_cleaning_valves ] )# turn turn off master valve
   cf.insert_link( "link_5",    "WaitTime",             [ 5,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_6",    "Reset",                [] )

   cf.define_chain("monitor_master_on_switch",False) #TBD
   #cf.insert_link("link_1",  "WaitTime",             [5,0,0,0] ) 
   #cf.insert_link("link_2",  "Code",                 [ detect_on_switch_on ] )
   #cf.insert_link("link_3",  "One_Step",             [ clear_redis_set_keys ] )
   #cf.insert_link("link_4",  "Enable_Chain",         [["manual_master_valve_on_chain"]] )
   #cf.insert_link("link_5",  "Enable_Chain",         [["manual_master_valve_off_chain"]] )
   #cf.insert_link("link_6",  "WaitTime",             [3600*8,0,0,0] ) # wait 8 hours
   #cf.insert_link("link_7",  "Disable_Chain",        [["manual_master_valve_on_chain"]] )
   #cf.insert_link("link_8",  "One_Step",             [ irrigation_io_control.turn_off_master_valves ])   
   #cf.insert_link("link_9",  "Reset",                [])
   cf.insert_link("link_9",  "Halt",                [])


   cf.define_chain("monitor_master_on_web",False) #TBD
   cf.insert_link( "link_0",    "Log",                  ["monitor master on web"] )
   cf.insert_link("link_1",  "Enable_Chain",         [["manual_master_valve_on_chain"]] )
   cf.insert_link("link_2",  "WaitTime",             [ 3600*8,0,0,0] ) # wait 8 hour
   cf.insert_link("link_3",  "Enable_Chain",         [["manual_master_valve_on_chain"]] )
   cf.insert_link("link_4",  "Disable_Chain",        [["manual_master_valve_off_chain"]] )
   cf.insert_link("link_5",  "One_Step",             [ irrigation_io_control.turn_off_master_valves ])   
   cf.insert_link("link_6",  "Disable_Chain",        [["monitor_master_on_web"]] )
  

     


   cf.define_chain("manual_master_valve_off_chain",False ) #TBD
   cf.insert_link("link_1",    "WaitTime",             [5,0,0,0] ) 
   #cf.insert_link("link_1",    "Code",                 [ detect_switch_off ] )
   #cf.insert_link("link_2",    "One_Step",             [ clear_redis_clear_keys ] )
   #cf.insert_link("link_3",    "One_Step",             [ clear_redis_set_keys ] )
   #cf.insert_link("link_4",    "Enable_Chain",         [["monitor_master_on_switch"]] ) 
   #cf.insert_link("link_5",    "Disable_Chain",        [["manual_master_valve_on_chain"]] ) 
   #cf.insert_link("link_6",    "Disable_Chain",        [["monitor_master_on_web"]] )     
   #cf.insert_link("link_7",    "One_Step",             [ irrigation_io_control.turn_off_master_valves ] )# turn turn on master valve
   #cf.insert_link("link_8",    "One_Step",             [ irrigation_io_control.turn_off_cleaning_valves ] )# turn turn off master valve
   cf.insert_link("link_6",    "Disable_Chain",        [["manual_master_valve_off_chain"]] )


   cf.define_chain("gpm_triggering_clean_filter",True) #TBDf

   cf.insert_link( "link_1",  "WaitEvent",      [ "MINUTE_TICK" ] )
   #cf.insert_link( "link_1",  "Log",            ["check to clean filter"] )
   cf.insert_link( "link_2",  "One_Step",       [ monitor.check_to_clean_filter ] )
   cf.insert_link( "link_3",  "Reset",      [] )

   cf.define_chain("update_modbus_statistics",True) #tested
   
   #cf.insert_link( "link_1",  "Log",            ["update modbus statistics"] )
   cf.insert_link( "link_2",  "One_Step",       [ monitor.update_modbus_statistics ] )
   cf.insert_link( "link_3",  "WaitTime",       [ 15,25,0,0] ) # wait 15 minutes
   cf.insert_link( "link_4",  "Reset",      [] )

   cf.define_chain("clear_modbus_statistics",True) #tested
   cf.insert_link( "link_1",  "WaitTod",        ["*",1,"*","*"] )
   #cf.insert_link( "link_2",  "Log",            ["clear modbus statistics"] )
   cf.insert_link( "link_3",  "One_Step",       [ monitor.clear_modbus_statistics ] )
   cf.insert_link( "link_4",  "WaitTod",        ["*",2,"*","*"] )
   cf.insert_link( "link_5",  "Reset",          [] )
   

   cf.define_chain("plc_watch_dog", True ) #TBD
   #cf.insert_link( "link_1",  "Log",        ["plc watch dog thread"] )
   #cf.insert_link( "link_2",  "One_Step",   [ plc_watch_dog.read_mode ] )
   #cf.insert_link( "link_3",  "One_Step",   [ plc_watch_dog.read_mode_switch ] ) 
   cf.insert_link( "link_4",  "One_Step",   [ plc_watch_dog.read_wd_flag  ]      )
   cf.insert_link( "link_5",  "One_Step",   [ plc_watch_dog.write_wd_flag ]      )
   cf.insert_link( "link_1", "WaitTime",    [ 30,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_7",  "Reset",    [] )



   cf.define_chain( "plc_monitor_control_queue", True ) #tested
   cf.insert_link( "link_1", "WaitTime", [ 1,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_2", "One_Step", [ sprinkler_control.dispatch_sprinkler_mode ] ) 
   cf.insert_link( "link_3", "Reset",    [] )
  




   cf.define_chain("monitor_irrigation_job_queue", True ) # tested
   cf.insert_link( "link_1",  "WaitTime",       [ 5,0,0,0] ) # wait 5 seconds
   cf.insert_link( "link_2",  "Code",           [ sprinkler_queue.load_irrigation_cell ] )
   cf.insert_link( "link_3",  "Code",           [ sprinkler_element.start] )
   cf.insert_link( "link_4",  "WaitTime",       [ 1,0,0,0] ) # wait 1 seconds
   cf.insert_link( "link_5",  "One_Step",       [ monitor.measure_current ] )
   cf.insert_link( "link_6",  "Code",            [ sprinkler_element.check_current ] )
   cf.insert_link( "link_7",  "Enable_Chain",   [["monitor_irrigation_cell","monitor_current_sub" ]])
   cf.insert_link( "link_8",  "WaitEvent",      ["CELL_DONE" ] )
   cf.insert_link( "link_9",  "Reset",          [] )


   #cf.define_chain("monitor_current_sub", False )
   #cf.insert_link( "link_0",  "Log"  ,           [["monitor_current_sub chain is working"]])
   #cf.insert_link( "link_1",  "WaitTime",        [ 15,0,0,0]) # wait 15 second
   #cf.insert_link( "link_2",  "One_Step",       [ monitor.measure_current_a ] )
   #cf.insert_link( "link_3",  "One_Step",       [ sprinkler_element.check_current ] )
   #cf.insert_link( "link_4",  "Reset",          [] )


   cf.define_chain("monitor_irrigation_cell", False ) #Tested
   cf.insert_link( "link_1",  "WaitTime",        [ 15,0,0,0]) # wait 15 second
   cf.insert_link( "link_2",  "One_Step",       [ sprinkler_element.check_current ] )
   cf.insert_link( "link_3",  "One_Step",       [ sprinkler_element.check_for_excessive_flow_rate ] )
   cf.insert_link( "link_4",  "Code",           [ sprinkler_element.monitor ] ) 
   cf.insert_link( "link_5",  "SendEvent",      ["CELL_DONE"] ) 
   cf.insert_link( "link_6",  "Disable_Chain",  [["monitor_irrigation_cell","monitor_current_sub" ]])


   cf.define_chain("monitor_well_pressure", False ) #Tested
   #cf.insert_link( "link_1",  "WaitTime",        [ 15,0,0,0]) # wait 15 second
   #cf.insert_link( "link_2",  "One_Step",       [ sprinkler_element.check_current ] )
   #cf.insert_link( "link_3",  "One_Step",       [ sprinkler_element.check_for_excessive_flow_rate ] )
   #cf.insert_link( "link_4",  "Code",           [ sprinkler_element.monitor ] ) 
   #cf.insert_link( "link_5",  "SendEvent",      ["CELL_DONE"] ) 
   cf.insert_link( "link_4",  "Reset",          [] )

   
   cf_environ = py_cf.Execute_Cf_Environment( cf )
   cf_environ.execute()
   
  

       
     

      


class Help_Functions(object):

   def __init__(self,cf):
       self.cf = cf

   #
   #  Return code functions
   #
   def terminate( self ):
      self.cf.insert_link( "Terminate", [] )

   def halt(self ):
       self.cf.insert_link("Halt",[] )

   def reset( self ):
       self.cf.insert_link("Reset",[] )

   def chain_flow_reset( self ): 
       self.cf.insert_link("Reset_Chain_Flow",[])
       


   #
   #   Manipulate Chains
   #
   def enable_chains( self, list_of_chains ):
       self.cf.insert_link("Enable_Chain",[list_of_chains] )

   def disable_chains( self, list_of_chains ):
       self.cf.insert_link("Disable_Chain",[list_of_chains] )

   def suspend_chains( self, list_of_chains ):
       self.cf.insert_link("Suspend_Chain",[list_of_chains] )

   def resume_chains( self, list_of_chains ):
       self.cf.insert_link("Resume_Chain",[list_of_chains] )

   #
   #  debug function
   #
   def log( self, debug_message ):
       self.cf.insert_link( "Log",[ debug_message ] )

   #
   #  One Time Functions
   #
   def one_step( self, function,*params ):
       
       list_data = [function]
       list_data.extend(params)
       self.cf.insert_link("One_Step",list_data )
 
   #
   # Event Functions
   #  
   def send_event( self, event, event_data = "" ):
       
       self.cf.insert_link("Send_Event",[event,event_data] )
       

   #
   #   Opcode which acts on an event
   #

   def check_event( self, event, function, *params ):
       
       list_data = [ event, function ]
       list_data.extend(params)
       self.cf.insert_link("Check_Event",list_data)

   #
   #   user function with full return code flexiability
   #
   def code( self, function, *params ):
       list_data = [ function ]
       list_data.extend(params)
       self.cf.insert_link("Code",list_data )



   #
   #   Wait  Functions
   #

   def wait_tod( self, dow="*",hour="*",minute="*",second="*" ):
       self.cf.insert_link("Wait_Tod",[dow,hour,minute,second] )

   def wait_tod_ge( self, dow="*",hour="*",minute="*",second="*" ):
       self.cf.insert_link("Wait_Tod_GE",[dow,hour,minute,second] )

   def wait_tod_le( self,dow="*",hour="*",minute="*",second="*" ):
       self.cf.insert_link("Wait_Tod_LE",[dow,hour,minute,second] )

   def wait_event_count( self,event="TIME_TICK", count = 1 ):
       self.cf.insert_link("Wait_Event_Count",[event, count] )

   def wait_function( self, function ,*params):
       list_data = [function]
       list_data.extend(params)
       self.cf.insert_link("Wait_Fn", list_data)


   #
   #   Verify Reset  Functions
   #

   def verify_tod_reset( self, dow="*",hour="*",minute="*",second="*", reset_event = None, reset_data = None ):
       self.cf.insert_link("Verify_Tod",[dow,hour,minute,second,[reset_event,reset_data], True] )

   def verify_tod_ge_reset( self, dow="*",hour="*",minute="*",second="*",reset_event = None, reset_data = None ):
       self.cf.insert_link("Verify_Tod_GE",[dow,hour,minute,second,[reset_event,reset_data],True] )

   def verify_tod_le_reset( self,dow="*",hour="*",minute="*",second="*",reset_event = None , reset_data = None):
       self.cf.insert_link("Verify_Tod_LE",[dow,hour,minute,second,[reset_event,reset_data],True] )

   def verify_not_event_count_reset( self,event="TIME_TICK", count = 1, reset_event = None, reset_data = None ):
       self.cf.insert_link("Verify_Not_Event_Count",[event, count, [reset_event,reset_data], True] )

   def verify_function_reset( self, reset_event,reset_event_data, function, *params):
       list_data = [function,[reset_event,reset_event_data], True]  
       list_data.extend(params)

       self.cf.insert_link("Verify_Fn", list_data)

   #
   #   Verify Terminate  Functions
   #
   def verify_tod_terminate( self, dow="*",hour="*",minute="*",second="*", reset_event = None, reset_data = None ):
       self.cf.insert_link("Verify_Tod",[dow,hour,minute,second,[reset_event,reset_data], False] )

   def verify_tod_ge_terminate( self, dow="*",hour="*",minute="*",second="*",reset_event = None , reset_data = None):
       self.cf.insert_link("Verify_Tod_GE",[dow,hour,minute,second,[reset_event,reset_data],False] )

   def verify_tod_le_terminate( self,dow="*",hour="*",minute="*",second="*",reset_event = None, reset_data = None ):
       self.cf.insert_link("Verify_Tod_LE",[dow,hour,minute,second,[reset_event,reset_data],False] )

   def verify_not_event_count_terminate( self,event="TIME_TICK", count = 1, reset_event = None , reset_data = None):
       self.cf.insert_link("Verify_Not_Event_Count",[event, count, [reset_event,reset_data] ,False] )

   def verify_function_terminate( self, reset_event ,reset_event_data, function, *params):
       list_data = [function,[reset_event,reset_event_data], False] 
       list_data.extend(params)
       self.cf.insert_link("Verify_Fn", list_data)


   #
   #   Assert Reset  Functions
   #

   def assert_tod_reset( self, dow="*",hour="*",minute="*",second="*", reset_event = None, reset_data = None ):
       self.cf.insert_link("Assert_Tod",[dow,hour,minute,second,[reset_event,reset_data], True] )

   def assert_tod_ge_reset( self, dow="*",hour="*",minute="*",second="*",reset_event = None, reset_data = None ):
       self.cf.insert_link("Assert_Tod_GE",[dow,hour,minute,second,[reset_event,reset_data],True] )

   def assert_tod_le_reset( self,dow="*",hour="*",minute="*",second="*",reset_event = None , reset_data = None):
       self.cf.insert_link("Assert_Tod_LE",[dow,hour,minute,second,[reset_event,reset_data],True] )

   def assert_not_event_count_reset( self,event="TIME_TICK", count = 1, reset_event = None, reset_data = None ):
       self.cf.insert_link("Assert_Not_Event_Count",[event, count, [reset_event,reset_data], True] )

   def assert_function_reset( self, function,  reset_event=None,reset_event_data=None,params =[]):
       list_data = [function,[reset_event,reset_event_data], True]  
       list_data.extend(params)

       self.cf.insert_link("Assert_Fn", list_data)

   #
   #   Assert Terminate  Functions
   #
   def assert_tod_terminate( self, dow="*",hour="*",minute="*",second="*", reset_event = None, reset_data = None ):
       self.cf.insert_link("Assert_Tod",[dow,hour,minute,second,[reset_event,reset_data], False] )

   def assert_tod_ge_terminate( self, dow="*",hour="*",minute="*",second="*",reset_event = None , reset_data = None):
       self.cf.insert_link("Assert_Tod_GE",[dow,hour,minute,second,[reset_event,reset_data],False] )

   def assert_tod_le_terminate( self,dow="*",hour="*",minute="*",second="*",reset_event = None, reset_data = None ):
       self.cf.insert_link("Assert_Tod_LE",[dow,hour,minute,second,[reset_event,reset_data],False] )

   def assert_not_event_count_terminate( self,event="TIME_TICK", count = 1, reset_event = None , reset_data = None):
       self.cf.insert_link("Assert_Not_Event_Count",[event, count, [reset_event,reset_data] ,False] )

   def assert_function_terminate( self, reset_event ,reset_event_data, function, *params):
       list_data = [function,[reset_event,reset_event_data], False] 
       list_data.extend(params)
       self.cf.insert_link("Assert_Fn", list_data)



if __name__ == "__main__":
   pass
   
   


 
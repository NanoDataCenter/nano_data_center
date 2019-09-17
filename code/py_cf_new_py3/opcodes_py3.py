
import datetime
import time



class Opcodes(object):

    def __init__(self):

       self.opcodes = {}
       self.opcodes["Terminate"]          = self.terminate_code
       self.opcodes["Reset"]              = self.reset_code
       self.opcodes["Halt"]               = self.halt_code
       self.opcodes["Enable_Chain"]       = self.enable_chain_code
       self.opcodes["Disable_Chain"]      = self.disable_chain_code
       self.opcodes["Suspend_Chain"]      = self.suspend_chain_code
       self.opcodes["Resume_Chain"]       = self.resume_chain_code   
       self.opcodes["Log"]                = self.log_code
       self.opcodes["One_Step"]           = self.one_step_code
       self.opcodes["Send_Event"]         = self.send_event_code 
       self.opcodes["Check_Event"]       = self.check_event_code 
       self.opcodes["Code"]               = self.code_code 
       self.opcodes["Wait_Tod"]           = self.wait_tod_code 
       self.opcodes["Wait_Tod_GE"]        = self.wait_tod_ge_code 
       self.opcodes["Wait_Tod_LE"]        = self.wait_tod_le_code 
       self.opcodes["Wait_Event_Count"]   = self.wait_event_count_code 
       self.opcodes["Wait_Fn"]            = self.wait_fn_code 
       self.opcodes["Verify_Tod"]         = self.verify_tod_code 
       self.opcodes["Verify_Tod_GE"]      = self.verify_tod_ge_code 
       self.opcodes["Verify_Tod_LE"]     = self.verify_tod_le_code 
       self.opcodes["Verify_Not_Event_Count"]       = self.verify_not_event_count_code 
       self.opcodes["Verify_Fn"]                    = self.verify_fn_code
       self.opcodes["Assert_Tod"]         = self.assert_tod_code 
       self.opcodes["Assert_Tod_GE"]      = self.assert_tod_ge_code 
       self.opcodes["Assert_Tod_LE"]     = self.assert_tod_le_code 
       self.opcodes["Assert_Not_Event_Count"]       = self.assert_not_event_count_code 
       self.opcodes["Assert_Fn"]                    = self.assert_fn_code


    def get_opcode(self, opcode_name):
        return self.opcodes[opcode_name]

    def add_opcode(self, name, code):
        self.opcodes[name] = code

    def terminate_code(self, cf_handle, chainObj, parameters, event):
        return "TERMINATE"


    def reset_code(self, cf_handle, chainObj, parameters, event):
        return "RESET"

    def halt_code(self, cf_handle, chainObj, parameters, event):
        return "HALT"




    def enable_chain_code(self, cf_handle, chainObj, parameters, event):
        chains = parameters[0]
        for j in chains:
            cf_handle.enable_chain_base(j)
        return "DISABLE"

    def disable_chain_code(self, cf_handle, chainObj, parameters, event):
        chains = parameters[0]
        for j in chains:
  
            cf_handle.disable_chain_base(j)

        return "DISABLE"

    def resume_chain_code(self, cf_handle, chainObj, parameters, event):
        chains = parameters[0]

        for j in chains:

            cf_handle.resume_chain_code(j)
        return "DISABLE"

    def suspend_chain_code(self, cf_handle, chainObj, parameters, event):
        chains = parameters[0]
        for j in chains:
            cf_handle.suspend_chain_code(j)

        return "DISABLE"



    def log_code(self, cf_handle, chainObj, parameters, event):
        if event["name"] == "INIT":
            print("Log ---",time.time(), parameters[0])
        return "DISABLE"


    def one_step_code(self, cf_handle, chainObj, parameters, event):
        if event["name"] != "INIT":

            func = parameters[0]
            func(cf_handle, chainObj, parameters, event)
        return "DISABLE"


    def send_event_code(self, cf_handle, chainObj, parameters, event):
        if event["name"] != "INIT":
           # print "send event ",parameters[0]
           event_name = parameters[0]
           if len(parameters) > 1:
               event_data = parameters[1]
           else:
               event_data = None

           event = {}
           event["name"] = event_name
           event["data"] = event_data
           cf_handle.event_queue.append(event)
       

        return "DISABLE"


    def check_event_code(self, cf_handle, chainObj, parameters, event):

        if event["name"] == "INIT":
            
            func = parameters[1]
            func(cf_handle, chainObj, parameters, event)
        elif event["name"] == parameters[0]:
            func = parameters[1]
            func(cf_handle, chainObj, parameters, event)
        return "CONTINUE"




    def code_code(self, cf_handle, chainObj, parameters, event):
        return_value = parameters[0](cf_handle, chainObj, parameters, event)
        # print "return_value%%%%%%%%%%%%%%%%%%%%%%", return_value
        return return_value



 
    def wait_event_count_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "HALT"
        
        if event["name"] == "INIT":
           parameters.append(0)
        else:
            if event["name"] == parameters[0]:
                
                parameters[-1] = parameters[-1] + 1
                if  parameters[-1] >= int(parameters[1]):
                    returnValue = "DISABLE"

        return returnValue


    def wait_tod_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "HALT"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue

        time_stamp = datetime.datetime.today()
        
        if ((dow == time_stamp.weekday()) or
                (dow == "*")) == False:
            return returnValue

        if ((hour == time_stamp.hour) or
                (hour == "*")) == False:
            return returnValue

        if ((minute == time_stamp.minute) or
                (minute == "*")) == False:
            return returnValue
 
        if ((second == time_stamp.second) or
                (second == "*")) == False:
            return returnValue

        return "DISABLE"

    def wait_tod_le_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "HALT"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue


        time_stamp = datetime.datetime.today()
    

        if ((dow == "*") or
                (dow >= time_stamp.weekday())) == False:
            return returnValue

        if ((hour == "*") or
                (hour >= time_stamp.hour)) == False:
            return returnValue

        if ((minute == "*") or
                (minute >= time_stamp.minute)) == False:
            return returnValue

        if ((second == "*") or
                (second >= time_stamp.second)) == False:
            return returnValue
     
        return "DISABLE"

    def wait_tod_ge_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "HALT"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue


        time_stamp = datetime.datetime.today()

        if ((dow == "*") or
                (dow <= time_stamp.weekday())) == False:
            return returnValue

        if ((hour == "*") or
                (hour <= time_stamp.hour)) == False:
            return returnValue

        if ((minute == "*") or
                (minute <= time_stamp.minute)) == False:
            return returnValue

        if ((second == "*") or
                (second <= time_stamp.second)) == False:
            return returnValue

        return "DISABLE"

    def wait_fn_code(self, cf_handle, chainObj, parameters, event):
        waitFn = parameters[0]
        if waitFn(cf_handle, chainObj, parameters, event):
            returnValue = "DISABLE"
        else:
            returnValue = "HALT"

        return returnValue


    def verify_return_code( self, cf_handle, reset_event, reset_flag ):
        
        if reset_event[0] != None:
               event = {}
               event["name"] = reset_event[0]
               event["data"] = reset_event[1]
               cf_handle.event_queue.append(event)
        if reset_flag == True:
           return_value = "RESET"
        else:
           return_value = "TERMINATE"
        return return_value


    def verify_fn_code(self, cf_handle, chainObj, parameters, event):
        
        reset_event  = parameters[1]
        reset_flag   = parameters[2]
        verifyFn     = parameters[0]
        
        if verifyFn (cf_handle, chainObj, parameters, event):
            returnValue = "CONTINUE"
        else:
    
            
            returnValue = self.verify_return_code( cf_handle, reset_event, reset_flag)
            
        
        return returnValue


      
    def verify_not_event_count_code(self, cf_handle, chainObj, parameters, event):
        reset_flag = parameters[3]
        reset_event = parameters[2]
        returnValue = "CONTINUE"
        if event["name"] == "INIT":
            parameters.append(0)
        else:
            if event["name"] == parameters[0]:
               
                parameters[-1] = parameters[-1] + 1
                if parameters[-1] >= int(parameters[1]):
                    returnValue = self.verify_return_code( cf_handle, reset_event, reset_flag)

        return returnValue


    def verify_tod_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "CONTINUE"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]
        reset_event        = parameters[4]
        reset_flag   = parameters[5]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue 


        time_stamp = datetime.datetime.today()

        if ((dow == time_stamp.weekday()) or
                (dow == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((hour == time_stamp.hour) or
                (hour == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((minute == time_stamp.minute) or
                (minute == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((second == time_stamp.second) or
                (second == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        return "CONTINUE"

    def verify_tod_le_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "CONTINUE"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]
        reset_event        = parameters[4]
        reset_flag   = parameters[5]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue 


        time_stamp = datetime.datetime.today()
        

        if ((dow == "*") or
                (dow >= time_stamp.weekday())) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((hour == "*") or
                (hour >= time_stamp.hour)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((minute == "*") or
                (minute >= time_stamp.minute)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((second == "*") or
                (second >= time_stamp.second)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)
     
        return "CONTINUE"

    def verify_tod_ge_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "CONTINUE"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]
        reset_event  = parameters[4]
        reset_flag   = parameters[5]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue 


        time_stamp = datetime.datetime.today()

        if ((dow == "*") or
                (dow <= time_stamp.weekday())) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((hour == "*") or
                (hour <= time_stamp.hour)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((minute == "*") or
                (minute <= time_stamp.minute)) == False:
            return self.verify_return_code( cf_handle, ereset_vent, reset_flag)

        if ((second == "*") or
                (second <= time_stamp.second)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        return "CONTINUE"


    def verify_fn_code(self, cf_handle, chainObj, parameters, event):
        
        reset_event  = parameters[1]
        reset_flag   = parameters[2]
        verifyFn     = parameters[0]
        
        if verifyFn ():
            returnValue = "CONTINUE"
        else:
    
            
            returnValue = self.verify_return_code( cf_handle, reset_event, reset_flag)
            
       
        return returnValue


      
    def assert_not_event_count_code(self, cf_handle, chainObj, parameters, event):
        reset_flag = parameters[3]
        reset_event = parameters[2]
        returnValue = "DISABLE"
        if event["name"] == "INIT":
            parameters.append(0)
        else:
            if event["name"] == parameters[0]:
                parameters[-1] = parameters[-1] + 1
                if parameters[-1] >= int(parameters[1]):
                    returnValue = self.verify_return_code( cf_handle, reset_event, reset_flag)

        return returnValue


    def assert_tod_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "DISABLE"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]
        reset_event        = parameters[4]
        reset_flag   = parameters[5]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue 


        time_stamp = datetime.datetime.today()

        if ((dow == time_stamp.weekday()) or
                (dow == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((hour == time_stamp.hour) or
                (hour == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((minute == time_stamp.minute) or
                (minute == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((second == time_stamp.second) or
                (second == "*")) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        return "CONTINUE"

    def assert_tod_le_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "DISABLE"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]
        reset_event        = parameters[4]
        reset_flag   = parameters[5]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue 


        time_stamp = datetime.datetime.today()
        

        if ((dow == "*") or
                (dow >= time_stamp.weekday())) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((hour == "*") or
                (hour >= time_stamp.hour)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((minute == "*") or
                (minute >= time_stamp.minute)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)


        if ((second == "*") or
                (second >= time_stamp.second)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)
     
        return "CONTINUE"

    def assert_tod_ge_code(self, cf_handle, chainObj, parameters, event):

        returnValue = "DISABLE"
        dow = parameters[0]
        hour = parameters[1]
        minute = parameters[2]
        second = parameters[3]
        reset_event  = parameters[4]
        reset_flag   = parameters[5]

        #
        # prevent excessive calculations
        if event["name"] != "TIME_TICK":
           return returnValue 


        time_stamp = datetime.datetime.today()

        if ((dow == "*") or
                (dow <= time_stamp.weekday())) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((hour == "*") or
                (hour <= time_stamp.hour)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        if ((minute == "*") or
                (minute <= time_stamp.minute)) == False:
            return self.verify_return_code( cf_handle, ereset_vent, reset_flag)

        if ((second == "*") or
                (second <= time_stamp.second)) == False:
            return self.verify_return_code( cf_handle, reset_event, reset_flag)

        return "CONTINUE"

    def assert_fn_code(self, cf_handle, chainObj, parameters, event):
        
        reset_event  = parameters[1]
        reset_flag   = parameters[2]
        verifyFn     = parameters[0]
        if event["name"] == "INIT":
           return "CONTINUE"
           
        if verifyFn (cf_handle, chainObj, parameters, event):

            returnValue = "DISABLE"
        else:
    
          
           returnValue = self.verify_return_code( cf_handle, reset_event, reset_flag)
 
        
        return returnValue



    def test_for_duplicate_functions(self):
       function_set = set()
       for i , item in self.opcodes.items():
           if item == None:
               raise ValueError("function is not defined opcode "+i)           
           if item in function_set:
              raise ValueError("duplicate opcode functions   opcode  "+i)
           function_set.add(item)
           
 
if __name__ == "__main__":
   print("test core opcodes")

   opcodes = Opcodes()
   opcodes.test_for_duplicate_functions()
   print("test is done")
   

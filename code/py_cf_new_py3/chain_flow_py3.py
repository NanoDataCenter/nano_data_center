import datetime
import time
import sys

from .opcodes_py3 import Opcodes
from .help_functions_py3 import Help_Functions


class CF_Base_Interpreter(object):

    def __init__(self):
        self.chains = []

        self.chain_map = {}
        self.event_queue = []
        self.current_chain = None
        self.opcodes = Opcodes()
        self.insert  = Help_Functions(self)
        self.valid_return_codes = {}
        self.valid_return_codes["CONTINUE"] = 1
        self.valid_return_codes["HALT"] = 1
        self.valid_return_codes["RESET"] = 1
        self.valid_return_codes["DISABLE"] = 1
        self.valid_return_codes["TERMINATE"] = 1
        self.valid_return_codes["SYSTEM_RESET"] = 1
        

    #
    # Chain and link construction
    #

    def define_chain(self, chain_name, auto_start, init_function = None, 
                           term_function = None, except_function = None):
        chain = {}
        chain["init_function"] = init_function
        chain["term_function"] = term_function
        chain["except_function"] = except_function
        chain["name"] = chain_name
        chain["index"] = 0
        chain["links"] = []
        chain["auto_start"] = auto_start
        chain["active"] = False
        chain["suspend"] = False
        self.current_chain = chain
        self.chain_map[ chain_name ] = len(self.chains)
        self.chains.append(chain)
 

    def insert_link(self, opcode_name, parameters):
        instruction = self.opcodes.get_opcode(opcode_name)
        link = {}
        link["op_code_name"] = opcode_name
        link["instruction"] = instruction  # [0] code [1] local parameters
        link["init_flag"] = True
        link["active_flag"] = True
        link["parameters"] = parameters
        assert self.current_chain is not None, "assertion test"
        self.current_chain["links"].append(link)

    def find_chain_object(self, chain_name):
        position = self.chain_map[chain_name]
        return self.chains[position]

    def chain_to_list(self, chain):
        return_value = chain
        if not isinstance(chain, list):
            assert isinstance(chain, str), "chain name is not a string "
            return_value = [chain]
        return return_value

    def reset_chain(self, chain):

        chain = self.chain_to_list(chain)
        for i in chain:
            assert isinstance(i, str), "chain name is not a string"
            k = self.find_chain_object(i)
            k["link_index"] = 0
            links = k["links"]
            for m in links:
                m["active_flag"] = True
                m["init_flag"] = True

    def resume_chain_code(self, chain):
        chain = self.chain_to_list(chain)
        for i in chain:
            assert isinstance(i, str), "chain name is not a string"
            k = self.find_chain_object(i)
            k["suspend"] = False
            k["active"] = True

    def suspend_chain_code(self, chain):
        chain = self.chain_to_list(chain)
        for i in chain:
            assert isinstance(i, str), "chain name is not a string"
            k = self.find_chain_object(i)
            k["active"] = False
            k["suspend"] = True

    def disable_chain_base(self, chain):
        chain = self.chain_to_list(chain)
        #print("disable chains",chain)
        for i in chain:
           
            assert isinstance(i, str), "chain name is not a string"
            k = self.find_chain_object(i)
            k["link_index"] = 0
            k["active"] = False
            if k["term_function"] != None:
               k["term_function"](self,k)
           
 
            links = k["links"]
            for m in links:
                m["active_flag"] = False
                m["init_flag"] = True
        

    def enable_chain_base(self, chain):
        chain = self.chain_to_list(chain)
        #print("enable chains",chain)
        for i in chain:
            assert isinstance(i, str), "chain name is not a string"
            k = self.find_chain_object(i)
            if k["active"] == False:
               if k["init_function"] != None:
                   if k["init_function"](self,k) == False:
                       return # abort enabling chain
 
            k["link_index"] = 0
            k["active"] = True
            links = k["links"]
            for m in links:
                m["active_flag"] = True
                m["init_flag"] = True

    def get_chain_state(self, chain):
        assert isinstance(chain, str), "chain name is not a string"
        obj = self.find_chain_object(chain)
        return obj["active_flag"]

    #
    # Link management
    #

    def find_link_object(self, chain, link):
        links = chain["links"]
        return links[link]


    def enable_link(self, link):
       chain = self.current_chain
       k = self.find_link_object(chain, link)
       k["init_flag"] = True
       k["active_flag"] = True

    def disable_link(self, link):

       chain = self.current_chain
       k = self.find_link_object(chain, link)
       k["init_flag"] = True
       k["active_flag"] = False



    def send_event(self, event_name, event_data=None):
        event = {}
        event["name"] = event_name
        event["data"] = event_data
        self.event_queue.append(event)

    def execute_initialize(self):
        self.event_queue = []
        for j in self.chains:

            if j["auto_start"]:
                self.enable_chain_base( [j["name"]] )

            else:
                j["active"] = False

    def execute_queue(self):
        while True:
            if len(self.event_queue) > 0:
                event = self.event_queue.pop()
                self.execute_event(event)
                
            else:
                
                return
        
    def execute_event(self, event):
        for chain in self.chains:
           
            if chain["active"]:                             
                self.current_chain = chain
                self.execute_chain(chain, event)

    def execute_chain(self, chain, event):
        loopFlag = True
        chain["link_index"] = 0
        while loopFlag:
            loopFlag = self.execute_link(chain, event)

    def execute_link( self, chain, event ):
        try:
           return self.execute_link_a( chain, event )
        except: 
           if chain["except_function"] != None:
               chain["except_function"](self,chain,event)
           exc_info = sys.exc_info()     
           raise exc_info[0].with_traceback(exc_info[1], exc_info[2])
           


    def execute_link_a(self, chain, event):
        link_index = chain["link_index"]
        self.current_link = link_index
        
        if link_index >= len(chain["links"]):
            return False

        link = chain["links"][link_index]
        opcode_name = link["op_code_name"]
        instruction = link["instruction"]
        init_flag = link["init_flag"]
        active_flag = link["active_flag"]
        parameters = link["parameters"]
        return_value = True

        if active_flag:
           if init_flag:
                init_event = {}
                init_event["name"] = "INIT"
                instruction(self, chain, parameters, init_event)

                link["init_flag"] = False
                

           temp = instruction(self, chain, parameters, event)
           return_value = self.check_return_code(chain, link, temp)

        else:
           return_value = True
       
        chain["link_index"] = self.current_link + 1
        return return_value
    
    def queue_event(self, event_name, event_data):
        temp = {}
        temp["name"] = event_name
        temp["data"] = event_data
        self.event_queue.append(temp)

    def check_return_code(self, chain, link, returnCode):

  
        return_value = False

        assert returnCode in self.valid_return_codes, "bad returnCode " + \
            chain["name"]
        if returnCode == "TERMINATE":
            # "TERMINATE ______________ chain name",chain["name"]
            self.disable_chain_base(chain["name"])
            return_value = False


        if returnCode == "CONTINUE":
           
            chain["link_index"] = chain["link_index"] + 1
            return_value = True

        if returnCode == "HALT":
            return_value = False

        if returnCode == "DISABLE":
            
            self.disable_link(chain["link_index"])
            chain["link_index"] = chain["link_index"] + 1
            return_value = True
            

        if returnCode == "RESET":

            self.reset_chain(chain["name"])
            chain["link_index"] = 0
            return_value = False

        if returnCode == "SYSTEM_RESET":
            self.execute_initialize()
            return_value = False

        return return_value

    def execute(self):
     time_stamp = datetime.datetime.today()
     old_day = time_stamp.day
     old_hour = time_stamp.hour
     old_minute = time_stamp.minute
     old_second = time_stamp.second
     self.execute_initialize()
     while True:
       time.sleep(.1)
       # self.cf.queue_event("SUB_SECOND_TICK",10)
       time_stamp = datetime.datetime.today()
       hour = time_stamp.hour
       minute = time_stamp.minute
       second = time_stamp.second
       day = time_stamp.day
       if old_second != second:
         self.queue_event("TIME_TICK", second)
       if old_minute != minute:
         self.queue_event("MINUTE_TICK", minute)
       if old_hour != hour:
         self.queue_event("HOUR_TICK", minute)
       if old_day != day:
         self.queue_event("DAY_TICK", day)

       old_hour = hour
       old_minute = minute
       old_second = second
       old_day = day
       try:
          
          self.execute_queue()
          
       except:
          print( "chain flow exception")
          print( "current chain is ", self.current_chain["name"] )
          print( "current link  is ", self.current_link)
          raise

# test code
if __name__ == "__main__":



    cf = CF_Base_Interpreter()
    cf.define_chain("Chain_1", True)
    cf.insert.log("Chain_1 is printed")
    cf.insert.reset( )
    cf.define_chain("Chain_2", True)
    cf.insert.log("Chain_2 is printed")
    cf.insert.reset()
    print("test ok")
    cf.execute()


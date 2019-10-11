

class Failure_Report(object):

   def __init__(self,handler):
       self.handler = handler
       self.valid_failure = {}
       self.add_failure_point("MASTER_VALVE",set(["OFF","ON","DISABLED","TIMED_OPERATION"]))
       
       
   def add_failure_point(self,failure_point,valid_states):
       self.valid_failure[failure_point] = valid_states


   def failure_report(self,current_op,failure_point,state,details):
       if failure_point in self.valid_failure:
           if state in self.valid_failure[failure_point]:
              print("store stream data",current_op,failure_point,state,details)
           else:
             raise ValueError("invalid state "+state)
       else:
             raise ValueError("invalid failure point "+failure_point)
             
       
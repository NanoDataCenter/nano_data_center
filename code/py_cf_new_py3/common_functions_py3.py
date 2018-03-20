

class Common_Functions(object):

   def __init__( self ):
       pass

   def cf_counter( self, cf_handle, chainObj, parameters, event ):
       return_value = True
       if event["name"] == "INIT":
           parameters.append(0)
           return_value = True
       if event["name"] == "TIME_TICK":
           parameters[-1] = parameters[-1] +1
           if parameters[-1] >= parameters[-2]:
              return_value = False
       return return_value
